import sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from pathlib import Path
import re

ENERGY_COL = "CPU_ENERGY (J)"
DELTA_COL = "Delta"

Z_OUTLIER_THRESHOLD = 3.0

FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

# Energy metric calculations

def compute_power(df: pd.DataFrame, energy_col: str = ENERGY_COL, delta_col: str = DELTA_COL) -> pd.DataFrame:
    out = df.copy()
    out["Delta_s"] = out[delta_col] / 1000.0
    out["dE_J"] = out[energy_col].diff()
    out["Power_W"] = out["dE_J"] / out["Delta_s"]
    return out

def clean_power_samples(df: pd.DataFrame) -> pd.DataFrame:
    keep = ((df["Delta_s"] > 0) & df["Power_W"].notna() & np.isfinite(df["Power_W"]))
    return df.loc[keep].copy()

def edp_from_trace(df: pd.DataFrame, energy_col: str = ENERGY_COL) -> tuple[float, float, float]:
    total_energy = float(df[energy_col].iloc[-1] - df[energy_col].iloc[0])
    total_time = float(df["Delta_s"].sum())
    edp = total_energy * total_time
    return total_energy, total_time, edp

# Statistic functions + plot

def zscore_outliers(series: pd.Series, threshold: float = Z_OUTLIER_THRESHOLD) -> pd.Series:
    z = stats.zscore(series, nan_policy="omit")
    return np.abs(z) > threshold

def shapiro_test(series: pd.Series):
    x = series.dropna().to_numpy()
    
    if len(x) > 5000:
        x = np.random.default_rng(0).choice(x, size=5000, replace=False)
    return stats.shapiro(x)
    
def welch_ttest(a: np.ndarray, b: np.ndarray):
    return stats.ttest_ind(a, b, equal_var=False, alternative="two-sided")

def mannwhitney_u(a: np.ndarray, b: np.ndarray):
    return stats.mannwhitneyu(a, b, alternative="two-sided")

def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    m1, m2 = a.mean(), b.mean()
    s1, s2 = a.std(ddof=1), b.std(ddof=1)
    pooled = np.sqrt(0.5 * (s1**2 + s2**2))
    return float((m2 - m1) / pooled) if pooled > 0 else np.nan

