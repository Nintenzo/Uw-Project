import pandas as pd

file = input("Enter the file name: ")
df = pd.read_csv(file, on_bad_lines="skip")
df = df[df["Gender"].str.lower() != "unknown"]
df.to_csv("cleaned_file.csv", index=False)
