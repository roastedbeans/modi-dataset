#!/usr/bin/env python3
"""Origin extraction + test/commercial classification for the normal captures.

Reads the AI-preprocessed CSVs (1945 cols, richer than spec) and classifies each
capture as commercial vs test/lab using a MULTI-FIELD MARKER set discovered from
the ground-truth files (PLMN 00101 vs gummei 450/xx). Each record records exactly
which markers fired, so the verdict is auditable.

Marker set:
  COMMERCIAL (any one wins): real gummei PLMN (450/xx), paged real-subscriber IMSI,
    NR band n78, large/real MME group (nas mme_grp_id != 2 or lte-rrc mmegi present),
    registered TAC != 7.
  TEST (no commercial marker, plus a test marker): PLMN 00101, registered TAC 7,
    Open5GS default core (MME code 1 + MME group 2), or SIB1-TAC 57 with LTE Band 8.

Source fields (ai variant): e212_gummei_*, e212_imsi, nr-rrc_freqbandindicatornr,
lte-rrc_freqbandindicator, nas-eps_emm_tai_tac, lte-rrc_trackingareacode,
nas-eps_emm_mme_code/grp_id, lte-rrc_mmec/mmegi, nas-5gs_amf_*, lte-rrc_cellidentity,
lte-rrc_referencesignalpower, lte-rrc_p_max, plus the usual RAT/security/identity cols.
"""
import csv, glob, json, os, re, struct, datetime
from collections import Counter

csv.field_size_limit(10_000_000)
ROOT = "/Users/roastedbeans/Documents/Github/modi-project"
AI = os.path.join(ROOT, "modi-parser/dataset_csv/ai/normal")
SPEC = os.path.join(ROOT, "modi-parser/dataset_csv/spec/normal")  # human-readable info/packet_type
PCAP = os.path.join(ROOT, "modi-dataset/pcap/compiled/normal_compiled")  # real capture timestamps
KST = datetime.timezone(datetime.timedelta(hours=9))  # captures are Seoul local time
HERE = os.path.join(ROOT, "modi-dataset/dataset-origin-analysis")
RENAME_MAP = os.path.join(HERE, "rename_map.csv")
OUT = os.path.join(HERE, "origin_records.json")

NULLS = {"-1", "", "None", None, "nan", "NaN"}
def ok(v):
    return v not in NULLS

# ---- reference tables ------------------------------------------------------
PLMN = {("450", "5"): "SK Telecom (KR 450/05)", ("450", "05"): "SK Telecom (KR 450/05)",
        ("450", "8"): "KT (KR 450/08)", ("450", "08"): "KT (KR 450/08)",
        ("450", "6"): "LG U+ (KR 450/06)", ("450", "06"): "LG U+ (KR 450/06)",
        ("1", "1"): "Test network 00101 (srsRAN/Open5GS lab)",
        ("001", "01"): "Test network 00101 (srsRAN/Open5GS lab)"}
TEST_PLMNS = {("1", "1"), ("001", "01")}
def plmn_name(mcc, mnc):
    if not (ok(mcc) and ok(mnc)):
        return None
    return PLMN.get((mcc, mnc), f"Unmapped commercial PLMN {mcc}/{mnc}")

IMSI_HOME = {"45005": "SK Telecom (KR)", "45003": "SK Telecom (KR)", "45008": "KT (KR)",
             "45002": "KT (KR)", "45004": "KT (KR)", "45006": "LG U+ (KR)", "45010": "LG U+ (KR)",
             "44020": "SoftBank (JP)", "44010": "NTT docomo (JP)",
             "51502": "Globe (PH) - auditor UE", "51503": "Smart (PH)", "51505": "Sun/Smart (PH)",
             "51511": "Smart (PH)", "51518": "Smart (PH)", "00101": "Test 00101"}
