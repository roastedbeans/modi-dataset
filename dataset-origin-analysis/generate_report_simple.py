"""Simple, flat HTML report of the normal-capture categorization (no per-row dropdowns).

Five sections: 3G, LTE testbed, LTE commercial, 5G testbed (SA), 5G commercial (NSA).
Field values are decoded straight from the ai captures: PLMN from the clean gummei/TAI
NAS fields (not the polluted IMSI PLMN list), bands/EARFCN/PCI/cell-id from RRC.
Writes normal_origin_analysis.html.
"""
import csv, glob, os, json, html, collections
csv.field_size_limit(2**31 - 1)
HERE = os.path.dirname(os.path.abspath(__file__))
AID = os.path.join(HERE, "..", "dataset_csv", "ai", "normal")
OUT = os.path.join(HERE, "normal_origin_analysis.html")

def dv(rows, col):
    return {r.get(col, "") for r in rows} - {"", "-1", "__MISSING__", None}
def fmt(s):
    o = sorted(s, key=lambda z: (len(z), z))
    return ", ".join(o) if o else "—"
def e(x):
    return html.escape(str(x))

recs = {}
rj = json.load(open(os.path.join(HERE, "origin_records.json")))
for r in (rj if isinstance(rj, list) else (rj.get("records") or list(rj.values())[0])):
    recs[r["file"]] = r

CATS = ["3G (commercial)", "LTE testbed", "LTE commercial", "5G testbed (SA)", "5G commercial (NSA)"]
groups = {c: [] for c in CATS}

for f in sorted(glob.glob(os.path.join(AID, "*.csv"))):
    b = os.path.basename(f)
    with open(f) as fh:
        rows = list(csv.DictReader(fh))
    rec = recs.get(b, {}); rat = rec.get("rat", {}); rl = rec.get("rat_label", "")
    orig = rec.get("orig_file", "?")
    # clean serving PLMN: gummei or TAI (NOT the IMSI list)
    g_mcc = dv(rows, "e212_gummei_mcc_show") | dv(rows, "e212_tai_mcc_show")
    g_mnc = dv(rows, "e212_gummei_mnc_show") | dv(rows, "e212_tai_mnc_show")
    imsi_mcc = dv(rows, "e212_mcc_show") | g_mcc
    imsi_mnc = dv(rows, "e212_mnc_show") | g_mnc
    is00101 = ("1" in imsi_mcc and "1" in imsi_mnc)
    lband = dv(rows, "lte-rrc_freqbandindicator_show"); nband = dv(rows, "nr-rrc_freqbandindicatornr_show")
    earf = dv(rows, "lte-rrc_carrierfreq_show"); pci = dv(rows, "lte-rrc_physcellid_show")
    cid = dv(rows, "lte-rrc_cellidentity_show") | {"nr:" + x for x in dv(rows, "nr-rrc_cellidentity_show")}
    op = rec.get("plmn", {}).get("operator"); opn = op[0].split(" (")[0] if op else "—"
    if is00101:
        plmn = "00101"
    elif g_mcc and g_mnc:
        plmn = f"{min(g_mcc)}/{int(min(g_mnc)):02d}"
    else:
        plmn = "—"
    band = fmt(lband | {"n" + x for x in nband})
    rowt = (e(orig), e(b), e(plmn), e(opn), e(band), e(fmt(earf)), e(fmt(pci)), e(fmt(cid)))
    if rl.startswith("3G"):
        groups["3G (commercial)"].append(rowt)
    elif rat.get("nr_rrc"):
        groups["5G testbed (SA)" if rat.get("nas_5gs") else "5G commercial (NSA)"].append(rowt)
    elif is00101:
        groups["LTE testbed"].append(rowt)
    else:
        groups["LTE commercial"].append(rowt)

cnt = {c: len(groups[c]) for c in CATS}
testbed = cnt["LTE testbed"] + cnt["5G testbed (SA)"]
commercial = 133 - testbed
tiles = [("Captures", 133), ("Testbed", testbed), ("Commercial", commercial),
         ("3G", cnt["3G (commercial)"]), ("LTE testbed", cnt["LTE testbed"]),
         ("LTE commercial", cnt["LTE commercial"]), ("5G testbed (SA)", cnt["5G testbed (SA)"]),
         ("5G commercial (NSA)", cnt["5G commercial (NSA)"])]
