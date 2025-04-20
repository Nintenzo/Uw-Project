import pandas as pd

# Load CSV without headers
df = pd.read_csv("Merged_1mrbigshot_miketrudell_nneka.csv", header=None)

# Assign temporary column names
df.columns = ['username', 'name']

# Allow names with only English letters and spaces
df = df[df['name'].str.match(r'^[A-Za-z ]+$', na=False)]

# Save result without headers
df.to_csv("filtered_file.csv", index=False, header=False)
