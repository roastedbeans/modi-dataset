#!/usr/bin/env python3
"""Deterministic origin extraction for dataset_csv/spec/normal.

For each normal capture CSV this records the network/cell "origin" evidence:
PLMN (MCC/MNC), cell identity, physical cell id, tracking area code, carrier
frequency (EARFCN -> band), cell-selection parameters, RAT, security
configuration, subscriber identifiers, and the signalling message mix.

The MCC/MNC and EARFCN->band mappings are 3GPP/ITU reference tables.
"""
import csv, glob, json, os, re, sys
from collections import Counter, defaultdict

csv.field_size_limit(10_000_000)
NORMAL = "/Users/roastedbeans/Documents/Github/modi-project/modi-parser/dataset_csv/spec/normal"
OUT = "/Users/roastedbeans/Documents/Github/modi-project/dataset-origin-analysis/origin_records.json"

NULLS = {"-1", "", "None", None, "nan", "NaN"}
def ok(v):
    return v not in NULLS

# --- reference tables -------------------------------------------------------
# MCC/MNC -> operator profile. In this testbed the PLMN is *configured* in
# Open5GS; the name is the real-world operator that PLMN identifies.
PLMN = {
    ("450", "5"): "SK Telecom (KR 450/05)",
    ("450", "05"): "SK Telecom (KR 450/05)",
    ("450", "8"): "KT (KR 450/08)",
    ("450", "08"): "KT (KR 450/08)",
    ("450", "6"): "LG U+ (KR 450/06)",
    ("450", "06"): "LG U+ (KR 450/06)",
    ("1", "1"): "Test network 00101 (srsRAN/Open5GS lab)",
    ("001", "01"): "Test network 00101 (srsRAN/Open5GS lab)",
}
# Origin class: only 00101 is the lab testbed; every other PLMN is a real
# commercial network (per dataset owner).
TEST_PLMNS = {("1", "1"), ("001", "01")}
def plmn_name(mcc, mnc):
    if not (ok(mcc) and ok(mnc)):
        return None
    return PLMN.get((mcc, mnc), f"Unmapped commercial PLMN {mcc}/{mnc}")

# IMSI home-network (MCC/MNC) -> operator, for identities seen on the air
# (a UE's own SUPI and, on commercial cells, paged subscribers' IMSIs).
IMSI_HOME = {
    "45005": "SK Telecom (KR)", "45003": "SK Telecom (KR)",
    "45008": "KT (KR)", "45002": "KT (KR)", "45004": "KT (KR)",
    "45006": "LG U+ (KR)", "45010": "LG U+ (KR)",
    "44020": "SoftBank (JP)", "44010": "NTT docomo (JP)",
    "51502": "Globe (PH) - auditor UE", "51503": "Smart (PH)",
    "51505": "Sun/Smart (PH)", "51511": "Smart (PH)", "51518": "Smart (PH)",
    "00101": "Test 00101",
}
# Capturing auditor handset's own SIM (Globe PH), roaming on the Korean cells.
AUDITOR_IMSI = "515027302508642"
def imsi_home(imsi):
    if not imsi or len(imsi) < 5:
        return None
    mccmnc = imsi[:5]
    return IMSI_HOME.get(mccmnc, f"MCC {imsi[:3]} / MNC {imsi[3:5]}")

