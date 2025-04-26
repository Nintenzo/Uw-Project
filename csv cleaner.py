import pandas as pd

df = pd.read_csv("users.csv", on_bad_lines="skip")
df = df[df["Gender"].str.lower() != "unknown"]
df.to_csv("cleaned_file.csv", index=False)
