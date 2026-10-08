"""Seed (or remove) the fictional DEMO directory.

Run from the backend folder:
    PYTHONPATH=. python scripts/seed_demo_directory.py            # add missing demo records
    PYTHONPATH=. python scripts/seed_demo_directory.py --remove   # delete demo records only
"""
import sys

from app.db.database import SessionLocal
from app.services.demo_seed import remove_demo_directory, seed_demo_directory


def main() -> None:
    db = SessionLocal()
    try:
        if '--remove' in sys.argv:
            print(remove_demo_directory(db))
        else:
            print(seed_demo_directory(db))
    finally:
        db.close()


if __name__ == '__main__':
    main()