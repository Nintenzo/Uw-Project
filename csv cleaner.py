import pandas as pd

df = pd.read_csv("gender_Merged_1mrbigshot_miketrudell_nneka.csv", on_bad_lines="skip")
df = df[df["Gender"].str.lower() != "unknown"]
df.to_csv("cleaned_file.csv", index=False)