tiles_html = "".join(f"<div class='tile'><div class='tnum'>{v}</div><div class='tlab'>{e(k)}</div></div>" for k, v in tiles)

COLS = ["Original name", "Current name", "PLMN", "Operator", "Band(s)", "EARFCN", "PCI", "Cell-ID"]
def section(cat):
    g = sorted(groups[cat], key=lambda r: r[1])
    head = "".join(f"<th>{e(c)}</th>" for c in COLS)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in g)
    return (f"<h2>{e(cat)} <span class='c'>{len(g)}</span></h2>"
            f"<table class='files'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>")
sections = "\n".join(section(c) for c in CATS)

CSS = """:root{--bg:#0f1419;--panel:#161d26;--panel2:#1c2530;--line:#2a3542;--ink:#e6edf3;--mut:#8b98a8}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink)}
code{font-family:ui-monospace,Menlo,monospace;font-size:.9em}.wrap{max-width:1280px;margin:0 auto;padding:28px 24px 80px}
h1{font-size:22px;margin:0 0 4px}.sub{color:var(--mut);margin:0 0 18px;font-size:13px}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.tnum{font-size:22px;font-weight:700}.tlab{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.04em}
.legend{color:var(--mut);font-size:12px;margin:6px 0 22px;padding:10px 14px;background:var(--panel);border:1px solid var(--line);border-radius:8px}
h2{font-size:15px;margin:30px 0 10px;letter-spacing:.02em}h2 .c{color:var(--mut);font-weight:500;font-size:13px;margin-left:6px}
table.files{width:100%;border-collapse:collapse;margin-top:4px;font-size:12px;table-layout:fixed}
table.files th,table.files td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;word-break:break-word;overflow-wrap:anywhere}
table.files thead th{background:var(--panel2);color:var(--mut);position:sticky;top:0;z-index:2}
table.files tbody tr:hover{background:var(--panel)}
table.files td:nth-child(2){color:#79c0ff}
table.files th:nth-child(1){width:14%}table.files th:nth-child(2){width:16%}table.files th:nth-child(3){width:6%}table.files th:nth-child(4){width:9%}table.files th:nth-child(5){width:8%}table.files th:nth-child(6){width:11%}table.files th:nth-child(7){width:14%}table.files th:nth-child(8){width:22%}
footer{margin-top:36px;color:var(--mut);font-size:11px;border-top:1px solid var(--line);padding-top:14px}
@media(max-width:900px){.tiles{grid-template-columns:repeat(2,1fr)}table.files{display:block;overflow-x:auto}}"""

HTML = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Normal-Capture Categorization</title>
<style>{CSS}</style></head><body><div class="wrap">
<h1>Normal-Capture Radio / Cell Categorization</h1>
<p class="sub"><code>dataset_csv/ai/normal</code> &middot; 133 benign LTE / 5G / 3G UE-side captures &middot; field values decoded from the captures, not inferred</p>
<div class="tiles">{tiles_html}</div>
<p class="legend"><b>Tells.</b> LTE testbed = NAS PLMN <b>00101</b>. 5G testbed = <b>5G SA</b> (<code>nas-5gs</code>, open5gs core). Commercial = real network — LTE, <b>5G NSA</b> (n78 + <code>nas-eps</code>, real SKT anchor), 3G. PLMN is the clean gummei / TAI NAS value (the IMSI PLMN-list field is polluted and not used).</p>
{sections}
<footer>Generated by <code>generate_report_simple.py</code>. Testbed {testbed} / commercial {commercial}. Two files re-labeled to test this revision: <code>lte_test_00101_2026_04_14_16_02_08</code>, <code>5g_test_00101_2026_05_12_15_05_00</code>.</footer>
</div></body></html>"""

open(OUT, "w").write(HTML)
print("wrote", OUT, "| counts:", cnt, "| testbed", testbed, "commercial", commercial)