AUDITOR_IMSI = "515027302508642"
def imsi_home(imsi):
    if not imsi or len(imsi) < 5:
        return None
    return IMSI_HOME.get(imsi[:5], f"MCC {imsi[:3]} / MNC {imsi[3:5]}")

# LTE DL EARFCN -> (lo, hi, band, FDL_low) for the channel-centre figure.
LTE_BANDS = [(0,599,1,2110),(600,1199,2,1930),(1200,1949,3,1805),(1950,2399,4,2110),
    (2400,2649,5,869),(2750,3449,7,2620),(3450,3799,8,925),(5180,5279,13,746),
    (6150,6449,20,816),(9210,9659,28,758)]
BAND_NOMINAL = {1:"2100 MHz",3:"1800 MHz",5:"850 MHz",7:"2600 MHz",8:"900 MHz",28:"700 MHz",
                20:"800 MHz",13:"700 MHz"}
def earfcn_band(e):
    try:
        e = int(e)
    except (TypeError, ValueError):
        return None
    for lo, hi, band, fdl in LTE_BANDS:
        if lo <= e <= hi:
            return {"earfcn": e, "band": band, "center_mhz": round(fdl + 0.1*(e-lo), 1),
                    "nominal": BAND_NOMINAL.get(band, f"B{band}")}
    return {"earfcn": e, "band": None, "center_mhz": None, "nominal": None}

# ---- filename grouping (from original normal_* names) ----------------------
def file_group(name):
    if re.match(r"normal_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}", name):
        return "timestamped DIAG session"
    if name.startswith("normal_3_18_26_lte"):
        return "LTE batch (2026-03-18)"
    if name.startswith("normal_udp_streaming"):
        return "UDP streaming"
    if name.startswith("normal_voltecall"):
        return "VoLTE call"
    if name.startswith("normal_5g_session"):
        return "5G session"
    if name.startswith("normal_mixed"):
        return "mixed activity"
    if name.startswith("normal_data"):
        return "data session"
    return "other"

def capture_start(name):
    m = re.match(r"normal_(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_(\d{2})", name)
    if m:
        y, mo, d, h, mi, s = m.groups()
        return f"{y}-{mo}-{d} {h}:{mi}:{s}"
    if name.startswith("normal_3_18_26_lte"):
        return "2026-03-18 (LTE batch)"
    return None

def pcap_epoch(cur_csv_name):
    """First-packet epoch from the matching pcap (real capture time)."""
    p = os.path.join(PCAP, cur_csv_name[:-4] + ".pcap")
    if not os.path.exists(p):
        return None
    with open(p, "rb") as f:
        m = f.read(24)[:4]
        endian = ">" if m in (b"\xa1\xb2\xc3\xd4", b"\xa1\xb2\x3c\x4d") else \
                 "<" if m in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1") else None
        if endian is None:
            return None
        ph = f.read(16)
        if len(ph) < 16:
            return None
        return struct.unpack(endian + "IIII", ph)[0]

def datestamp(rec):
    """YYYY_MM_DD_HH_MM_SS. Use the original filename timestamp when present,
    otherwise the real capture time from the pcap (Seoul local time). No labels."""
    m = re.match(r"normal_(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_(\d{2})", rec["orig_file"])
    if m:
        return "_".join(m.groups())
    ep = pcap_epoch(rec["file"])
    if ep:
        return datetime.datetime.fromtimestamp(ep, KST).strftime("%Y_%m_%d_%H_%M_%S")
    return re.sub(r"^normal_", "", rec["orig_file"][:-4]).replace("_", "")

# ---- column helpers --------------------------------------------------------
def dset(rows, col):
    return sorted({r.get(col) for r in rows if ok(r.get(col))}, key=lambda x: (len(x), x))

def present(rows, prefix):
    for r in rows:
        for k, v in r.items():
            if k.startswith(prefix) and k.endswith("_show") and ok(v):
                return True
    return False

