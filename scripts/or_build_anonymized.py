#!/usr/bin/env python3
"""Oregon replication of scripts/build_anonymized.py -- identical logic, OR filenames.

Produces the journal-safe / public-repo version of the Oregon replication dataset.
All direct facility identifiers are removed and replaced with stable, non-identifying
IDs (facility_id F##### matching the WA scheme's next available range, cluster_id
OR### distinct from WA's OP### prefix) so that no individual home or operator can be
named or re-identified. City is removed (re-identification risk in small towns when
combined with capacity, specialty, enforcement/complaint counts, and cluster
membership); County is retained as the coarsest geographic level needed to reproduce
county-level results -- same convention as the WA package.

Outputs (to OUT_DIR/):
  OR_Providers_Enriched_ANON.csv
  OR_Reports_ANON.csv
  OR_Facility_RedFlags_ANON.csv
  OR_Operator_PhoneClusters_ANON.csv
  OR_County_Concentration.csv       (copied; no identifiers)
  OR_County_Normalized_Risk.csv     (copied; no identifiers)
Private crosswalks (facility_id/cluster_id -> raw keys) are written separately and
are deliberately NOT part of the public package.
"""

import os as _os
_BASE = _os.path.dirname(_os.path.abspath(__file__))
DATA_DIR = _os.environ.get("AFH_DATA_DIR", _os.path.join(_os.path.dirname(_BASE), "data"))
ANON_DIR = _os.environ.get("AFH_ANON_DIR", _os.path.join(_os.path.dirname(_BASE), "anonymized_data"))
PRIV_DIR = _os.environ.get("AFH_PRIV_DIR", _os.path.join(_os.path.dirname(_BASE), "private"))
_os.makedirs(ANON_DIR, exist_ok=True)
_os.makedirs(PRIV_DIR, exist_ok=True)

import pandas as pd, shutil
DATA = DATA_DIR + "/"

enr = pd.read_csv(DATA + "OR_Providers_Enriched.csv", dtype=str)

lic_sorted = sorted(enr["License_Number"].dropna().unique())
fac_id = {lic: f"OR-F{str(i + 1).zfill(5)}" for i, lic in enumerate(lic_sorted)}

phone_counts = enr["phone_key"].value_counts()
multi_phones = sorted([p for p in phone_counts.index
                       if pd.notna(p) and p != "" and phone_counts[p] >= 2])
cluster_id = {p: f"OR{str(i + 1).zfill(3)}" for i, p in enumerate(multi_phones)}

DROP = ["Facility_Name", "Physical_Address", "Mailing_Address", "Mail_City", "Mail_ZIP",
        "Phone", "Contact", "Reports_URL", "reports_url", "Service_Disclosure_URL",
        "addr_key", "phone_key", "SourceURL", "exclusion_name_match",
        "License_Expiration_Date", "Latitude", "Longitude", "ZIP", "City"]


def anonymize(df, has_phone=True):
    df = df.copy()
    if "License_Number" in df.columns:
        df.insert(0, "facility_id", df["License_Number"].map(fac_id))
        df = df.drop(columns=["License_Number"])
    if has_phone and "phone_key" in df.columns:
        df["cluster_id"] = df["phone_key"].map(cluster_id).fillna("")
    df = df.drop(columns=[c for c in DROP if c in df.columns])
    return df


anonymize(enr).to_csv(_os.path.join(ANON_DIR, "OR_Providers_Enriched_ANON.csv"), index=False)

rep = pd.read_csv(DATA + "OR_Reports.csv", dtype=str)
anonymize(rep, has_phone=False).to_csv(
    _os.path.join(ANON_DIR, "OR_Reports_ANON.csv"), index=False)

rf = pd.read_csv(DATA + "OR_Facility_RedFlags.csv", dtype=str)
anonymize(rf, has_phone=False).to_csv(
    _os.path.join(ANON_DIR, "OR_Facility_RedFlags_ANON.csv"), index=False)

cl = pd.read_csv(DATA + "OR_Operator_PhoneClusters.csv")
cl["cluster_id"] = cl["phone_key"].map(cluster_id)
keep = [c for c in ["cluster_id", "n_licenses", "counties", "total_enforcement",
                    "total_investigations", "total_civil_fines"] if c in cl.columns]
cl[keep].sort_values("cluster_id").to_csv(
    _os.path.join(ANON_DIR, "OR_Operator_PhoneClusters_ANON.csv"), index=False)

for f in ["OR_County_Concentration.csv", "OR_County_Normalized_Risk.csv"]:
    src = DATA + f
    if _os.path.exists(src):
        shutil.copy(src, _os.path.join(ANON_DIR, f))

pd.DataFrame({"facility_id": list(fac_id.values()),
              "License_Number": list(fac_id.keys())}).to_csv(
    _os.path.join(PRIV_DIR, "PRIVATE_OR_facility_id_crosswalk.csv"), index=False)
pd.DataFrame({"cluster_id": list(cluster_id.values()),
              "phone_key_raw": list(cluster_id.keys())}).to_csv(
    _os.path.join(PRIV_DIR, "PRIVATE_OR_cluster_id_crosswalk.csv"), index=False)

e = pd.read_csv(_os.path.join(ANON_DIR, "OR_Providers_Enriched_ANON.csv"))
for c in ["n_enforcement", "phone_shared_count", "Licensed_Capacity"]:
    e[c] = pd.to_numeric(e[c], errors="coerce")
print("=== OREGON ANONYMIZED PACKAGE BUILT ===")
print(f"  Facilities: {len(e)} (expect 792)")
print(f"  Beds: {int(e['Licensed_Capacity'].sum())} (expect 12823)")
print(f"  In clusters (phone_shared_count>=2): {int((e['phone_shared_count'] >= 2).sum())} (expect 101)")
print(f"  >=1 enforcement: {int((e['n_enforcement'] >= 1).sum())} (expect 149)")
print(f"  Clusters: {len(cluster_id)} (expect 49)")
print(f"  County split: {dict(e['County'].value_counts())}")
print(f"  'City' column present: {'City' in e.columns} (expect False)")
print(f"  'Facility_Name' column present: {'Facility_Name' in e.columns} (expect False)")
