import os

frontend_src = r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src"

for root, dirs, files in os.walk(frontend_src):
    for file in files:
        if file.endswith(".tsx") or file.endswith(".ts"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8-sig") as f:
                content = f.read().replace("\ufeff", "")
            
            # Replace localhost URLs with cloud-friendly relative paths
            new_content = content.replace("http://127.0.0.1:8000/api/", "/api/")
            new_content = new_content.replace("http://localhost:8000/api/", "/api/")
            new_content = new_content.replace("http://127.0.0.1:8000", "")
            new_content = new_content.replace("http://localhost:8000", "")
            
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated APIs in: {file}")

print("All frontend endpoints converted to Cloud /api/ routes!")
