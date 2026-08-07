# Scenario-to-Normal-Data Coverage

> **Superseded — counts below describe an earlier corpus.** This analysis was
> derived from the 192-trace set (140 normal). The corpus is now **331 traces:
> 194 normal and 137 attack**, and the CSVs it cites were additionally missing
> their whole NAS layer due to a parser/toolchain defect since fixed. Every
> per-category count, trace total and confidence verdict below therefore needs
> re-deriving against the regenerated `dataset_csv/` before it is cited.

Mapping of the planned data-collection scenarios to the normal traces that the
192-trace MODI evaluation set actually contains (140 normal traces in
`dataset_csv/spec/normal/`). Coverage is judged from the layer-3 control-plane
footprint each trace carries (procedure types, distinct serving/neighbor cell
identities, tracking-area-code diversity, handover-sync elements), since the
SPEC view is RRC and NAS only.

Legend: ✅ clearly shown, ⚠️ partial or indirect, ❌ gap.

## Scenarios fitted to the dataset (verified)

Each scenario is decided by a message label or field that is present or absent in
the trace. The `Traces` column is a trace-level count: traces containing at least
one occurrence of the signature, verified against the real `info` vocabulary
(129 distinct labels, 37 460 rows). No row relies on an assumed label.

| Scenario | Description | Observable layer-3 signature | Traces |
|----------|-------------|------------------------------|--------|
| S1 LTE registration | UE attach with full AKA, security mode, default-bearer setup | `Attach request`, `Authentication request`, `Security mode command`, `ESM information` | **43** (32 LTE-comm, 10 5G-comm NSA, 1 5G-test) |
| S2 Connected-mode signaling | Reconfiguration, reestablishment, service request, ciphered NAS transfer (control-plane bracket of a session) | `RRCConnection Reconfiguration(/Complete)`, `RRCConnection Reestablishment*`, `SERVICE REQUEST`, `*Information Transfer, Ciphered NAS` | **64** reconfig (30 LTE-test, 30 5G-comm, 3 LTE-comm) |
| S3 Paging / MT notification | Network pages idle UE; SIB broadcasts | `paging`, `paging Type1` | **88** (49 LTE-comm, 31 5G-comm, 6 3G-comm, 2 5G-test) |
| S4 Commercial mobility / reselection | Multi-cell movement, measurement reporting, occasional signaled handover | `measurement Report` / `NR-measurement Report` + at least 2 distinct cellIdentity / TAC; `mobilityControlInfo` for handover | **40** meas (30 5G-comm, 8 LTE-comm); 6 carry the HO IE |
| S5 Testbed baseline (00101) | Scripted lab sessions, connected-mode reconfiguration / reestablishment loops | PLMN 00101 plus `Reconfiguration` / `Reestablishment` loops | **39** (31 LTE-test, 8 5G-test) |
| S6 Testbed signaled handover | Dual-cell handover with the handover command | `mobilityControlInfo` in a 00101 trace, cells `0019b010` and `0019c010` in TAC `0007` | **1** (`lte_test_..16_23_40`) |
| S7 5G SA registration | Pure NR-RRC plus 5GMM registration | `NR-rrc Setup Complete, Registration request`, `nas-5gs_*` fields | **2** (`5g_test` 05_12, 06_05) |

### Verification (trace-level signature presence)

Count = traces in the category containing at least one occurrence of the signature.

