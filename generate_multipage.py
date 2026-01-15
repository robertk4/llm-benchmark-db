import pandas as pd
import os
import shutil
import json
import re

# --- CONFIGURATION ---
OUTPUT_DIR = "docs"
CSV_FILE = "perf-df-pytorch-cuda-bnb-1xA10.csv"

# Affiliate Links (Customize these later)

my_tag = "robertk4-20"

LINKS = {
    "low_vram": f"https://amazon.com/s?k=rtx+4060+16gb&tag={my_tag}", # < 12GB
    "mid_vram": f"https://amazon.com/s?k=rtx+4070+super&tag={my_tag}", # 12-16GB
    "high_vram": f"https://amazon.com/s?k=rtx+3090+24gb&tag={my_tag}", # 24GB
    "pro_vram": f"https://amazon.com/s?k=rtx+6000+ada&tag={my_tag}"   # > 24GB
}

def clean_slug(text):
    """Converts a model name into a URL-friendly slug."""
    # Remove 'meta-llama/' prefixes etc
    text = text.split("/")[-1]
    # Lowercase and replace weird chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return slug

def get_affiliate_link(vram_needed):
    """Returns the correct GPU buy link based on VRAM requirements."""
    if vram_needed <= 8: return LINKS["low_vram"]
    if vram_needed <= 16: return LINKS["mid_vram"]
    if vram_needed <= 24: return LINKS["high_vram"]
    return LINKS["pro_vram"]

def generate_site():
    # 1. Prepare Output Directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(f"{OUTPUT_DIR}/model")

    # 2. Load Data
    print(f"Loading {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE)
    
    # Filter for Batch Size = 1 (Real user chat scenario)
    df = df[df["config.scenario.input_shapes.batch_size"] == 1].copy()

    # Process models into a clean list
    models = []
    for index, row in df.iterrows():
        full_name = row['config.backend.model']
        clean_name = full_name.split("/")[-1]
        
        # Use verified columns from our debug session
        speed = row['report.decode.throughput.value']
        vram_mb = row['report.prefill.memory.max_allocated']

        if pd.notna(speed) and pd.notna(vram_mb) and vram_mb > 0:
            vram_gb = round(vram_mb / 1024, 2)
            slug = clean_slug(full_name)
            
            models.append({
                "name": clean_name,
                "full_name": full_name,
                "slug": slug,
                "speed": round(speed, 2),
                "vram": vram_gb,
                "link": f"model/{slug}/"
            })

    # Sort by VRAM (popular sorting method)
    models.sort(key=lambda x: x['vram'])

    print(f"Generating {len(models)} pages...")

    # 3. Generate Individual Landing Pages
    for model in models:
        model_dir = f"{OUTPUT_DIR}/model/{model['slug']}"
        os.makedirs(model_dir, exist_ok=True)
        
        # Determine strict requirements
        rec_gpu = "RTX 3060 / 4060"
        if model['vram'] > 8: rec_gpu = "RTX 4070 / 3080"
        if model['vram'] > 12: rec_gpu = "RTX 3090 / 4090"
        if model['vram'] > 24: rec_gpu = "RTX 6000 Ada / A6000"

        buy_link = get_affiliate_link(model['vram'])

        # Simple "Similar Models" logic (same VRAM range)
        similar_models = [m for m in models if abs(m['vram'] - model['vram']) < 2 and m['slug'] != model['slug']][:5]
        similar_html = "".join([f'<li><a href="../../model/{m["slug"]}/">{m["name"]}</a> ({m["vram"]} GB)</li>' for m in similar_models])

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Can I Run {model['name']}? VRAM & Speed Benchmark</title>
            <meta name="description" content="Benchmarks for {model['name']}. Requires {model['vram']} GB VRAM. Runs at {model['speed']} tokens/sec. Check your GPU compatibility.">
            <style>
                body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }}
                .card {{ background: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }}
                h1 {{ margin-bottom: 5px; }}
                .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
                .stat-box {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
                .stat-val {{ display: block; font-size: 24px; font-weight: bold; color: #2563eb; }}
                .stat-label {{ font-size: 14px; color: #64748b; }}
                .btn {{ display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; }}
                .btn:hover {{ background: #1d4ed8; }}
                .breadcrumbs {{ font-size: 14px; margin-bottom: 20px; }}
                .breadcrumbs a {{ color: #64748b; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="breadcrumbs">
                <a href="../../index.html">← Back to Leaderboard</a>
            </div>

            <div class="card">
                <h1>{model['name']} Benchmark</h1>
                <p>Performance data for <strong>{model['full_name']}</strong> on consumer hardware.</p>
                
                <div class="stat-grid">
                    <div class="stat-box">
                        <span class="stat-val">{model['vram']} GB</span>
                        <span class="stat-label">VRAM Required</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-val">{model['speed']} t/s</span>
                        <span class="stat-label">Generation Speed</span>
                    </div>
                </div>

                <h3>Can you run it?</h3>
                <p>To run this model comfortably, you need a GPU with at least <strong>{model['vram']} GB</strong> of VRAM.</p>
                <p><strong>Recommended GPU:</strong> {rec_gpu}</p>
                
                <div style="margin-top: 20px;">
                    <a href="{buy_link}" target="_blank" class="btn">Check {rec_gpu} Pricing &rarr;</a>
                </div>
            </div>

            <h3>Similar Models</h3>
            <ul>
                {similar_html}
            </ul>
        </body>
        </html>
        """
        
        with open(f"{model_dir}/index.html", "w", encoding="utf-8") as f:
            f.write(html_content)

    # 4. Generate Main Index (The Home Page)
    # This is a simplified version of your calculator, linking to the deep pages.
    table_rows = ""
    for model in models:
        table_rows += f"""
        <tr>
            <td><a href="{model['link']}">{model['name']}</a></td>
            <td>{model['vram']} GB</td>
            <td>{model['speed']} t/s</td>
        </tr>
        """

    index_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="google-site-verification" content="Z7SA16tBCKR9ckuoLUKjwHXx6nuNz8otXZpknU_OxKY" />
        <title>LLM VRAM Database - Can I Run It?</title>
        <style>
            body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8fafc; }}
            a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
            a:hover {{ text-decoration: underline; }}
            input {{ width: 100%; padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; box-sizing: border-box; }}
        </style>
    </head>
    <body>
        <h1>LLM Hardware Database</h1>
        <p>Search {len(models)} local AI models to see VRAM requirements and speed benchmarks.</p>
        
        <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search for models (e.g. Llama)...">

        <table id="modelTable">
            <thead>
                <tr>
                    <th>Model Name</th>
                    <th>VRAM (GB)</th>
                    <th>Speed (t/s)</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        <script>
            function filterTable() {{
                var input, filter, table, tr, td, i, txtValue;
                input = document.getElementById("searchInput");
                filter = input.value.toUpperCase();
                table = document.getElementById("modelTable");
                tr = table.getElementsByTagName("tr");
                for (i = 0; i < tr.length; i++) {{
                    td = tr[i].getElementsByTagName("td")[0];
                    if (td) {{
                        txtValue = td.textContent || td.innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                            tr[i].style.display = "";
                        }} else {{
                            tr[i].style.display = "none";
                        }}
                    }}       
                }}
            }}
        </script>
    </body>
    </html>
    """

    with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"DONE! Website generated in '{OUTPUT_DIR}/'.")

if __name__ == "__main__":
    generate_site()
