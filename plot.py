import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def violinPlot():

    df = pd.read_csv("results/processedDatas.csv")

    df["Camera_State"] = df["Experiment Name"].apply(
        lambda x: "Camera ON" if "on" in x.lower() else "Camera OFF"
    )

    metric = "CPU Energy (Joules)"
    # metric = "Average Power (Watts)"

    plt.figure(figsize=(8, 6))

    sns.violinplot(
        data=df,
        x="Camera_State",
        y=metric,
        inner="box"   
    )

    plt.title("Camera ON vs OFF")
    plt.xlabel("")
    plt.tight_layout()

    plt.show()

violinPlot()