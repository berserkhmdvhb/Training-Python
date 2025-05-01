import sys
import argparse
from colorama import init, Fore, Style
from cf_lib import find_chars

init(autoreset=True)

if sys.platform == "win32":
    import os
    # Force Windows terminal to UTF-8
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')


def threshold_range(value: str) -> float:
    val = float(value)
    if not (0.0 <= val <= 1.0):
        raise argparse.ArgumentTypeError("Threshold must be between 0.0 and 1.0")
    return val


def main():
    parser = argparse.ArgumentParser(
        description="Find Unicode characters by name using substring or fuzzy search."
    )
    parser.add_argument('-q', '--query', type=str, required=True, help='Query string to search Unicode names.')
    parser.add_argument('--fuzzy', action='store_true', help='Enable fuzzy search when no exact matches found.')
    parser.add_argument('--threshold', type=threshold_range, default=0.7,
                        help='Fuzzy match threshold (0.0 to 1.0)')
    args = parser.parse_args()

    if not args.query.strip():
        print("Error: Query string is empty.", file=sys.stderr)
        sys.exit(1)

    try:
        for line in find_chars(args.query, fuzzy=args.fuzzy, threshold=args.threshold):
            parts = line.split('\t')
            if len(parts) >= 3:
                print(f"{Fore.CYAN}{parts[0]}{Style.RESET_ALL}\t"
                      f"{Fore.YELLOW}{parts[1]}{Style.RESET_ALL}\t"
                      f"{parts[2]}")
            else:
                print(line)
    except KeyboardInterrupt:
        print("\nSearch cancelled by user.", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
