#!/usr/bin/env python3
"""Render the normal-capture origin analysis to a single self-contained HTML
file: graphs and tables only, minimal text. Reads origin_records.json.
"""
import json, html, os, collections

BASE = "/Users/roastedbeans/Documents/Github/modi-project/dataset-origin-analysis"
DATA = json.load(open(os.path.join(BASE, "origin_records.json")))
AGG, RECS = DATA["aggregate"], DATA["records"]

def esc(x):
    return html.escape(str(x)) if x is not None else ""

def join(lst, sep=", ", dash="—"):
    lst = [x for x in (lst or []) if x not in (None, "", "-1")]
    return sep.join(esc(x) for x in lst) if lst else dash

def bands_label(rec):
    seen, out = set(), []
    for b in rec.get("frequency", {}).get("bands", []):
        if b and b.get("band") and f"B{b['band']}" not in seen:
            seen.add(f"B{b['band']}")
            out.append(f"B{b['band']} ({b.get('nominal','')})")
    return ", ".join(out) if out else "—"

def operator_label(rec):
    return ", ".join(rec.get("plmn", {}).get("operator") or []) or "—"

def imsi_label(rec):
    ia = rec.get("imsi_analysis", {})
    n = ia.get("distinct_imsi_count", 0)
    if not n:
        return "0"
    f = ia.get("foreign_paged_count", 0)
    return f"{n}" + (f" ({f} fgn)" if f else "")

def barchart(d, total=None, unit=""):
    if not d:
        return "<p class='muted'>none</p>"
    total = total or max(d.values())
    rows = []
    for k, v in sorted(d.items(), key=lambda kv: -kv[1]):
        pct = (v / total * 100) if total else 0
        rows.append(f"<div class='bar-row'><span class='bar-lab' title='{esc(k)}'>{esc(k)}</span>"
                    f"<span class='bar-track'><span class='bar-fill' style='width:{pct:.1f}%'></span></span>"
                    f"<span class='bar-val'>{esc(v)}{esc(unit)}</span></div>")
    return "<div class='barchart'>" + "".join(rows) + "</div>"

# ---- per-file detail + rows ----
def detail_block(rec):
    sec, ids, ia = rec.get("security", {}), rec.get("identifiers", {}), rec.get("imsi_analysis", {})
    cs, nas, amf = rec.get("cell_selection", {}), rec.get("nas_messages", {}), rec.get("amf", {})
    qrx, qdb = cs.get("q_rxlevmin") or [], cs.get("q_rxlevmin_dbm") or []
    qlabel = ", ".join(f"{v} ({db} dBm)" for v, db in zip(qrx, qdb)) if qrx else "—"
    def kv(k, v): return f"<div class='kv'><span class='k'>{k}</span><span class='v'>{v}</span></div>"
    g = ["<div class='detail-grid'>"]
    g.append(kv("Original name", f"<code>{esc(rec.get('orig_file',''))}</code>"))
    g.append(kv("Origin reason", esc(rec.get("origin_reason", ""))))
    g.append(kv("EARFCNs", join(rec.get("frequency", {}).get("earfcns"))))
    g.append(kv("LTE cell id / PCI", f"{join(rec.get('cell',{}).get('lte_cellidentity'),dash='')} / {join(rec.get('cell',{}).get('lte_physcellid'),dash='')}".strip(" /") or "—"))
    g.append(kv("NR cell id", join(rec.get("cell", {}).get("nr_cellidentity"))))
    g.append(kv("q-RxLevMin", qlabel))
    g.append(kv("cellBarred", join(cs.get("cellbarred"))))
    g.append(kv("AS/NAS algorithms", join(sec.get("advertised_algorithms"))))
    g.append(kv("NAS sec-header EPS/5GS", f"{join(sec.get('nas_eps_security_header'),dash='')} / {join(sec.get('nas_5gs_security_header'),dash='')}".strip(" /") or "—"))
    g.append(kv("AMF region/set/ptr", f"{join(amf.get('region_id'),dash='')}/{join(amf.get('set_id'),dash='')}/{join(amf.get('pointer'),dash='')}".strip("/") or "—"))
    g.append(kv("IMSI home networks", join([f'{k}: {v}' for k, v in ia.get('by_home_network', {}).items()])))
    g.append(kv("EMM / 5GMM msgs", f"{join(nas.get('emm_eps'),dash='')} {join(nas.get('mm_5gs'),dash='')}".strip() or "—"))
    g.append("</div>")
    top = rec.get("top_info", [])[:10]
    if top:
        g.append("<div class='infochips'><span class='k'>Top signalling:</span> " +
                 "".join(f"<span class='chip'>{esc(t['info'])} <b>×{t['n']}</b></span>" for t in top) + "</div>")
    return "".join(g)

