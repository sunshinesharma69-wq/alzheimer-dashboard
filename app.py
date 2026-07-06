import gzip
import json
import os
import re
from pathlib import Path
import tempfile
from flask import Flask, Response, jsonify, render_template, request

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
HEATMAP_FILE = STATIC_DIR / "heatmap.png"

PROJECT = {
    "title": "AI-Based Drug Repurposing for Alzheimer Disease",
    "subtitle": "Flask dashboard built from the real notebook outputs and real input files",
    "dataset": "GSE5281 series matrix + DGIdb interactions-2024.tsv",
    "intro": (
        "This dashboard presents the findings from the Alzheimer disease drug repurposing "
        "project using your actual GEO expression data and DGIdb interaction table."
    ),
    "sample_stats": [
        {"label": "Total samples", "value": "161"},
        {"label": "Control samples", "value": "74"},
        {"label": "AD samples", "value": "87"},
        {"label": "Expression features", "value": "33,297"},
    ],
    "model_results": [
        {
            "name": "Random Forest",
            "accuracy": 0.9069852941176471,
            "accuracy_std": 0.0,
            "roc_auc": 0.9595238095238094,
            "roc_auc_std": 0.0,
            "f1": 0.8893772893772894,
            "f1_std": 0.0,
            "note": "Baseline ensemble model",
        },
        {
            "name": "SVM",
            "accuracy": 0.950368,
            "accuracy_std": 0.0467,
            "roc_auc": 0.987649,
            "roc_auc_std": 0.0195,
            "f1": 0.945522,
            "f1_std": 0.0506,
            "note": "Best overall performer",
        },
        {
            "name": "XGBoost",
            "accuracy": 0.89375,
            "accuracy_std": 0.0628,
            "roc_auc": 0.968576,
            "roc_auc_std": 0.0358,
            "f1": 0.877884,
            "f1_std": 0.0718,
            "note": "Strong ROC-AUC, lower accuracy",
        },
        {
            "name": "Logistic Regression",
            "accuracy": 0.944118,
            "accuracy_std": 0.0437,
            "roc_auc": 0.982937,
            "roc_auc_std": 0.0257,
            "f1": 0.936804,
            "f1_std": 0.0477,
            "note": "Strong linear baseline",
        },
    ],
    "top_genes": [
        {"gene": "ZFP36L1", "importance": 0.014842},
        {"gene": "TTC1", "importance": 0.013760},
        {"gene": "TRIM8", "importance": 0.010387},
        {"gene": "LDHA", "importance": 0.010361},
        {"gene": "NDRG4", "importance": 0.010176},
        {"gene": "ATP5F1C", "importance": 0.010055},
        {"gene": "GOT2", "importance": 0.009206},
        {"gene": "PSMB2", "importance": 0.009050},
        {"gene": "BRAF", "importance": 0.008865},
        {"gene": "MICU1", "importance": 0.008796},
    ],
    "drug_hits": [
        {"drug": "BORTEZOMIB", "count": 6},
        {"drug": "CARFILZOMIB", "count": 6},
        {"drug": "IXAZOMIB", "count": 3},
        {"drug": "MARIZOMIB", "count": 3},
        {"drug": "OPROZOMIB", "count": 3},
        {"drug": "IXAZOMIB CITRATE", "count": 3},
        {"drug": "VINBLASTINE SULFATE", "count": 2},
        {"drug": "ENFORTUMAB VEDOTIN-EJFV", "count": 2},
        {"drug": "FOSBRETABULIN DISODIUM", "count": 2},
        {"drug": "CROLIBULIN", "count": 2},
        {"drug": "SOFITUZUMAB VEDOTIN", "count": 2},
        {"drug": "PATUPILONE", "count": 2},
        {"drug": "PACLITAXEL DOCOSAHEXAENOIC ACID", "count": 2},
        {"drug": "RG-7600", "count": 2},
        {"drug": "INDUSATUMAB VEDOTIN", "count": 2},
    ],
    "top_pathways": [
        {"term": "Parkinson disease", "adjusted_p": 4.805350e-31},
        {"term": "Huntington disease", "adjusted_p": 4.326289e-26},
        {"term": "Alzheimer disease", "adjusted_p": 5.682081e-24},
        {"term": "Prion disease", "adjusted_p": 5.682081e-24},
        {"term": "Pathways of neurodegeneration", "adjusted_p": 9.139233e-23},
        {"term": "Amyotrophic lateral sclerosis", "adjusted_p": 9.338849e-22},
        {"term": "Oxidative phosphorylation", "adjusted_p": 3.214384e-19},
        {"term": "Diabetic cardiomyopathy", "adjusted_p": 2.440077e-12},
        {"term": "Thermogenesis", "adjusted_p": 1.938302e-10},
        {"term": "Non-alcoholic fatty liver disease", "adjusted_p": 7.846409e-10},
    ],
    "validation": {
        "accuracy": 0.65,
        "external_auc": 0.6976,
        "interpretation": "Moderate external validation",
        "confusion_matrix": [
            [23, 10],
            [18, 29],
        ],
        "classification_summary": [
            {"label": "AD", "precision": 0.56, "recall": 0.70, "f1": 0.62, "support": 87},
            {"label": "Control", "precision": 0.74, "recall": 0.62, "f1": 0.67, "support": 74},
        ],
    },
    "final_candidates": [
        {
            "drug": "ALPRAZOLAM",
            "bbb": "Good",
            "mechanism": "GABA-A receptor modulator - reduces neuroinflammation",
            "ad_link": "Anxiety and GABA dysfunction are relevant to AD neurobiology",
            "priority": "HIGH",
        },
        {
            "drug": "PATUPILONE",
            "bbb": "Good",
            "mechanism": "Microtubule stabilizer - prevents tau aggregation",
            "ad_link": "Directly relevant to tau pathology in AD",
            "priority": "HIGH",
        },
        {
            "drug": "PANAVEINE",
            "bbb": "Moderate",
            "mechanism": "Alkaloid - limited CNS data, needs investigation",
            "ad_link": "Requires further study",
            "priority": "MODERATE",
        },
    ],
    "search_drugs": [
        {
            "drug": "ALPRAZOLAM",
            "category": "Final candidate",
            "detail": "Good BBB penetrance; prioritized as a high-priority candidate because it is a CNS-active drug with relevance to GABA dysfunction and AD neurobiology.",
            "evidence": "Notebook priority: HIGH",
        },
        {
            "drug": "PATUPILONE",
            "category": "Final candidate",
            "detail": "Good BBB penetrance; prioritized as a high-priority candidate due to microtubule stabilization and tau-pathology relevance.",
            "evidence": "Notebook priority: HIGH",
        },
        {
            "drug": "PANAVEINE",
            "category": "Final candidate",
            "detail": "Moderate BBB status; kept as a secondary candidate because the notebook flagged limited CNS data and the need for further investigation.",
            "evidence": "Notebook priority: MODERATE",
        },
        {
            "drug": "BORTEZOMIB",
            "category": "DGIdb hit",
            "detail": "Appears among the strongest DGIdb hits with 6 interactions in the notebook output, making it a visible repurposing lead to inspect.",
            "evidence": "DGIdb interaction count: 6",
        },
        {
            "drug": "CARFILZOMIB",
            "category": "DGIdb hit",
            "detail": "Appears among the strongest DGIdb hits with 6 interactions in the notebook output.",
            "evidence": "DGIdb interaction count: 6",
        },
        {
            "drug": "IXAZOMIB",
            "category": "DGIdb hit",
            "detail": "Appears among the repeated DGIdb drug-gene matches and is part of the top interaction table.",
            "evidence": "DGIdb interaction count: 3",
        },
        {
            "drug": "MARIZOMIB",
            "category": "DGIdb hit",
            "detail": "Appears among the repeated DGIdb drug-gene matches and is part of the top interaction table.",
            "evidence": "DGIdb interaction count: 3",
        },
        {
            "drug": "OPROZOMIB",
            "category": "DGIdb hit",
            "detail": "Appears among the repeated DGIdb drug-gene matches and is part of the top interaction table.",
            "evidence": "DGIdb interaction count: 3",
        },
        {
            "drug": "VINBLASTINE SULFATE",
            "category": "DGIdb hit",
            "detail": "Present in the DGIdb table and also flagged in the notebook as having poor BBB penetrance, so it is not a strong CNS candidate.",
            "evidence": "DGIdb interaction count: 2",
        },
        {
            "drug": "ENFORTUMAB VEDOTIN-EJFV",
            "category": "DGIdb hit",
            "detail": "Present in the DGIdb table but not suitable for brain delivery because of poor BBB penetration for large antibody-drug conjugates.",
            "evidence": "DGIdb interaction count: 2",
        },
    ],
    "pipeline": [
        "Load the GEO expression matrix and assign AD/control labels.",
        "Map the expression probes to gene symbols.",
        "Rank differentially expressed genes and train ML models.",
        "Use DGIdb to find drug-gene interaction evidence.",
        "Run KEGG pathway enrichment and external validation.",
        "Apply BBB and literature-based prioritization.",
    ],
    "source_files": [
        "data/GSE5281_series_matrix.txt.gz",
        "data/interactions-2024.tsv",
    ],
    "heatmap_image": "heatmap.png",
    "conclusion": (
        "SVM was the best performing classifier in the notebook, while the final repurposing "
        "prioritization highlighted Alprazolam and Patupilone as the strongest brain-penetrant "
        "candidates from the curated output."
    ),
}


