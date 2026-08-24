import json, os

# 1. Root vercel.json
root_vercel = {
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://crimenet-ai.onrender.com/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
with open(r"c:\Users\Aditya\Downloads\SIH 2026\vercel.json", "w", encoding="utf-8") as f:
    json.dump(root_vercel, f, indent=2)

# 2. Frontend vercel.json
frontend_vercel = {
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://crimenet-ai.onrender.com/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\vercel.json", "w", encoding="utf-8") as f:
    json.dump(frontend_vercel, f, indent=2)

print("Vercel configuration created successfully!")