# LTE DL EARFCN -> (band, approx DL centre MHz). 3GPP TS 36.101 Table 5.7.3-1.
LTE_BANDS = [
    (0, 599, 1, 2110), (600, 1199, 2, 1930), (1200, 1949, 3, 1805),
    (1950, 2399, 4, 2110), (2400, 2649, 5, 869), (2650, 2749, 6, 875),
    (2750, 3449, 7, 2620), (3450, 3799, 8, 925), (3800, 4149, 9, 1844),
    (4150, 4749, 10, 2110), (4750, 4949, 11, 1476), (5010, 5179, 12, 729),
    (5180, 5279, 13, 746), (5280, 5379, 14, 758), (5730, 5849, 17, 734),
    (5850, 5999, 18, 860), (6000, 6149, 19, 875), (6150, 6449, 20, 816),
    (6450, 6599, 21, 1496), (6600, 7399, 22, 3510), (7500, 7699, 23, 2180),
    (7700, 8039, 24, 1542), (8040, 8689, 25, 1962), (8690, 9039, 26, 869),
    (9040, 9209, 27, 860), (9210, 9659, 28, 758), (9660, 9769, 30, 2355),
    (9770, 9869, 31, 462), (9870, 10359, 32, 1474),
    (36000, 36199, 33, 1910), (36200, 36349, 34, 2010),
    (36350, 36949, 35, 1850), (36950, 37549, 36, 1930),
    (37550, 37749, 37, 1910), (37750, 38249, 38, 2595),
    (38250, 38649, 39, 1900), (38650, 39649, 40, 2350),
    (39650, 41589, 41, 2593), (41590, 43589, 42, 3500),
    (43590, 45589, 43, 3700), (45590, 46589, 44, 763),
]
# Common marketing label for the band's frequency range.
BAND_NOMINAL = {1: "2100 MHz", 2: "1900 MHz", 3: "1800 MHz", 4: "AWS 1700/2100",
                5: "850 MHz", 7: "2600 MHz", 8: "900 MHz", 20: "800 MHz",
                28: "700 MHz", 38: "2600 MHz TDD", 40: "2300 MHz TDD",
                41: "2500 MHz TDD", 42: "3500 MHz", 70: "AWS-4 2000 MHz"}

def earfcn_band(earfcn):
    """Resolve a DL EARFCN to its band and the true channel centre frequency.

    Centre = FDL_low + 0.1 * (NDL - NOffs-DL), 3GPP TS 36.101. Here the table's
    `lo` is NOffs-DL and `fdl_low` is the band's start frequency.
    """
    try:
        e = int(earfcn)
    except (TypeError, ValueError):
        return None
    for lo, hi, band, fdl_low in LTE_BANDS:
        if lo <= e <= hi:
            centre = round(fdl_low + 0.1 * (e - lo), 1)
            return {"earfcn": e, "band": band, "center_mhz": centre,
                    "nominal": BAND_NOMINAL.get(band, f"B{band}")}
    return {"earfcn": e, "band": None, "center_mhz": None, "nominal": None}

# --- file grouping ----------------------------------------------------------
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
    m = re.match(r"normal_(\d+)_(\d+)_(\d+)_lte", name)
    if m:
        return f"2026-03-18 (LTE batch)"
    return None

# --- per-file column helpers ------------------------------------------------
def dset(rows, col):
    s = []
    for r in rows:
        v = r.get(col)
        if ok(v):
            s.append(v)
    return sorted(set(s), key=lambda x: (len(x), x))

def present(rows, prefix):
    """True if any column starting with prefix has a non-null _show value."""
    for r in rows:
        for k, v in r.items():
            if k.startswith(prefix) and k.endswith("_show") and ok(v):
                return True
    return False

# Algorithm flag columns -> human label
SEC_FLAGS = {
    "nas-5gs_mm_5g_ea0": "5G-EA0 (null)", "nas-5gs_mm_128_5g_ea1": "128-5G-EA1",
    "nas-5gs_mm_128_5g_ea2": "128-5G-EA2", "nas-5gs_mm_128_5g_ea3": "128-5G-EA3",
    "nas-5gs_mm_5g_ia0": "5G-IA0 (null)", "nas-5gs_mm_5g_128_ia1": "128-5G-IA1",
    "nas-5gs_mm_5g_128_ia2": "128-5G-IA2", "nas-5gs_mm_5g_128_ia3": "128-5G-IA3",
    "nas-eps_emm_eea0": "EEA0 (null)", "nas-eps_emm_128eea1": "128-EEA1",
    "nas-eps_emm_128eea2": "128-EEA2", "nas-eps_emm_eea3": "EEA3",
    "nas-eps_emm_eia0": "EIA0 (null)", "nas-eps_emm_128eia1": "128-EIA1",
    "nas-eps_emm_128eia2": "128-EIA2", "nas-eps_emm_eia3": "EIA3",
}

