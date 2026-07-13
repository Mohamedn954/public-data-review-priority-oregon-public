#!/usr/bin/env python3
"""Generate the seven recommended figures for OR_Standalone_Policy_Paper.md.
Matches the visual style of the companion WA manuscript's figures
(figures/Fig4_Framework.png, figures/Fig5_TwoPhase.png,
figures/WA_County_Concentration_Enforcement.png): matplotlib, DejaVu Sans,
rounded FancyBboxPatch diagram boxes, bold titles, italic subtitles and
captions. All numbers below are pulled directly from the paper's own
results sections and the underlying anonymized data; nothing here is
illustrative or invented.
"""
import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams["font.family"] = "DejaVu Sans"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "figures")
os.makedirs(OUT, exist_ok=True)

BLUE = "#1f6fa8"
BLUE_FILL = "#dbe9f4"
BROWN = "#8a5a2b"
BROWN_FILL = "#f0e0cc"
GREEN = "#3a6b35"
GREEN_FILL = "#dfeedd"
GRAY = "#4d4d4d"


def savefig(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Figure 1: Framework architecture diagram
# ---------------------------------------------------------------------------
def fig1_architecture():
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.text(5, 9.55, "Figure 1. Oregon Pipeline Architecture", ha="center",
            fontsize=17, fontweight="bold")
    ax.text(5, 9.05, "Same four scripts as the Washington pilot; only file paths and Oregon-specific field mappings differ (Section 3.3)",
            ha="center", fontsize=11, style="italic", color=GRAY)

    input_box = dict(boxstyle="round,pad=0.4", facecolor=BLUE_FILL, edgecolor=BLUE, linewidth=1.8)
    script_box = dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=GRAY, linewidth=1.4)
    out_box = dict(boxstyle="round,pad=0.4", facecolor=GREEN_FILL, edgecolor=GREEN, linewidth=1.8)

    ax.text(1.7, 7.9, "Oregon public data\n(roster, inspections,\nviolations, regulatory\nactions, Census 65+)",
            ha="center", va="center", fontsize=10, bbox=input_box)

    steps = [
        ("or_build_enriched.py", "Merge + address/phone key\nnormalization (Section 3.3)", 7.6),
        ("or_build_clusters.py", "Aggregate shared-phone\noperator clusters (Section 4.4)", 5.9),
        ("or_build_rf_coding.py", "Apply RF-01–RF-20 thresholds\n(Section 7)", 4.2),
        ("or_build_normalized.py", "Per-1,000-seniors density\n(Section 4.3)", 2.5),
    ]
    for title, sub, y in steps:
        ax.text(4.6, y, f"{title}\n{sub}", ha="center", va="center",
                fontsize=9.5, bbox=script_box)
        ax.annotate("", xy=(4.6, y + 0.75), xytext=(4.6, y + 1.35 if y != 7.6 else y),
                     arrowprops=dict(arrowstyle="-", color="none"))

    for y0, y1 in [(7.15, 6.35), (5.45, 4.65), (3.75, 2.95)]:
        ax.annotate("", xy=(4.6, y1), xytext=(4.6, y0),
                    arrowprops=dict(arrowstyle="->", color=GRAY, linewidth=1.6))

    ax.annotate("", xy=(3.35, 7.6), xytext=(2.55, 7.85),
                arrowprops=dict(arrowstyle="->", color=BLUE, linewidth=1.6))

    ax.text(8.3, 5.2, "Results\n(Sections 4–7):\ncounty rates,\nclustering,\nRF evidence\nmatrix",
            ha="center", va="center", fontsize=10, bbox=out_box)
    ax.annotate("", xy=(7.15, 5.2), xytext=(5.85, 4.2),
                arrowprops=dict(arrowstyle="->", color=GREEN, linewidth=1.8))

    ax.text(5, 0.5, "Diagram shows the pipeline's data flow only; it does not depict facility-level output.",
            ha="center", fontsize=9, style="italic", color=GRAY)
    savefig(fig, "OR_Fig1_Architecture.png")


