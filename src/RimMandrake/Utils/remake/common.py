"""Shared readers for the remake gate tools: a ModsConfig profile, a def-dump capture, mod roots."""
import json
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
MODLISTS = os.path.join(REPO, "infrastructure/state/modlists")
PAINT_DEFAULT = os.path.join(MODLISTS, "ModsConfig.PAINT.RULED_2026-10-20.xml")
sys.path.insert(0, os.path.dirname(HERE))


def default_dump():
    try:
        import game_paths
        return game_paths.DEF_DUMP
    except Exception:
        return None


def wsl(p):
    """Windows path from a capture manifest -> WSL path; WSL/relative paths pass through."""
    if len(p) > 2 and p[1] == ":":
        return "/mnt/" + p[0].lower() + "/" + p[3:].replace("\\", "/")
    return p


def load_profile(path):
    return [li.text.strip().lower() for li in ET.parse(path).getroot().find("activeMods") if li.text]


def load_capture(dump):
    """(manifest, roots{pkg: wsl root}) of a def-dump capture."""
    man = json.load(open(os.path.join(dump, "manifest.json")))
    roots = {m["packageId"].lower(): wsl(m.get("rootDir") or "") for m in man["mods"]}
    return man, roots


def load_defs(dump, def_type):
    p = os.path.join(dump, "defs", def_type + ".json")
    if not os.path.isfile(p):
        return []
    return json.load(open(p)).get("defs", [])


def iter_def_files(dump):
    d = os.path.join(dump, "defs")
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            yield os.path.join(d, f)


def is_core(pkg):
    return pkg.startswith("ludeon.")
