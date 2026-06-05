"""Rename the two mislabeled normal captures to their proper testbed names.

  lte_commercial_45005_2026_04_14_16_02_08  -> lte_test_00101_2026_04_14_16_02_08   (NAS PLMN 00101 = testbed)
  5g_commercial_45005_2026_05_12_15_05_00   -> 5g_test_00101_2026_05_12_15_05_00    (5G SA / nas-5gs = open5gs testbed)

Applied across dataset_csv/spec, dataset_csv/ai, pcap/compiled, the detector copy,
and the dataset_csv_real symlinks, with origin_records.json + rename_map.csv updated
and a reversal map written for full undo.
"""
import os, json, csv

ROOT = "/Users/roastedbeans/Documents/Github/modi-project"
DET_SPEC = ROOT + "/paper-pipeline/experiments/markovs_chain_v2/dataset_csv/spec/normal"
RENAMES = {
    "lte_commercial_45005_2026_04_14_16_02_08": "lte_test_00101_2026_04_14_16_02_08",
    "5g_commercial_45005_2026_05_12_15_05_00":  "5g_test_00101_2026_05_12_15_05_00",
}
FILE_DIRS = [
    (ROOT + "/modi-dataset/dataset_csv/spec/normal", ".csv"),
    (ROOT + "/modi-dataset/dataset_csv/ai/normal", ".csv"),
    (ROOT + "/modi-dataset/pcap/compiled/normal_compiled", ".pcap"),
    (DET_SPEC, ".csv"),
]
SYMLINK_DIRS = [ROOT + "/paper-pipeline/experiments/markovs_chain_v2/dataset_csv_real/normal"]

def main():
    reversal = []
    for d, ext in FILE_DIRS:
        for old, new in RENAMES.items():
            op = os.path.join(d, old + ext); np = os.path.join(d, new + ext)
            if os.path.isfile(op) and not os.path.islink(op):
                os.rename(op, np); reversal.append((np, op))
                print(f"  renamed {os.path.relpath(op, ROOT)} -> {new+ext}")
            else:
                print(f"  SKIP {os.path.relpath(op, ROOT)}")
    for d in SYMLINK_DIRS:
        for old, new in RENAMES.items():
            link = os.path.join(d, old + ".csv")
            if os.path.islink(link):
                os.remove(link)
                os.symlink(os.path.join(DET_SPEC, new + ".csv"), os.path.join(d, new + ".csv"))
                reversal.append(("LINK:" + os.path.join(d, new + ".csv"), "LINK:" + link))
                print(f"  symlink {old}.csv -> {new}.csv")
    # origin_records.json
    orp = ROOT + "/modi-dataset/dataset-origin-analysis/origin_records.json"
    recs = json.load(open(orp))
    rl = recs if isinstance(recs, list) else (recs.get("records") or list(recs.values())[0])
    omap = {o + ".csv": n + ".csv" for o, n in RENAMES.items()}
    for r in rl:
        if r.get("file") in omap:
            r["origin_class"] = "test"
            r["origin_reason"] = "testbed: NAS PLMN 00101" + (" / 5G SA (nas-5gs, open5gs)" if r["file"].startswith("5g") else "")
            r["file"] = omap[r["file"]]
            if r.get("target_name"): r["target_name"] = omap[r["target_name"] + ".csv"][:-4] if (r["target_name"] + ".csv") in omap else r["target_name"]
    json.dump(recs, open(orp, "w"), indent=2)
    print("  updated origin_records.json")
    # rename_map.csv
    rmp = ROOT + "/modi-dataset/dataset-origin-analysis/rename_map.csv"
    rows = list(csv.reader(open(rmp)))
    for row in rows:
        if len(row) >= 2 and row[1] in RENAMES: row[1] = RENAMES[row[1]]
    csv.writer(open(rmp, "w", newline="")).writerows(rows)
    print("  updated rename_map.csv")
    rev = ROOT + "/modi-dataset/dataset-origin-analysis/RELABEL_2FILE_REVERSAL.json"
    json.dump(reversal, open(rev, "w"), indent=2)
    print(f"\nwrote reversal map {os.path.relpath(rev, ROOT)} ({len(reversal)} entries)")

if __name__ == "__main__":
    main()
