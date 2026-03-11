#!/usr/bin/env python3
"""barchart - Terminal bar chart and sparkline generator.

Single-file, zero-dependency CLI. Reads data from args, stdin, or CSV.
"""

import sys
import argparse
import csv
import io


BARS = " ▏▎▍▌▋▊▉█"
SPARKS = "▁▂▃▄▅▆▇█"


def cmd_bar(args):
    data = _read_data(args)
    if not data: return 1
    max_val = max(v for _, v in data)
    max_label = max(len(l) for l, _ in data) if data else 0
    width = args.width

    for label, val in data:
        bar_len = int(val / max_val * width) if max_val else 0
        bar = "█" * bar_len
        print(f"  {label:{max_label}s}  {bar} {val:.1f}" if isinstance(val, float) else f"  {label:{max_label}s}  {bar} {val}")


def cmd_horizontal(args):
    """Horizontal stacked view."""
    data = _read_data(args)
    if not data: return 1
    max_val = max(v for _, v in data)
    total = sum(v for _, v in data)
    for label, val in data:
        pct = val / total * 100
        bar_len = int(val / max_val * args.width) if max_val else 0
        bar = "█" * bar_len + "░" * (args.width - bar_len)
        print(f"  {label:15s} [{bar}] {pct:5.1f}% ({val})")


def cmd_spark(args):
    """Sparkline from numbers."""
    nums = args.numbers if args.numbers else [float(l.strip()) for l in sys.stdin if l.strip()]
    if not nums: return 1
    mn, mx = min(nums), max(nums)
    rng = mx - mn if mx != mn else 1
    line = ""
    for n in nums:
        idx = int((n - mn) / rng * 7)
        line += SPARKS[min(idx, 7)]
    print(f"  {line}")
    print(f"  Min: {mn}  Max: {mx}  Avg: {sum(nums)/len(nums):.1f}")


def cmd_histogram(args):
    """Histogram from numbers."""
    nums = args.numbers if args.numbers else [float(l.strip()) for l in sys.stdin if l.strip()]
    if not nums: return 1
    bins = args.bins
    mn, mx = min(nums), max(nums)
    rng = mx - mn if mx != mn else 1
    bin_width = rng / bins
    counts = [0] * bins
    for n in nums:
        idx = min(int((n - mn) / bin_width), bins - 1)
        counts[idx] += 1
    max_count = max(counts)
    for i, count in enumerate(counts):
        lo = mn + i * bin_width
        hi = lo + bin_width
        bar_len = int(count / max_count * 30) if max_count else 0
        bar = "█" * bar_len
        print(f"  {lo:8.1f}-{hi:8.1f}  {bar} {count}")


def _read_data(args):
    if hasattr(args, 'data') and args.data:
        result = []
        for item in args.data:
            if "=" in item:
                k, v = item.split("=", 1)
                result.append((k, float(v)))
            elif ":" in item:
                k, v = item.split(":", 1)
                result.append((k, float(v)))
        return result
    # Read from stdin
    lines = sys.stdin.read().strip().split("\n")
    result = []
    for line in lines:
        if "," in line:
            parts = line.split(",", 1)
        elif "\t" in line:
            parts = line.split("\t", 1)
        elif "=" in line:
            parts = line.split("=", 1)
        else:
            continue
        try:
            result.append((parts[0].strip(), float(parts[1].strip())))
        except (ValueError, IndexError):
            pass
    return result


def main():
    p = argparse.ArgumentParser(prog="barchart", description="Terminal bar charts")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("bar", aliases=["b"], help="Bar chart")
    s.add_argument("data", nargs="*", help="label=value pairs"); s.add_argument("-w", "--width", type=int, default=30)
    s = sub.add_parser("horizontal", aliases=["h"], help="Horizontal with percentages")
    s.add_argument("data", nargs="*"); s.add_argument("-w", "--width", type=int, default=30)
    s = sub.add_parser("spark", aliases=["s"], help="Sparkline")
    s.add_argument("numbers", type=float, nargs="*")
    s = sub.add_parser("histogram", aliases=["hist"], help="Histogram")
    s.add_argument("numbers", type=float, nargs="*"); s.add_argument("-b", "--bins", type=int, default=10)
    args = p.parse_args()
    if not args.cmd: p.print_help(); return 1
    cmds = {"bar": cmd_bar, "b": cmd_bar, "horizontal": cmd_horizontal, "h": cmd_horizontal,
            "spark": cmd_spark, "s": cmd_spark, "histogram": cmd_histogram, "hist": cmd_histogram}
    return cmds[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