SEC_FLAGS = {"nas-5gs_mm_5g_ea0":"5G-EA0 (null)","nas-5gs_mm_128_5g_ea1":"128-5G-EA1",
    "nas-5gs_mm_128_5g_ea2":"128-5G-EA2","nas-5gs_mm_128_5g_ea3":"128-5G-EA3",
    "nas-5gs_mm_ia0":"5G-IA0 (null)","nas-5gs_mm_5g_128_ia1":"128-5G-IA1",
    "nas-5gs_mm_5g_128_ia2":"128-5G-IA2","nas-5gs_mm_5g_128_ia3":"128-5G-IA3",
    "nas-eps_emm_eea0":"EEA0 (null)","nas-eps_emm_128eea1":"128-EEA1","nas-eps_emm_128eea2":"128-EEA2",
    "nas-eps_emm_eea3":"EEA3","nas-eps_emm_eia0":"EIA0 (null)","nas-eps_emm_128eia1":"128-EIA1",
    "nas-eps_emm_128eia2":"128-EIA2","nas-eps_emm_eia3":"EIA3"}

def load_orig_map():
    """current new_stem -> original normal_* stem (for group/date parsing)."""
    m = {}
    if os.path.exists(RENAME_MAP):
        for row in csv.DictReader(open(RENAME_MAP)):
            m[row["new_stem"]] = row["old_stem"]
    return m

ORIG = load_orig_map()

def spec_info(cur):
    """packet_type/direction/top_info from the spec variant (ai encodes these to numbers)."""
    p = os.path.join(SPEC, cur)
    if not os.path.exists(p):
        return {}, {}, []
    rows = list(csv.DictReader(open(p, newline="")))
    pt = dict(Counter(r.get("packet_type", "") for r in rows))
    dr = dict(Counter(r.get("direction", "") for r in rows))
    ti = [{"info": k, "n": n} for k, n in
          Counter(r.get("info", "") for r in rows if ok(r.get("info"))).most_common(15)]
    return pt, dr, ti

