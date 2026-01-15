import os

# --- CONFIGURATION ---
# I updated this to your REAL url
BASE_URL = "https://robertk4.github.io/llm-benchmark-db/"

# I updated this to look in the 'docs' folder where your 506 pages are
OUTPUT_DIR = "docs"

def generate_sitemap():
    print(f"Scanning '{OUTPUT_DIR}' for pages...")
    
    urls = []
    
    # 1. Scan the docs folder
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            if file == "index.html":
                # Get the relative path from the docs folder
                # e.g., model\llama-2-7b\index.html
                rel_path = os.path.relpath(root, OUTPUT_DIR)
                
                # Normalize slashes for web (Windows uses \)
                rel_path = rel_path.replace("\\", "/")
                
                if rel_path == ".":
                    # Homepage
                    full_url = BASE_URL
                else:
                    # Model Page (e.g., https://site.com/model/llama-2-7b/)
                    full_url = f"{BASE_URL}{rel_path}/"
                
                urls.append(full_url)

    # 2. Build the XML string
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        xml_content += f"  <url>\n    <loc>{url}</loc>\n  </url>\n"
    
    xml_content += '</urlset>'

    # 3. Save to docs/sitemap.xml
    with open(f"{OUTPUT_DIR}/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)

    print(f"Success! Created sitemap.xml with {len(urls)} pages.")

if __name__ == "__main__":
    generate_sitemap()
