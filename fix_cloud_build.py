import os, json

# 1. Update frontend/package.json to build directly with Vite
pkg_path = r"c:\Users\Aditya\Downloads\SIH 2026\frontend\package.json"
with open(pkg_path, "r", encoding="utf-8") as f:
    pkg = json.load(f)

pkg["scripts"]["build"] = "vite build"
with open(pkg_path, "w", encoding="utf-8") as f:
    json.dump(pkg, f, indent=2)

# 2. Clean App.tsx unused state
app_path = r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx"
with open(app_path, "r", encoding="utf-8-sig") as f:
    app_code = f.read().replace("\ufeff", "")

app_code = app_code.replace("  const [spotlightOpen, setSpotlightOpen] = useState(false)\n  const [searchQuery, setSearchQuery] = useState('')\n", "")
with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_code)

# 3. Clean CaseManagement.tsx unused imports
case_path = r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\pages\CaseManagement.tsx"
if os.path.exists(case_path):
    with open(case_path, "r", encoding="utf-8-sig") as f:
        case_code = f.read().replace("\ufeff", "")
    case_code = case_code.replace("import { useState, useEffect } from 'react'", "import { useState } from 'react'")
    case_code = case_code.replace("import axios from 'axios'\n", "")
    with open(case_path, "w", encoding="utf-8") as f:
        f.write(case_code)

# 4. Clean utils.ts if exists
utils_path = r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\lib\utils.ts"
if os.path.exists(utils_path):
    with open(utils_path, "w", encoding="utf-8") as f:
        f.write("export function cn(...classes: (string | undefined | null | boolean)[]) { return classes.filter(Boolean).join(' ') }\n")

print("Build configuration optimized!")
