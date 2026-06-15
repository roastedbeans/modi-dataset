#!/usr/bin/env python3
"""Combine per-time-window CSVs into one CSV per session, per type.

For each 5g_sessionN folder, the per-time-window CSVs are concatenated into a
single session-level CSV. The two file types are kept separate:
  - *_essential.csv     -> combined/5g_sessionN_essential.csv
  - *_ai_essential.csv  -> combined/5g_sessionN_ai_essential.csv

A leading `source_time_window` column records which time-window file each row
came from. ai_essential files have two schemas, so columns are aligned to the
ordered union of all headers across the session (missing cells left blank).
"""
import csv
import glob
import os
import sys

csv.field_size_limit(sys.maxsize)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "combined")
SESSIONS = ["5g_session1", "5g_session2", "5g_session3", "5g_session4", "5g_session5"]
PREFIX = "diag_log_"


def time_window_key(path, suffix):
    base = os.path.basename(path)
    base = base[len(PREFIX):] if base.startswith(PREFIX) else base
    if base.endswith(suffix):
        base = base[: -len(suffix)]
    return base


def files_for(session, suffix):
    """Return non-empty files ending in `suffix`, excluding the ai variant when
    suffix is the plain '_essential.csv'."""
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, session, "*" + suffix))):
        if suffix == "_essential.csv" and p.endswith("_ai_essential.csv"):
            continue
        if os.path.getsize(p) == 0:
            print(f"  skip empty: {os.path.basename(p)}")
            continue
        out.append(p)
    return out


def combine(session, suffix, out_name):
    paths = files_for(session, suffix)
    if not paths:
        print(f"  no files for {suffix}")
        return

    # Pass 1: build ordered union of columns across all files in the session.
    union = []
    seen = set()
    headers = {}
    for p in paths:
        with open(p, newline="") as fh:
            header = next(csv.reader(fh), [])
        headers[p] = header
        for col in header:
            if col not in seen:
                seen.add(col)
                union.append(col)

    out_cols = ["source_time_window"] + union
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, out_name)

    total_rows = 0
    with open(out_path, "w", newline="") as out_fh:
        writer = csv.DictWriter(out_fh, fieldnames=out_cols, extrasaction="ignore")
        writer.writeheader()
        for p in paths:
            tw = time_window_key(p, suffix)
            with open(p, newline="") as fh:
                reader = csv.DictReader(fh)
                n = 0
                for row in reader:
                    row["source_time_window"] = tw
                    writer.writerow(row)
                    n += 1
                total_rows += n
            print(f"  + {os.path.basename(p)}: {n} rows")
    print(f"  => {out_name}: {len(paths)} files, {total_rows} data rows, {len(out_cols)} cols\n")


def main():
    for session in SESSIONS:
        print(f"== {session} ==")
        combine(session, "_essential.csv", f"{session}_essential.csv")
        combine(session, "_ai_essential.csv", f"{session}_ai_essential.csv")


if __name__ == "__main__":
    main()
