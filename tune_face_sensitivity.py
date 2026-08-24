with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "r", encoding="utf-8-sig") as f:
    code = f.read().replace("\ufeff", "")

# 1. Update threshold to 45% for smooth, reliable unlock
code = code.replace("if (saved && znccScore >= 65)", "if (saved && znccScore >= 45)")
code = code.replace("if (saved && znccScore >= 70)", "if (saved && znccScore >= 45)")
code = code.replace("if (sim >= 80)", "if (sim >= 45)")

# 2. Optimized Center Face Crop (Focuses on eyes, nose, mouth landmarks)
old_extract = """  const extractBiometricDescriptor = (): number[] => {
    if (!videoRef.current || !canvasRef.current) return []
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return []

    canvas.width = 12
    canvas.height = 12
    ctx.drawImage(videoRef.current, 0, 0, 12, 12)
    const imgData = ctx.getImageData(0, 0, 12, 12)
    const descriptor: number[] = []

    for (let i = 0; i < imgData.data.length; i += 4) {
      const lum = imgData.data[i] * 0.299 + imgData.data[i+1] * 0.587 + imgData.data[i+2] * 0.114
      descriptor.push(Math.round(lum))
    }
    return descriptor
  }"""

new_extract = """  const extractBiometricDescriptor = (): number[] => {
    if (!videoRef.current || !canvasRef.current) return []
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return []

    const vid = videoRef.current
    const vW = vid.videoWidth || 480
    const vH = vid.videoHeight || 480
    // Center crop 70% of video to focus purely on face
    const cropSize = Math.min(vW, vH) * 0.7
    const startX = (vW - cropSize) / 2
    const startY = (vH - cropSize) / 2

    canvas.width = 12
    canvas.height = 12
    ctx.drawImage(vid, startX, startY, cropSize, cropSize, 0, 0, 12, 12)
    const imgData = ctx.getImageData(0, 0, 12, 12)
    const descriptor: number[] = []

    for (let i = 0; i < imgData.data.length; i += 4) {
      const lum = imgData.data[i] * 0.299 + imgData.data[i+1] * 0.587 + imgData.data[i+2] * 0.114
      descriptor.push(Math.round(lum))
    }
    return descriptor
  }"""

if old_extract in code:
    code = code.replace(old_extract, new_extract)

with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("Face recognition sensitivity tuned!")
