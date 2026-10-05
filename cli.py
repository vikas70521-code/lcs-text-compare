"""
cli.py - command line front end for the Text Comparison System.

Examples
    python cli.py samples/doc_a.txt samples/doc_b.txt
    python cli.py a.txt b.txt --mode line
    python cli.py a.txt b.txt --mode char --case-sensitive
"""
import argparse
import sys

from lcs import compare

RED, GREEN, BOLD, RESET = "\033[91m", "\033[92m", "\033[1m", "\033[0m"


def read_file(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as err:
        sys.exit(f"Cannot read '{path}': {err.strerror}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two text files using LCS.")
    parser.add_argument("file_a")
    parser.add_argument("file_b")
    parser.add_argument("--mode", choices=["word", "line", "char"], default="word",
                        help="comparison granularity (default: word)")
    parser.add_argument("--algorithm", choices=["auto", "dp", "hirschberg"], default="auto")
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--keep-punctuation", action="store_true",
                        help="treat 'word,' and 'word' as different (word mode)")
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args()

    res = compare(read_file(args.file_a), read_file(args.file_b), mode=args.mode,
                  ignore_case=not args.case_sensitive,
                  ignore_punct=not args.keep_punctuation, algorithm=args.algorithm)

    use_color = not args.no_color and sys.stdout.isatty()
    print(f"\n{BOLD if use_color else ''}LCS TEXT COMPARISON{RESET if use_color else ''}")
    print("-" * 44)
    print(f"Tokens in A / B : {res['len_a']} / {res['len_b']}  ({res['mode']} level)")
    print(f"LCS length      : {res['lcs_length']}")
    print(f"Similarity      : {res['similarity'] * 100:.1f}%   (2*LCS / (|A|+|B|))")
    print(f"A kept in B     : {res['coverage_a'] * 100:.1f}%    B taken from A: {res['coverage_b'] * 100:.1f}%")
    print(f"Algorithm       : {res['algorithm']}   ({res['time_ms']} ms, {res['cells']:,} cells)")
    print("-" * 44)
    print("Legend: [-removed-] only in A    {+added+} only in B\n")

    sep = res["separator"] or ""
    pieces = []
    for run in res["runs"]:
        text = run["text"]
        if run["type"] == "delete":
            text = f"{RED}[-{text}-]{RESET}" if use_color else f"[-{text}-]"
        elif run["type"] == "insert":
            text = f"{GREEN}{{+{text}+}}{RESET}" if use_color else f"{{+{text}+}}"
        pieces.append(text)
    print((sep if sep != "\n" else "\n").join(pieces))


if __name__ == "__main__":
    main()
