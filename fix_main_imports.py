with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Add proper imports at the very top of main.py
required_imports = """import json, os, math
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
"""

if "from pydantic import BaseModel" not in code:
    code = required_imports + "\n" + code

with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("backend/app/main.py fixed with BaseModel and all necessary imports!")