| signature | LTE-comm (61) | LTE-test (31) | 5G-comm (31) | 5G-test (8) | 3G-comm (9) |
|-----------|:---:|:---:|:---:|:---:|:---:|
| Attach request | 32 | 0 | 10 | 1 | 0 |
| Registration request (5G SA) | 0 | 0 | 0 | 2 | 0 |
| Authentication request | 32 | 0 | 2 | 0 | 0 |
| Security mode command | 32 | 4 | 23 | 0 | 0 |
| ESM information (bearer) | 32 | 0 | 0 | 0 | 0 |
| RRC Reconfiguration | 3 | 30 | 30 | 1 | 0 |
| Reestablishment request | 0 | 30 | 2 | 0 | 0 |
| Service request | 0 | 4 | 16 | 0 | 0 |
| TAU request | 0 | 4 | 3 | 0 | 0 |
| Measurement report | 8 | 2 | 30 | 0 | 0 |
| `mobilityControlInfo` (HO IE) | 0 | 1 | 5 | 0 | 0 |
| Paging | 49 | 0 | 31 | 2 | 6 |
| NR content (EN-DC or SA) | 17 | 0 | 31 | 5 | 0 |
| UMTS content | 43 | 1 | 3 | 3 | 9 |

### Confidence verdicts (evidence before certainty)

- **S1 LTE registration — confirmed.** In 32/61 LTE-commercial traces the full
  chain co-occurs (Attach and Authentication and Security mode and ESM), so these
  are complete attach procedures, not isolated fragments. The 10 5G-commercial
  "attach" traces are the LTE NAS anchor of an NSA session.
- **S2 Connected-mode signaling — confirmed (64 traces),** but the testbed share
  is reestablishment-loop driven (26/31 LTE-test start mid-session on a
  Reestablishment Request, 0 carry Attach), and user-plane payload is not in the
  layer-3 view, so this is signaling only.
- **S3 Paging — strongly confirmed.** 88 traces, 16 974 paging rows.
- **S4 Commercial mobility — confirmed via measurement reporting** (30/31
  5G-commercial), with multi-cell / multi-TAC transit captures (up to 360 cells,
  38 TACs). Signaled handover is thin: 6 traces (5 NSA-commercial plus 1 testbed).
- **S5 Testbed baseline — confirmed as a 39-trace pool,** but the captured
  behaviour is connected-mode reconfiguration / reestablishment, not attach loops
  (0/31 LTE-test carry an Attach).
- **S6 Testbed signaled handover — not a population (1 trace).** Collection gap.
- **S7 5G SA registration — not a population (2 traces).** The dataset's 5G is
  overwhelmingly NSA / EN-DC; pure 5G SA NAS appears in two testbed captures only.

### Two findings that revise the earlier mapping

1. **The testbed records no Attach.** 0/31 LTE-test and only 1/8 5G-test carry an
   Attach or Registration Request; the testbed pool is connected-mode loops
   captured mid-session. Any claim that the lab provides registration baselines is
   not supported by the traces.
2. **"5G" in this dataset means NSA.** All 31 5G-commercial traces carry NR but
   register over LTE NAS (EN-DC); 5G SA registration is two testbed traces. 5G SA
   coverage is therefore empirically thin, consistent with and sharper than the
   thesis's "structural at the model level, thin at the empirical level" statement.

The remainder of this document keeps the original seven-scenario mapping for
reference.

## Original mapping (as-planned scenarios)