# ---------------------------------------------------------------------------
# Figure 2: Washington-versus-Oregon AFH-only comparison
# ---------------------------------------------------------------------------
def fig2_wa_or_comparison():
    metrics = ["≥1 enforcement\nrecord", "≥1 investigation\nrecord", "RF-03\n(≥2 shared contact)"]
    wa = [4.8, 17.0, 4.7]
    orv = [10.5, 19.9, 3.5]

    fig, ax = plt.subplots(figsize=(9, 6))
    x = range(len(metrics))
    w = 0.35
    b1 = ax.bar([i - w / 2 for i in x], wa, width=w, label="Washington AFH (n=3,457)", color="#1f77b4")
    b2 = ax.bar([i + w / 2 for i in x], orv, width=w, label="Oregon AFH-only (n=629)", color="#ff7f0e")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3, f"{b.get_height():.1f}%",
                    ha="center", fontsize=10)
    ax.set_xticks(list(x))
    ax.set_xticklabels(metrics, fontsize=11)
    ax.set_ylabel("% of facilities", fontsize=11)
    ax.set_title("Figure 2. Washington vs. Oregon, AFH-Only Comparison", fontsize=15, fontweight="bold", pad=14)
    ax.legend(fontsize=10, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.5, -0.12, "Like-for-like comparison: Washington Adult Family Homes vs. Oregon Adult Foster Homes (Section 8.3),\nOregon's analogous type; pooled four-facility-type Oregon figures (Section 4.2) are not directly comparable.\nFigures are retained-record prevalence, not a common-observation-period rate.",
              ha="center", fontsize=8.5, style="italic", color=GRAY)
    savefig(fig, "OR_Fig2_WA_OR_Comparison.png")


# ---------------------------------------------------------------------------
# Figure 3: RF evidence matrix visualized
# ---------------------------------------------------------------------------
def fig3_rf_matrix():
    # Short display labels only (visual shorthand, not a fact that can drift).
    # Evidentiary status is read from OR_RF_Evidence_Matrix.csv, the single
    # source of truth also cited in the manuscript's Section 3.5, so this
    # figure cannot silently drift out of sync with Section 7's table.
    short_labels = {
        "RF-01": "Rapid facility growth",
        "RF-02": "Spending vs. beneficiary growth",
        "RF-03": "Multi-facility operator concentration",
        "RF-04": "Geographic / out-of-state operator",
        "RF-05": "Incomplete enrollment data",
        "RF-06": "Excluded party linkage",
        "RF-07": "Concealed ownership",
        "RF-08": "Shared-contact network cluster",
        "RF-09": "Phantom / mailbox address",
        "RF-10": "Impossible / overlapping hours",
        "RF-11": "Maximum-unit billing",
        "RF-12": "Unauthorized-location billing",
        "RF-13": "Billing despite ineligibility",
        "RF-14": "Fabricated documentation",
        "RF-15": "Stolen credentials",
        "RF-16": "Referrals not acted upon",
        "RF-17": "Sanctions / enforcement history",
        "RF-18": "Reactive, capacity-constrained oversight",
        "RF-19": "Program design vulnerability",
        "RF-20": "Unresolved audit findings",
    }
    matrix_path = os.path.join(BASE, "OR_RF_Evidence_Matrix.csv")
    with open(matrix_path, newline="") as f:
        matrix_rows = list(csv.DictReader(f))
    rows = [(r["RF_ID"], short_labels[r["RF_ID"]], r["Oregon_Evidentiary_Status"]) for r in matrix_rows]
    colors = {
        "Operationalized": "#2c7fb8",
        "Operationalized, recalibrated": "#2c7fb8",
        "Partially Operationalized": "#7fb8de",
        "Case Supported": "#3a9d5d",
        "System Supported": "#8fbf6a",
        "Contextually Assessed": "#f2b134",
        "Publicly Testable, Not Completed": "#c9a13b",
        "Internal Data Required": "#d9634e",
        "Not Established": "#b0abab",
    }

    fig, ax = plt.subplots(figsize=(11, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(rows) + 2.6)
    ax.axis("off")
    ax.text(5, len(rows) + 2.2, "Figure 3. Master RF-01–RF-20 Oregon Evidence Matrix", ha="center",
            fontsize=16, fontweight="bold")
    ax.text(5, len(rows) + 1.7, "Every indicator classified by strongest available Oregon-specific evidence (Section 7)",
            ha="center", fontsize=10.5, style="italic", color=GRAY)

    for i, (rf, label, cat) in enumerate(rows):
        y = len(rows) - i
        ax.text(0.15, y, rf, fontsize=9.5, fontweight="bold", va="center")
        ax.text(1.15, y, label, fontsize=9.5, va="center")
        ax.add_patch(FancyBboxPatch((6.0, y - 0.32), 3.85, 0.62, boxstyle="round,pad=0.02",
                                     facecolor=colors[cat], edgecolor="none"))
        ax.text(7.925, y, cat, fontsize=7.5, va="center", ha="center", color="white", fontweight="bold")

    legend_items = list(dict.fromkeys([c for _, _, c in rows]))
    ax.text(0.15, -0.7, "Color reflects the eight evidence-strength categories defined in Section 7, "
                        "strongest (Operationalized) to weakest applicable (Not Established).",
            fontsize=8.7, style="italic", color=GRAY)
    savefig(fig, "OR_Fig3_RF_Evidence_Matrix.png")


# ---------------------------------------------------------------------------
# Figure 4: Facility-type composition by county
# ---------------------------------------------------------------------------
def fig4_facility_composition():
    counties = ["Clackamas\n(n=324)", "Washington\n(n=468)"]
    afh = [238, 391]
    alf = [29, 31]
    nf = [13, 9]
    rcf = [44, 37]

    fig, ax = plt.subplots(figsize=(8, 6))
    bottoms = [0, 0]
    for vals, label, color in [(afh, "AFH", "#1f77b4"), (rcf, "RCF", "#ff7f0e"),
                                (alf, "ALF", "#2ca02c"), (nf, "NF", "#d62728")]:
        ax.bar(counties, vals, bottom=bottoms, label=label, color=color)
        for i, v in enumerate(vals):
            if v > 0:
                ax.text(i, bottoms[i] + v / 2, str(v), ha="center", va="center",
                        fontsize=9.5, color="white", fontweight="bold")
        bottoms = [b + v for b, v in zip(bottoms, vals)]

    ax.set_ylabel("Facilities", fontsize=11)
    ax.set_title("Figure 4. Facility-Type Composition by County", fontsize=15, fontweight="bold", pad=14)
    ax.set_ylim(0, max(bottoms) * 1.08)
    ax.legend(fontsize=10, title="Facility type")
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.5, -0.02, "Underlies Section 5's facility-type-confounding diagnostic: Washington County's population is\nmore heavily AFH-weighted than Clackamas County's.",
              ha="center", fontsize=9, style="italic", color=GRAY)
    savefig(fig, "OR_Fig4_Facility_Composition.png")