def extract(path):
    cur = os.path.basename(path)
    stem = cur[:-4]
    orig = ORIG.get(stem, stem) + ".csv"
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    rec = {"file": cur, "orig_file": orig, "group": file_group(orig),
           "capture_start": capture_start(orig), "rows": len(rows)}
    if not rows:
        rec["empty"] = True
        rec["rat_label"] = "unknown"
        rec["origin_class"], rec["origin_reason"] = "unknown", "empty capture"
        rec["markers"] = {"commercial": [], "test": []}
        rec["plmn"] = {"gummei_mcc": [], "gummei_mnc": [], "is_00101": False, "operator": None}
        rec["frequency"] = {"lte_bandind": [], "nr_bandind": [], "earfcns": [], "bands": []}
        rec["imsi_analysis"] = {"distinct_imsi_count": 0, "by_home_network": {},
                                "foreign_paged_count": 0, "auditor_ue_present": False, "examples": []}
        return rec

    ts = [float(r["timestamp"]) for r in rows if ok(r.get("timestamp"))
          and re.match(r"^-?\d+(\.\d+)?$", r.get("timestamp", ""))]
    rec["duration_s"] = round(max(ts) - min(ts), 2) if ts else None
    rec["packet_type"], rec["direction"], rec["top_info"] = spec_info(cur)

    # ---- RAT ----
    has_lte = present(rows, "lte-rrc_"); has_nr = present(rows, "nr-rrc_")
    has_eps = present(rows, "nas-eps_"); has_5gs = present(rows, "nas-5gs_")
    rec["rat"] = {"lte_rrc": has_lte, "nr_rrc": has_nr, "nas_eps_4g": has_eps, "nas_5gs": has_5gs}
    rrc_rows = rec["packet_type"].get("rrc", 0) + rec["packet_type"].get("nas+rrc", 0)
    if has_nr and has_lte:
        rat = "5G-NSA / LTE+NR"
    elif has_nr or has_5gs:
        rat = "5G"
    elif has_lte or has_eps:
        rat = "LTE (EPS)"
    elif rrc_rows:
        rat = "3G (UMTS)"
    else:
        rat = "unknown"
    rec["rat_label"] = rat

    # ---- PLMN / identity ----
    g_mcc = dset(rows, "e212_gummei_mcc_show"); g_mnc = dset(rows, "e212_gummei_mnc_show")
    imsis = dset(rows, "e212_imsi_show")
    plmns = {(m, n) for m in g_mcc for n in g_mnc}
    imsi_plmns = {(im[:3], str(int(im[3:5]))) for im in imsis if len(im) >= 5 and im[:5].isdigit()}
    is_00101 = bool((plmns | imsi_plmns) & TEST_PLMNS)
    commercial_ops = sorted({plmn_name(m, n) for m, n in plmns
                             if plmn_name(m, n) and (m, n) not in TEST_PLMNS})
    rec["plmn"] = {"gummei_mcc": g_mcc, "gummei_mnc": g_mnc, "is_00101": is_00101,
                   "operator": commercial_ops or None,
                   "nr_plmn_infolist": dset(rows, "nr-rrc_plmn_identityinfolist_show"),
                   "selected_plmn": dset(rows, "lte-rrc_selectedplmn_identity_show")}
    home_ct = Counter(imsi_home(im) for im in imsis if imsi_home(im))
    foreign = [im for im in imsis if im[:3] not in ("450", "001") and im[:5] != "51502"]
    rec["imsi_analysis"] = {"distinct_imsi_count": len(imsis),
        "by_home_network": dict(home_ct.most_common()), "foreign_paged_count": len(foreign),
        "auditor_ue_present": AUDITOR_IMSI in imsis, "examples": imsis[:6]}

    # ---- bands (direct freqbandindicator + EARFCN centres) ----
    lte_bandind = dset(rows, "lte-rrc_freqbandindicator_show")
    nr_bandind = dset(rows, "nr-rrc_freqbandindicatornr_show")
    earfcns = sorted(set(dset(rows, "lte-rrc_carrierfreq_show") + dset(rows, "lte-rrc_dl_carrierfreq_show")),
                     key=lambda x: int(x) if x.lstrip('-').isdigit() else 0)
    rec["frequency"] = {"lte_bandind": lte_bandind, "nr_bandind": nr_bandind,
        "earfcns": earfcns, "bands": [earfcn_band(e) for e in earfcns]}

    # ---- cells ----
    rec["cell"] = {"lte_cellidentity": dset(rows, "lte-rrc_cellidentity_show"),
        "lte_physcellid": dset(rows, "lte-rrc_physcellid_show"),
        "lte_targetphyscellid": dset(rows, "lte-rrc_targetphyscellid_show"),
        "nr_cellidentity": dset(rows, "nr-rrc_cellidentity_show")}

    # ---- TAC ----
    rec["tac"] = {"lte_rrc": dset(rows, "lte-rrc_trackingareacode_show"),
        "nas_eps_reg": dset(rows, "nas-eps_emm_tai_tac_show"),
        "nas_5gs": dset(rows, "nas-5gs_tac_show"),
        "nr_rrc": dset(rows, "nr-rrc_trackingareacode_show")}

    # ---- core network identity ----
    rec["core_id"] = {"lte_mmec": dset(rows, "lte-rrc_mmec_show"),
        "lte_mmegi": dset(rows, "lte-rrc_mmegi_show"),
        "nas_mme_code": dset(rows, "nas-eps_emm_mme_code_show"),
        "nas_mme_grp": dset(rows, "nas-eps_emm_mme_grp_id_show"),
        "amf_region": dset(rows, "nas-5gs_amf_region_id_show"),
        "amf_set": dset(rows, "nas-5gs_amf_set_id_show"),
        "amf_pointer": dset(rows, "nas-5gs_amf_pointer_show")}

    # ---- cell config (testbed defaults vs real) ----
    qrx = dset(rows, "lte-rrc_q_rxlevmin_show")
    rec["cell_config"] = {"q_rxlevmin": qrx,
        "q_rxlevmin_dbm": [f"-{2*int(v)}" for v in qrx if v.lstrip('-').isdigit()],
        "referencesignalpower": dset(rows, "lte-rrc_referencesignalpower_show"),
        "p_max": dset(rows, "lte-rrc_p_max_show"),
        "cellbarred": dset(rows, "lte-rrc_cellbarred_show"),
        "cellreselectionpriority": dset(rows, "lte-rrc_cellreselectionpriority_show")}

    # ---- security ----
    sec_algos = []
    for col, label in SEC_FLAGS.items():
        if any(x in ("1", "Supported", "true", "True") for x in dset(rows, col + "_show")):
            sec_algos.append(label)
    rec["security"] = {"lte_rrc_ciphering": dset(rows, "lte-rrc_cipheringalgorithm_show"),
        "lte_rrc_integrity": dset(rows, "lte-rrc_integrityprotalgorithm_show"),
        "nr_rrc_ciphering": dset(rows, "nr-rrc_cipheringalgorithm_show"),
        "nas_eps_security_header": dset(rows, "nas-eps_security_header_type_show"),
        "nas_5gs_security_header": dset(rows, "nas-5gs_security_header_type_show"),
        "advertised_algorithms": sorted(set(sec_algos))}
    rec["identifiers"] = {"imsi": imsis, "suci_msin": dset(rows, "nas-5gs_mm_suci_msin_show"),
        "5g_tmsi": dset(rows, "nas-5gs_5g_tmsi_show"), "m_tmsi": dset(rows, "nas-eps_emm_m_tmsi_show"),
        "imeisv": dset(rows, "nas-5gs_mm_imeisv_show")}
    rec["nas_messages"] = {"mm_5gs": dset(rows, "nas-5gs_mm_message_type_showname"),
        "emm_eps": dset(rows, "nas-eps_nas_msg_emm_type_showname")}

    classify(rec)
    return rec

