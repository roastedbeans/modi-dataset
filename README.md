# MODI Dataset

A public Layer-3 PCAP corpus of LTE and 5G-NR cellular sessions captured directly from the User Equipment (UE) baseband. The dataset is intended for research on UE-side detection of False Base Station (FBS) and other radio-access misbehavior.

## Motivation

Public cellular traces captured at the UE itself are scarce. Most available datasets are simulated, network-side, or limited to a single attack family, which makes it hard to develop and reproducibly evaluate detectors that must run on the device. MODI Dataset fills that gap with paired benign and adversarial captures collected on the same testbed and exposed through the same on-device pipeline, so researchers can build and compare UE-resident detectors against a consistent baseline.

## Contents

```
pcap/
└── compiled/
    ├── attacks_compiled/          # 70 PCAPs  — FBS / misbehavior traces, 29 scenarios in 8 categories
    ├── normal_compiled/           # 162 PCAPs — benign cellular sessions
    ├── testbed_insecure_compiled/ # 23 PCAPs  — lab captures, not usable as benign or attack ground truth (see below)
    └── flagged_review_compiled/   # 9 PCAPs   — labelled normal, flagged for a genuine spec violation (see below)
```

| Category                     | Representative scenarios                                                                                                  |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Encryption / security bypass | `null_encryption` (× 2), `no_security_headers` (LTE × 6, 5G × 2), `ciphered_nas_anomaly`                                  |
| Identity catching            | `imsi_catching`, `imei_catching`, `capability_hijacking`                                                                  |
| Network downgrade            | `downgrade` (× 10), `downgrade_tau_attack`, `detach_downgrade` (× 3), `sib1_tac_attack`                                   |
| Service rejection            | `service_reject` (× 2), `attach_reject` (× 2), `tau_reject`, `tau_reject_nmap`, `rrc_reestablish_reject`                  |
| Authentication abuse         | `authentication_failure`, `auth_relay_synch_failure`, `malformed_identity_request`                                        |
| Location / tracking          | `location_tracking_measurement_report`, `paging_channel_hijacking`, `handover_hijacking`                                  |
| Resource / energy depletion  | `signal_ddos` (× 15), `energy_depletion`, `replay_energy_depletion_auth`, `panic_attack` (× 2)                            |
| Stealth / state manipulation | `stealthy_kicking_off` (× 6), `lullaby_attack_rrc_reconfiguration` (× 2), `emm_information`                               |

The benign corpus breaks down as 72 `lte_commercial`, 48 `5g_commercial`, 31 `lte_test`,
10 `3g_commercial` and 1 `5g_commercial_45008` capture.

### Data-quality exclusions

Two categories were split out of `attacks_compiled`/`normal_compiled` after
verification against a rule-based UE-side detector (spec-violation checks over
RRC + NAS) surfaced systematic labelling problems in a since-added batch of
captures. Neither issue affects the original, hand-verified 47-trace attack set
or the bulk of the normal corpus.

- **67 traces removed from `attacks_compiled`** (46 of 64 `signal_ddos`, 16 of
  26 `downgrade`, plus 5 isolated traces from other scenarios). Each one has
  zero connection-layer signalling rows and no NAS content — a pure SIB/paging
  broadcast recording with no observable trace of the labelled attack. The
  detector, an independent message-rate check, and a NAS-presence check all
  agree the attack event is not inside the captured window. These are removed
  entirely, not retained under another label — see `MODI-parser`'s dataset
  evaluation notes for the full per-file list.
- **`testbed_insecure_compiled/` (23 traces)**, formerly `normal_compiled`'s
  `5g_test_00101` captures: the Open5GS 5G-SA lab core runs NEA0 (null
  ciphering) with null-scheme SUCI (cleartext IMSI) by configuration, which is
  indistinguishable from an attack at the RRC/NAS layer. They are genuine
  benign *sessions* but not valid *ground truth* for a spec-compliance
  detector either way — split out rather than deleted.
