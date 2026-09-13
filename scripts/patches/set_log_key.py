with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "r", encoding="utf-8") as f:
    code = f.read()

# Set Intruder Log key to Aditya@09
code = code.replace(
    "if (entered !== 'Aditya@4912' && entered.toLowerCase() !== 'aditya@4912')",
    "if (entered !== 'Aditya@09' && entered.toLowerCase() !== 'aditya@09')"
)

with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: Intruder Log Password is now strictly Aditya@09!")
