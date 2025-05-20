#!/usr/bin/env python3
"""
preprocess.py

Usage:
    python -u preprocess.py --input crows_pairs   --output data/cp.json
    python -u preprocess.py --input stereoset     --output data/ss.json
    python -u preprocess.py --input crows_pairs   --output out.json --check   # extra check

Key fixes for Estonian/UTF‑8 text:
  • Read CSV with utf‑8‑sig (eats BOM if one sneaks in)
  • Always open text files with explicit encoding
  • json.dump(..., ensure_ascii=False) so “ä/õ/…” stay literal
  • newline="" on CSV opens to avoid stray blank lines on Windows
"""

import argparse
import csv
import json
import pprint
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, choices=["crows_pairs", "stereoset"],
                   help="Which dataset to preprocess")
    p.add_argument("--output", required=True, help="Path to write cleaned JSON")
    p.add_argument("--check", action="store_true",
                   help="Print the first three rows after reading (debug aid)")
    return p.parse_args()


def preprocess_crows_pairs(csv_path: str = "est_CineBias.csv") -> list[dict]:
    """Extract stereotypical / anti‑stereotypical sentences from Crows‑Pairs."""
    rows: list[dict] = []
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "direction"      : row["stereo_antistereo"],
                "bias_type"      : row["bias_type"],
                "stereotype"     : row["sent_more"],
                "anti-stereotype": row["sent_less"],
            })
    return rows


def preprocess_stereoset(json_path: str = "ss.json") -> list[dict]:
    """Extract stereotypical / anti‑stereotypical sentences from StereoSet."""
    with open(json_path, encoding="utf-8") as f:
        raw = json.load(f)

    rows: list[dict] = []
    for ann in raw["data"]["intrasentence"]:
        ex = {"bias_type": ann["bias_type"]}
        for s in ann["sentences"]:
            ex[s["gold_label"]] = s["sentence"]
        rows.append(ex)
    return rows


def main() -> None:
    args = parse_args()

    if args.input == "crows_pairs":
        data = preprocess_crows_pairs()
    else:  # stereoset
        data = preprocess_stereoset()

    if args.check:
        print("‑‑ First 3 parsed rows (repr) ‑‑")
        pprint.pp(data[:3], width=120)
        print("‑‑‑‑‑‑‑‑‑‑‑‑\n")

    # Ensure we keep literal Unicode in the JSON file
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fw:
        json.dump(data, fw, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()