def classify(rec):
    """Marker-based test/commercial classification. Commercial markers win."""
    cm, tm = [], []  # commercial / test markers that fired
    plmn = rec["plmn"]; core = rec["core_id"]; tac = rec["tac"]; freq = rec["frequency"]
    ia = rec["imsi_analysis"]

    # COMMERCIAL markers
    if plmn["operator"]:
        cm.append("gummei " + ", ".join(plmn["operator"]))
    if not plmn["is_00101"] and any(not im.startswith("001") for im in rec["identifiers"]["imsi"]):
        cm.append(f"real subscriber IMSI ({ia['foreign_paged_count']} foreign)")
    if "78" in freq["nr_bandind"]:
        cm.append("NR band n78 (commercial 5G)")
    comm_mme_grp = [v for v in core["nas_mme_grp"] if v != "2"]
    if comm_mme_grp or core["lte_mmegi"]:
        cm.append("real MME group " + ",".join(sorted(set(comm_mme_grp + core["lte_mmegi"]))[:3]))
    comm_reg_tac = [v for v in tac["nas_eps_reg"] if v != "7"]
    if comm_reg_tac:
        cm.append("registered TAC " + ",".join(comm_reg_tac[:3]))

    # TEST markers: NAS-core identity + SIB serving-cell config. These are not
    # polluted by neighbour/capability lists, unlike RRC band/TAC fields.
    if plmn["is_00101"]:
        tm.append("PLMN 00101")
    if "7" in tac["nas_eps_reg"]:
        tm.append("registered TAC 7 (Open5GS)")
    if "1" in core["nas_mme_code"] and "2" in core["nas_mme_grp"]:
        tm.append("Open5GS core (MME code 1 / group 2)")
    if "0" in rec["cell_config"]["referencesignalpower"]:
        tm.append("referenceSignalPower 0 (srsRAN cell)")

    # Supporting (NOT decisive) context: RRC band/TAC seen, polluted by neighbours.
    support = []
    if "57" in tac["lte_rrc"]:
        support.append("SIB1-TAC 57 seen")
    if "8" in freq["lte_bandind"]:
        support.append("LTE Band 8 seen")

    if cm:
        oc, reason = "commercial", cm[0]
    elif tm:
        oc, reason = "test/lab", tm[0]
    elif rec["rat_label"] != "unknown":
        oc, reason = "commercial", "no testbed marker (commercial network default)"
    else:
        oc, reason = "unknown", "no signalling / no marker"
    rec["origin_class"] = oc
    rec["origin_reason"] = reason
    rec["markers"] = {"commercial": cm, "test": tm, "supporting": support}

