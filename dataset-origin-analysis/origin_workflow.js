export const meta = {
  name: 'dataset-origin-analysis',
  description: 'Adversarially verify origin derivations and write narrative for the normal-capture origin report',
  phases: [
    { title: 'Verify', detail: 'check reference tables, commercial/test split, anomalies against raw data' },
    { title: 'Narrate', detail: 'write grounded narrative sections' },
    { title: 'Synthesize', detail: 'merge into one consumable JSON' },
  ],
}

const RECORDS = '/Users/roastedbeans/Documents/Github/modi-project/dataset-origin-analysis/origin_records.json'
const NORMAL = '/Users/roastedbeans/Documents/Github/modi-project/modi-parser/dataset_csv/spec/normal'
const README = '/Users/roastedbeans/Documents/Github/modi-project/modi-dataset/README.md'

const GROUND = `
GROUND TRUTH (from dataset owner + README), UPDATED origin rule:
- The normal set has TWO origins, now 102 commercial and 31 test/lab (counts in origin_records.json
  aggregate by_origin_class / by_origin_reason).
- The lab is the srsRAN + Open5GS + LibreSDR B220 mini testbed. It is identified by ANY of: PLMN 00101,
  OR LTE Band 8 (900 MHz), OR NR n78/n79 (the testbed runs 5G on n78/n79). The CSV schema has NO NR
  carrier ARFCN, so "NR present with no commercial identity" stands in for an n78/n79 testbed capture.
- A REAL COMMERCIAL identity ALWAYS WINS over the band rule: a 450/xx serving PLMN (450/05 = SK Telecom,
  450/08 = KT) or paging of foreign-roamer IMSIs (a single 00101 SIM cannot page Chinese/Japanese
  subscribers) marks a capture commercial even if it also touches Band 8 or NR. So 11 NR/5G-NSA files
  that carry SKT/KT PLMN + foreign paging are genuine commercial 5G, NOT test.
- The 31 test/lab files: 4 by PLMN 00101 (normal_data/data2/data6/data7), 3 by LTE Band 8
  (normal_data3/data4/data5), 24 by NR-without-commercial-identity (normal_mixed*, udp_streaming*,
  voltecall*, 5g_session_72, 2026_05_14_14_31_43).
- Commercial captures were taken on rooted Qualcomm phones (OnePlus 9 Pro, Samsung S20/S22) via the MODI
  app (diag_mdlog) in Seoul; the capturing UE roams on a Globe PH SIM (own IMSI 515027302508642).
- Per-file evidence is in origin_records.json at ${RECORDS} (each record has origin_class + origin_reason).
  Raw CSVs in ${NORMAL}; Wireshark _show/_value/_showname triples, -1 = field absent. Operator identity
  is reliable from e212_gummei and full e212_imsi only; per-digit lte-rrc/nr-rrc mcc/mnc are unreliable.
You may Read origin_records.json and run Bash on the raw CSVs. Return ONLY the requested object, terse and evidence-based.`

const VERIFY_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['confirmations', 'corrections', 'caveats'],
  properties: {
    confirmations: { type: 'array', items: { type: 'string' }, description: 'Derivations that check out, with the evidence' },
    corrections: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['item', 'claimed', 'correct', 'evidence'],
        properties: {
          item: { type: 'string' }, claimed: { type: 'string' },
          correct: { type: 'string' }, evidence: { type: 'string' },
        },
      },
    },
    caveats: { type: 'array', items: { type: 'string' }, description: 'Limitations/uncertainties a reader must know' },
  },
}

phase('Verify')
const [vTables, vSplit, vAnomalies] = await parallel([
  () => agent(`${GROUND}

TASK: Adversarially verify the REFERENCE-TABLE derivations used in origin_records.json.
Check and either confirm or correct:
1. LTE EARFCN -> band/centre-frequency mapping for the EARFCNs actually observed in the data
   (read the "band_observations" aggregate and a few records' frequency.earfcns; verify e.g. 3200->B7,
   9410->B28 per 3GPP TS 36.101).
2. PLMN -> operator names (450/05=SK Telecom, 450/08=KT).
3. lte-rrc_q_rxlevmin decode (SIB1 q-RxLevMin is in 2 dBm steps; value 64 -> ? dBm). cellbarred meaning.
4. RAT classification logic (lte_rrc/nr_rrc/nas_eps/nas_5gs presence -> LTE vs 5G-NSA vs 5G).
5. nas security_header_type values (0,1,2,3,4) meaning.
Sample raw CSVs where useful.`, { label: 'verify:reference-tables', phase: 'Verify', schema: VERIFY_SCHEMA }),

  () => agent(`${GROUND}

TASK: Adversarially verify the UPDATED commercial-vs-test split (102 commercial / 31 test/lab) and the
band-based test rule.
1. Confirm the 31 test/lab files are correctly labeled: the 3 Band-8 files (normal_data3/4/5) really serve
   or measure only LTE Band 8 with no commercial PLMN and no foreign paging; the 24 NR files have NR
   present, no 450/xx PLMN, and (almost all) zero paged IMSIs. Spot-check raw CSVs.
2. Confirm the 11 NR files kept COMMERCIAL (SKT/KT PLMN + foreign paging) genuinely cannot be testbed:
   a single 00101 SIM cannot page Chinese/Japanese roamers. Spot-check 1-2.
3. Stress the rule: is "NR present + no commercial identity => n78/n79 testbed" safe given there is no NR
   ARFCN in the schema? Could any of those 24 actually be commercial 5G with the attach just not captured?
   Give the strongest counter-argument and whether the label still holds.
4. Note any file you believe is mislabeled under the new rule.`, { label: 'verify:origin-split', phase: 'Verify', schema: VERIFY_SCHEMA }),

  () => agent(`${GROUND}

TASK: Investigate ANOMALIES/edge cases and say whether each is a real data property or an artifact.
1. The 9 "unknown" RAT files: normal_2026_04_13_15_26_14, _04_15_14_15_17, _04_15_14_17_31,
   _04_15_14_54_29, _04_15_15_39_25, _04_15_16_16_44, _04_17_20_54_19, _04_21_15_06_48, _04_21_15_07_44.
   What do they actually contain? (read a few)
2. Duration outliers: normal_2026_04_20_14_35_18 reports ~58392 s (16 h). Is the timestamp column a
   monotonic capture clock or can it jump? Check.
3. The single 5G-only file (normal_5g_session_72) and dual-band (B7+B28) files: real or measurement-config
   neighbour frequencies vs serving cell?
4. Empty or near-empty captures.
Return findings as confirmations/corrections/caveats.`, { label: 'verify:anomalies', phase: 'Verify', schema: VERIFY_SCHEMA }),
])

