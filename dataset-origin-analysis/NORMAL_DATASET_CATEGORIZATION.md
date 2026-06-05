# MODI Normal Dataset — Radio/Cell Categorization

Source: `modi-dataset/dataset_csv/ai/normal/` (133 captures). Original names from `origin_records.orig_file`. MCC/MNC/band/EARFCN/PCI are decoded from the captures (NAS `e212` + RRC fields), not inferred.

**Tells:** LTE testbed = NAS PLMN **00101**. 5G testbed = **5G SA** (`nas-5gs`, open5gs core). Commercial = real network — LTE, **5G NSA** (n78 + `nas-eps`), 3G.

## Summary

| Category | Count |
|---|---|
| 3G (commercial) | 9 |
| LTE testbed | 31 |
| LTE commercial | 61 |
| 5G testbed (SA) | 1 |
| 5G commercial (NSA) | 31 |
| **Total** | **133** |

## 3G (commercial) (9)

| Original name | Current name | PLMN | Operator | Band(s) | EARFCN | PCI | Cell-ID |
|---|---|---|---|---|---|---|---|
| normal_2026_04_13_15_26_14.csv | 3g_commercial_45005_2026_04_13_15_26_14.csv | 440/20 | — | — | — | — | — |
| normal_2026_04_15_14_15_17.csv | 3g_commercial_45005_2026_04_15_14_15_17.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_15_14_17_31.csv | 3g_commercial_45005_2026_04_15_14_17_31.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_15_14_54_29.csv | 3g_commercial_45005_2026_04_15_14_54_29.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_15_15_39_25.csv | 3g_commercial_45005_2026_04_15_15_39_25.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_15_16_16_44.csv | 3g_commercial_45005_2026_04_15_16_16_44.csv | 434/11 | — | — | — | — | — |
| normal_2026_04_17_20_54_19.csv | 3g_commercial_45005_2026_04_17_20_54_19.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_21_15_06_48.csv | 3g_commercial_45005_2026_04_21_15_06_48.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_21_15_07_44.csv | 3g_commercial_45005_2026_04_21_15_07_44.csv | — | — | — | — | — | — |

## LTE testbed (31)

| Original name | Current name | PLMN | Operator | Band(s) | EARFCN | PCI | Cell-ID |
|---|---|---|---|---|---|---|---|
| normal_data.csv | lte_test_00101_2025_11_28_16_12_11.csv | 00101 | — | 8 | 3600, 3650 | 1, 2 | 19, 20 |
| normal_data2.csv | lte_test_00101_2025_11_28_16_14_38.csv | 00101 | — | 8 | 3600, 3650 | 1, 2, 27 | 19, 20 |
| normal_data3.csv | lte_test_00101_2025_11_28_16_17_07.csv | 00101 | — | 8 | 3600 | 1, 2 | 20 |
| normal_data4.csv | lte_test_00101_2025_11_28_16_19_43.csv | 00101 | — | 8 | 3600 | 1, 2 | 20 |
| normal_data5.csv | lte_test_00101_2025_11_28_16_21_22.csv | 00101 | — | 8 | 3600 | 1, 2, 15 | 20 |
| normal_data6.csv | lte_test_00101_2025_11_28_16_23_40.csv | 00101 | — | 1, 3, 5, 7… | 3600, 3650 | 1, 2 | 19, 20, 21, 25… |
| normal_data7.csv | lte_test_00101_2025_11_28_16_26_06.csv | 00101 | — | 8 | 3600, 3650 | 1, 2 | 19, 20 |
| normal_3_18_26_lte_2.csv | lte_test_00101_2026_03_18_17_15_21.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_4.csv | lte_test_00101_2026_03_18_17_18_35.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_5.csv | lte_test_00101_2026_03_18_17_20_23.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_6.csv | lte_test_00101_2026_03_18_17_22_19.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_7.csv | lte_test_00101_2026_03_18_17_24_11.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_8.csv | lte_test_00101_2026_03_18_17_25_59.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_9.csv | lte_test_00101_2026_03_18_17_28_45.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_10.csv | lte_test_00101_2026_03_18_17_29_35.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_11.csv | lte_test_00101_2026_03_18_17_31_23.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_12.csv | lte_test_00101_2026_03_18_17_33_09.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_13.csv | lte_test_00101_2026_03_18_17_34_49.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_14.csv | lte_test_00101_2026_03_18_17_37_21.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_15.csv | lte_test_00101_2026_03_18_17_38_53.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_16.csv | lte_test_00101_2026_03_18_17_40_41.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_17.csv | lte_test_00101_2026_03_18_17_42_39.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_18.csv | lte_test_00101_2026_03_18_17_45_37.csv | 00101 | — | 1, 3, 5, 7… | 2850 | 1, 2 | 19, 20, 21, 22… |
| normal_3_18_26_lte_19.csv | lte_test_00101_2026_03_18_17_46_51.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_20.csv | lte_test_00101_2026_03_18_17_48_33.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_21.csv | lte_test_00101_2026_03_18_17_50_25.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_22.csv | lte_test_00101_2026_03_18_17_52_43.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_24.csv | lte_test_00101_2026_03_18_17_54_17.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_25.csv | lte_test_00101_2026_03_18_17_55_57.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_3_18_26_lte_26.csv | lte_test_00101_2026_03_18_17_58_13.csv | 00101 | — | 8 | 2850 | 1, 2 | 19 |
| normal_2026_04_14_16_02_08.csv | lte_test_00101_2026_04_14_16_02_08.csv | 00101 | — | 1, 3, 5, 7… | — | — | 18, 20, 21, 22… |

