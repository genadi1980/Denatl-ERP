p = "tracker.py"
with open(p, "rb") as f:
    data = f.read()

for i, line in enumerate(data.splitlines(), start=1):
    try:
        s = line.decode("utf-8")
    except Exception:
        s = line.decode("utf-8", "backslashreplace")
    print(f"{i:03}: {s!r}")