| # | Scenario | Coverage | Normal data that shows it | Count |
|---|----------|----------|---------------------------|-------|
| 1 | Idle/Registration | ✅ Clear | `lte_commercial_*` attach captures (short, median 24 s, attach in 32/61), `5g_test_*` registration (3/8), `3g_commercial_*` (9) | ~50 traces |
| 2 | Mobility Handover | ⚠️ Partial | `5g_commercial_*` mobility captures (handover-sync element in 5, measurement reports in 30/31) plus one scripted `lte_test_*` handover; commercial mobility is well covered, but explicitly A3/A5-labeled *controlled* handover is thin | 5 + 1 |
| 3 | Data Session | ⚠️ Control-plane only | `lte_test_*` reconfiguration loops (reconfig in 30/31, median 92 s), long `5g_commercial_*` sessions (reconfig in 30/31) | ~60 traces |
| 4 | Paging/Notification | ✅ Clear | paging records in 49 `lte_commercial_*`, 31 `5g_commercial_*`, 6 `3g_commercial_*`; CN-triggered service requests in 16 `5g_commercial_*` | 86 traces |
| 5 | Mixed Environment | ✅ Clear (vehicular) | high-mobility commercial transit captures — `5g_commercial_45005_2026_04_30_14_03_33` (148 cells, 7 TACs, 62 min) and `..._15_08_32` (360 cells, 38 TACs, 114 min), plus several 13-cell / 3–5-TAC LTE and 5G captures | ~8 traces |
| 6 | Test Environment | ✅ Clear | all PLMN-00101 testbed traces: 31 `lte_test_*` + 8 `5g_test_*`, scripted attach / reconfiguration | 39 traces |
| 7 | Test Environment (With Handover) | ❌ Gap | of 9 testbed traces with a cell/TAC change, only `lte_test_..2025_11_28_16_23_40` carries an explicit `mobilityControlInfo` handover-command IE with measurement reports; 3 more in the same dual-cell session flip cells via reconfig/reestablishment, the rest are SIB1 neighbor-cell sweeps | 1 signaled + 3 reconfig |

## Reading

- **Strong, unambiguous coverage:** Idle/Registration (1), Paging/Notification (4),
  Mixed Environment / vehicular mobility (5), and Test Environment (6). These map
  to large, clearly-signed trace pools.
- **Partial / indirect:** Mobility Handover (2) is well covered on the commercial
  side but light on *controlled* lab handover. Data Session (3) is visible only as
  its control-plane footprint — see caveat below.
- **Gap to fill:** Test Environment (With Handover) (7). Only one testbed trace
  carries an explicit handover-command IE, so this scenario is effectively
  unfilled (see breakdown below).

## Test Environment handover detail

Of the 39 testbed traces (PLMN 00101), 9 show a TAC or cell-ID change. Verifying
the message sequence around each change splits them into three cases — only one
is a signaled handover. The dual-eNB pair is cells `0019b010` ↔ `0019c010` in
TAC `0007` (two cells of the testbed, differing only in the last cell-ID nibble).

| Trace | RAT | cells / TACs | Sequence | Handover? |
|-------|-----|--------------|----------|-----------|
| `lte_test_..2025_11_28_16_23_40` | LTE | 10 / 3 | `mobilityControlInfo` IE (×2) + 2 measurement reports | ✅ signaled HO |
| `lte_test_..2025_11_28_16_14_38` | LTE | 2 / 1 | measurement report → SIB1 of new cell | ⚠️ meas-driven, no HO IE |
| `lte_test_..2025_11_28_16_12_11` | LTE | 2 / 1 | reconfig → cell flip → reestablishment | ⚠️ reconfig/reestab |
| `lte_test_..2025_11_28_16_26_06` | LTE | 2 / 1 | reconfig → cell flip → reestablishment | ⚠️ reconfig/reestab |
| `lte_test_..2026_03_18_17_45_37` | LTE | 12 / 4 | Reestablishment Request → new cell | ❌ RLF recovery |
| `lte_test_..2026_04_14_16_02_08` | LTE | 22 / 5 | 55 changes, all between back-to-back SIB1 rows | ❌ SIB1 sweep |
| `5g_test_..2026_05_26_17_39_36` | 5G | 13 / 4 | changes only between consecutive SIB1 rows | ❌ SIB1 sweep |
| `5g_test_..2026_05_26_17_40_31` | 5G | 13 / 4 | changes only between consecutive SIB1 rows | ❌ SIB1 sweep |
| `5g_test_..2026_05_26_17_43_42` | 5G | 13 / 4 | changes only between consecutive SIB1 rows | ❌ SIB1 sweep |