# ---- target name -----------------------------------------------------------
def rat_token(rec):
    l = rec["rat_label"]
    return "5g" if l.startswith("5G") else "3g" if l.startswith("3G") else "lte" if l.startswith("LTE") else "unk"

def plmn_token(rec):
    if rec["origin_class"] == "test/lab":
        return "00101"
    if rec["origin_class"] == "unknown":
        return "noplmn"
    mcc, mnc = rec["plmn"]["gummei_mcc"], rec["plmn"]["gummei_mnc"]
    if mcc and mnc:
        return f"{mcc[0]}{int(mnc[0]):02d}"
    kr = {"SK Telecom (KR)": "45005", "KT (KR)": "45008", "LG U+ (KR)": "45006"}
    best, bestn = None, 0
    for k, v in rec["imsi_analysis"]["by_home_network"].items():
        if k in kr and v > bestn:
            best, bestn = kr[k], v
    return best or "45005"

def origin_token(rec):
    return {"commercial": "commercial", "test/lab": "test", "unknown": "unknown"}[rec["origin_class"]]

def target_name(rec):
    return f"{rat_token(rec)}_{origin_token(rec)}_{plmn_token(rec)}_{datestamp(rec)}.csv"

def main():
    files = sorted(glob.glob(os.path.join(AI, "*.csv")))
    records = [extract(f) for f in files]
    for r in records:
        r["target_name"] = target_name(r)

    band_ct = Counter()
    for r in records:
        for b in set(int(x) for x in r["frequency"]["lte_bandind"] if x.isdigit()):
            band_ct[f"B{b} ({BAND_NOMINAL.get(b, '?')})"] += 1
    agg = {"n_files": len(records),
        "by_group": dict(Counter(r["group"] for r in records)),
        "by_rat": dict(Counter(r["rat_label"] for r in records)),
        "by_origin_class": dict(Counter(r["origin_class"] for r in records)),
        "by_origin_reason": dict(Counter(r["origin_reason"] for r in records).most_common()),
        "by_operator": dict(Counter((r["plmn"]["operator"] or ["(no PLMN observed)"])[0] for r in records)),
        "lte_band_files": dict(band_ct.most_common()),
        "nr_band_files": dict(Counter(b for r in records for b in set(r["frequency"]["nr_bandind"])).most_common()),
        "total_packets": sum(r.get("rows", 0) for r in records),
        "reclassified": sum(1 for r in records if r["target_name"] != r["file"])}

    out = {"origin_model": {
        "source": "ai variant (1945 cols)",
        "markers_commercial": "gummei 450/xx, real-subscriber IMSI, NR band n78, real MME group (!=2), registered TAC !=7",
        "markers_test": "PLMN 00101, registered TAC 7, Open5GS core (MME code 1 + group 2), or SIB1-TAC 57 + LTE Band 8",
        "rule": "any commercial marker -> commercial; else any test marker -> test/lab; else unknown",
    }, "aggregate": agg, "records": records}
    json.dump(out, open(OUT, "w"), indent=2)
    print("wrote", OUT)
    print(json.dumps({k: agg[k] for k in ["n_files", "by_origin_class", "by_rat", "by_origin_reason", "reclassified"]}, indent=2))

if __name__ == "__main__":
    main()