## LTE commercial (61)

| Original name | Current name | PLMN | Operator | Band(s) | EARFCN | PCI | Cell-ID |
|---|---|---|---|---|---|---|---|
| normal_data8.csv | lte_commercial_45005_2026_03_09_16_07_03.csv | 450/12 | — | 1, 3, 5, 7… | — | — | 20, 21, 22, 25… |
| normal_data9.csv | lte_commercial_45005_2026_03_09_16_20_37.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_data10.csv | lte_commercial_45005_2026_03_11_14_17_48.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_data11.csv | lte_commercial_45005_2026_03_11_14_44_44.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_data12.csv | lte_commercial_45005_2026_03_11_15_16_53.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_data13.csv | lte_commercial_45005_2026_03_11_15_48_45.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_mixed3.csv | lte_commercial_45005_2026_03_20_14_44_44.csv | — | — | — | — | 354 | — |
| normal_mixed4.csv | lte_commercial_45005_2026_03_20_14_45_11.csv | — | — | — | — | 359 | — |
| normal_mixed5.csv | lte_commercial_45005_2026_03_20_14_45_35.csv | — | — | — | — | 298, 359 | — |
| normal_mixed7.csv | lte_commercial_45005_2026_03_20_14_47_37.csv | — | — | — | — | 359 | — |
| normal_mixed8.csv | lte_commercial_45005_2026_03_20_14_48_03.csv | — | — | — | — | 359 | — |
| normal_mixed14.csv | lte_commercial_45005_2026_03_20_14_57_13.csv | — | — | — | — | — | — |
| normal_udp_streaming1.csv | lte_commercial_45005_2026_03_20_15_57_18.csv | — | — | — | — | — | — |
| normal_udp_streaming3.csv | lte_commercial_45005_2026_03_20_15_58_11.csv | — | — | — | — | — | — |
| normal_2026_04_10_14_44_18.csv | lte_commercial_45005_2026_04_10_14_44_18.csv | KR450/05 | SK Telecom | 3 | 9410 | — | 25 |
| normal_2026_04_10_16_30_01.csv | lte_commercial_45005_2026_04_10_16_30_01.csv | KR450/05 | SK Telecom | 3 | 9410 | — | 25 |
| normal_2026_04_13_14_34_31.csv | lte_commercial_45005_2026_04_13_14_34_31.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_13_15_22_40.csv | lte_commercial_45005_2026_04_13_15_22_40.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_14_10_56_52.csv | lte_commercial_45005_2026_04_14_10_56_52.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_14_13_27_04.csv | lte_commercial_45005_2026_04_14_13_27_04.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_14_13_41_27.csv | lte_commercial_45005_2026_04_14_13_41_27.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_14_13_54_11.csv | lte_commercial_45005_2026_04_14_13_54_11.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_14_14_10_56.csv | lte_commercial_45005_2026_04_14_14_10_56.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_14_14_35_51.csv | lte_commercial_45005_2026_04_14_14_35_51.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_14_15_06_29.csv | lte_commercial_45005_2026_04_14_15_06_29.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_14_15_35_52.csv | lte_commercial_45005_2026_04_14_15_35_52.csv | KR450/05 | SK Telecom | 1, 3, 5, 7 | 3200 | — | 21, 25, 26, 31… |
| normal_2026_04_15_14_16_57.csv | lte_commercial_45005_2026_04_15_14_16_57.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_15_14_24_27.csv | lte_commercial_45005_2026_04_15_14_24_27.csv | KR450/05 | SK Telecom | 1, 3, 5, 7… | 3200 | — | 20, 21, 22, 25… |
| normal_2026_04_15_15_13_05.csv | lte_commercial_45005_2026_04_15_15_13_05.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_15_15_42_36.csv | lte_commercial_45005_2026_04_15_15_42_36.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_15_15_43_26.csv | lte_commercial_45005_2026_04_15_15_43_26.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_15_16_40_41.csv | lte_commercial_45005_2026_04_15_16_40_41.csv | 450/11 | — | — | — | — | — |
| normal_2026_04_15_17_03_56.csv | lte_commercial_45005_2026_04_15_17_03_56.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_15_17_04_50.csv | lte_commercial_45005_2026_04_15_17_04_50.csv | 450/11 | — | — | — | — | — |
| normal_2026_04_15_17_06_38.csv | lte_commercial_45005_2026_04_15_17_06_38.csv | KR450/05 | SK Telecom | 3 | 9410 | — | 25 |
| normal_2026_04_15_17_39_37.csv | lte_commercial_45005_2026_04_15_17_39_37.csv | 450/11 | — | — | 9410 | — | — |
| normal_2026_04_15_17_40_16.csv | lte_commercial_45005_2026_04_15_17_40_16.csv | KR450/05 | SK Telecom | 3 | 9410 | — | 25 |
| normal_2026_04_16_10_57_05.csv | lte_commercial_45005_2026_04_16_10_57_05.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_16_10_57_43.csv | lte_commercial_45005_2026_04_16_10_57_43.csv | 450/5 | — | — | — | — | — |
| normal_2026_04_16_12_51_27.csv | lte_commercial_45005_2026_04_16_12_51_27.csv | KR450/05 | SK Telecom | 3 | 9410 | — | 25 |
| normal_2026_04_16_13_38_02.csv | lte_commercial_45005_2026_04_16_13_38_02.csv | 450/11 | — | — | — | — | — |
| normal_2026_04_16_13_54_42.csv | lte_commercial_45005_2026_04_16_13_54_42.csv | KR450/05 | SK Telecom | 3 | 9410 | — | 25 |
| normal_2026_04_16_14_45_33.csv | lte_commercial_45005_2026_04_16_14_45_33.csv | 450/2 | — | — | — | — | — |
| normal_2026_04_16_17_22_52.csv | lte_commercial_45005_2026_04_16_17_22_52.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_16_17_28_17.csv | lte_commercial_45005_2026_04_16_17_28_17.csv | 450/11 | — | — | — | — | — |
| normal_2026_04_17_02_38_53.csv | lte_commercial_45005_2026_04_17_02_38_53.csv | KR450/05 | SK Telecom | 3, 5 | 3200 | — | 28, 79 |
| normal_2026_04_18_03_19_54.csv | lte_commercial_45005_2026_04_18_03_19_54.csv | KR450/05 | SK Telecom | 5 | 3200 | — | 79 |
| normal_2026_04_18_04_02_08.csv | lte_commercial_45005_2026_04_18_04_02_08.csv | 450/30 | — | 1, 3, 5, 8 | — | — | 26, 28, 75, 79… |
| normal_2026_04_18_04_06_14.csv | lte_commercial_45005_2026_04_18_04_06_14.csv | — | — | — | — | — | — |
| normal_2026_04_18_04_15_54.csv | lte_commercial_45005_2026_04_18_04_15_54.csv | 450/2 | — | 5 | 3200 | — | 79 |
| normal_2026_04_18_04_17_50.csv | lte_commercial_45005_2026_04_18_04_17_50.csv | 450/2 | — | 5 | 3200 | — | 79 |
| normal_2026_04_18_04_34_07.csv | lte_commercial_45005_2026_04_18_04_34_07.csv | KR450/05 | SK Telecom | 5 | 3200 | — | 79 |
| normal_2026_04_21_16_03_18.csv | lte_commercial_45005_2026_04_21_16_03_18.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_21_17_59_47.csv | lte_commercial_45005_2026_04_21_17_59_47.csv | KR450/05 | SK Telecom | — | — | — | — |
| normal_2026_04_27_16_45_46.csv | lte_commercial_45005_2026_04_27_16_45_46.csv | — | — | — | — | — | — |
| normal_2026_04_27_16_56_50.csv | lte_commercial_45005_2026_04_27_16_56_50.csv | 450/11 | — | 3 | 9410 | — | 25 |
| normal_2026_04_27_17_00_49.csv | lte_commercial_45005_2026_04_27_17_00_49.csv | — | — | — | — | — | — |
| normal_2026_04_27_17_01_29.csv | lte_commercial_45005_2026_04_27_17_01_29.csv | KR450/05 | SK Telecom | 3 | 3200 | — | 25 |
| normal_2026_04_30_14_02_29.csv | lte_commercial_45005_2026_04_30_14_02_29.csv | 450/30 | — | 5 | — | 0 | 24 |
| normal_2026_05_06_17_13_54.csv | lte_commercial_45005_2026_05_06_17_13_54.csv | 450/5 | — | — | — | — | — |
| normal_2026_05_06_17_26_33.csv | lte_commercial_45005_2026_05_06_17_26_33.csv | — | — | — | — | — | — |

