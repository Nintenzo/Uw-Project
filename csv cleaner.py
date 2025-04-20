import pandas as pd

df = pd.read_csv("filtered_file.csv")
df = df[df["Gender"].str.lower() != "unknown"]
df.to_csv("cleaned_file.csv", index=False)
