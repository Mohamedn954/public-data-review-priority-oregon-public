# Codebook

Field-by-field reference for every dataset in this repository, complementing
`OR_Standalone_Policy_Paper.md` Section 3 (methods) and `PROVENANCE_MAP.md` (which maps
manuscript claims to the file and script that produced them).

**This document accompanies the public, de-identified replication package.** Every file
described below lives in `anonymized_data/` and contains no facility names, addresses,
telephone numbers, or license numbers. A corresponding non-public repository retains the
identifiable licensing records used during data construction and is not distributed
publicly. The `facility_id`/`cluster_id` crosswalks, and the raw research
records behind the corroboration finding described below, live in a separate,
non-networked repository that is not distributed at all, public or private.

## De-identification rule

`facility_id` (format `OR-F#####`) replaces `License_Number` as the row key in every
`anonymized_data/` file; `cluster_id` (format `OR###`) replaces the raw `phone_key` for
any facility in a shared-phone cluster of two or more licenses. `Facility_Name`,
`Physical_Address`, `City`, `ZIP`, `Phone`, and `Contact` are dropped entirely from the
public files. The crosswalks linking `facility_id`/`cluster_id` back to real identifiers
are not part of the public package and are not part of this project's private companion
repository either; see above.

## anonymized_data/OR_Providers_Enriched_ANON.csv (792 rows)

The core analysis file: one row per facility, merged from the roster and detail scrape,
enriched with shared-contact keys. Produced by `scripts/or_build_enriched.py`.

| Field | Meaning |
|---|---|
| `facility_id` | De-identified row key |
| `License_Status` | Always `Open` in this snapshot (Status=Open filter applied at scrape) |
| `County` | Clackamas or Washington, from the state portal's own county field (Section 3.1) |
| `Licensed_Capacity` | Licensed bed count |
| `Specialty` | Facility type: AFH (Adult Foster Home, Oregon's official term), ALF, RCF, NF, or a memory-care variant, collapsed to the four base types for Sections 4 and 5 |
| `Contract` | Medicaid contract designation as published, if any |
| `RCS_Region_Unit`, `Has_Public_Reports` | Carried in the schema for Washington-pipeline compatibility; 100% missing for Oregon (Section 3.4), not a substantive finding |
| `n_inspections`, `n_investigations`, `n_enforcement`, `n_limitations`, `n_civil_fines`, `n_stop_placement`, `n_conditions`, `n_docs_total` | Counts of retained public documents by category (Section 3.3 field mapping); `n_stop_placement` is NA/not observed for all facilities (Section 3.3), not a true zero |
| `latest_year`, `latest_enforcement_year` | Most recent year with any retained document; not populated in this replication |
| `addr_shared_count`, `phone_shared_count` | Facilities sharing the same normalized address / phone key, including the facility itself (Section 4.4) |
| `cluster_id` | `OR001`... if `phone_shared_count >= 2`, else blank |

## anonymized_data/OR_Reports_ANON.csv (792 rows)

Per-facility detail-page counts before merge; feeds `OR_Providers_Enriched_ANON.csv`.
Same count fields as above, keyed by `facility_id` and `County` only.

## anonymized_data/OR_Facility_RedFlags_ANON.csv (792 rows)

RF-03, RF-08, and derived flags applied per facility. Produced by `scripts/or_build_rf_coding.py`.
`RF03_multi_home_operator` (phone_shared_count >= 2), `RF08_network_cluster`
(phone_shared_count >= 3), `high_complaint_load` (n_investigations >= 3),
`has_enforcement`, `has_stop_placement` (always False, NA field), `has_condition`,
`RF06_exclusion_match` (always blank, RF-06 cross-match not performed, Section 7).

## anonymized_data/OR_Operator_PhoneClusters_ANON.csv (49 rows)

One row per shared-phone cluster (`phone_shared_count >= 2`), aggregated by `cluster_id`.
Underlies Section 5's Tier A-D diagnostic and Section 5.1's threshold-sensitivity table.

## anonymized_data/OR_County_Concentration.csv, OR_County_Normalized_Risk.csv

County-level aggregates only; contain no facility-level rows, so they carry no
de-identification requirement. Source for Section 4.2 (pooled rates), Section 4.3
(demographic normalization), and the facility-type-stratified table added to Section 4.2.

## anonymized_data/OR_A5_Cluster_Corroboration_ANON.csv (49 rows)

Cluster-level output of a registry-corroboration check: for each of the 49 `cluster_id`
values in `OR_Operator_PhoneClusters_ANON.csv`, whether a shared officer, owner, manager,
or business address linking the licensed entities was found in the Oregon Secretary of
State business registry, independent of facility type or Section 5's Tier A-D
categorization (Section 5.2 of the working paper).

| Field | Meaning |
|---|---|
| `cluster_id` | Matches `OR_Operator_PhoneClusters_ANON.csv` |
| `n_facilities` | Cluster size |
| `county` | Clackamas or Washington |
| `evidence_class` | Same openly disclosed brand / Same officers, owners, or managers / Same residential or business address only / Same legal entity / No public connection found / Indeterminate |
| `corroboration_result` | Corroborated / Corroborated (control-related) / Corroborated (administrative-linkage only) / Corroborated (direct) / Not corroborated / Indeterminate |

## Raw, identifiable data (not in this repository)

The private companion repository's `data/` folder carries the same schema as
`anonymized_data/` above, keyed by `License_Number` with real facility names, addresses,
and phone numbers retained. Neither it, nor the `facility_id`/`cluster_id` crosswalks, nor
the raw registry-search records behind the file above, are part of this public package.
