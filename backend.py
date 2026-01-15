import pandas as pd
import json

# Load the file
df = pd.read_csv("perf-df-pytorch-cuda-bnb-1xA10.csv")

# 1. Filter for single-user chat (batch size = 1)
#    We use the column name we confirmed earlier.
df_clean = df[df["config.scenario.input_shapes.batch_size"] == 1].copy()

output_data = []

for index, row in df_clean.iterrows():
    full_name = row['config.backend.model']
    # Clean up the name (remove "meta-llama/" prefix)
    clean_name = full_name.split("/")[-1]
    
    # 2. Get the specific data points
    # Speed: We verified this column has data earlier
    speed = row['report.decode.throughput.value']
    
    # VRAM: We are using the 'prefill' max allocation (MB)
    vram_mb = row['report.prefill.memory.max_allocated']

    # 3. Validation: Only add if data is real (not NaN and greater than 0)
    if pd.notna(speed) and pd.notna(vram_mb) and vram_mb > 0:
        output_data.append({
            "name": clean_name,
            "full_name": full_name,
            "speed": round(speed, 2),
            "vram": round(vram_mb / 1024, 2) # Convert MB to GB
        })

# 4. Save
with open("model_data.json", "w") as f:
    json.dump(output_data, f, indent=2)

print(f"Success! Processed {len(output_data)} models.")