def extract(path):
    name = os.path.basename(path)
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    rec = {"file": name, "group": file_group(name),
           "capture_start": capture_start(name), "rows": len(rows)}
    if not rows:
        rec["empty"] = True
        return rec

    # timing
    ts = [float(r["timestamp"]) for r in rows if ok(r.get("timestamp"))
          and re.match(r"^-?\d+(\.\d+)?$", r.get("timestamp", ""))]
    rec["duration_s"] = round(max(ts) - min(ts), 2) if ts else None

    # message mix
    rec["packet_type"] = dict(Counter(r.get("packet_type", "") for r in rows))
    rec["direction"] = dict(Counter(r.get("direction", "") for r in rows))
    rec["top_info"] = [{"info": k, "n": n} for k, n in
                       Counter(r.get("info", "") for r in rows if ok(r.get("info"))).most_common(15)]

    # RAT
    has_lte = present(rows, "lte-rrc_")
    has_nr = present(rows, "nr-rrc_")
    has_eps = present(rows, "nas-eps_")
    has_5gs = present(rows, "nas-5gs_")
    rec["rat"] = {"lte_rrc": has_lte, "nr_rrc": has_nr,
                  "nas_eps_4g": has_eps, "nas_5gs": has_5gs}
    # 3G detection: RRC packets present but no LTE/NR/NAS schema field is
    # populated. The UMTS RRC (TS 25.331) dissector fills only info/packet_type
    # in this schema, so an rrc-only capture with empty lte-rrc/nr-rrc columns
    # is a 3G/UMTS trace (PCCH paging, SIBs, or DCCH Direct Transfer).
    rrc_rows = rec["packet_type"].get("rrc", 0) + rec["packet_type"].get("nas+rrc", 0)
    if has_nr and has_lte:
        label = "5G-NSA / LTE+NR"
    elif has_nr or has_5gs:
        label = "5G"
    elif has_lte or has_eps:
        label = "LTE (EPS)"
    elif rrc_rows:
        label = "3G (UMTS)"
    else:
        label = "unknown"
    rec["rat_label"] = label

    # PLMN / operator
    plmns = set()
    g_mcc = dset(rows, "e212_gummei_mcc_show"); g_mnc = dset(rows, "e212_gummei_mnc_show")
    imsis = dset(rows, "e212_imsi_show")
    for mcc in g_mcc:
        for mnc in g_mnc:
            plmns.add((mcc, mnc))
    # also derive PLMNs from full IMSIs (MCC=first3, MNC=next2)
    imsi_plmns = {(im[:3], str(int(im[3:5]))) for im in imsis if len(im) >= 5 and im[:5].isdigit()}
    all_plmns = plmns | imsi_plmns
    is_00101 = bool(all_plmns & TEST_PLMNS)
    commercial_ops = sorted({plmn_name(m, n) for m, n in plmns
                             if plmn_name(m, n) and (m, n) not in TEST_PLMNS})
    rec["plmn"] = {
        "gummei_mcc": g_mcc, "gummei_mnc": g_mnc,
        "is_00101": is_00101,
        "operator": commercial_ops or None,
    }
    # IMSI home-network breakdown: how many distinct subscriber identities and
    # which home networks. Many distinct IMSIs => paging traffic on a live cell.
    home_ct = Counter(imsi_home(im) for im in imsis if imsi_home(im))
    foreign = [im for im in imsis if im[:3] not in ("450", "001") and im[:5] != "51502"]
    rec["imsi_analysis"] = {
        "distinct_imsi_count": len(imsis),
        "by_home_network": dict(home_ct.most_common()),
        "foreign_paged_count": len(foreign),
        "auditor_ue_present": AUDITOR_IMSI in imsis,
        "examples": imsis[:6],
    }

    # cells
    rec["cell"] = {
        "lte_cellidentity": dset(rows, "lte-rrc_cellidentity_show"),
        "lte_physcellid": dset(rows, "lte-rrc_physcellid_show"),
        "lte_targetphyscellid": dset(rows, "lte-rrc_targetphyscellid_show"),
        "nr_cellidentity": dset(rows, "nr-rrc_cellidentity_show"),
    }
    # TAC
    rec["tac"] = {
        "lte_rrc": dset(rows, "lte-rrc_trackingareacode_show"),
        "nas_5gs": dset(rows, "nas-5gs_tac_show"),
        "nas_eps_tai": dset(rows, "nas-eps_emm_tai_tac_show"),
    }
    # frequency / band
    freqs = sorted(set(dset(rows, "lte-rrc_carrierfreq_show")
                       + dset(rows, "lte-rrc_dl_carrierfreq_show")), key=lambda x: int(x))
    rec["frequency"] = {
        "earfcns": freqs,
        "bands": [earfcn_band(e) for e in freqs],
    }
    # cell selection. q-RxLevMin: raw _show is |signaled|; real value dBm = -2*shown.
    qrx = dset(rows, "lte-rrc_q_rxlevmin_show")
    rec["cell_selection"] = {
        "q_rxlevmin": qrx,
        "q_rxlevmin_dbm": [f"-{2*int(v)}" for v in qrx if v.lstrip('-').isdigit()],
        "cellbarred": dset(rows, "lte-rrc_cellbarred_show"),
        "cellreselectionpriority": dset(rows, "lte-rrc_cellreselectionpriority_show"),
        "defaultpagingcycle": dset(rows, "lte-rrc_defaultpagingcycle_show"),
    }

    # security
    sec_algos = []
    for col, label in SEC_FLAGS.items():
        for suf in ("_show",):
            v = dset(rows, col + suf)
            if any(x in ("1", "Supported", "true", "True") for x in v):
                sec_algos.append(label)
    rec["security"] = {
        "lte_rrc_ciphering": dset(rows, "lte-rrc_cipheringalgorithm_show"),
        "lte_rrc_integrity": dset(rows, "lte-rrc_integrityprotalgorithm_show"),
        "nr_rrc_ciphering": dset(rows, "nr-rrc_cipheringalgorithm_show"),
        "nr_rrc_integrity": dset(rows, "nr-rrc_integrityprotalgorithm_show"),
        "nas_5gs_security_header": dset(rows, "nas-5gs_security_header_type_show"),
        "nas_eps_security_header": dset(rows, "nas-eps_security_header_type_show"),
        "advertised_algorithms": sorted(set(sec_algos)),
        "has_msg_auth_code": bool(dset(rows, "nas-5gs_msg_auth_code_show")
                                  or dset(rows, "nas-eps_msg_auth_code_show")),
    }

    # subscriber identifiers / privacy posture
    rec["identifiers"] = {
        "imsi": imsis,
        "suci_msin": dset(rows, "nas-5gs_mm_suci_msin_show"),
        "suci_scheme": dset(rows, "nas-5gs_mm_suci_scheme_id_show"),
        "5g_tmsi": dset(rows, "nas-5gs_5g_tmsi_show"),
        "m_tmsi": dset(rows, "nas-eps_emm_m_tmsi_show"),
        "s_tmsi": dset(rows, "lte-rrc_s_tmsi_element_show"),
        "imeisv": dset(rows, "nas-5gs_mm_imeisv_show"),
    }
    # AMF identity (5G core)
    rec["amf"] = {
        "region_id": dset(rows, "nas-5gs_amf_region_id_show"),
        "set_id": dset(rows, "nas-5gs_amf_set_id_show"),
        "pointer": dset(rows, "nas-5gs_amf_pointer_show"),
    }
    # NAS message types
    rec["nas_messages"] = {
        "mm_5gs": dset(rows, "nas-5gs_mm_message_type_showname"),
        "emm_eps": dset(rows, "nas-eps_nas_msg_emm_type_showname"),
    }

    # Origin class. The srsRAN/Open5GS testbed is identified by PLMN 00101 and by
    # its radio: LTE Band 8 and NR n78/n79. A real commercial identity (a 450/xx
    # PLMN or paging of foreign-roamer IMSIs) cannot be produced by the single-SIM
    # 00101 testbed, so it always wins. Note: NR carrier ARFCN is not in the CSV
    # schema, so "NR present without a commercial identity" stands in for n78/n79.
    has_commercial = bool(commercial_ops)
    # Any real-subscriber IMSI (the auditor's own roaming SIM, or a paged
    # third-party subscriber whether Korean 450 or foreign) can only appear on a
    # live commercial cell. The isolated 00101 testbed core knows one test SIM.
    has_real_subscriber = any(not im.startswith("001") for im in imsis)
    foreign_n = rec["imsi_analysis"]["foreign_paged_count"]
    has_nr = has_nr or has_5gs
    has_band8 = any(b.get("band") == 8 for b in rec["frequency"]["bands"])
    if is_00101:
        rec["origin_class"], rec["origin_reason"] = "test/lab", "PLMN 00101 (test SIM)"
    elif has_commercial:
        rec["origin_class"], rec["origin_reason"] = "commercial", "commercial PLMN " + ", ".join(commercial_ops)
    elif has_real_subscriber:
        rec["origin_class"], rec["origin_reason"] = "commercial", (
            f"live-cell paging of real subscriber IMSIs ({foreign_n} foreign)" if foreign_n
            else "live-cell identity of a real subscriber IMSI")
    elif has_nr:
        rec["origin_class"], rec["origin_reason"] = "test/lab", "NR n78/n79, no commercial identity"
    elif has_band8:
        rec["origin_class"], rec["origin_reason"] = "test/lab", "LTE Band 8, no commercial identity"
    else:
        rec["origin_class"], rec["origin_reason"] = "commercial", "LTE on commercial bands, attach not captured"
    return rec

