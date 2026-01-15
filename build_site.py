import pandas as pd
import json

# 1. Load the data (using the columns we verified work)
df = pd.read_csv("perf-df-pytorch-cuda-bnb-1xA10.csv")
df_clean = df[df["config.scenario.input_shapes.batch_size"] == 1].copy()

models_list = []

for index, row in df_clean.iterrows():
    full_name = row['config.backend.model']
    clean_name = full_name.split("/")[-1]
    
    # Using the verified columns from your debug session
    speed = row['report.decode.throughput.value']
    vram_mb = row['report.prefill.memory.max_allocated']

    if pd.notna(speed) and pd.notna(vram_mb) and vram_mb > 0:
        models_list.append({
            "name": clean_name,
            "full_name": full_name,
            "speed": round(speed, 2),
            "vram": round(vram_mb / 1024, 2) # MB to GB
        })

# Convert list to a JSON string for JavaScript
json_data = json.dumps(models_list)

# 2. Define the HTML Template (with the data injected directly inside)
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Speed Calculator</title>
    <style>
        :root {{ --primary: #2563eb; --bg: #f8fafc; --card: #ffffff; --text: #1e293b; --success: #10b981; --danger: #ef4444; }}
        body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); max-width: 800px; margin: 0 auto; padding: 20px; }}
        .card {{ background: var(--card); padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        select {{ width: 100%; padding: 10px; margin-top: 5px; border-radius: 6px; border: 1px solid #ccc; font-size: 16px; }}
        .result-item {{ display: flex; justify-content: space-between; align-items: center; padding: 12px; border-bottom: 1px solid #eee; }}
        .result-item:last-child {{ border-bottom: none; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 14px; }}
        .badge-speed {{ background: #eff6ff; color: var(--primary); }}
        .badge-vram {{ background: #f1f5f9; color: #64748b; margin-right: 10px; }}
        .upsell {{ color: var(--danger); text-decoration: none; font-weight: bold; font-size: 14px; }}
        .upsell:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>🚀 LLM Hardware Calculator</h2>
        <label><strong>Select Your GPU:</strong></label>
        <select id="gpuSelect" onchange="render()">
            <option value="8">NVIDIA RTX 3070 / 4060 (8GB)</option>
            <option value="12">NVIDIA RTX 3060 / 4070 (12GB)</option>
            <option value="16">NVIDIA RTX 4080 (16GB)</option>
            <option value="24" selected>NVIDIA RTX 3090 / 4090 (24GB)</option>
        </select>
        <p style="margin-top:10px; color:#666;" id="stats"></p>
    </div>

    <div class="card" id="results"></div>

    <script>
        // DATA INJECTED BY PYTHON
        const rawData = {json_data};
        
        const affiliateLinks = {{
            "upgrade_24gb": "https://amazon.com/s?k=rtx+3090", 
            "upgrade_48gb": "https://amazon.com/s?k=rtx+6000+ada" 
        }};

        function render() {{
            const userVram = parseInt(document.getElementById('gpuSelect').value);
            const list = document.getElementById('results');
            list.innerHTML = '';
            
            // Allow 15% overhead for Windows/System
            const usableVram = userVram * 0.85; 

            // Sort by Speed (Fastest first)
            const sortedData = [...rawData].sort((a, b) => b.speed - a.speed);
            
            let compatibleCount = 0;

            sortedData.forEach(model => {{
                const fits = model.vram <= usableVram;
                if (fits) compatibleCount++;

                const div = document.createElement('div');
                div.className = 'result-item';
                div.style.opacity = fits ? '1' : '0.6';
                div.style.background = fits ? 'white' : '#fff1f2';

                let actionHtml = '';
                if (fits) {{
                    actionHtml = `<span class="badge badge-speed">${{model.speed}} t/s</span>`;
                }} else {{
                    const link = model.vram > 24 ? affiliateLinks.upgrade_48gb : affiliateLinks.upgrade_24gb;
                    actionHtml = `<a href="${{link}}" target="_blank" class="upsell">Need ${{Math.ceil(model.vram)}}GB GPU &rarr;</a>`;
                }}

                div.innerHTML = `
                    <div>
                        <strong>${{model.name}}</strong><br>
                        <span class="badge badge-vram">${{model.vram}} GB VRAM</span>
                    </div>
                    <div>${{actionHtml}}</div>
                `;
                list.appendChild(div);
            }});

            document.getElementById('stats').innerText = `${{compatibleCount}} models run natively on your hardware.`;
        }}

        // Run on load
        render();
    </script>
</body>
</html>
"""

# 3. Write the file
with open("final_calculator.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Success! Created final_calculator.html with {len(models_list)} models inside.")
