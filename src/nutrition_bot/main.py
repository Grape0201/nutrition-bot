import argparse
from .bot import run_bot

def main():
    parser = argparse.ArgumentParser(description="Nutrition Discord Bot")
    parser.add_argument(
        "--sync", "-s", action="store_true", help="Sync slash commands with Discord"
    )
    args = parser.parse_args()

    run_bot(sync_commands=args.sync)

if __name__ == "__main__":
    main()