def main():
    files = sorted(glob.glob(os.path.join(NORMAL, "*.csv")))
    records = [extract(f) for f in files]

    # aggregates
    agg = {
        "n_files": len(records),
        "by_group": dict(Counter(r["group"] for r in records)),
        "by_rat": dict(Counter(r.get("rat_label", "unknown") for r in records)),
        "by_origin_class": dict(Counter(r.get("origin_class", "commercial") for r in records)),
        "by_origin_reason": dict(Counter(r.get("origin_reason", "") for r in records).most_common()),
        "by_operator": dict(Counter(
            (r.get("plmn", {}).get("operator") or ["(no PLMN observed in capture)"])[0]
            for r in records)),
        "total_packets": sum(r.get("rows", 0) for r in records),
        "total_duration_s": round(sum(r.get("duration_s") or 0 for r in records), 1),
    }
    # band histogram: distinct files in which each band appears (not raw hits)
    band_ct = Counter()
    for r in records:
        seen = set()
        for b in r.get("frequency", {}).get("bands", []):
            if b and b.get("band"):
                seen.add((b["band"], b["nominal"]))
        for band, nominal in seen:
            band_ct[f"B{band} ({nominal})"] += 1
    agg["band_observations_files"] = dict(band_ct.most_common())

    out = {"origin_model": {
        "commercial": {
            "what": "Real commercial cellular networks (every PLMN except 00101).",
            "operators_seen": "SK Telecom (450/05), KT (450/08), plus paged subscriber IMSIs from these and neighbouring networks.",
            "ue": ["OnePlus 9 Pro", "Samsung S20", "Samsung S22 (rooted, Qualcomm baseband)"],
            "auditor_sim": "Capturing handset roams on a Globe Philippines SIM (own IMSI 515027302508642, MCC 515/02) on the Korean cells.",
            "collector": "MODI app wrapping diag_mdlog (-f Diag.cfg -s 100 -n 2)",
            "site": "Seoul, South Korea (Kookmin University area)",
            "evidence": "Live SIB broadcasts, Paging Type1 of many distinct third-party subscriber IMSIs (including foreign roamers), real eNB cell identities and EARFCNs.",
        },
        "test_lab": {
            "what": "Controlled testbed. Identified by PLMN 00101 and by its radio: LTE Band 8 and NR n78/n79.",
            "core": "Open5GS", "ran": "srsRAN (eNodeB LTE / gNB 5G-NR)",
            "sdr": "LibreSDR B220 mini",
            "radio": "LTE Band 8 (900 MHz); NR n78 (3.5 GHz) / n79 (4.7 GHz) TDD",
            "evidence": "Single provisioned 00101 SIM, no foreign paging, default lab cell parameters, testbed bands.",
            "note": "The CSV schema has no NR carrier ARFCN, so an NR capture with no commercial PLMN and no live paging stands in for the n78/n79 testbed 5G.",
        },
        "note": "Per dataset owner: the lab testbed is PLMN 001/01 plus its radio bands (LTE Band 8, NR n78/n79). A real commercial identity (450/xx PLMN or foreign-roamer paging) marks a capture commercial and overrides the band rule.",
    }, "aggregate": agg, "records": records}

    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)
    print("wrote", OUT)
    print(json.dumps(agg, indent=2))

if __name__ == "__main__":
    main()
