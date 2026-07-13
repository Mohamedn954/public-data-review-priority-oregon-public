#!/usr/bin/env python3
"""Verify the Oregon replication study's headline numbers against the public,
de-identified anonymized_data/ package alone (no private-repo raw files
needed), and confirm no raw facility identifiers (names, addresses, phone
numbers, city) leak into those files.

This mirrors the Washington repo's verify_headline_numbers.py approach: it
checks numbers already reported in OR_Replication_Report.md and
OR_Standalone_Policy_Paper.md against the data actually shipped in this
repo. It does not re-run the analysis pipeline.

Usage: python3 verify_oregon_numbers.py [path-to-repo-root]
"""
import csv
import os
import sys

BASE_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".."
)
DATA_DIR = os.path.join(BASE_DIR, "anonymized_data")

EXPECTED = {
    "facilities": 792,
    "clackamas": 324,
    "washington": 468,
    "rf03_clustered": 101,
    "rf08_network_cluster": 5,
    "clusters": 49,
    "max_cluster_size": 5,
    "a5_brand": 36,
    "a5_officers": 8,
    "a5_address_only": 2,
    "a5_legal_entity": 1,
    "a5_not_corroborated": 1,
    "a5_indeterminate": 1,
}

# Real facility/operator names, street addresses, or phone numbers must never
# appear in the anonymized package. These column names are what the raw
# (private-repo-only) files use; their presence here would mean the drop-list
# in or_build_anonymized.py failed to strip an identifying field.
FORBIDDEN_COLUMNS = [
    "Facility_Name", "Physical_Address", "Mailing_Address", "Mail_City",
    "Mail_ZIP", "Phone", "Contact", "City", "ZIP", "Latitude", "Longitude",
    "addr_key", "phone_key", "SourceURL", "Reports_URL",
]

failures = []


def check(label, actual, expected):
    status = "OK" if actual == expected else "MISMATCH"
    if actual != expected:
        failures.append(label)
    print(f"  {label}: {actual} (expect {expected}) [{status}]")


def read_csv(name):
    path = os.path.join(DATA_DIR, name)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_no_forbidden_columns(name):
    path = os.path.join(DATA_DIR, name)
    with open(path, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    leaked = [c for c in FORBIDDEN_COLUMNS if c in header]
    if leaked:
        failures.append(f"{name} leaks columns: {', '.join(leaked)}")
        print(f"  {name}: LEAKS {leaked} [MISMATCH]")
    else:
        print(f"  {name}: no forbidden identifying columns present [OK]")


print(f"Reading Oregon anonymized data from: {os.path.abspath(DATA_DIR)}\n")

print("=== OR_Providers_Enriched_ANON.csv ===")
facilities = read_csv("OR_Providers_Enriched_ANON.csv")
check("facilities", len(facilities), EXPECTED["facilities"])

county_counts = {}
for r in facilities:
    county_counts[r["County"]] = county_counts.get(r["County"], 0) + 1
check("Clackamas County facilities", county_counts.get("Clackamas", 0), EXPECTED["clackamas"])
check("Washington County facilities", county_counts.get("Washington", 0), EXPECTED["washington"])

rf03 = sum(1 for r in facilities if int(r["phone_shared_count"]) >= 2)
rf08 = sum(1 for r in facilities if int(r["phone_shared_count"]) >= 3)
check("RF-03 (phone_shared_count>=2)", rf03, EXPECTED["rf03_clustered"])
check("RF-08 (phone_shared_count>=3)", rf08, EXPECTED["rf08_network_cluster"])

print("\n=== OR_Operator_PhoneClusters_ANON.csv ===")
clusters = read_csv("OR_Operator_PhoneClusters_ANON.csv")
check("Phone clusters", len(clusters), EXPECTED["clusters"])
max_size = max(int(r["n_licenses"]) for r in clusters)
check("Largest cluster size", max_size, EXPECTED["max_cluster_size"])

print("\n=== OR_A5_Cluster_Corroboration_ANON.csv ===")
a5 = read_csv("OR_A5_Cluster_Corroboration_ANON.csv")
check("A5 rows (clusters reviewed)", len(a5), EXPECTED["clusters"])
a5_ids = {r["cluster_id"] for r in a5}
cluster_ids = {r["cluster_id"] for r in clusters}
if a5_ids != cluster_ids:
    failures.append("A5 cluster_id set does not match OR_Operator_PhoneClusters_ANON.csv")
    print(f"  cluster_id sets match OR_Operator_PhoneClusters_ANON.csv: MISMATCH")
else:
    print(f"  cluster_id sets match OR_Operator_PhoneClusters_ANON.csv [OK]")

a5_class_counts = {}
for r in a5:
    a5_class_counts[r["evidence_class"]] = a5_class_counts.get(r["evidence_class"], 0) + 1
check("A5 same openly disclosed brand", a5_class_counts.get("Same openly disclosed brand", 0), EXPECTED["a5_brand"])
check("A5 same officers, owners, or managers", a5_class_counts.get("Same officers, owners, or managers", 0), EXPECTED["a5_officers"])
check("A5 same address only", a5_class_counts.get("Same residential or business address only", 0), EXPECTED["a5_address_only"])
check("A5 same legal entity", a5_class_counts.get("Same legal entity", 0), EXPECTED["a5_legal_entity"])
check("A5 no public connection found", a5_class_counts.get("No public connection found", 0), EXPECTED["a5_not_corroborated"])
check("A5 indeterminate", a5_class_counts.get("Indeterminate", 0), EXPECTED["a5_indeterminate"])

print("\n=== No raw identifiers leaked into anonymized_data/ ===")
for fname in [
    "OR_Providers_Enriched_ANON.csv",
    "OR_Reports_ANON.csv",
    "OR_Facility_RedFlags_ANON.csv",
    "OR_Operator_PhoneClusters_ANON.csv",
    "OR_A5_Cluster_Corroboration_ANON.csv",
]:
    check_no_forbidden_columns(fname)

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) did not match: {', '.join(failures)}")
    sys.exit(1)
print("All Oregon headline numbers verified, and no raw identifiers found in anonymized_data/.")