# ---------------------------------------------------------------------------
# Figure 5: Threshold sensitivity
# ---------------------------------------------------------------------------
def fig5_threshold_sensitivity():
    thresholds = [2, 3, 4, 5]
    all_types = [101, 5, 5, 5]
    afh_only = [22, 0, 0, 0]

    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.plot(thresholds, all_types, marker="o", linewidth=2.2, color="#1f77b4",
            label="All facility types (n=792)")
    ax.plot(thresholds, afh_only, marker="s", linewidth=2.2, color="#ff7f0e",
            label="AFH-only (n=629)")
    ax.axvline(3, color=GRAY, linestyle="--", linewidth=1, alpha=0.6)
    ax.text(3.05, 90, "RF-08\nthreshold", fontsize=9, color=GRAY)
    for x, y in zip(thresholds, all_types):
        ax.text(x, y + 3, str(y), ha="center", fontsize=9, color="#1f77b4")
    for x, y in zip(thresholds, afh_only):
        ax.text(x, y + 3, str(y), ha="center", fontsize=9, color="#ff7f0e")

    ax.set_xticks(thresholds)
    ax.set_xlabel("Shared-license threshold", fontsize=11)
    ax.set_ylabel("Facilities flagged", fontsize=11)
    ax.set_title("Figure 5. RF-08 Threshold Sensitivity", fontsize=15, fontweight="bold", pad=14)
    ax.legend(fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.5, -0.02, "The all-facility-type curve is driven entirely by one same-brand, five-license cluster from\nthreshold 3 upward (Section 5.1); the AFH-only curve never reaches that threshold in this dataset.",
              ha="center", fontsize=9, style="italic", color=GRAY)
    savefig(fig, "OR_Fig5_Threshold_Sensitivity.png")


