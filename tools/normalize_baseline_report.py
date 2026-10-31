"""Add 006 environment and slow-frame fields to a first-version benchmark JSON."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def normalize(raw: dict, refresh_rate_hz: int, display_driver: str,
              display_size: tuple[int, int]) -> dict:
    intervals = raw.get("frame_intervals_ms")
    if not isinstance(intervals, list) or not intervals:
        raise ValueError("Input report must include a non-empty frame_intervals_ms array")
    ordered = sorted(intervals)
    longest = run = over_33 = 0
    for value in intervals:
        if value > 33:
            over_33 += 1
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    result = dict(raw)
    result["display_driver"] = raw.get("driver") or display_driver
    result.pop("driver", None)
    result["display_size"] = list(display_size)
    result["refresh_rate_hz"] = refresh_rate_hz
    result["os"] = raw.get("machine", "unknown")
    result["load"] = {**raw.get("load", {}), "mowers": 5}
    result["over_33ms_frames"] = over_33
    result["longest_over_33ms_run"] = longest
    result["p95_frame_ms"] = round(ordered[math.ceil(.95 * len(ordered)) - 1], 2)
    result["baseline_average_fps"] = None
    result["average_fps_vs_baseline_pct"] = None
    result["measurement_scope"] = (
        "7305e3d packaged baseline; real Windows display window; clock.tick(60)"
    )
    result["acceptance"] = {
        "status": "BASELINE",
        "criteria": "reference sample; not evaluated as feature pass/fail",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--refresh-rate-hz", required=True, type=int)
    parser.add_argument("--display-driver", default="windows")
    parser.add_argument("--display-size", default="1600x1000")
    args = parser.parse_args()
    try:
        display_size = tuple(int(part) for part in args.display_size.lower().split("x"))
        if len(display_size) != 2 or min(display_size) <= 0:
            raise ValueError
    except ValueError:
        parser.error("--display-size must be WIDTHxHEIGHT with positive integers")
    if args.refresh_rate_hz <= 0:
        parser.error("--refresh-rate-hz must be positive")
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    report = normalize(raw, args.refresh_rate_hz, args.display_driver, display_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(f"Normalized {args.input} -> {args.output}")


if __name__ == "__main__":
    main()