def row(rec):
    oc = rec.get("origin_class", "commercial")
    rat = rec.get("rat_label", "unknown")
    dur = rec.get("duration_s")
    dur_s = f"{dur:.0f}s" if isinstance(dur, (int, float)) else "—"
    badge_oc = f"<span class='badge oc-{oc.replace('/','')}' title='{esc(rec.get('origin_reason',''))}'>{esc('TEST' if oc=='test/lab' else 'COMM')}</span>"
    rat_cls = {"LTE (EPS)": "rat-lte", "5G-NSA / LTE+NR": "rat-nsa", "5G": "rat-5g", "3G (UMTS)": "rat-3g"}.get(rat, "rat-unk")
    search = " ".join([rec["file"], oc, rat, operator_label(rec)]).lower()
    return f"""<tr class="frow" data-oc="{oc}" data-rat="{esc(rat)}" data-search="{esc(search)}">
  <td class="fname"><button class="expander" aria-label="expand">▸</button> <code>{esc(rec['file'])}</code></td>
  <td>{badge_oc}</td><td><span class="badge {rat_cls}">{esc(rat)}</span></td>
  <td>{esc(operator_label(rec))}</td><td>{esc(join(rec.get('cell',{}).get('lte_cellidentity')))}</td>
  <td>{esc(bands_label(rec))}</td><td>{esc(join(rec.get('tac',{}).get('lte_rrc')))}</td>
  <td class="num">{imsi_label(rec)}</td><td class="num">{esc(rec.get('rows',0))}</td><td class="num">{esc(dur_s)}</td>
</tr>
<tr class="drow" hidden><td colspan="10">{detail_block(rec)}</td></tr>"""

table_rows = "\n".join(row(r) for r in sorted(RECS, key=lambda r: r["file"]))

# ---- tiles ----
com_n = AGG["by_origin_class"].get("commercial", 0)
lab_n = AGG["by_origin_class"].get("test/lab", 0)
tiles = [("Captures", AGG["n_files"]), ("Commercial", com_n), ("Test / lab", lab_n),
         ("LTE", AGG["by_rat"].get("LTE (EPS)", 0)),
         ("5G (NSA+SA)", AGG["by_rat"].get("5G-NSA / LTE+NR", 0) + AGG["by_rat"].get("5G", 0)),
         ("3G UMTS", AGG["by_rat"].get("3G (UMTS)", 0))]
tiles_html = "".join(f"<div class='tile'><div class='tnum'>{esc(v)}</div><div class='tlab'>{esc(k)}</div></div>" for k, v in tiles)

