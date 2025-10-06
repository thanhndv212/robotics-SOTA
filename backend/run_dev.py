"""Developer entry point for the Robotics SOTA backend.

This script is designed to be invoked directly (``python run_dev.py``) or
through the helper shell script ``start-dev.sh``. It takes care of ensuring the
SQLite database exists, optionally importing seed lab data, and finally running
the Flask development server with sensible defaults. A couple of Flask CLI
commands are also exposed for manual database management.
"""

from __future__ import annotations

import argparse
import logging
import os
from typing import Optional

import click

from app import create_app, db
from app.models import Lab
from app.services.lab_importer import import_initial_data

CONFIG_NAME = os.getenv("FLASK_ENV", "development")
DEFAULT_HOST = os.getenv("DEV_SERVER_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("PORT", 8080))
DEFAULT_DEBUG = os.getenv("FLASK_DEBUG", "1").lower() in {"1", "true", "yes"}

logger = logging.getLogger("run_dev")

app = create_app(CONFIG_NAME)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )


def _ensure_database(
    *,
    skip_import: bool = False,
    force_import: bool = False,
) -> None:
    """Create tables and optionally seed the labs table from CSV."""

    with app.app_context():
        db.create_all()
        lab_count = Lab.query.count()
        logger.info("Lab records present before import: %s", lab_count)

        if skip_import and not force_import:
            logger.debug("Skipping lab import per configuration")
            return

        should_import = lab_count == 0 or force_import
        if not should_import:
            logger.info("Existing lab data detected; skipping import.")
            return

        result: Optional[dict] = import_initial_data()
        if result:
            imported = result.get("imported", 0)
            logger.info("Imported %s lab records from CSV", imported)
        else:
            logger.warning(
                "Lab import returned no data; please verify the CSV file",
            )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Robotics SOTA backend in development mode.",
    )

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Hostname to bind",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Port to bind",
    )

    parser.add_argument(
        "--debug",
        dest="debug",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_DEBUG,
        help="Enable Flask debug mode (default: on)",
    )
    parser.add_argument(
        "--reload",
        dest="reload",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "Force enable/disable the reloader. Defaults to matching --debug."
        ),
    )

    parser.add_argument(
        "--skip-import",
        action="store_true",
        help="Skip importing labs if the table is empty.",
    )
    parser.add_argument(
        "--force-import",
        action="store_true",
        help="Force a labs import even if records already exist.",
    )
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="Only perform database setup, do not launch the server.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Emit additional debug logging output.",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _configure_logging(verbose=args.verbose)

    logger.info(
        "Launching Robotics SOTA backend (host=%s, port=%s, debug=%s)",
        args.host,
        args.port,
        args.debug,
    )

    _ensure_database(
        skip_import=args.skip_import,
        force_import=args.force_import,
    )

    if args.no_run:
        logger.info("Database setup complete; exiting (--no-run)")
        return

    use_reloader = args.reload if args.reload is not None else args.debug
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        use_reloader=use_reloader,
    )


@app.cli.command("init-db")
def init_db_command() -> None:
    """Initialize the database without importing lab data."""

    _ensure_database(skip_import=True, force_import=False)
    click.echo("Database initialized.")


@app.cli.command("import-labs")
@click.option(
    "--force",
    is_flag=True,
    help="Re-import labs even if they already exist.",
)
def import_labs_command(force: bool) -> None:
    """Import lab data from the CSV file."""

    _ensure_database(skip_import=False, force_import=force)
    click.echo("Lab data import completed.")


if __name__ == "__main__":
    main()
