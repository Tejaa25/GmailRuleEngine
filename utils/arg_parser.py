import argparse


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Gmail Rule Engine - Fetch and process emails based on rules"
    )
    parser.add_argument(
        "--init-db", action="store_true", help="Initialize database and exit"
    )
    return parser.parse_args()