def pick_best_model(models):
    return max(models, key=lambda item: item["roc_auc"])


def build_model_chart_series(models):
    return {
        "labels": [item["name"] for item in models],
        "accuracy": [item["accuracy"] for item in models],
        "roc_auc": [item["roc_auc"] for item in models],
        "f1": [item["f1"] for item in models],
        "y_max": 1.0,
    }


GENE_CATALOG_CACHE = None


def build_gene_description(gene_name, top_drugs, interaction_count):
    if not top_drugs:
        return (
            f"{gene_name} is present in the current repurposing dataset and currently has no linked drug record. "
            "It can still be reviewed as a candidate target for future annotation."
        )

    drug_names = []
    for drug in top_drugs[:4]:
        drug_name = drug.get("drug_name")
        if pd.isna(drug_name):
            continue
        cleaned_name = str(drug_name).strip()
        if cleaned_name and cleaned_name.lower() != "nan":
            drug_names.append(cleaned_name)

    drug_preview = ", ".join(drug_names) if drug_names else "several linked drugs"

    return (
        f"{gene_name} is part of the Alzheimer-focused repurposing network in this project. "
        f"It appears in {interaction_count} interaction record(s) and is linked to {drug_preview}. "
        f"This gives a clinician-style overview of the most relevant drug connections for {gene_name} in the current dataset."
    )


