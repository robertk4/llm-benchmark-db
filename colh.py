import pandas as pd

df = pd.read_csv("perf-df-pytorch-cuda-bnb-1xA10.csv")

# These are the 3 most likely alternatives
candidates = [
    "report.prefill.memory.max_allocated", 
    "report.load_model.memory.max_allocated",
    "report.load.memory.max_allocated"
]

print("--- SEARCHING FOR VALID DATA ---\n")

for col in candidates:
    if col in df.columns:
        # Get values that are greater than 0
        valid_data = df[df[col] > 0][col]
        
        if not valid_data.empty:
            avg_val = valid_data.mean()
            print(f"✅ FOUND DATA IN: {col}")
            print(f"   Sample Value: {valid_data.iloc[0]} (Check if this looks like MB or Bytes)")
            print(f"   Average: {avg_val:.2f}\n")
        else:
            print(f"❌ {col} is empty (all zeros).\n")
    else:
        print(f"⚠️ {col} does not exist in this CSV.\n")
