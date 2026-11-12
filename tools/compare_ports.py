#!/usr/bin/env python3
"""Compare the three A2UI 1.0 currency-agent builds file by file, from each repo's git HEAD.

For each role (catalog, macros, rescue, agent, ...) prints line counts and how many lines
of the AWS and Azure file differ from the Google Cloud file (difflib, added + removed).
"""
import difflib, hashlib, subprocess, sys
from pathlib import Path

HOME = Path.home()
REPOS = {
    "gcp":   HOME / "currency-claude-agui-a2ui1",
    "aws":   HOME / "currency-strands-agui-a2ui1",
    "azure": HOME / "currency-maf-agui-a2ui1",
}
# role -> path per cloud (None = no such file)
ROLES = [
    ("Charts catalog (JSON)", "currency_agent/custom_catalog.json", "app/agent/currency_agent/custom_catalog.json", "app/agent/currency_agent/custom_catalog.json"),
    ("Macros", "currency_agent/macros.py", "app/agent/currency_agent/macros.py", "app/agent/currency_agent/macros.py"),
    ("Reply-text rescue", "currency_agent/a2ui_rescue.py", "app/agent/currency_agent/a2ui_rescue.py", "app/agent/currency_agent/a2ui_rescue.py"),
    ("Agent + A2UI tool", "currency_agent/agent.py", "app/agent/currency_agent/agent.py", "app/agent/currency_agent/agent.py"),
    ("MCP server", "mcp-server/server.py", "app/agent/mcp_server.py", "app/agent/mcp_server.py"),
    ("AG-UI entry point", "frontend-react/agent/main.py", "app/agent/main.py", "app/agent/main.py"),
    ("Macro tests", "tests/test_macros.py", "tests/test_macros.py", "tests/test_macros.py"),
    ("Rescue tests", "tests/test_a2ui_rescue.py", "tests/test_a2ui_rescue.py", "tests/test_a2ui_rescue.py"),
    ("Render suite", "docs/a2ui-1-0/tools/render_suite.py", "tools/render_suite.py", "tools/render_suite.py"),
]
FE = "frontend-react/src/"
for f in ["app/page.tsx", "app/layout.tsx", "app/globals.css", "app/api/copilotkit/[[...slug]]/route.ts",
          "components/A2UICustomCatalog.tsx", "components/A2uiMessages.tsx", "components/a2uiResult.ts",
          "components/CopilotProvider.tsx", "components/currency.tsx", "components/weather.tsx",
          "components/proverbs.tsx", "app/api/agentcore/route.ts"]:
    ROLES.append((f"UI {f}", FE + f, FE + f, FE + f))


def show(repo, path):
    r = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{path}"], capture_output=True)
    return r.stdout.decode() if r.returncode == 0 else None


def changed(a, b):
    n = 0
    for line in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0):
        if line.startswith(("+++", "---", "@@")):
            continue
        if line.startswith(("+", "-")):
            n += 1
    return n


def h(s):
    return hashlib.sha256(s.encode()).hexdigest()[:8] if s is not None else "-"


print("commits:", {k: subprocess.run(["git", "-C", str(v), "rev-parse", "--short", "HEAD"],
                                     capture_output=True, text=True).stdout.strip() for k, v in REPOS.items()})
print(f"| Role | GCP lines | AWS lines | Azure lines | AWS vs GCP changed | Azure vs GCP changed | AWS vs Azure changed | identical |")
print("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |")
tot = {"same3": 0, "roles": 0}
for role, g, a, z in ROLES:
    src = {"gcp": show(REPOS["gcp"], g), "aws": show(REPOS["aws"], a), "azure": show(REPOS["azure"], z)}
    lines = {k: (len(v.splitlines()) if v is not None else "-") for k, v in src.items()}
    def c(x, y):
        return changed(src[x], src[y]) if src[x] is not None and src[y] is not None else "-"
    hashes = {h(v) for v in src.values() if v is not None}
    present = sum(v is not None for v in src.values())
    ident = "all three" if present == 3 and len(hashes) == 1 else ("AWS = Azure" if src["aws"] and src["aws"] == src["azure"] else "")
    tot["roles"] += 1
    tot["same3"] += ident == "all three"
    print(f"| {role} | {lines['gcp']} | {lines['aws']} | {lines['azure']} | {c('gcp','aws')} | {c('gcp','azure')} | {c('aws','azure')} | {ident} |")
print(f"\n{tot['same3']} of {tot['roles']} roles byte-identical in all three repos")

# Roll-up: lines in roles byte-identical across all three, against each build's total over the listed roles.
shared = 0
total = {"gcp": 0, "aws": 0, "azure": 0}
for role, g, a, z in ROLES:
    src = {"gcp": show(REPOS["gcp"], g), "aws": show(REPOS["aws"], a), "azure": show(REPOS["azure"], z)}
    for k, v in src.items():
        if v is not None:
            total[k] += len(v.splitlines())
    if all(v is not None for v in src.values()) and len({h(v) for v in src.values()}) == 1:
        shared += len(src["gcp"].splitlines())
print(f"lines in byte-identical files: {shared}")
for k, v in total.items():
    print(f"{k}: {v} lines over the listed roles; byte-identical share {shared}/{v} = {100*shared/v:.0f}%")
