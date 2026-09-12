#!/usr/bin/env python3
"""Retheme the embedded codebase-health page to the hub's brown palette.

The health generator ships a light :root palette; the hub is dark brown
(owner, 2026-09-12: the embedded tab must sit in the hub's colormap). The
page reads every color — treemap included — from CSS vars via col(), so
swapping the :root block rethemes it whole. Run after the health page
regenerates; the publish manifest points at the output.
"""
import pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parents[2] / "Transient/codebase_health_artifact.html"
OUT = HERE / "tabs/health.html"

HUB_ROOT = """--ground:#2A211A; --panel:#362B21; --ink:#EFE3D0; --ink-2:#B39C82; --ink-3:#8B8075;
  --rule:#4A3B2C; --rule-2:#3F3327;
  --red:#C4573B; --blue:#5B84A6; --green:#7FA65A; --grey:#8B8075; --unk:#D9A13B;
  --accent:#D98E32;
"""

s = SRC.read_text(encoding="utf-8")
new, n = re.subn(r"(:root\{)(.*?)(\})", lambda m: m.group(1) + HUB_ROOT + m.group(3), s, count=1, flags=re.S)
if n != 1:
    sys.exit("no :root block found — health page format changed, retheme by hand")
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(new, encoding="utf-8")
print(f"wrote {OUT} ({len(new)} bytes) — hub brown palette applied")