def load_gene_catalog():
    global GENE_CATALOG_CACHE
    if GENE_CATALOG_CACHE is not None:
        return GENE_CATALOG_CACHE
    
    # Path ka jhanjhat hi khatam, direct static folder se load karein
    try:
        with open("static/gene_catalog.json", "r") as f:
            GENE_CATALOG_CACHE = json.load(f)
            return GENE_CATALOG_CACHE
    except Exception:
        return []




def parse_gene_input(raw_text):
    cleaned = []
    for chunk in re.split(r"[\n,;]+", raw_text or ""):
        gene = chunk.strip().upper()
        if gene and gene not in cleaned:
            cleaned.append(gene)
    return cleaned


def extract_sample_labels(series_matrix_path):
    labels = []

    with gzip.open(series_matrix_path, "rt") as file_handle:
        for line in file_handle:
            lower_line = line.lower()
            if "bio-source name" in lower_line or "!sample_characteristics_ch1" in lower_line:
                parts = line.strip().split("\t")
                for part in parts[1:]:
                    text = part.lower()
                    if "affected" in text or "alzheimer" in text or "ad" in text:
                        labels.append("AD")
                    else:
                        labels.append("Control")
                break

    return labels


def ensure_heatmap_image():
    if HEATMAP_FILE.exists():
        return

    series_matrix_path = DATA_DIR / "GSE5281_series_matrix.txt.gz"
    if not series_matrix_path.exists():
        return

    data = pd.read_csv(
        series_matrix_path,
        sep="\t",
        comment="!",
        low_memory=False,
    )

    data = data.set_index(data.columns[0])
    data = data.apply(pd.to_numeric, errors="coerce").fillna(0).T

    labels = extract_sample_labels(series_matrix_path)
    if len(labels) != len(data):
        labels = ["Control"] * len(data)

    variances = data.var(axis=0).sort_values(ascending=False).head(20).index.tolist()
    heatmap_data = data[variances]

    label_palette = ["#2e728c" if label == "Control" else "#cb7440" for label in labels]

    HEATMAP_FILE.parent.mkdir(parents=True, exist_ok=True)

    cluster = sns.clustermap(
        heatmap_data.T,
        cmap="vlag",
        col_colors=label_palette,
        standard_scale=0,
        figsize=(14, 9),
        xticklabels=False,
        yticklabels=True,
    )
    cluster.fig.suptitle("Heatmap of Top Variable Expression Features", y=1.02, fontsize=16)
    cluster.savefig(HEATMAP_FILE, dpi=160, bbox_inches="tight")
    plt.close("all")


