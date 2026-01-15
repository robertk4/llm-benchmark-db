import pandas as pd

# Load the file
df = pd.read_csv("perf-df-pytorch-cuda-bnb-1xA10.csv")

# 1. Check what Batch Sizes actually exist
print("--- AVAILABLE BATCH SIZES ---")
print(df["config.scenario.input_shapes.batch_size"].unique())

# 2. Check the raw VRAM numbers (to see if they are in MB or Bytes)
print("\n--- SAMPLE VRAM (Raw Values) ---")
# We take the first 5 non-empty values
print(df["report.decode.memory.max_process_vram"].dropna().head(5))

# 3. Check the speed
print("\n--- SAMPLE SPEED (Raw Values) ---")
print(df["report.decode.throughput.value"].dropna().head(5))
