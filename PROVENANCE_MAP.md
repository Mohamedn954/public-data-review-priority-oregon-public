# Provenance Map

Maps every table, figure, and headline number in `OR_Standalone_Policy_Paper.md` to the
file and script that produced it, and states whether it is reproducible from this public
`anonymized_data/` package alone or additionally requires the non-public companion
repository.

| Paper element | Source file(s) | Script | Reproducible from public package alone? |
|---|---|---|---|
| Section 4.1 (792 facilities, record counts) | `OR_Providers_Enriched_ANON.csv`, `OR_Reports_ANON.csv` | `or_build_enriched.py` | Yes |
| Section 4.2 pooled county table | `OR_County_Concentration.csv` | `or_build_normalized.py` | Yes |
| Section 4.2 facility-type-stratified table | `OR_Facility_RedFlags_ANON.csv` (grouped by County x Specialty) | `or_build_rf_coding.py` | Yes |
| Section 4.3 demographic normalization | `OR_County_Normalized_Risk.csv` | `or_build_normalized.py` | Yes |
| Section 4.4, Section 5, Section 5.1 (clustering, tiers, threshold sensitivity) | `OR_Operator_PhoneClusters_ANON.csv`, `OR_Providers_Enriched_ANON.csv` | `or_build_clusters.py` | Yes for the counts; Tier A-D facility-type labels require the private `data/` roster's `Specialty` and address fields, not shipped at facility level in the anonymized package beyond the aggregate counts already reported in the paper |
| Section 5.2 (registry corroboration of shared-contact clusters) | `OR_A5_Cluster_Corroboration_ANON.csv` | N/A, manual registry research against the Oregon Secretary of State business registry | Yes for the anonymized 5-class tally reported in the paper's table; the underlying registry search records (real names, addresses) are not reproducible from any repository in this project's public or private companion set |
| Figure 1 (pipeline architecture) | Diagram only, no data dependency | `or_build_figures.py` | Yes |
| Figure 2 (WA vs. OR AFH-only comparison) | `OR_Providers_Enriched_ANON.csv` (Oregon side); WA `anonymized_data/WA_AFH_3County_Enriched_ANON.csv` (Washington side, companion repository) | `or_build_figures.py` | Oregon side yes; Washington side requires the companion Washington public repository |
| Figure 3 (RF evidence matrix) | Section 7 table (manual classification, not a computed statistic) | `or_build_figures.py` | Yes (renders the table's own categories, introduces no new number) |
| Figure 4 (facility-type composition) | `OR_Facility_RedFlags_ANON.csv` | `or_build_figures.py` | Yes |
| Figure 5 (threshold sensitivity) | `OR_Operator_PhoneClusters_ANON.csv`, `OR_Providers_Enriched_ANON.csv` | `or_build_figures.py` | Yes |
| Figure 6 (oversight/enforcement timeline) | Dates only, from Section 6's cited sources | `or_build_figures.py` | Yes |
| Figure 7 (research roadmap) | Section 9 text, no data dependency | `or_build_figures.py` | Yes |
| Section 6.1 case narratives | Official public filings (`SOURCE_MANIFEST.md`), not a repository data file | N/A, manual research | Yes, all cited sources are public |
| Section 6.2 SOQ evaluation findings | Official reports (`SOURCE_MANIFEST.md`) | N/A, manual research | Yes |
| Section 7 RF matrix classifications | Sections 4-6 collectively | N/A, manual synthesis documented in Section 7's own text | Yes |
| `verify_oregon_numbers.py` | All `anonymized_data/` files above | Recomputes and checks every headline number in Sections 4, 5, and 7 against the shipped dataset | Yes |

**What requires the private repository specifically:** the raw `data/` roster (real
facility names, addresses, phone numbers), and full re-execution of the data-collection
step from Oregon's public portal forward. No number reported in the paper's tables or
figures requires the private repository to independently verify; the private repository
is needed only to reconstruct the pipeline from raw source data rather than from the
already-merged, de-identified intermediate files. The `facility_id`/`cluster_id`
crosswalks and the raw registry-search records behind Section 5.2's finding are not part
of the private repository either; they live in a separate, non-networked repository that
is not distributed at all.