ensure_heatmap_image()


@app.route("/genes", methods=["GET", "POST"])
def genes_page():
    selected_genes = []
    error_message = None

    if request.method == "POST":
        raw_text = request.form.get("gene_list", "")
        requested_genes = parse_gene_input(raw_text)
        gene_lookup = {item["gene"].upper(): item for item in load_gene_catalog()}

        if not requested_genes:
            error_message = "Please add at least one gene symbol to review."
        else:
            selected_genes = [gene_lookup[gene] for gene in requested_genes if gene in gene_lookup]
            missing_genes = [gene for gene in requested_genes if gene not in gene_lookup]
            if not selected_genes:
                error_message = f"No matching genes were found in the dataset: {', '.join(missing_genes)}"
            elif missing_genes:
                error_message = f"Some genes were not found in the dataset: {', '.join(missing_genes)}"

    return render_template(
        "genes.html",
        project=PROJECT,
        best_model=pick_best_model(PROJECT["model_results"]),
        genes=load_gene_catalog()[:120],
        selected_genes=selected_genes,
        error_message=error_message,
    )


@app.route("/api/genes")
def api_genes():
    query = request.args.get("q", "").strip().upper()
    catalog = load_gene_catalog()

    if query:
        filtered = [item for item in catalog if query in item["gene"].upper()]
    else:
        filtered = catalog

    return jsonify(filtered)


@app.route("/api/genes/analyze", methods=["POST"])
def api_gene_analyze():
    raw_text = request.form.get("gene_list", "")
    requested_genes = parse_gene_input(raw_text)
    gene_lookup = {item["gene"].upper(): item for item in load_gene_catalog()}
    results = [gene_lookup[gene] for gene in requested_genes if gene in gene_lookup]
    return jsonify({"results": results})


@app.route("/")
def index():
    return render_template(
        "index.html",
        project=PROJECT,
        best_model=pick_best_model(PROJECT["model_results"]),
        model_chart=build_model_chart_series(PROJECT["model_results"]),
    )


@app.route("/report")
def report():
    return render_template(
        "report.html",
        project=PROJECT,
        best_model=pick_best_model(PROJECT["model_results"]),
        model_chart=build_model_chart_series(PROJECT["model_results"]),
    )


def build_report_text():
    lines = []
    lines.append(PROJECT["title"])
    lines.append(PROJECT["subtitle"])
    lines.append("")
    lines.append("Dataset")
    lines.append(f"- {PROJECT['dataset']}")
    lines.append(f"- Total samples: {PROJECT['sample_stats'][0]['value']}")
    lines.append(f"- Control samples: {PROJECT['sample_stats'][1]['value']}")
    lines.append(f"- AD samples: {PROJECT['sample_stats'][2]['value']}")
    lines.append(f"- Expression features: {PROJECT['sample_stats'][3]['value']}")
    lines.append("")
    lines.append("Model comparison")
    for row in PROJECT["model_results"]:
        lines.append(
            f"- {row['name']}: accuracy {row['accuracy']:.4f}, ROC-AUC {row['roc_auc']:.4f}, F1 {row['f1']:.4f}"
        )
    lines.append("")
    lines.append("Top genes")
    for gene in PROJECT["top_genes"]:
        lines.append(f"- {gene['gene']}: importance {gene['importance']:.6f}")
    lines.append("")
    lines.append("Pathways used")
    for pathway in PROJECT["top_pathways"]:
        lines.append(f"- {pathway['term']}: adjusted p-value {pathway['adjusted_p']:.3e}")
    lines.append("")
    lines.append("External validation")
    lines.append(f"- Accuracy: {PROJECT['validation']['accuracy']:.2f}")
    lines.append(f"- External AUC-ROC: {PROJECT['validation']['external_auc']:.4f}")
    lines.append(f"- Interpretation: {PROJECT['validation']['interpretation']}")
    lines.append("")
    lines.append("Final candidates")
    for drug in PROJECT["final_candidates"]:
        lines.append(
            f"- {drug['drug']} ({drug['priority']}): BBB {drug['bbb']} | {drug['mechanism']} | {drug['ad_link']}"
        )
    lines.append("")
    lines.append(PROJECT["conclusion"])
    return "\n".join(lines)


@app.route("/download-report")
def download_report():
    content = build_report_text()
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": 'attachment; filename="alzheimer_drug_repurposing_report.txt"'},
    )


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_ENV") != "production"
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=debug_mode, host=host, port=port)
