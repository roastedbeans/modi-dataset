#!/usr/bin/env python3
"""Rename the normal captures to {rat}_{origin}_{plmn}_{date|label} across all
copies (2 CSV dirs, 2 pcap dirs, 1 XML dir) and write a reversible rename map.

PLMN is inferred from related dataset context: test/lab -> 00101 (the testbed
core), commercial -> gummei PLMN if present, else the dominant Korean paged
network, else 45005 (the auditor's SK Telecom serving network).

Usage: python3 rename_dataset.py            # dry run (prints, no changes)
       python3 rename_dataset.py --apply     # perform renames
"""
import json, os, re, sys, csv
from collections import Counter

BASE = "/Users/roastedbeans/Documents/Github/modi-project"
RECORDS = os.path.join(BASE, "dataset-origin-analysis/origin_records.json")
MAP_OUT = os.path.join(BASE, "dataset-origin-analysis/rename_map.csv")
DIRS = [  # (directory, extension)
    (os.path.join(BASE, "modi-parser/dataset_csv/spec/normal"), ".csv"),
    (os.path.join(BASE, "modi-dataset/dataset_csv/spec/normal"), ".csv"),
    (os.path.join(BASE, "modi-parser/dataset_csv/ai/normal"), ".csv"),
    (os.path.join(BASE, "modi-dataset/dataset_csv/ai/normal"), ".csv"),
    (os.path.join(BASE, "modi-parser/pcap/compiled/normal_compiled"), ".pcap"),
    (os.path.join(BASE, "modi-dataset/pcap/compiled/normal_compiled"), ".pcap"),
    (os.path.join(BASE, "modi-parser/xml/normal_compiled"), ".xml"),
]

def rat_token(r):
    l = r["rat_label"]
    return "5g" if l.startswith("5G") else "3g" if l.startswith("3G") else "lte"

def plmn_token(r):
    if r["origin_class"] == "test/lab":
        return "00101"
    mcc, mnc = r["plmn"]["gummei_mcc"], r["plmn"]["gummei_mnc"]
    if mcc and mnc:
        return f"{mcc[0]}{int(mnc[0]):02d}"
    kr = {"SK Telecom (KR)": "45005", "KT (KR)": "45008", "LG U+ (KR)": "45006"}
    best, bestn = None, 0
    for k, v in r["imsi_analysis"]["by_home_network"].items():
        if k in kr and v > bestn:
            best, bestn = kr[k], v
    return best or "45005"

def datestamp(fn):
    m = re.match(r"normal_(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_(\d{2})", fn)
    if m:
        return "_".join(m.groups())
    m = re.match(r"normal_(\d+)_(\d+)_(\d+)_lte_(\d+)", fn)
    if m:
        mo, da, yr, idx = m.groups()
        return f"20{yr}_{int(mo):02d}_{int(da):02d}_{idx}"
    return re.sub(r"^normal_", "", fn[:-4]).replace("_", "")

def build_map():
    recs = json.load(open(RECORDS))["records"]
    m = {}
    for r in recs:
        stem = r["file"][:-4]  # drop .csv
        new = f"{rat_token(r)}_{'commercial' if r['origin_class']=='commercial' else 'test'}_{plmn_token(r)}_{datestamp(r['file'])}"
        m[stem] = new
    return m

def main():
    apply = "--apply" in sys.argv
    m = build_map()
    col = [k for k, v in Counter(m.values()).items() if v > 1]
    assert not col, f"COLLISIONS: {col}"
    print(f"{len(m)} files, {len(set(m.values()))} unique new stems, 0 collisions")
    print("PLMN token distribution:", dict(Counter(v.split('_')[2] for v in m.values())))
    print("RAT x origin:", dict(Counter('_'.join(v.split('_')[:2]) for v in m.values())))

    # write reversible map
    with open(MAP_OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["old_stem", "new_stem"])
        for k, v in sorted(m.items()):
            w.writerow([k, v])
    print("wrote", MAP_OUT)

    # rename across all dirs
    renamed, missing = 0, 0
    for d, ext in DIRS:
        if not os.path.isdir(d):
            print("  SKIP missing dir", d); continue
        for stem, new in m.items():
            src, dst = os.path.join(d, stem + ext), os.path.join(d, new + ext)
            if os.path.exists(src):
                if apply:
                    os.rename(src, dst)
                renamed += 1
            else:
                missing += 1
        print(f"  {'renamed' if apply else 'would rename'} in {os.path.relpath(d, BASE)} ({ext})")
    print(f"total file ops: {renamed} | missing: {missing} | mode: {'APPLY' if apply else 'DRY-RUN'}")

if __name__ == "__main__":
    main()
