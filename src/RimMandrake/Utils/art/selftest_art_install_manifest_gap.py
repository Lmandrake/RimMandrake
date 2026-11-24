#!/usr/bin/env python3
"""SELFTEST_FIX_GSS_ART_MANIFEST_SIZES_SLAT class guard: `art install` of a Gimme Some Slack texture that
gss_art_manifest.py has no rule for reports it at install time (not at night). A ruled texture, and any other mod,
stay silent. Reads the real manifest rules; plants only the rel names (nothing is written)."""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import artledger as L

# `--against <git rev>`: run the same checks on that revision's artledger.py (the class-guard replay: the fault
# instance is the tree before the guard landed; `rimflow guard ... --instance "--against <rev>"` shows it red there).
if "--against" in sys.argv:
    import subprocess, tempfile, importlib.util as _iu
    _rev = sys.argv[sys.argv.index("--against") + 1]
    _src = subprocess.run(["git", "-C", str(L.REPO_ROOT), "show", f"{_rev}:src/RimMandrake/Utils/art/artledger.py"],
                          capture_output=True, text=True, check=True).stdout
    _src = _src.replace("REPO_ROOT = Path(__file__).resolve().parents[4]", f"REPO_ROOT = Path({str(L.REPO_ROOT)!r})")
    _tmp = Path(tempfile.mkdtemp()) / "artledger_old.py"
    _tmp.write_text(_src)
    _sp = _iu.spec_from_file_location("artledger_old", _tmp)
    _R = L.REPO_ROOT
    L = _iu.module_from_spec(_sp); _sp.loader.exec_module(L)
    L.REPO_ROOT = _R

FAILS = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


G, F = "src/RimMandrake/GimmeSomeSlack", "src/RimMandrake/FlowWorks"
# a rule exists today: a real shipped texture, discovered not named
import importlib.util
mp = L.REPO_ROOT / "src/RimMandrake/GimmeSomeSlack/review/gss_art_manifest.py"
sp = importlib.util.spec_from_file_location("m", mp); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
ruled = [f.relative_to(M.GSS_TEX).as_posix() for f in sorted(M.GSS_TEX.rglob("*.png"))]
ruled = [r for r in ruled if M.classify_gss(r) and M.classify_gss(r)[0] in M.PARTS]
check(len(ruled) > 20, f"read {len(ruled)} shipped ruled GSS textures")
if not hasattr(L, "manifest_rule_gap"):
    check(False, "artledger has no manifest_rule_gap: `art install` cannot report a texture with no manifest rule")
    print(f"{len(FAILS)} FAIL"); sys.exit(1)
bad = [r for r in ruled if L.manifest_rule_gap(G, r)]
check(not bad, f"every shipped ruled texture passes the guard (worst: {bad[:1]}; {len(ruled)} read)")
# planted: no rule
for rel in ("RimMandrake/GimmeSomeSlack/ZzNoRulePart_north.png", "RimMandrake/GimmeSomeSlack/Styles/Modern/ZzNoRule.png",
            "RimMandrake/GimmeSomeSlack/Aerial/ZzNoRule.png"):
    msg = L.manifest_rule_gap(G, rel)
    check(bool(msg) and "ZzNoRule" in msg and "PARTS" in msg, f"unruled {rel} is reported with the rule to add")
check(bool(L.manifest_rule_gap(F, "RimMandrake/FlowWorks/Hose/ZzNoRule.png")), "unruled FlowWorks Hose texture is reported")
# must stay green: other mods and non-manifest folders
check(L.manifest_rule_gap("src/RimMandrake/Other", "RimMandrake/GimmeSomeSlack/ZzNoRule.png") is None, "another mod is not checked")
check(L.manifest_rule_gap(F, "RimMandrake/FlowWorks/Things/ZzNoRule.png") is None, "FlowWorks non-Hose art is not checked")
check(L.manifest_rule_gap(G, "RimMandrake/GimmeSomeSlack/ConduitTransparent.png") is None, "a rule that classifies as 'nothing to judge' passes")
print(f"{len(FAILS)} FAIL")
sys.exit(1 if FAILS else 0)
