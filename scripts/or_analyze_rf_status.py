#!/usr/bin/env python3
"""Fast-track Section 5 essential analyses for the Oregon RF-01-RF-20
strengthening plan. Computes, from the public anonymized_data/ package alone
(no records-request data required):

  1. Facility counts and licensed capacity by county and facility type
  2. Facility-based investigation/enforcement rates with exact numerators/denominators
  3. Facility-type-standardized county comparison
  4. RF-08 results under multiple thresholds (2/3/4/5) and campus-pair exclusion
  5. AFH-only like-for-like Oregon vs. Washington comparison
  6. Public-record missingness / cross-source discrepancy summary

All numbers here are descriptive counts from the de-identified public package;
none of this constitutes claims-level validation. See the fast-track plan's
evidence-status system for how each output should be labeled in the paper.
"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
OR_DIR = os.path.join(os.path.dirname(BASE), "anonymized_data")
# This repo is Oregon-only; the WA comparison in section 5 needs a checked-out
# copy of the WA repo's anonymized_data/ package. Point WA_ANON_DIR at it, e.g.:
#   WA_ANON_DIR=/path/to/public-data-review-priority-afh/anonymized_data python3 or_analyze_rf_status.py
WA_DIR = os.environ.get("WA_ANON_DIR")

or_df = pd.read_csv(os.path.join(OR_DIR, "OR_Providers_Enriched_ANON.csv"))
wa_df = None
if WA_DIR and os.path.exists(os.path.join(WA_DIR, "WA_AFH_3County_Enriched_ANON.csv")):
    wa_df = pd.read_csv(os.path.join(WA_DIR, "WA_AFH_3County_Enriched_ANON.csv"))


def hr(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ---------------------------------------------------------------------------
# 1. Facility counts and licensed capacity by county and facility type
# ---------------------------------------------------------------------------
hr("1. Facility counts and licensed capacity, by county x facility type")
t1 = (
    or_df.groupby(["County", "Specialty"])
    .agg(facilities=("facility_id", "count"), total_beds=("Licensed_Capacity", "sum"))
    .reset_index()
)
print(t1.to_string(index=False))
print(f"\nTOTAL: {len(or_df)} facilities, {int(or_df['Licensed_Capacity'].sum())} licensed beds")

# ---------------------------------------------------------------------------
# 2. Facility-based investigation/enforcement rates, exact num/denom
# ---------------------------------------------------------------------------
hr("2. Facility-based investigation / enforcement rates (exact numerator/denominator)")
n = len(or_df)
n_inv = int((or_df["n_investigations"] >= 1).sum())
n_enf = int((or_df["n_enforcement"] >= 1).sum())
print(f"Facilities with >=1 investigation: {n_inv}/{n} ({100*n_inv/n:.1f}%)")
print(f"Facilities with >=1 enforcement action: {n_enf}/{n} ({100*n_enf/n:.1f}%)")
for county in sorted(or_df["County"].unique()):
    sub = or_df[or_df["County"] == county]
    ni = int((sub["n_investigations"] >= 1).sum())
    ne = int((sub["n_enforcement"] >= 1).sum())
    print(f"  {county}: investigations {ni}/{len(sub)} ({100*ni/len(sub):.1f}%), "
          f"enforcement {ne}/{len(sub)} ({100*ne/len(sub):.1f}%)")

# ---------------------------------------------------------------------------
# 3. Facility-type-standardized county comparison
# ---------------------------------------------------------------------------
hr("3. Facility-type-standardized county comparison (rates within type, then overall)")
or_df["has_inv"] = or_df["n_investigations"] >= 1
or_df["has_enf"] = or_df["n_enforcement"] >= 1
t3 = (
    or_df.groupby(["County", "Specialty"])
    .agg(facilities=("facility_id", "count"),
         inv_rate_pct=("has_inv", lambda s: round(100 * s.mean(), 1)),
         enf_rate_pct=("has_enf", lambda s: round(100 * s.mean(), 1)))
    .reset_index()
)
print(t3.to_string(index=False))
print("\nNote: raw county comparison (unstratified) risks confounding since County x "
      "Specialty composition differs; use the stratified table above, not a single "
      "county-level rate, when comparing Clackamas vs. Washington County.")

# ---------------------------------------------------------------------------
# 4. RF-08 threshold sensitivity + campus-pair exclusion
# ---------------------------------------------------------------------------
hr("4. RF-08 (shared-contact network) threshold sensitivity, all facilities vs. AFH-only")
for label, subset in [("All facility types", or_df), ("AFH-only", or_df[or_df["Specialty"] == "AFH"])]:
    print(f"\n-- {label} (n={len(subset)}) --")
    for thresh in (2, 3, 4, 5):
        cnt = int((subset["phone_shared_count"] >= thresh).sum())
        print(f"  phone_shared_count >= {thresh}: {cnt} facilities ({100*cnt/len(subset):.1f}%)")
    # Campus-pair exclusion proxy: same address AND same phone cluster likely = single campus
    campus_like = int(((subset["addr_shared_count"] >= 2) & (subset["phone_shared_count"] >= 2)).sum())
    non_campus = int((subset["phone_shared_count"] >= 2).sum()) - campus_like
    print(f"  Of phone-clustered facilities (>=2), {campus_like} also share address (possible "
          f"same-campus license pairs); {non_campus} are phone-linked without a shared address.")

# ---------------------------------------------------------------------------
# 5. AFH-only Oregon vs. Washington like-for-like comparison
# ---------------------------------------------------------------------------
hr("5. AFH-only Oregon vs. Washington comparison (like-for-like)")
or_afh = or_df[or_df["Specialty"] == "AFH"]
comparisons = [("Oregon AFH", or_afh)]
if wa_df is not None:
    comparisons.append(("Washington AFH", wa_df))  # WA package is AFH-only by construction
else:
    print("WA_ANON_DIR not set (or file not found); skipping the Washington side of this "
          "comparison. See the comment above WA_DIR near the top of this script.")
for label, df_ in comparisons:
    n_ = len(df_)
    clustered = int((df_["phone_shared_count"] >= 2).sum())
    rf08 = int((df_["phone_shared_count"] >= 3).sum())
    n_clusters = df_[df_["phone_shared_count"] >= 2]["cluster_id"].nunique() if "cluster_id" in df_.columns else None
    print(f"{label}: n={n_}, RF-03 (>=2 shared) = {clustered} ({100*clustered/n_:.1f}%), "
          f"RF-08 (>=3 shared) = {rf08} ({100*rf08/n_:.1f}%), distinct clusters (>=2) = {n_clusters}")

# ---------------------------------------------------------------------------
# 6. Public-record missingness / cross-source discrepancy summary
# ---------------------------------------------------------------------------
hr("6. Public-record missingness summary (Oregon)")
na_counts = or_df.isna().sum()
na_counts = na_counts[na_counts > 0].sort_values(ascending=False)
if len(na_counts):
    for col, cnt in na_counts.items():
        print(f"  {col}: {cnt}/{n} missing ({100*cnt/n:.1f}%)")
else:
    print("  No NaN fields detected.")
print()
zero_but_suspect = []
for col in ["n_stop_placement"]:
    if col in or_df.columns and (or_df[col] == 0).all():
        zero_but_suspect.append(col)
if zero_but_suspect:
    print(f"  FLAG: {zero_but_suspect} are uniformly 0 across all {n} facilities. Per the "
          f"P0 correction, this must be verified as a true zero vs. an unavailable/unscraped "
          f"field before being reported as a substantive finding; if unavailable, relabel as "
          f"NA / not observed rather than 0.")

hr("Done. Rerun with `python3 or_analyze_rf_status.py` from this directory (or any dir, paths are relative to the script).")
