import pandas as pd
from pathlib import Path

def processData():
    data_dir = Path("results/data")
    output_file = Path("results/processedDatas.csv")

    results = []

    csVFiles = sorted(data_dir.glob("*.csv"))

    for i in csVFiles:
        
        df = pd.read_csv(i)

        df.columns = df.columns.str.strip()

        if df.empty:
            continue

        if "Delta" not in df.columns or "CPU_ENERGY (J)" not in df.columns:
            continue

        totalTime = df["Delta"].sum() / 1000

        energyAll = df["CPU_ENERGY (J)"].diff().clip(lower=0).sum()
        powerAverage = energyAll / totalTime if totalTime > 0 else 0

        filename = i.stem
        parts = filename.split("_")

        run_number = parts[-1] if len(parts) > 1 else "1"
        experiment_type = "_".join(parts[:-1]) if len(parts) > 1 else filename

        results.append({
            "Experiment Name": experiment_type,
            "Run": run_number,
            "Execution Time (seconds)": totalTime,
            "CPU Energy (Joules)": energyAll,
            "Average Power (Watts)": powerAverage,
        })


    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_file, index=False)
        print(f"jus to check if all files were used = {len(results)}")

processData()