import sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

ENERGY_COL = "CPU_ENERGY (J)"
DELTA_COL = "Delta"

Z_OUTLIER_THRESHOLD = 3.0

def compute_power(df: pd.DataFrame, energy_col: str = ENERGY_COL, delta_col: str = DELTA_COL) -> pd.DataFrame:
    out = df.copy()
    out["Delta_s"] = out[delta_col] / 1000.0
    out["dE_J"] = out[energy_col].diff()
    out["Power_W"] = out["dE_J"] / out["Delta_s"]
    return out

def clean_power_samples(df: pd.DataFrame) -> pd.DataFrame:
    keep = ((df["Delta_s"] > 0) & df["Power_W"].notna() & np.isfinite(df["Power_W"]))
    return df.loc[keep].copy()

def zscore_outliers(series: pd.Series, threshold: float = Z_OUTLIER_THRESHOLD) -> pd.Series:
    z = stats.zscore(series, nan_policy="omit")
    return np.abs(z) > threshold

def shapiro_test(series: pd.Series):
    x = series.dropna().to_numpy()
    
    if len(x) > 5000:
        x = np.random.default_rng(0).choice(x, size=5000, replace=False)
    return stats.shapiro(x)

def edp_from_trace(df: pd.DataFrame, energy_col: str = ENERGY_COL) -> tuple[float, float, float]:
    total_energy = float(df[energy_col].iloc[-1] - df[energy_col].iloc[0])
    total_time = float(df["Delta_s"].sum())
    edp = total_energy * total_time
    return total_energy, total_time, edp

def violin_plot(data_by_group: dict[str, np.ndarray], title: str, ylabel: str):
    labels = list(data_by_group.keys())
    data = [data_by_group[k] for k in labels]
    
    plt.figure()
    plt.violinplot(data, showmeans=True)
    plt.xticks(range(1, len(labels) + 1), labels)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.show()
    
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

def analyze_group(df_g: pd.DataFrame, name: str):
    df_p = compute_power(df_g)
    df_p = clean_power_samples(df_p)
    
    # avg_power_raw = float(df_p["Power_W"].mean())

    out_mask = zscore_outliers(df_p["Power_W"])
    n_out = int(out_mask.sum())
    df_filtered = df_p.loc[~out_mask].copy()
    
    avg_power = float(df_filtered["Power_W"].mean())
    
    df_for_edp = compute_power(df_g)
    df_for_edp = df_for_edp[df_for_edp["Delta_s"] > 0].copy()
    total_energy, total_time, edp = edp_from_trace(df_for_edp)

    sh_stat, sh_p = shapiro_test(df_filtered["Power_W"])
    
    return {
        "name": name, 
        "avg_power_W": avg_power,
        "total_energy_J": total_energy,
        "total_time_s": total_time,
        "EDP_Js": edp,
        "n_samples_power": int(len(df_p)),
        "n_outliers_power": n_out,
        "shapiro_stat": float(sh_stat),
        "shapiro_p": float(sh_p),
        "power_samples_filtered": df_filtered["Power_W"].to_numpy(),
        "df_power_filtered": df_filtered,
    }