## 5G testbed (SA) (1)

| Original name | Current name | PLMN | Operator | Band(s) | EARFCN | PCI | Cell-ID |
|---|---|---|---|---|---|---|---|
| normal_5g_session_72.csv | 5g_test_00101_2026_05_12_15_05_00.csv | — | — | n78 | — | — | nr:75 |

## 5G commercial (NSA) (31)

| Original name | Current name | PLMN | Operator | Band(s) | EARFCN | PCI | Cell-ID |
|---|---|---|---|---|---|---|---|
| normal_mixed1.csv | 5g_commercial_45005_2026_03_20_14_42_14.csv | 450/30 | — | 3, n78 | 475, 1694, 3743… | 8, 298, 354, 359 | 25 |
| normal_mixed2.csv | 5g_commercial_45005_2026_03_20_14_44_10.csv | — | — | n78 | 475, 10836 | 298, 354, 359 | — |
| normal_mixed6.csv | 5g_commercial_45005_2026_03_20_14_46_02.csv | 450/30 | — | 8, n78 | 475 | 298, 354, 359 | 22 |
| normal_mixed9.csv | 5g_commercial_45005_2026_03_20_14_48_28.csv | 450/30 | — | 1, 3, n78 | 475 | 25, 48, 242, 298… | 20, 21, 24, 25… |
| normal_mixed10.csv | 5g_commercial_45005_2026_03_20_14_53_45.csv | 450/30 | — | 8, n78 | 475 | 25, 48 | 17, 66 |
| normal_mixed11.csv | 5g_commercial_45005_2026_03_20_14_55_32.csv | 450/30 | — | 8, n78 | 475, 10836 | 25, 298 | 17 |
| normal_mixed12.csv | 5g_commercial_45005_2026_03_20_14_56_03.csv | — | — | n78 | 475, 10836 | 48 | — |
| normal_mixed13.csv | 5g_commercial_45005_2026_03_20_14_56_32.csv | 450/8 | — | 3, n78 | 475, 10836 | 48 | 23 |
| normal_mixed15.csv | 5g_commercial_45005_2026_03_20_14_57_37.csv | — | — | n78 | — | — | — |
| normal_mixed16.csv | 5g_commercial_45005_2026_03_20_14_58_02.csv | 450/30 | — | 1, 8, n78 | 475, 10836 | — | 17, 23, 24 |
| normal_mixed18.csv | 5g_commercial_45005_2026_03_20_15_01_49.csv | 450/30 | — | 3, n78 | 475, 10836 | — | 20, 23 |
| normal_udp_streaming2.csv | 5g_commercial_45005_2026_03_20_15_57_46.csv | — | — | n78 | — | — | — |
| normal_udp_streaming4.csv | 5g_commercial_45005_2026_03_20_15_58_33.csv | — | — | n78 | — | 48 | — |
| normal_udp_streaming5.csv | 5g_commercial_45005_2026_03_20_15_59_01.csv | 450/30 | — | 1, 3, n78 | 475, 3743, 10836 | 48 | 20, 23 |
| normal_udp_streaming6.csv | 5g_commercial_45005_2026_03_20_16_00_50.csv | — | — | n78 | 3743, 10836 | — | — |
| normal_udp_streaming7.csv | 5g_commercial_45005_2026_03_20_16_01_16.csv | 450/30 | — | 3, n78 | 475, 10836 | — | 20 |
| normal_voltecall2.csv | 5g_commercial_45005_2026_03_20_16_40_43.csv | — | — | n78 | — | — | — |
| normal_voltecall3.csv | 5g_commercial_45005_2026_03_20_16_41_54.csv | — | — | n78 | — | 48 | — |
| normal_voltecall4.csv | 5g_commercial_45005_2026_03_20_16_43_02.csv | — | — | n78 | — | 48 | — |
| normal_voltecall1.csv | 5g_commercial_45005_2026_03_20_16_45_20.csv | — | — | n78 | — | 298 | — |
| normal_2026_04_20_13_30_14.csv | 5g_commercial_45005_2026_04_20_13_30_14.csv | KR450/05 | SK Telecom | 1, n78 | 1350 | — | 81 |
| normal_2026_04_20_14_35_18.csv | 5g_commercial_45005_2026_04_20_14_35_18.csv | KR450/05 | SK Telecom | 1, 3, n78 | 275, 1350, 2500… | — | 23, 24, 25, 26… |
| normal_2026_04_21_17_47_29.csv | 5g_commercial_45005_2026_04_21_17_47_29.csv | KR450/05 | SK Telecom | 3, 5, n78 | 1350, 9410 | 297 | 25, 72 |
| normal_2026_04_21_17_48_59.csv | 5g_commercial_45005_2026_04_21_17_48_59.csv | KR450/05 | SK Telecom | 3, n78 | 275, 9410 | — | 25 |
| normal_2026_04_27_16_46_12.csv | 5g_commercial_45005_2026_04_27_16_46_12.csv | KR450/05 | SK Telecom | 1, 5, n78 | 1350 | — | 72, 81 |
| normal_2026_04_27_16_48_51.csv | 5g_commercial_45005_2026_04_27_16_48_51.csv | KR450/05 | SK Telecom | 3, n78 | 275, 9410 | — | 25 |
| normal_2026_04_30_14_03_33.csv | 5g_commercial_45005_2026_04_30_14_03_33.csv | KR450/05 | SK Telecom | 1, 3, 5, 7… | 2500, 2850, 3200… | 0, 55, 105, 184 | 17, 18, 19, 20… |
| normal_2026_04_30_15_08_32.csv | 5g_commercial_45005_2026_04_30_15_08_32.csv | KR450/05 | SK Telecom | 1, 3, 5, 7… | 100, 275, 1350… | 0, 16, 36, 105… | 15, 16, 17, 18… |
| normal_2026_05_14_14_31_43.csv | 5g_commercial_45005_2026_05_14_14_31_43.csv | 450/12 | — | 1, 3, 5, 7… | — | — | 20, 21, 25, 26… |
| normal_2026_05_14_15_22_36.csv | 5g_commercial_45005_2026_05_14_15_22_36.csv | KR450/05 | SK Telecom | 1, 3, 5, n78 | 275, 1350, 3200… | — | 20, 25, 81 |
| normal_mixed17.csv | 5g_commercial_45008_2026_03_20_15_00_58.csv | KR450/08 | KT | 3, 8, n78 | 475, 3743, 10836 | — | 17, 20 |