def common_language(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    u = stats.mannwhitneyu(a, b, alternative="two-sided").statistic
    n1, n2 = len(a), len(b)
    return float(u / (n1 * n2)) if n1 * n2 > 0 else np.nan

def violin_plot(data_by_group: dict[str, np.ndarray], title: str, ylabel: str, filename: str | None = None, show: bool = True):
    labels = list(data_by_group.keys())
    data = [data_by_group[k] for k in labels]
    
    plt.figure()
    plt.violinplot(data, showmeans=True)
    plt.xticks(range(1, len(labels) + 1), labels)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    
    if filename is not None:
        path = FIG_DIR / filename
        plt.savefig(path, dpi=300, bbox_inches="tight")
        print(f"Saved figure → {path}")

    if show:
        plt.show()
    else:
        plt.close()

# Final energy analysis function

def analyze_group(df_g: pd.DataFrame, name: str):
    df_p = compute_power(df_g)
    df_p = clean_power_samples(df_p)
    
    avg_power = float(df_p["Power_W"].mean())

    # out_mask = zscore_outliers(df_p["Power_W"])
    # n_out = int(out_mask.sum())
    # df_filtered = df_p.loc[~out_mask].copy()
    
    # avg_power = float(df_filtered["Power_W"].mean())
    
    df_for_edp = compute_power(df_g)
    df_for_edp = df_for_edp[df_for_edp["Delta_s"] > 0].copy()
    total_energy, total_time, edp = edp_from_trace(df_for_edp)

    # sh_stat, sh_p = shapiro_test(df_filtered["Power_W"])
    
    return {
        "name": name, 
        "avg_power_W": avg_power,
        "total_energy_J": total_energy,
        "total_time_s": total_time,
        "EDP_Js": edp,
        "n_samples_power": int(len(df_p)),
        # "n_outliers_power": n_out,
        # "shapiro_stat": float(sh_stat),
        # "shapiro_p": float(sh_p),
        # "power_samples_filtered": df_filtered["Power_W"].to_numpy(),
        # "df_power_filtered": df_filtered,
    }
    
# Data preprocessing

def parse_metadata_from_filename(p: Path) -> dict:
    stem = p.stem.lower()

    # app
    if stem.startswith("zoom"):
        app = "zoom"
    elif stem.startswith("teams"):
        app = "teams"
    else:
        app = "zoom" if "zoom" in stem else ("teams" if "teams" in stem else None)

    # iteration = last _number
    m_iter = re.search(r"_(\d+)$", stem)
    iteration = int(m_iter.group(1)) if m_iter else None

    # helpers: token matching with underscores
    def has_token(tok: str) -> bool:
        return re.search(rf"(^|_){re.escape(tok)}(_|$)", stem) is not None

    def extract_flag(name: str):
        m = re.search(rf"(^|_){re.escape(name)}_(on|off)(_|\b|$)", stem)
        return m.group(2) if m else None

    # camera: camera_on/off
    camera = extract_flag("camera") or extract_flag("cam")

    # blur: blur / noblur OR blur_on/off
    blur = extract_flag("blur")
    if blur is None:
        if has_token("noblur"):
            blur = "off"
        elif has_token("blur"):
            blur = "on"

    # share: share / noshare OR share_on/off
    share = extract_flag("share") or extract_flag("screenshare") or extract_flag("screen")
    if share is None:
        if has_token("noshare"):
            share = "off"
        elif has_token("share"):
            share = "on"

    condition = stem[:m_iter.start()].rstrip("_-") if m_iter else stem

    return {
        "file": str(p),
        "app": app,
        "camera": camera,
        "blur": blur,
        "share": share,
        "iteration": iteration,
        "condition": condition,
    }

def process_folder(folder: str | Path, pattern: str = "*.csv") -> pd.DataFrame:
    folder = Path(folder)
    rows = []

    for csv_path in folder.rglob(pattern):
        try:
            df = pd.read_csv(csv_path)
            meta = parse_metadata_from_filename(csv_path)
            res = analyze_group(df, name=csv_path.name)
            rows.append({**meta, **res})
        except Exception as e:
            print(f"[WARN] Skipping {csv_path}: {e}")

    df_runs = pd.DataFrame(rows)

    for col in ["app", "camera", "blur", "share", "iteration", "condition", "file"]:
        if col not in df_runs.columns:
            df_runs[col] = np.nan

    df_runs["iteration"] = pd.to_numeric(df_runs["iteration"], errors="coerce")
    return df_runs

df_runs = process_folder("results")
print(df_runs.shape)
print(df_runs.head())

df_runs.to_csv("df_runs.csv", index=False)
print("Saved df_runs.csv")

def clean_and_test_runs(df_cond: pd.DataFrame, metric: str = "avg_power_W", z_thresh: float = Z_OUTLIER_THRESHOLD):
    
    values = df_cond[metric].dropna()
    
    if len(values) < 3:
        return df_cond.copy(), np.nan, 0

    out_mask = zscore_outliers(values, threshold=z_thresh)
    df_clean = df_cond.loc[values.index[~out_mask]].copy()
    n_out = int(out_mask.sum())

    sh_p = shapiro_test(df_clean[metric]).pvalue if len(df_clean) >= 3 else np.nan
    return df_clean, sh_p, n_out

# Statistics start here!

def compare_settings(label_a: str, df_a: pd.DataFrame, label_b: str, df_b: pd.DataFrame, metric: str = "avg_power_W", title: str = "", filename: str | None = None):
    a_clean, p_a, out_a = clean_and_test_runs(df_a, metric=metric)
    b_clean, p_b, out_b = clean_and_test_runs(df_b, metric=metric)

    a = a_clean[metric].dropna().to_numpy()
    b = b_clean[metric].dropna().to_numpy()

    print(f"{label_a}: n={len(df_a)} clean={len(a_clean)} outliers={out_a} shapiro_p={p_a}")
    print(f"{label_b}: n={len(df_b)} clean={len(b_clean)} outliers={out_b} shapiro_p={p_b}")

    violin_plot({label_a: a, label_b: b}, title=title, ylabel=metric, filename=filename)

    both_normal = (p_a >= 0.05) and (p_b >= 0.05)

    if both_normal:
        t = welch_ttest(a, b)
        eff = cohens_d(a, b)
        test_name = "Welch t-test"
        eff_name = "Cohen's d"
        pval = float(t.pvalue)
    else:
        u = mannwhitney_u(a, b)
        eff = common_language(a, b)
        test_name = "Mann–Whitney U"
        eff_name = "Common language"
        pval = float(u.pvalue)
        
    print(f"TEST: {test_name}  p={pval:.6g}  effect({eff_name})={eff:.4f}")
    
    return {
        "metric": metric,
        "label_a": label_a,
        "label_b": label_b,
        "n_a": int(len(df_a)),
        "n_b": int(len(df_b)),
        "n_a_clean": int(len(a_clean)),
        "n_b_clean": int(len(b_clean)),
        "outliers_a": int(out_a),
        "outliers_b": int(out_b),
        "shapiro_p_a": float(p_a) if p_a == p_a else np.nan,
        "shapiro_p_b": float(p_b) if p_b == p_b else np.nan,
        "test": test_name,
        "pvalue": pval,
        "effect_name": eff_name,
        "effect": float(eff),
        "mean_a": float(np.mean(a)) if len(a) else np.nan,
        "mean_b": float(np.mean(b)) if len(b) else np.nan,
        "median_a": float(np.median(a)) if len(a) else np.nan,
        "median_b": float(np.median(b)) if len(b) else np.nan,
        "figure": filename,
        "title": title,
    }
    
def subset_for_factor(df_runs: pd.DataFrame, factor: str) -> pd.DataFrame:
    return df_runs[df_runs[factor].notna()].copy()

def run_everything(df_runs: pd.DataFrame, metrics=("avg_power_W", "EDP_Js"), factors=("camera", "blur", "share"), apps=("zoom", "teams")) -> pd.DataFrame:
    rows = []
    
    for metric in metrics:
        for factor in factors:
            df_factor = subset_for_factor(df_runs, factor)
            
            combined_data = {}
            valid_apps = []
            
            for app in apps:
                df_app = df_factor.query("app==@app")
                df_on = df_app.query(f"{factor}=='on'")
                df_off = df_app.query(f"{factor}=='off'")
                
                if len(df_on) == 0 or len(df_off) == 0:
                    continue
                
                a_clean, p_a, out_a = clean_and_test_runs(df_on, metric=metric)
                b_clean, p_b, out_b = clean_and_test_runs(df_off, metric=metric)
                
                a = a_clean[metric].dropna().to_numpy()
                b = b_clean[metric].dropna().to_numpy()
                
                label_on = f"{app.capitalize()} ON"
                label_off = f"{app.capitalize()} OFF"
                
                combined_data[label_on] = a
                combined_data[label_off] = b
                valid_apps.append(app)
                
                print(f"{label_on}: n={len(df_on)} clean={len(a_clean)} outliers={out_a} shapiro_p={p_a}")
                print(f"{label_off}: n={len(df_off)} clean={len(b_clean)} outliers={out_b} shapiro_p={p_b}")
                
                both_normal = (p_a >= 0.05) and (p_b >= 0.05)
                
                if both_normal:
                    t = welch_ttest(a, b)
                    eff = cohens_d(a, b)
                    test_name = "Welch t-test"
                    eff_name = "Cohen's d"
                    pval = float(t.pvalue)
                else:
                    u = mannwhitney_u(a, b)
                    eff = common_language(a, b)
                    test_name = "Mann–Whitney U"
                    eff_name = "Common language"
                    pval = float(u.pvalue)
                
                print(f"Test: {test_name}  p={pval:.6g}  effect({eff_name})={eff:.4f}")
                
                rows.append({
                    "metric": metric,
                    "label_a": f"{app.capitalize()} {factor} ON",
                    "label_b": f"{app.capitalize()} {factor} OFF",
                    "n_a": int(len(df_on)),
                    "n_b": int(len(df_off)),
                    "n_a_clean": int(len(a_clean)),
                    "n_b_clean": int(len(b_clean)),
                    "outliers_a": int(out_a),
                    "outliers_b": int(out_b),
                    "shapiro_p_a": float(p_a) if p_a == p_a else np.nan,
                    "shapiro_p_b": float(p_b) if p_b == p_b else np.nan,
                    "test": test_name,
                    "pvalue": pval,
                    "effect_name": eff_name,
                    "effect": float(eff),
                    "mean_a": float(np.mean(a)) if len(a) else np.nan,
                    "mean_b": float(np.mean(b)) if len(b) else np.nan,
                    "median_a": float(np.median(a)) if len(a) else np.nan,
                    "median_b": float(np.median(b)) if len(b) else np.nan,
                    "figure": f"{factor}_{metric}_combined.png",
                    "title": f"{factor.capitalize()} – {metric} (ON vs OFF)",
                    "app": app,
                    "factor": factor,
                })
            
            if combined_data:
                title = f"{factor.capitalize()} – {metric} (ON vs OFF)"
                fig_name = f"{factor}_{metric}_combined.png"
                
                violin_plot(combined_data, title=title, ylabel=metric, filename=fig_name, show=False)
                print()

    df_summary = pd.DataFrame(rows)
    
    Path("processed").mkdir(exist_ok=True)

    out_csv = Path("processed") / "stat_summary_everything.csv"
    df_summary.to_csv(out_csv, index=False)
    print(f"Saved summary → {out_csv}")

    return df_summary

df_summary = run_everything(df_runs)
print(df_summary[["app","factor","metric","test","pvalue","effect_name","effect","figure"]])