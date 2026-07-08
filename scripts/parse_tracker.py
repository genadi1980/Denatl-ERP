import ast, traceback, sys

try:
    src = open("tracker.py", "r", encoding="utf-8").read()
    ast.parse(src)
    print("OK")
except Exception:
    etype, e, tb = sys.exc_info()
    if isinstance(e, SyntaxError):
        print(f"SyntaxError: {e.msg} at line {e.lineno}, offset {e.offset}")
        with open("tracker.py", "r", encoding="utf-8") as f:
            lines = f.readlines()
            start = max(0, e.lineno - 3)
            end = min(len(lines), e.lineno + 2)
            for i in range(start, end):
                marker = "->" if (i + 1) == e.lineno else "  "
                print(f"{marker} {i + 1}: {lines[i].rstrip()}")
    else:
        traceback.print_exc()
    sys.exit(1)
