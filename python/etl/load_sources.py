from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW  = ROOT / "data" / "raw"
OUT  = ROOT / "data" / "outputs"
IMG  = ROOT / "images"

for p in (RAW, OUT, IMG):
    p.mkdir(parents=True, exist_ok=True)

print("[paths]")
print("ROOT:", ROOT)
print("RAW :", RAW, "exists?", RAW.exists())
print("OUT :", OUT, "exists?", OUT.exists())
print("IMG :", IMG, "exists?", IMG.exists())

required = [
    RAW / "raw-department.txt",
    RAW / "raw-department-budget.json",
    RAW / "raw-department-budget2.json",
]
missing = [str(p) for p in required if not p.exists()]
if missing:
    raise SystemExit("Missing raw files:\n" + "\n".join(missing))

print("OK — raw files present.")