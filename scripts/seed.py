import argparse
import csv
import ast
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
import sys

from sqlmodel import Session, select

# Ensure project root is on sys.path when script run directly
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Try to ensure stdout/stderr use UTF-8 to avoid encoding errors on Windows consoles
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    # Python <3.7 or streams not reconfigurable — ignore
    pass

from app.database import init_db, SessionLocal
from app.models import User, Game, Review, Favorite
from app.routes.auth import get_password_hash

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DEFAULT_CSV = Path("data/steam_games.csv")


def parse_args():
    p = argparse.ArgumentParser(description="Seed the database with sample users/games/reviews/favorites")
    p.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to steam games CSV")
    p.add_argument("--limit", type=int, default=200, help="Max number of games to import (0 = no limit)")
    p.add_argument("--skip-existing", action="store_true", help="Skip games that already exist by steam_appid or title")
    return p.parse_args()


def get_csv_path(provided_path: Path):
    return provided_path if provided_path.exists() else DEFAULT_CSV




def parse_list_field(s):
    if not s:
        return []
    s = s.strip()
    try:
        return ast.literal_eval(s)
    except Exception:
        return [x.strip() for x in s.strip("[]").split(",") if x.strip()]


def parse_bool(s):
    if isinstance(s, bool):
        return s
    if not s:
        return False
    s = s.strip().lower()
    return s in ("true", "1", "yes", "y", "t")


def parse_int(s, default=0):
    try:
        return int(float(s))
    except Exception:
        return default


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    if s.lower().startswith("not released"):
        return None
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def main():
    args = parse_args()
    csv_path = get_csv_path(args.csv)
    limit = args.limit
    skip_existing = args.skip_existing

    init_db()
    session = SessionLocal()
    count = 0
    errors = 0

    try:
        # Create sample users (developer + player) if they don't exist
        dev_user = session.exec(select(User).where(User.username == "dev_user")).first()
        if not dev_user:
            dev_user = User(username="dev_user", email="dev@example.com", hashed_password=get_password_hash("password"), role="developer")
            session.add(dev_user)

        player_user = session.exec(select(User).where(User.username == "player_user")).first()
        if not player_user:
            player_user = User(username="player_user", email="player@example.com", hashed_password=get_password_hash("password"), role="player")
            session.add(player_user)

        session.commit()
        session.refresh(dev_user)
        session.refresh(player_user)

        # Read CSV and import games
        if not csv_path.exists():
            logging.error(f"CSV not found: {csv_path.resolve()}")
        else:
            with csv_path.open("r", encoding="utf-8-sig") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    if limit and limit > 0 and count >= limit:
                        break

                    try:
                        steam_appid = None
                        try:
                            steam_appid = int(row.get("steam_appid") or 0)
                        except Exception:
                            steam_appid = None

                        title = (row.get("name") or row.get("title") or "Unknown").strip()

                        # skip duplicates if requested
                        if skip_existing:
                            existing_q = None
                            if steam_appid:
                                existing_q = session.exec(select(Game).where(Game.steam_appid == steam_appid)).first()
                            if not existing_q:
                                existing_q = session.exec(select(Game).where(Game.title == title)).first()
                            if existing_q:
                                logging.info(f"Skipping existing game: {title} ({steam_appid})")
                                continue

                        developers = parse_list_field(row.get("developers", "[]"))
                        publishers = parse_list_field(row.get("publishers", "[]"))
                        categories = parse_list_field(row.get("categories", "[]"))
                        genres = parse_list_field(row.get("genres", "[]"))
                        required_age = parse_int(row.get("required_age", 0))
                        n_achievements = parse_int(row.get("n_achievements", 0))
                        platforms = parse_list_field(row.get("platforms", "[]"))
                        is_released = parse_bool(row.get("is_released", "False"))
                        release_date = parse_date(row.get("release_date", ""))
                        description = (row.get("additional_content") or "")[:2000]

                        # check duplicates by steam_appid/title
                        exists = None
                        if steam_appid:
                            exists = session.exec(select(Game).where(Game.steam_appid == steam_appid)).first()
                        if not exists:
                            exists = session.exec(select(Game).where(Game.title == title)).first()
                        if exists:
                            logging.info(f"Game already exists, skipping: {title} ({steam_appid})")
                            continue

                        g = Game(
                            steam_appid=steam_appid,
                            title=title,
                            developers=developers,
                            publishers=publishers,
                            categories=categories,
                            genres=genres,
                            required_age=required_age,
                            n_achievements=n_achievements,
                            platforms=platforms,
                            is_released=is_released,
                            release_date=release_date,
                            description=description,
                        )
                        session.add(g)
                        count += 1

                        if count % 50 == 0:
                            session.commit()
                    except Exception as e:
                        errors += 1
                        logging.error(f"Failed to import row {count+1}: {e}")

            session.commit()

        # Add some sample favorites and reviews for player_user
        from sqlmodel import select as _select

        game_objs = session.exec(_select(Game).limit(5)).all()
        for i, g in enumerate(game_objs):
            # prevent duplicate favorites
            existing = session.exec(select(Favorite).where((Favorite.user_id == player_user.id) & (Favorite.game_id == g.id))).first()
            if not existing:
                fav = Favorite(user_id=player_user.id, game_id=g.id)
                session.add(fav)

            rev = Review(user_id=player_user.id, game_id=g.id, rating=4, content=f"Sample review #{i+1}")
            session.add(rev)

        session.commit()
        logging.info(f"Imported {count} games, created sample users and {len(game_objs)} favorites/reviews. Errors: {errors}")

    finally:
        session.close()


if __name__ == "__main__":
    main()
