with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "r", encoding="utf-8") as f:
    code = f.read()

# Fix passcode comparison to accept Aditya@4912 (case-insensitive & trimmed)
code = code.replace(
    "const entered = pinCode.trim().toLowerCase()\n    const valid = ['Aditya@4912']\n    const isOk = valid.includes(entered)",
    "const entered = pinCode.trim()\n    const isOk = entered === 'Aditya@4912' || entered.toLowerCase() === 'aditya@4912'"
)

# Fix Face Authority Key
code = code.replace(
    "const entered = faceAuthKey.trim().toLowerCase()\n    const valid = ['Aditya@4912']\n    \n    if (!valid.includes(entered))",
    "const entered = faceAuthKey.trim()\n    if (entered !== 'Aditya@4912' && entered.toLowerCase() !== 'aditya@4912')"
)

# Fix Change Password Key
code = code.replace(
    "const entered = masterAuthInput.trim().toLowerCase()\n    const valid = ['Aditya@4912']\n\n    if (!valid.includes(entered))",
    "const entered = masterAuthInput.trim()\n    if (entered !== 'Aditya@4912' && entered.toLowerCase() !== 'aditya@4912')"
)

with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("LOGIN BUG FIXED! Aditya@4912 will now unlock smoothly!")
