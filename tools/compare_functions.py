#!/usr/bin/env python3
"""Compare named top-level functions/constants across the three agent.py files (git HEAD)."""
import ast, subprocess
from pathlib import Path
H = Path.home()
SRC = {
    "gcp": (H / "currency-claude-agui-a2ui1", "currency_agent/agent.py"),
    "aws": (H / "currency-strands-agui-a2ui1", "app/agent/currency_agent/agent.py"),
    "azure": (H / "currency-maf-agui-a2ui1", "app/agent/currency_agent/agent.py"),
}
def defs(cloud):
    repo, path = SRC[cloud]
    text = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{path}"], capture_output=True, text=True).stdout
    tree = ast.parse(text)
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = ast.get_source_segment(text, node)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            tgt = node.targets[0] if isinstance(node, ast.Assign) else node.target
            if isinstance(tgt, ast.Name):
                out[tgt.id] = ast.get_source_segment(text, node)
    return out
d = {c: defs(c) for c in SRC}
names = sorted(set().union(*[set(v) for v in d.values()]))
print("| Name | GCP | AWS | Azure | AWS == Azure | GCP == AWS |")
print("| :--- | :--- | :--- | :--- | :--- | :--- |")
for n in names:
    p = {c: n in d[c] for c in SRC}
    aa = "yes" if p["aws"] and p["azure"] and d["aws"][n] == d["azure"][n] else ""
    ga = "yes" if p["gcp"] and p["aws"] and d["gcp"][n] == d["aws"][n] else ""
    print(f"| {n} | {'x' if p['gcp'] else ''} | {'x' if p['aws'] else ''} | {'x' if p['azure'] else ''} | {aa} | {ga} |")
