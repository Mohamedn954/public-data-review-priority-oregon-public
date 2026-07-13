#!/usr/bin/env python3
"""Oregon replication of scripts/build_clusters.py -- identical logic, OR filenames."""

import os as _os
_BASE = _os.path.dirname(_os.path.abspath(__file__))
DATA_DIR = _os.environ.get("AFH_DATA_DIR", _os.path.join(_os.path.dirname(_BASE), "data"))

import pandas as pd
DATA = DATA_DIR + "/"
df = pd.read_csv(DATA+"OR_Providers_Enriched.csv", dtype=str)
df["phone_shared_count"] = pd.to_numeric(df["phone_shared_count"], errors="coerce").fillna(1).astype(int)
for c in ["n_enforcement","n_investigations","n_civil_fines"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

clusters = df[(df["phone_shared_count"]>=2) & (df["phone_key"].fillna("")!="")].copy()
clusters = clusters.sort_values(["phone_shared_count","phone_key"], ascending=[False,True])
agg = clusters.groupby("phone_key").agg(
    n_licenses=("License_Number","count"),
    facilities=("Facility_Name", lambda s: " | ".join(sorted(set(s))[:6])),
    counties=("County", lambda s: ",".join(sorted(set(s)))),
    cities=("City", lambda s: ",".join(sorted(set(s))[:6])),
    total_enforcement=("n_enforcement","sum"),
    total_investigations=("n_investigations","sum"),
    total_civil_fines=("n_civil_fines","sum"),
).reset_index().sort_values("n_licenses", ascending=False)
agg.to_csv(DATA+"OR_Operator_PhoneClusters.csv", index=False)

print("=== OREGON PHONE CLUSTERS (raw, same method as WA build_clusters.py) ===")
print("Total multi-license phone clusters:", len(agg))
print(agg.head(15).to_string())
