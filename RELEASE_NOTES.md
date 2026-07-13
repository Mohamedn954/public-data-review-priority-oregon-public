# Release Notes

## Canonical citation

> Hussein, M. N. (2026). *Can Public Long-Term-Care Oversight Methods Travel
> Across States? A Two-County Oregon Cross-State Applicability Study*
> [Data set and replication package]. Version 1.0.
> https://github.com/Mohamedn954/public-data-review-priority-oregon-public

This is the **public, journal-safe replication package**. The private
companion repository, `public-data-review-priority-oregon`, holds the
original, non-anonymized facility-level data used to produce this package.

## Version and release date

- **Version:** 1.0
- **Release date:** 2026-07-13
- This is the first frozen release of the Oregon cross-state applicability
  study, covering the full Clackamas/Washington County replication, the
  eight-tier RF-01 through RF-20 evidentiary matrix, and the two official
  enforcement matters and two SOQ licensing-unit evaluations discussed in the
  manuscript. This release corresponds to the `v1` git tag on this
  repository's single squashed commit.

## Contents of this release

- `anonymized_data/`: the de-identified replication dataset (facility_id and
  cluster_id in place of real identifiers).
- `OR_Facility_Type_Crosswalk.csv`: resolves Oregon's raw licensing
  `Specialty` values (including memory-care endorsements) to the four base
  facility types (AFH, ALF, RCF, NF) the manuscript reports.
- `OR_RF_Evidence_Matrix.csv`: the manuscript's Section 7 master evidence
  matrix (all 20 RF indicators, evidentiary status, and basis) in
  machine-readable form.
- `scripts/`: the five `or_build_*.py` pipeline scripts, `or_build_figures.py`
  (generates all seven manuscript figures, reading its RF classifications
  directly from `OR_RF_Evidence_Matrix.csv` so the figure cannot drift out of
  sync with the matrix), `verify_oregon_numbers.py` (independent headline-number
  verification), and `or_analyze_rf_status.py`.
- `figures/`: the seven manuscript figures as PNG files.
- `CODEBOOK.md`, `PROVENANCE_MAP.md`, `SOURCE_MANIFEST.md`.
- `requirements.txt`: Python dependencies (`pandas>=2.0`, `matplotlib>=3.8`).
- `LICENSE` (CC BY 4.0) and `CITATION.cff`.

## Validation status

- **Internal consistency:** `verify_oregon_numbers.py` confirms every
  headline number in the manuscript reproduces from `anonymized_data/` alone,
  and that no raw identifier leaks into that folder.
- **External validation:** none. This release has **not** been peer-reviewed
  and has **not** been validated against Oregon Health Authority claims data.
  It is a companion to, not part of, the published Washington manuscript
  (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7070198).
- **Not validated:** no RF indicator or evidentiary-status classification in
  this repository has been checked against claims outcomes or confirmed
  fraud/waste/abuse findings.

## Guardrails and intended use

This project is a cross-state applicability and evidentiary-boundary study,
not a fraud score, a validated predictive model, or an enforcement
determination. No Oregon facility or operator is identified, ranked, or
alleged to have committed fraud in any manuscript claim or derived output.

**Not intended use:** as a standalone tool for auditing, sanctioning,
excluding, or making any adverse determination about a specific facility or
operator; or as a substitute for claims-informed program-integrity review.

## Update — 2026-07-19

- Added `anonymized_data/OR_A5_Cluster_Corroboration_ANON.csv`: the working paper's new
  Section 5.2 reports a registry-corroboration check of all 49 shared-contact clusters
  against the Oregon Secretary of State business registry (47 of 49 corroborated, 11 of
  those recoverable only through registry evidence rather than facility naming). This
  file is the anonymized cluster-level output of that check, now covered by
  `verify_oregon_numbers.py`. Related language in `README.md`, `CODEBOOK.md`, and
  `PROVENANCE_MAP.md` was updated to match.

## Archival location / DOI

- **DOI:** not yet minted. Zenodo/DOI archival, tied to this repository's
  `v1` tag, has not been started as of this release, consistent with the
  same open item on the companion Washington public repository.
- **Current authoritative location:** the `main` branch of
  `https://github.com/Mohamedn954/public-data-review-priority-oregon-public`,
  frozen at the `v1` tag.