The many-cell / many-TAC captures (`04_14_16_02_08`, the three `5g_test_05_26`)
change cell-ID only between consecutive SIB1 broadcasts — the UE logs SIB1 from
many configured neighbor cells, a scan, with no measurement report and no
reconfiguration-with-sync. A proper dual-gNB, A3-triggered handover set with the
HO command IE captured needs a dedicated collection run.

## Caveats (why some scenarios are "partial")

- **No user-plane visibility.** The SPEC traces are RRC + NAS control plane only.
  VoLTE / IMS / SIP, HTTP-3, and UDP-streaming payloads return zero matches across
  all 140 traces, so the *application content* of a Data Session cannot be
  confirmed from this data — only the bearer-setup and reconfiguration signaling.
- **Radio metrics live elsewhere.** RSRP / RSRQ / SINR / PCI-list fluctuations are
  in the AI-essential / NetMonster view, not the SPEC view. Mobility here is proxied
  by distinct cell-identity and tracking-area-code counts.
- **Device-per-trace is not recoverable from filenames.** Commercial traces are the
  three handsets (OnePlus 9 Pro, Samsung Galaxy S20, Galaxy S22) on SK Telecom
  (PLMN 45005); testbed traces are the same handsets on the lab core (PLMN 00101).
  The specific device per file is not encoded in the trace name.

## Supporting evidence (per-category indicators, 140 normal traces)

| Category | n | dur (med) | cells med/max | TAC max | handover-sync | meas>0 | paging>0 | attach>0 | reconfig>0 |
|----------|---|-----------|---------------|---------|---------------|--------|----------|----------|------------|
| `lte_commercial` | 61 | 24 s | 1 / 13 | 4 | 0 | 8 | 49 | 32 | 5 |
| `lte_test` | 31 | 92 s | 1 / 22 | 5 | 1 | 2 | 0 | 0 | 30 |
| `5g_commercial` | 31 | 63 s | 1 / 360 | 38 | 5 | 30 | 31 | 10 | 30 |
| `5g_test` | 8 | 5 s | 1 / 13 | 4 | 0 | 0 | 2 | 1 | 1 |
| `3g_commercial` | 9 | 12 s | 0 / 0 | 0 | 0 | 0 | 6 | 0 | 0 |

`cells` = distinct serving/neighbor cell identities seen in SIB1; `TAC` = distinct
tracking area codes (mobility proxy); `handover-sync` = traces carrying
`mobilityControlInfo` / `reconfigurationWithSync` / `targetPhysCellId`.

## Planned scenario table (annotated with observed coverage)

| Scenario Name | Description | Collected Data | Observed coverage |
|---------------|-------------|----------------|-------------------|
| Idle/Registration | 3GPP UE power-on attach, PLMN selection, TAU, RRC Idle-to-Connected, no anomalies | Already have | ✅ lte_commercial / 5g_test / 3g_commercial |
| Mobility Handover | Intra-frequency handovers, A3/A5 measurement reports (RSRP/RSRQ), cell reselection under controlled mobility | — | ⚠️ commercial mobility yes; controlled lab handover thin |
| Data Session | Web (HTTP/3), VoLTE, UDP streaming; GTP-U tunnels with IP payloads | — | ⚠️ control-plane footprint only (no user-plane in layer-3 view) |
| Paging/Notification | Operator paging for MT calls/SMS, valid SIB1/SIB2, CN-triggered service requests | — | ✅ 86 traces with paging |
| Mixed Environment | Urban static scans, vehicular mobility (30–60 km/h), varying BS loads, RSRP fluctuation, PCI lists | — | ✅ high-mobility commercial transit captures |
| Test Environment | Controlled lab single/multi eNB/gNB, scripted attach/handover loops, baseline 3GPP traces | have | ✅ 39 PLMN-00101 testbed traces |
| Test Environment (With Handover) | Dual eNB/gNB, scripted A3-triggered handovers and measurement reports | have | ❌ 1 signaled-HO trace (`16_23_40`, cells `0019b010`↔`0019c010`); needs collection |
