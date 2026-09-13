import json, os

# 1. Add valid Vercel SPA + API proxy rewrite
vercel_config = {
  "rewrites": [
    {
      "source": "/api/:match*",
      "destination": "https://crimenet-ai.onrender.com/api/:match*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\vercel.json", "w", encoding="utf-8") as f:
    json.dump(vercel_config, f, indent=2)

# 2. Add crash-proof safety guards to App.tsx
app_path = r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx"
with open(app_path, "r", encoding="utf-8-sig") as f:
    code = f.read().replace("\ufeff", "")

code = code.replace(
    "if (res.data.photo) {",
    "if (res && res.data && typeof res.data === 'object' && res.data.photo) {"
)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(code)

# 3. Ensure base: '/' in vite.config.ts
vite_path = r"c:\Users\Aditya\Downloads\SIH 2026\frontend\vite.config.ts"
with open(vite_path, "w", encoding="utf-8") as f:
    f.write("""import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    host: true,
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'https://crimenet-ai.onrender.com',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
""")

print("Vercel white screen fix applied!")