const verifyDigest = JSON.stringify({ vTables, vSplit, vAnomalies }, null, 1)
log('Verification complete; writing narrative grounded in corrections')

phase('Narrate')
const SECTION_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['html'],
  properties: { html: { type: 'string', description: 'Self-contained HTML fragment (use <h3>,<p>,<ul>,<table>; no <script>, no inline color styles). Plain prose grounded in the data.' } },
}
const NARR = `${GROUND}

VERIFICATION RESULTS (apply any corrections; respect caveats):
${verifyDigest}

Write a grounded, factual HTML FRAGMENT (no <html>/<body>/<script>, no document wrapper). Use the exact
numbers from origin_records.json aggregate. Do not invent. Plain, plain-language technical prose. Avoid
the words "corpus" and "verbatim". No semicolons in prose, no em dashes.`

const [secOverview, secRf, secSecId, secGroups] = await parallel([
  () => agent(`${NARR}

SECTION: "Origin overview". 2-3 short paragraphs: what the normal set is (133 captures), the two origins
(102 commercial real South Korean networks vs 31 srsRAN/Open5GS lab captures) and HOW the test set is
identified (PLMN 00101, LTE Band 8, NR n78/n79, with commercial PLMN or foreign paging overriding the
band rule). Give the test-set composition (4 by PLMN 00101, 3 by Band 8, 24 by NR-without-commercial-
identity). State the RAT mix (LTE/5G-NSA/5G/3G-UMTS counts from the aggregate), the collection method
(rooted Qualcomm UE + MODI/diag_mdlog, Globe PH roaming SIM), and the headline that these are the benign
baseline for a UE-side FBS detector.`, { label: 'narrate:overview', phase: 'Narrate', schema: SECTION_SCHEMA }),

  () => agent(`${NARR}

SECTION: "Radio origin: cells, bands, tracking areas". Describe what base-station origin evidence the
captures expose: serving/neighbour EARFCNs and the LTE bands they map to (use band_observations), the
eNB cell identities and physical cell IDs observed, tracking area codes, and cell-selection parameters
(q-RxLevMin, cellBarred, reselection priorities). Explain these come from SIB1/SIB broadcasts of the
serving cell. One compact summary <table> of the band distribution is welcome.`, { label: 'narrate:rf-cell', phase: 'Narrate', schema: SECTION_SCHEMA }),

  () => agent(`${NARR}

SECTION: "Security configuration and subscriber identities". Cover: NAS/AS security algorithms advertised
(EEA/EIA, 5G-EA/IA, including null EEA0/EIA0), NAS security-header-type values seen, presence of message
authentication codes, and the identity picture: SUCI/IMSI/TMSI/5G-TMSI usage, and the key privacy point
that commercial captures contain paged IMSIs of many third-party subscribers from foreign home networks
while the lab captures contain none. Keep it precise.`, { label: 'narrate:sec-id', phase: 'Narrate', schema: SECTION_SCHEMA }),

  () => agent(`${NARR}

SECTION: "Activity groups". Briefly characterise each filename group and its origin/traffic profile:
timestamped DIAG session (67), LTE batch 2026-03-18 (23), mixed activity (18), data session (13),
UDP streaming (7), VoLTE call (4), 5G session (1). Note which groups are commercial vs lab and what
signalling each tends to show. A small <table> (group, count, origin, notes) is ideal.`, { label: 'narrate:groups', phase: 'Narrate', schema: SECTION_SCHEMA }),
])

phase('Synthesize')
const FINAL_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['key_findings', 'corrections_applied', 'caveats'],
  properties: {
    key_findings: { type: 'array', items: { type: 'string' }, description: '6-10 crisp headline findings about the origin of the normal data' },
    corrections_applied: { type: 'array', items: { type: 'string' }, description: 'Any reference-table or label corrections the report should reflect' },
    caveats: { type: 'array', items: { type: 'string' }, description: 'Limitations a reader must keep in mind' },
  },
}
const synth = await agent(`${GROUND}

VERIFICATION RESULTS:
${verifyDigest}

TASK: Produce the consolidated headline JSON for the origin report. key_findings = the 6-10 most important,
evidence-backed statements about where the normal captures come from (origins, operators, RAT, bands,
identity/privacy, lab-vs-commercial). corrections_applied = concrete fixes the report must reflect (e.g. a
band or dBm decode that was wrong). caveats = honest limitations (e.g. per-digit mcc fields, missing PLMN
in many files, timestamp meaning).`, { label: 'synthesize', phase: 'Synthesize', schema: FINAL_SCHEMA })

return {
  verify: { vTables, vSplit, vAnomalies },
  sections: {
    overview: secOverview.html,
    rf_cell: secRf.html,
    security_identity: secSecId.html,
    groups: secGroups.html,
  },
  synthesis: synth,
}