HTML = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Normal-Capture Origin Analysis</title>
<style>
:root{{--bg:#0f1419;--panel:#161d26;--panel2:#1c2530;--line:#2a3542;--ink:#e6edf3;--mut:#8b98a8;--acc:#4aa3ff}}
*{{box-sizing:border-box}}
body{{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink)}}
code{{font-family:ui-monospace,Menlo,monospace;font-size:.9em}}
.wrap{{max-width:1280px;margin:0 auto;padding:28px 24px 80px}}
h1{{font-size:22px;margin:0 0 4px}}
.sub{{color:var(--mut);margin:0 0 18px;font-size:13px}}
.tiles{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:16px 0}}
.tile{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}}
.tnum{{font-size:22px;font-weight:700}}
.tlab{{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.04em}}
.legend{{color:var(--mut);font-size:12px;margin:6px 0 22px;padding:8px 12px;background:var(--panel);border:1px solid var(--line);border-radius:8px}}
h2{{font-size:16px;margin:26px 0 12px;color:var(--mut);text-transform:uppercase;letter-spacing:.04em;font-weight:600}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 18px}}
.panel h3{{margin:0 0 10px;font-size:13px;color:var(--mut);text-transform:uppercase;letter-spacing:.03em}}
.barchart{{display:flex;flex-direction:column;gap:6px}}
.bar-row{{display:grid;grid-template-columns:165px 1fr 52px;align-items:center;gap:10px;font-size:12px}}
.bar-lab{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.bar-track{{background:var(--panel2);border-radius:5px;height:14px;overflow:hidden}}
.bar-fill{{display:block;height:100%;background:linear-gradient(90deg,#2563eb,#4aa3ff)}}
.bar-val{{text-align:right;color:var(--mut);font-variant-numeric:tabular-nums}}
.controls{{position:sticky;top:0;z-index:5;background:var(--bg);padding:12px 0 8px;display:flex;gap:10px;flex-wrap:wrap;align-items:center;border-bottom:1px solid var(--line)}}
.controls input,.controls select{{background:var(--panel);border:1px solid var(--line);color:var(--ink);border-radius:8px;padding:8px 10px;font-size:13px}}
.controls input{{min-width:280px}}
.controls .count{{color:var(--mut);margin-left:auto;font-size:13px}}
table.files{{width:100%;border-collapse:collapse;margin-top:4px;font-size:12px}}
table.files th,table.files td{{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
table.files thead th{{position:sticky;top:56px;background:var(--panel2);z-index:4;cursor:pointer;white-space:nowrap}}
table.files tbody tr.frow:hover{{background:var(--panel)}}
.num{{text-align:right;font-variant-numeric:tabular-nums}}
.cstart{{color:var(--mut);white-space:nowrap}}
.badge{{display:inline-block;padding:2px 7px;border-radius:6px;font-size:11px;font-weight:600;white-space:nowrap}}
.oc-commercial{{background:rgba(63,185,80,.16);color:#56d364;border:1px solid rgba(63,185,80,.35)}}
.oc-testlab{{background:rgba(210,153,34,.16);color:#e3b341;border:1px solid rgba(210,153,34,.4)}}
.rat-lte{{background:rgba(74,163,255,.16);color:#79c0ff;border:1px solid rgba(74,163,255,.35)}}
.rat-nsa{{background:rgba(188,140,255,.16);color:#d2a8ff;border:1px solid rgba(188,140,255,.35)}}
.rat-5g{{background:rgba(255,123,156,.16);color:#ff9bb3;border:1px solid rgba(255,123,156,.4)}}
.rat-3g{{background:rgba(255,166,87,.14);color:#ffa657;border:1px solid rgba(255,166,87,.35)}}
.rat-unk{{background:rgba(139,152,168,.16);color:var(--mut);border:1px solid var(--line)}}
.expander{{background:none;border:0;color:var(--mut);cursor:pointer;font-size:12px;padding:0 4px 0 0}}
.frow.open .expander{{transform:rotate(90deg)}}
.muted{{color:var(--mut)}}
.detail-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:4px 24px;padding:10px 6px}}
.kv{{display:grid;grid-template-columns:160px 1fr;gap:10px;border-bottom:1px dotted var(--line);padding:3px 0;font-size:12px}}
.kv .k{{color:var(--mut)}}
.infochips{{padding:8px 6px}}
.chip{{display:inline-block;background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:2px 7px;margin:2px;font-size:11px}}
.drow td{{background:#0c1117;border-bottom:2px solid var(--line)}}
footer{{margin-top:36px;color:var(--mut);font-size:11px;border-top:1px solid var(--line);padding-top:14px}}
@media(max-width:1000px){{.tiles{{grid-template-columns:repeat(3,1fr)}}.grid2{{grid-template-columns:1fr}}}}
</style></head>
<body><div class="wrap">
<h1>Normal-Capture Origin Analysis</h1>
<p class="sub"><code>dataset_csv/spec/normal</code> &middot; {AGG['n_files']} benign LTE / 5G / 3G UE-side captures &middot; renamed <code>{{rat}}_{{origin}}_{{plmn}}_{{date}}</code></p>

<div class="tiles">{tiles_html}</div>
<p class="legend"><b>Test / lab</b> = PLMN 00101, LTE Band&nbsp;8, or NR n78/n79 with no commercial identity (srsRAN + Open5GS + LibreSDR). &nbsp;<b>Commercial</b> = 450/xx PLMN (SK Telecom 450/05, KT 450/08) or live paging of real subscriber IMSIs. A commercial identity overrides the band rule.</p>

<h2>Charts</h2>
<div class="grid2">
  <div class="panel"><h3>Origin class</h3>{barchart(AGG['by_origin_class'], AGG['n_files'])}</div>
  <div class="panel"><h3>Radio access technology</h3>{barchart(AGG['by_rat'], AGG['n_files'])}</div>
  <div class="panel"><h3>Operator (PLMN observed)</h3>{barchart(AGG['by_operator'], AGG['n_files'])}</div>
  <div class="panel"><h3>LTE band coverage (files)</h3>{barchart(AGG['band_observations_files'], AGG['n_files'])}</div>
  <div class="panel"><h3>Activity group (original)</h3>{barchart(AGG['by_group'], AGG['n_files'])}</div>
  <div class="panel"><h3>Classification reason</h3>{barchart(AGG['by_origin_reason'], AGG['n_files'])}</div>
</div>

<h2>Per-capture table</h2>
<div class="controls">
  <input type="search" id="q" placeholder="filter by file, operator, RAT…">
  <select id="foc"><option value="">all origins</option><option value="commercial">commercial</option><option value="test/lab">test/lab</option></select>
  <select id="frat"><option value="">all RAT</option><option value="LTE (EPS)">LTE</option><option value="5G-NSA / LTE+NR">5G-NSA</option><option value="5G">5G-SA</option><option value="3G (UMTS)">3G UMTS</option></select>
  <span class="count" id="count"></span>
</div>
<table class="files" id="ftab"><thead><tr>
<th data-c="0">File</th><th data-c="1">Origin</th><th data-c="2">RAT</th><th data-c="3">Operator</th>
<th data-c="4">Cell ID</th><th data-c="5">Band</th><th data-c="6">TAC</th><th data-c="7" class="num">IMSIs</th>
<th data-c="8" class="num">Pkts</th><th data-c="9" class="num">Dur</th>
</tr></thead><tbody>
{table_rows}
</tbody></table>

<footer>Generated from <code>origin_records.json</code> (deterministic extraction + adversarial verification). Files renamed across 2 CSV + 2 pcap + 1 XML folders; reverse map at <code>rename_map.csv</code>.</footer>
</div>
<script>
(function(){{
  var tab=document.getElementById('ftab');
  tab.querySelectorAll('tr.frow').forEach(function(tr){{
    tr.addEventListener('click',function(e){{
      if(e.target.tagName==='A')return;
      var d=tr.nextElementSibling;tr.classList.toggle('open');
      if(d&&d.classList.contains('drow'))d.hidden=!d.hidden;
    }});
  }});
  var q=document.getElementById('q'),foc=document.getElementById('foc'),frat=document.getElementById('frat'),count=document.getElementById('count');
  function apply(){{
    var s=q.value.toLowerCase().trim(),oc=foc.value,rt=frat.value,n=0,total=0;
    tab.querySelectorAll('tr.frow').forEach(function(tr){{
      total++;
      var ok=(!s||tr.dataset.search.indexOf(s)>=0)&&(!oc||tr.dataset.oc===oc)&&(!rt||tr.dataset.rat===rt);
      tr.style.display=ok?'':'none';
      var d=tr.nextElementSibling;
      if(d&&d.classList.contains('drow')&&!ok){{d.hidden=true;tr.classList.remove('open');}}
      if(ok)n++;
    }});
    count.textContent=n+' / '+total+' captures';
  }}
  q.addEventListener('input',apply);foc.addEventListener('change',apply);frat.addEventListener('change',apply);apply();
  var dir={{}};
  tab.querySelectorAll('thead th').forEach(function(th){{
    th.addEventListener('click',function(){{
      var c=+th.dataset.c,body=tab.tBodies[0];
      var pairs=Array.from(body.querySelectorAll('tr.frow')).map(function(r){{return [r,r.nextElementSibling];}});
      dir[c]=!dir[c];var mul=dir[c]?1:-1;
      pairs.sort(function(a,b){{
        var x=a[0].children[c].innerText.trim(),y=b[0].children[c].innerText.trim();
        var nx=parseFloat(x.replace(/[^0-9.\\-]/g,'')),ny=parseFloat(y.replace(/[^0-9.\\-]/g,''));
        if(!isNaN(nx)&&!isNaN(ny))return (nx-ny)*mul;
        return x.localeCompare(y)*mul;
      }});
      pairs.forEach(function(p){{body.appendChild(p[0]);if(p[1])body.appendChild(p[1]);}});
    }});
  }});
}})();
</script></body></html>"""

OUT = os.path.join(BASE, "normal_origin_analysis.html")
with open(OUT, "w") as fh:
    fh.write(HTML)
print("wrote", OUT, f"({len(HTML):,} bytes)")
