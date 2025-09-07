import argparse
from report import pipeline

parser = argparse.ArgumentParser(
        description="Generate LDV review report",
        epilog="""
Example usage:
    python main.py
    or
    python main.py -m 9 -reuse-cache -scrape_dir ./cache_data/LDV_places.jsonl

Arguments:
    -m            Month as integer (1-12). Default is 'current' (uses current month).
    -reuse-cache  If set, reuses cached data for process_input. Default is False.
    -scrape_dir   Directory to scrape data from. Default is './cache_data/LDV_places.jsonl'.

Details:
    This script generates a review report for LDV places. You can specify the month, reuse cached data, and provide a custom scrape directory.
    If no arguments are provided, defaults will be used.
"""
)
parser.add_argument("-m", type=int, help="Month as integer (1-12)", default="current")
parser.add_argument("-reuse-cache", action="store_true", help="Reuse cached data for process_input")
parser.add_argument("-scrape_dir", type=str, help="Directory to scrape data from", default=None)
args = parser.parse_args()

if __name__ == "__main__":
    # Run the pipeline with the provided arguments
    pipeline(
        month=args.m,
        file_path=args.scrape_dir if args.scrape_dir else "./cache_data/LDV_places.jsonl",
        reuse_cache=args.reuse_cache
    )
