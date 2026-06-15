"""Generate MANIFEST.json for a dataset variant (spec/ or ai/).

Each entry: filename, sha256, n_rows, label (normal|attack), subcategory
(attack scenario slug), rat (LTE|5G|3G from filename prefix), size_bytes.
The manifest is the frozen fingerprint cited by the paper; any experiment
script can verify it before running.
"""
import csv, glob, hashlib, json, os, re, sys

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

def subcat(name):
    base = re.sub(r"\.csv$", "", os.path.basename(name))
    return re.sub(r"_\d+$", "", base)

def rat_of(name):
    b = os.path.basename(name)
    for p, r in (("5g_", "5G"), ("lte_", "LTE"), ("3g_", "3G")):
        if b.startswith(p):
            return r
    return "LTE"  # attack captures are LTE testbed unless prefixed otherwise

def entry(path, label):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    with open(path, newline="") as f:
        n_rows = sum(1 for _ in csv.reader(f)) - 1
    return {"file": os.path.basename(path), "sha256": h.hexdigest(),
            "n_rows": n_rows, "label": label, "subcategory": subcat(path),
            "rat": rat_of(path), "size_bytes": os.path.getsize(path)}

def main(variant_dir):
    out = {"variant": os.path.basename(variant_dir.rstrip("/")), "files": []}
    for label in ("normal", "attack"):
        for p in sorted(glob.glob(os.path.join(variant_dir, label, "*.csv"))):
            out["files"].append(entry(p, label))
    out["n_normal"] = sum(1 for e in out["files"] if e["label"] == "normal")
    out["n_attack"] = sum(1 for e in out["files"] if e["label"] == "attack")
    dest = os.path.join(variant_dir, "MANIFEST.json")
    with open(dest, "w") as f:
        json.dump(out, f, indent=1)
    print(f"{dest}: {out['n_normal']} normal + {out['n_attack']} attack")

if __name__ == "__main__":
    main(sys.argv[1])
