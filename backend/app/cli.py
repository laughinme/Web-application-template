import argparse
import asyncio
import getpass
import os

from app.core.config import get_settings
from app.db.database import Database
from app.service.moderation import ensure_admin


async def create_admin(email: str, password: str) -> str:
    db = Database(get_settings())
    try:
        async with db.unit_of_work() as uow:
            return await ensure_admin(uow, email=email, password=password)
    finally:
        await db.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    admin = commands.add_parser("create-admin", help="create an admin or promote an existing user")
    admin.add_argument("email")
    args = parser.parse_args()

    if args.command == "create-admin":
        password = os.environ.get("ADMIN_PASSWORD") or getpass.getpass("Password: ")
        print(asyncio.run(create_admin(args.email, password)))  # noqa: T201 - CLI output


if __name__ == "__main__":
    main()