# ---------------------------------------------------------------------------
# Figure 6: Oregon oversight and enforcement timeline
# ---------------------------------------------------------------------------
def fig6_timeline():
    import datetime as dt
    events = [
        (dt.date(2025, 2, 1), "SOQ Rapid Response\nReport published", GREEN, "above"),
        (dt.date(2025, 7, 3), "Case 1: Clackamas AFH\nguilty plea announced", BLUE, "below"),
        (dt.date(2026, 1, 27), "Case 2: Washington County\nAFH federal indictment", BROWN, "above"),
        (dt.date(2026, 7, 9), "Data collection window:\nWA County Jul 6, Clackamas\nCounty Jul 12, 2026", GRAY, "below"),
    ]
    fig, ax = plt.subplots(figsize=(12, 5))
    start = dt.date(2025, 1, 1)
    end = dt.date(2026, 9, 1)
    ax.hlines(0, start, end, color=GRAY, linewidth=2)
    ax.set_xlim(start, end)
    ax.set_ylim(-2.6, 2.6)
    ax.axis("off")
    ax.text((start + (end - start) / 2), 2.35, "Figure 6. Oregon Oversight and Enforcement Timeline",
            ha="center", fontsize=16, fontweight="bold")
    ax.text((start + (end - start) / 2), 1.95,
            "Relative to this study's data-collection window (Section 6)",
            ha="center", fontsize=10.5, style="italic", color=GRAY)

    for date, label, color, side in events:
        ax.plot([date], [0], marker="o", markersize=9, color=color, zorder=5)
        y = 0.9 if side == "above" else -0.9
        va = "bottom" if side == "above" else "top"
        ax.plot([date, date], [0, y * 0.7], color=color, linewidth=1.2)
        ax.text(date, y, f"{date.strftime('%b %Y')}\n{label}", ha="center", va=va,
                fontsize=9, color="black",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, linewidth=1.2))

    fig.text(0.5, -0.02, "Case 2 (indicted January 2026) reflects pending federal charges, not a conviction; see Section 6.1 and Section 11.",
              ha="center", fontsize=9, style="italic", color=GRAY)
    savefig(fig, "OR_Fig6_Oversight_Timeline.png")


# ---------------------------------------------------------------------------
# Figure 7: Research roadmap
# ---------------------------------------------------------------------------
def fig7_roadmap():
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.text(6, 5.6, "Figure 7. Research Roadmap (Section 9)", ha="center", fontsize=16, fontweight="bold")
    ax.text(6, 5.15, "Three concrete, falsifiable next steps, none executed in this study", ha="center",
            fontsize=10.5, style="italic", color=GRAY)

    boxes = [
        (1.0, "1. Claims-Informed\nValidation", BLUE, BLUE_FILL,
         "Test whether Tier B (brand) vs.\nTier C/D (AFH operator) clusters\ndiffer in OHA claims data"),
        (4.6, "2. SOQ Follow-Up\nTracking", BROWN, BROWN_FILL,
         "Re-run RF-16/18/20 once SOQ's\nremaining 2 of 3 deliverables\npublish (Section 6.2)"),
        (8.2, "3. Third-State\nGeneralization", GREEN, GREEN_FILL,
         "Test a state with a single-\nfacility-type or different\nownership-disclosure regime"),
    ]
    for x, title, edge, fill, body in boxes:
        ax.add_patch(FancyBboxPatch((x, 1.6), 2.6, 2.7, boxstyle="round,pad=0.15",
                                     facecolor=fill, edgecolor=edge, linewidth=1.8))
        ax.text(x + 1.3, 3.7, title, ha="center", va="center", fontsize=11.5, fontweight="bold", color=edge)
        ax.text(x + 1.3, 2.65, body, ha="center", va="center", fontsize=9)

    for x0, x1 in [(3.6, 4.6), (7.2, 8.2)]:
        ax.annotate("", xy=(x1, 2.95), xytext=(x0, 2.95),
                    arrowprops=dict(arrowstyle="->", color=GRAY, linewidth=2))

    ax.text(6, 0.6, "None of the three requires new statutory authority to define; only step 1 requires claims access to execute.",
            ha="center", fontsize=9.5, style="italic", color=GRAY)
    savefig(fig, "OR_Fig7_Research_Roadmap.png")


if __name__ == "__main__":
    fig1_architecture()
    fig2_wa_or_comparison()
    fig3_rf_matrix()
    fig4_facility_composition()
    fig5_threshold_sensitivity()
    fig6_timeline()
    fig7_roadmap()
    print("Done.")