- **`flagged_review_compiled/` (9 traces)**, formerly `normal_compiled`: 5
  `lte_commercial` (4 from one 2026-05-21 session) and 4 `5g_commercial`
  captures on the commercial network that trip null-cipher / broadcast-rate
  checks. Unlike the testbed case there is no known configuration explanation
  — these need manual review before being restored to `normal_compiled` or
  relabelled, and should not be treated as verified in either direction.

### File naming

- **Normal**: `normal_YYYY_MM_DD_HH_MM_SS.pcap` — capture start time; sessions are independent.
- **Attack**: `<scenario>_<NN>.pcap` — `snake_case` scenario slug + zero-padded index starting at `01`. Variants keep their tag between scenario and index (e.g. `no_security_headers_5g_session_01.pcap`, `tau_reject_nmap_01.pcap`).
- PCAPs are GSMTAP-encapsulated and retain full RRC and NAS payloads, so consumers can re-dissect with any field schema.

## Dataset gathering process

### Testbed

| Component           | Configuration                                                              |
| ------------------- | -------------------------------------------------------------------------- |
| Core network        | Open5GS                                                                    |
| RAN                 | srsRAN (eNodeB for LTE, gNB for 5G-NR)                                     |
| SDR front-end       | LibreSDR B220 mini                                                         |
| UE devices          | OnePlus 9 Pro, Samsung S20, Samsung S22 (rooted, Qualcomm baseband)        |
| On-device collector | MODI Android app wrapping `diag_mdlog`                                     |

The UE attaches over the air to the same Open5GS + srsRAN stack for both corpora. For normal captures the stack is configured per 3GPP specifications. For attack captures srsRAN and Open5GS are reconfigured to suppress, replay, or modify specific RRC and NAS messages so that each capture exhibits a single, verified 3GPP normative violation. Because the radio path is identical, detectors cannot exploit physical-layer differences between the two corpora.

### Capture path

```
UE (rooted Android, Qualcomm DIAG)
        │  diag_mdlog -f Diag.cfg -s 100 -n 2
        ▼
QMDL log files
        │  MODI parser: FileIO → QualcommParser
        ▼
GSMTAP-encapsulated PCAP  ← files in this repository
        │  MODI parser: ws_dissector (custom Wireshark dissectors)
        ▼
PDML → analysis_rrc.csv  +  analysis_nas.csv
```

The on-device preprocessing pipeline (QMDL → PCAP → CSV) is described in the MODI paper cited below.

### Validation

- **Normal traces** were manually reviewed against the LTE / 5G-NR protocol state machine to confirm the absence of anomalous RRC or NAS sequences before inclusion.
- **Attack traces** were verified packet-by-packet to confirm that the intended normative violation is present and isolated.

## Citation

If you use this dataset, please cite:

> Abella, V., Pawana, I W. A. J., You, I., & Park, H. (2026). MODI: On-Device Preprocessing of Qualcomm Diagnostic Logs for Cellular Protocol Analysis on Android. *Journal of Internet Services and Information Security*, 16(1), 612–623. https://doi.org/10.58346/JISIS.2026.I1.034

```bibtex
@article{abella2026modi,
  title   = {{MODI}: On-Device Preprocessing of {Qualcomm} Diagnostic Logs for Cellular Protocol Analysis on {Android}},
  author  = {Abella, Vincent and Pawana, I Wayan Adi Juliawan and You, Ilsun and Park, Hoonyong},
  journal = {Journal of Internet Services and Information Security},
  volume  = {16},
  number  = {1},
  pages   = {612--623},
  year    = {2026},
  doi     = {10.58346/JISIS.2026.I1.034}
}
```

## Ownership

The dataset was collected and curated by:

- Vincent Abella — Kookmin University, Seoul, South Korea
- I Wayan Adi Juliawan Pawana — Kookmin University, Seoul, South Korea / Udayana University, Badung, Indonesia
- Dr. Ilsun You — Kookmin University, Seoul, South Korea
- Hoonyong Park — Autocrypt Co. Ltd., Seoul, South Korea

Released for academic and non-commercial research use, consistent with the licensing of the accompanying publication (CC BY-NC). For commercial use or extended collaborations, contact the corresponding author at Kookmin University.
