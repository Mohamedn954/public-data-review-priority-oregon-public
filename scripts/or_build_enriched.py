#!/usr/bin/env python3
"""Oregon replication of scripts/build_enriched.py -- identical logic, OR filenames.
Merges OR_Providers_Master.csv + OR_Reports.csv, computes addr_key/phone_key using
the SAME simple normalization as the original WA script (no suffix stripping),
computes addr_shared_count/phone_shared_count as independent columns."""

import os as _os
_BASE = _os.path.dirname(_os.path.abspath(__file__))
DATA_DIR = _os.environ.get("AFH_DATA_DIR", _os.path.join(_os.path.dirname(_BASE), "data"))

import pandas as pd, re
DATA = DATA_DIR + "/"
master = pd.read_csv(DATA+"OR_Providers_Master.csv", dtype=str)
reports = pd.read_csv(DATA+"OR_Reports.csv", dtype=str)

num_cols = ["n_inspections","n_investigations","n_enforcement","n_limitations",
            "n_civil_fines","n_stop_placement","n_conditions","n_docs_total"]
for c in num_cols:
    reports[c] = pd.to_numeric(reports[c], errors="coerce").fillna(0).astype(int)

rep_keep = ["License_Number"] + num_cols + ["latest_year","latest_enforcement_year","reports_url"]
df = master.merge(reports[rep_keep], on="License_Number", how="left")
for c in num_cols:
    df[c] = df[c].fillna(0).astype(int)

df["Licensed_Capacity"] = pd.to_numeric(df["Licensed_Capacity"], errors="coerce")

def norm(s):
    if pd.isna(s): return ""
    return re.sub(r"\s+", " ", str(s).strip().upper())

for col, src in [("addr_key","Physical_Address"), ("phone_key","Phone")]:
    df[col] = df[src].apply(norm) if src in df.columns else ""

if df["addr_key"].astype(bool).any():
    addr_counts = df[df["addr_key"]!=""]["addr_key"].value_counts()
    df["addr_shared_count"] = df["addr_key"].map(addr_counts).fillna(1).astype(int)
else:
    df["addr_shared_count"] = 1

if df["phone_key"].astype(bool).any():
    phone_counts = df[df["phone_key"]!=""]["phone_key"].value_counts()
    df["phone_shared_count"] = df["phone_key"].map(phone_counts).fillna(1).astype(int)
else:
    df["phone_shared_count"] = 1

# Exclusion cross-check: not run here -- no OR-specific exclusion list source has
# been gathered yet. Column included for schema parity, left blank (documented gap).
df["exclusion_name_match"] = ""

df.to_csv(DATA+"OR_Providers_Enriched.csv", index=False)

tot_fac = len(df); tot_beds = df["Licensed_Capacity"].sum()
ct = df.groupby("County").agg(
    facilities=("License_Number","count"),
    beds=("Licensed_Capacity","sum"),
    avg_beds=("Licensed_Capacity","mean"),
    w_enforcement=("n_enforcement", lambda s: (s>0).sum()),
    w_investigations=("n_investigations", lambda s: (s>0).sum()),
    w_stop_placement=("n_stop_placement", lambda s: (s>0).sum()),
    w_conditions=("n_conditions", lambda s: (s>0).sum()),
    civil_fines=("n_civil_fines","sum"),
).reset_index()
ct["pct_of_2county_facilities"] = (ct["facilities"]/tot_fac*100).round(1)
ct["enforcement_rate_pct"] = (ct["w_enforcement"]/ct["facilities"]*100).round(1)
ct["investigation_rate_pct"] = (ct["w_investigations"]/ct["facilities"]*100).round(1)
ct.to_csv(DATA+"OR_County_Concentration.csv", index=False)

print("=== OREGON ENRICHED DATASET ===")
print("Facilities:", tot_fac, "| Beds:", int(tot_beds))
print()
print("=== COUNTY CONCENTRATION ===")
print(ct.to_string())
print()
print("=== NETWORK CLUSTERING (raw, unfiltered -- same method as WA script) ===")
print("Facilities sharing an address with >=2 licenses:", (df["addr_shared_count"]>=2).sum())
print("Max licenses at one address:", df["addr_shared_count"].max())
print("Facilities sharing a phone with >=2 licenses:", (df["phone_shared_count"]>=2).sum())
print("Max licenses at one phone:", df["phone_shared_count"].max())
print()
print("=== ENFORCEMENT INTENSITY (2-county) ===")
print("Facilities w/ enforcement:", (df["n_enforcement"]>0).sum())
print("Total civil fines:", int(df["n_civil_fines"].sum()))
print("Total stop-placement orders:", int(df["n_stop_placement"].sum()), "(NOTE: not available in this OR data source, always 0)")
print("Total conditions imposed:", int(df["n_conditions"].sum()))
