#!/usr/bin/env python3
"""Oregon replication of scripts/build_normalized.py -- facilities & beds per
1,000 seniors (65+), plus enforcement/investigation rates, for Clackamas and
Washington County, OR. Same per-1,000-seniors normalization logic as the WA
script. Census figures sourced from USAFacts (Census Bureau-derived; census.gov
blocked direct scraping), 2024/2025 vintage, since ltclicensing.oregon.gov and
county portals do not publish population denominators themselves."""

import os as _os
_BASE = _os.path.dirname(_os.path.abspath(__file__))
DATA_DIR = _os.environ.get("AFH_DATA_DIR", _os.path.join(_os.path.dirname(_BASE), "data"))

import csv
from collections import defaultdict
DATA = DATA_DIR + "/"

CENSUS_SRC = "USAFacts (Census Bureau-derived), 2024/2025 vintage"
CENSUS_ACCESSED = {"Clackamas": "2026-07-12", "Washington": "2026-07-06"}
# (total_population, population_65plus)
CENSUS = {
    "Clackamas": (426300, 89400),
    "Washington": (611700, 95600),
}

cnt = defaultdict(int); beds = defaultdict(int); mc = defaultdict(int)
with open(DATA+"OR_Providers_Master.csv") as f:
    for row in csv.DictReader(f):
        c = (row["County"] or "").strip().title()
        if not c: continue
        cnt[c] += 1
        try: beds[c] += int(float(row["Licensed_Capacity"] or 0))
        except: pass
        if (row["Contract"] or "").strip(): mc[c] += 1

enf = defaultdict(lambda: defaultdict(int))
with open(DATA+"OR_Reports.csv") as f:
    for row in csv.DictReader(f):
        c = (row["County"] or "").strip().title()
        if not c: continue
        if int(row["n_enforcement"] or 0) > 0: enf[c]["enf_fac"] += 1
        if int(row["n_investigations"] or 0) > 0: enf[c]["inv_fac"] += 1
        enf[c]["investigations"] += int(row["n_investigations"] or 0)
        enf[c]["enf_actions"] += int(row["n_enforcement"] or 0)
        enf[c]["civil_fines"] += int(row["n_civil_fines"] or 0)
        if int(row["n_investigations"] or 0) >= 3: enf[c]["high_complaint"] += 1

rows = []
for c in ["Clackamas", "Washington"]:
    tot, p65 = CENSUS[c]
    facs = cnt.get(c, 0); bd = beds.get(c, 0); mcc = mc.get(c, 0)
    e = enf[c]
    enf_rate = round(e["enf_fac"]/facs*100, 1) if facs else ""
    inv_rate = round(e["inv_fac"]/facs*100, 1) if facs else ""
    enf_per_1k = round(e["enf_actions"]/(p65/1000), 2) if p65 else ""
    inv_per_1k = round(e["investigations"]/(p65/1000), 2) if p65 else ""
    fac_per_1k = round(facs/(p65/1000), 2) if p65 else ""
    beds_per_1k = round(bd/(p65/1000), 2) if p65 else ""
    rows.append({
        "county": c,
        "total_population": tot,
        "population_65plus": p65,
        "pct_65plus": round(p65/tot*100, 1),
        "licensed_facilities_all_types": facs,
        "licensed_beds": bd,
        "Medicaid_contracted_facilities": mcc,
        "facilities_per_1000_seniors": fac_per_1k,
        "beds_per_1000_seniors": beds_per_1k,
        "facilities_with_enforcement": e["enf_fac"],
        "facilities_with_investigations": e["inv_fac"],
        "facilities_high_complaint_load": e["high_complaint"],
        "enforcement_rate_pct": enf_rate,
        "investigation_rate_pct": inv_rate,
        "enforcement_actions_per_1000_seniors": enf_per_1k,
        "investigations_per_1000_seniors": inv_per_1k,
        "total_civil_fine_docs": e["civil_fines"],
        "facility_source": f"ltclicensing.oregon.gov/Providers, accessed {CENSUS_ACCESSED[c]}",
        "enforcement_source": f"ltclicensing.oregon.gov/Inspections + /Violations + /RegulatoryActions, accessed {CENSUS_ACCESSED[c]}",
        "census_source": f"{CENSUS_SRC}; accessed {CENSUS_ACCESSED[c]}",
        "confidence_level": "High (facility & enforcement counts, direct scrape); Medium (Census, third-party USAFacts source, not census.gov directly)",
    })

cols = list(rows[0].keys())
with open(DATA+"OR_County_Normalized_Risk.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in rows: w.writerow(r)

print(f"{'County':12s} {'65+':>8s} {'Facs':>6s} {'/1k sr':>7s} {'beds/1k':>8s} {'enf%':>6s} {'inv%':>6s}")
for r in rows:
    print(f"{r['county']:12s} {r['population_65plus']:>8,} {r['licensed_facilities_all_types']:>6} {str(r['facilities_per_1000_seniors']):>7} {str(r['beds_per_1000_seniors']):>8} {str(r['enforcement_rate_pct']):>6} {str(r['investigation_rate_pct']):>6}")
