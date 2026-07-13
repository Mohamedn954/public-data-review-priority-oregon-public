# Oregon Replication of a Public-Data Review-Priority Framework for Medicaid Residential Care Oversight — Public Replication Package

This is the **public, journal-safe replication package** for the working paper *"Can Public
Long-Term-Care Oversight Methods Travel Across States? A Two-County Oregon Cross-State
Applicability Study"* (Mohamed Noor Hussein). The question it tests: does a public-data
review-priority framework, originally built for Washington State's Adult Family Home
sector, keep its core merge, normalization, clustering, and threshold logic intact once it
moves to a second state with a broader facility-type mix? The test case is Clackamas and
Washington County, Oregon, after Oregon-specific schema harmonization and source mapping,
across Adult Foster Homes (AFH, Oregon's official term for the facility type Washington
calls Adult Family Homes), Assisted Living Facilities (ALF), Residential Care Facilities
(RCF), and Nursing Facilities (NF).

A non-public companion repository holds the original, non-anonymized facility-level data
(names, addresses, phone numbers, license numbers) this package was built from. Nothing
here does: this repository contains **no facility-level identifiers**.

This is a companion to the Washington manuscript and its own public replication package at
[`public-data-review-priority-afh-public`](https://github.com/Mohamedn954/public-data-review-priority-afh-public),
not part of it. No manuscript result depends on anything in this repository, and nothing
here validates, revises, or supersedes the Washington pilot.

## What's included

- `anonymized_data/OR_Providers_Enriched_ANON.csv`, `OR_Reports_ANON.csv`,
  `OR_Facility_RedFlags_ANON.csv`, `OR_Operator_PhoneClusters_ANON.csv`: facility-level data
  with `facility_id` (e.g. `OR-F00001`) and `cluster_id` (e.g. `OR001`) in place of real
  identifiers.
- `anonymized_data/OR_A5_Cluster_Corroboration_ANON.csv`: cluster-level output of a
  registry-corroboration check of all 49 shared-phone clusters against the Oregon
  Secretary of State business registry (Section 5.2), reporting a 5-class evidence
  taxonomy with no names or addresses.
- `anonymized_data/OR_County_Concentration.csv` and `OR_County_Normalized_Risk.csv`:
  county-level aggregates, which contain no facility-level detail to begin with.
- `scripts/`: adapted copies of the real Washington pipeline scripts
  (`or_build_enriched.py`, `or_build_clusters.py`, `or_build_rf_coding.py`,
  `or_build_normalized.py`, `or_build_anonymized.py`), changed only in file paths and
  Oregon-specific field mappings, not in merge logic, key-normalization logic, or numeric
  thresholds; `or_analyze_rf_status.py`, supplementary Section 5 analyses runnable against
  `anonymized_data/` alone; `or_build_figures.py`, which generates all seven manuscript
  figures from numbers already reported in the paper's own tables; and
  `verify_oregon_numbers.py`, which independently recomputes every headline number in the
  manuscript and fails loudly on any mismatch.
- `figures/`: the seven manuscript figures as PNG files, reproducible from
  `anonymized_data/` alone via `or_build_figures.py`.
- `CODEBOOK.md`: field-by-field reference for every file in `anonymized_data/`.
- `PROVENANCE_MAP.md`: links each manuscript table and figure to the script that produced
  it and states whether it is reproducible from this public package alone.
- `SOURCE_MANIFEST.md`: every public URL the manuscript depends on, with its access date.
- `OR_Facility_Type_Crosswalk.csv`: resolves Oregon's raw licensing `Specialty` values
  (including memory-care endorsements) to the four base facility types (AFH, ALF, RCF, NF)
  the manuscript reports.
- `OR_RF_Evidence_Matrix.csv`: the manuscript's Section 7 master evidence matrix (all 20
  RF indicators, evidentiary status, and basis) in machine-readable form; `or_build_figures.py`
  reads this file directly when generating Figure 3, so the figure cannot drift out of sync
  with the matrix.
- `requirements.txt`: Python dependencies (`pandas>=2.0`, `matplotlib>=3.8`).
- `RELEASE_NOTES.md`: version history and validation status for this release.

The headline numbers are independently verifiable from `anonymized_data/` alone; full
regeneration from raw source data requires the private companion repository.

## What's excluded from this repository

The working paper (`OR_Standalone_Policy_Paper.md/.docx/.pdf`) is present as a local file if
you cloned this alongside the private companion repository, but is intentionally not
tracked in this public repository's git history; it remains fully tracked in the private
companion repository. This mirrors the convention used for the Washington manuscript.

The private companion repository additionally includes the raw roster and enforcement data
with real facility names, physical addresses, and telephone numbers. The crosswalks
mapping `facility_id`/`cluster_id` back to those real identifiers, and the raw
registry-search records behind the Section 5.2 corroboration finding, live in a separate,
non-networked repository that is not distributed at all, public or private.

## Why raw data is not published

Oregon's licensing portal is itself public, and Adult Foster Home facility names in Oregon's
data are frequently the individual operator's own personal name (not a business name).
Publishing that raw roster alongside an analytical narrative that categorizes and discusses
clusters of facilities creates a re-identification and reputational risk that a purely
aggregate or de-identified release does not. Real identifiers are held only in the private
companion repository.

## How to verify the headline numbers yourself

With `pandas` installed:

```bash
python3 -c "
import pandas as pd
e = pd.read_csv('anonymized_data/OR_Providers_Enriched_ANON.csv')
for c in ['phone_shared_count', 'n_enforcement', 'n_investigations']:
    e[c] = pd.to_numeric(e[c], errors='coerce')
print('facilities:', len(e))
print('county split:', e['County'].value_counts().to_dict())
print('phone_shared_count>=2 (RF-03):', int((e['phone_shared_count'] >= 2).sum()))
print('phone_shared_count>=3 (RF-08):', int((e['phone_shared_count'] >= 3).sum()))
"
```

Expected output: 792 facilities; Clackamas 324 / Washington 468; RF-03 = 101 facilities
forming 49 distinct clusters (see `anonymized_data/OR_Operator_PhoneClusters_ANON.csv`, 49
rows); RF-08 = 5, all belonging to one 5-license same-brand cluster.

## Guardrails, in brief

- This is a **methods-transfer test**, not a fraud-detection exercise and not a validated
  adverse-action tool. No fraud, abuse, or wrongdoing is alleged against any Oregon facility
  or operator anywhere in this repository.
- No facility or operator is named in any document in this repository.
- Numeric thresholds (RF-03 ≥2, RF-08 ≥3) are the Washington pipeline's original
  thresholds, retained without adjustment to test portability. They are not
  claims-validated, and the single RF-08 flag in this dataset is a same-brand,
  multi-property cluster; see `OR_A5_Cluster_Corroboration_ANON.csv` and Section 5.2 of
  the working paper for the registry-corroboration check of all 49 underlying clusters.
- This study covers two counties, one state, two snapshot dates six days apart. It is not a
  multi-state validated model and should not be generalized beyond what is directly tested
  here.

## License and citation

This repository is licensed under [CC BY 4.0](LICENSE). See `CITATION.cff` for
the preferred citation.
