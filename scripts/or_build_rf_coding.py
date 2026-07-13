#!/usr/bin/env python3
"""Oregon replication of scripts/build_rf_coding.py -- same facility-level flag
thresholds (RF-03 >=2, RF-08 >=3 on phone_shared_count; high_complaint_load
>=3 investigations), applied to the OR Enriched dataset. The WA script's
narrative testability matrix is WA-specific text and is NOT reproduced here;
this script covers only the facility-level, per-facility computable flags."""

import os as _os
_BASE = _os.path.dirname(_os.path.abspath(__file__))
DATA_DIR = _os.environ.get("AFH_DATA_DIR", _os.path.join(_os.path.dirname(_BASE), "data"))

import pandas as pd
DATA = DATA_DIR + "/"
df = pd.read_csv(DATA+"OR_Providers_Enriched.csv", dtype=str)
for c in ["n_inspections","n_investigations","n_enforcement","n_limitations",
          "n_civil_fines","n_stop_placement","n_conditions","phone_shared_count"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
df["Licensed_Capacity"] = pd.to_numeric(df["Licensed_Capacity"], errors="coerce")

df["RF08_network_cluster"] = (df["phone_shared_count"] >= 3)
df["RF03_multi_home_operator"] = (df["phone_shared_count"] >= 2)
df["high_complaint_load"] = (df["n_investigations"] >= 3)
df["has_enforcement"] = (df["n_enforcement"] > 0)
df["has_stop_placement"] = (df["n_stop_placement"] > 0)
df["has_condition"] = (df["n_conditions"] > 0)
df["RF06_exclusion_match"] = (df["exclusion_name_match"].fillna("") != "")

fac_cols = ["License_Number","Facility_Name","City","County","Licensed_Capacity",
            "Medicaid_Contract_Flag","Specialty","Contract",
            "n_inspections","n_investigations","n_enforcement","n_civil_fines",
            "n_stop_placement","n_conditions","phone_shared_count",
            "RF03_multi_home_operator","RF08_network_cluster","high_complaint_load",
            "has_enforcement","has_stop_placement","has_condition","RF06_exclusion_match",
            "latest_enforcement_year","reports_url"]
df[fac_cols].to_csv(DATA+"OR_Facility_RedFlags.csv", index=False)

print("=== OREGON FACILITY-LEVEL FLAG COUNTS (2-county, all facility types, raw method) ===")
print("Total facilities:", len(df))
print("RF03 multi-home operator (phone_shared_count>=2):", int(df["RF03_multi_home_operator"].sum()))
print("RF08 network cluster (phone_shared_count>=3):", int(df["RF08_network_cluster"].sum()))
print("High complaint load (>=3 investigations):", int(df["high_complaint_load"].sum()))
print("Has enforcement:", int(df["has_enforcement"].sum()))
print("Has stop-placement:", int(df["has_stop_placement"].sum()), "(NOTE: field not available in OR source, always 0)")
print("Has condition:", int(df["has_condition"].sum()))
print("RF06 exclusion match (verified):", int(df["RF06_exclusion_match"].sum()), "(NOTE: no OR exclusion-list source gathered yet, always 0)")

print()
print("=== BY FACILITY TYPE (Specialty field, first token) ===")
df["_type"] = df["Specialty"].fillna("").str.split(",").str[0]
byt = df.groupby("_type").agg(
    facilities=("License_Number","count"),
    RF03=("RF03_multi_home_operator","sum"),
    RF08=("RF08_network_cluster","sum"),
    has_enforcement=("has_enforcement","sum"),
).reset_index()
print(byt.to_string())
