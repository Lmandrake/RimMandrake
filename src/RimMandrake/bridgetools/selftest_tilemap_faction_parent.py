#!/usr/bin/env python3
"""selftest_tilemap_faction_parent.py - jawa/world_tile_map_generate never makes a factionless Settlement.

TILEMAP_GENERATE_FIX_FACTIONLESS_PARENT, measured live 2026-10-24: with the default
suggestedMapParent=Settlement on a tile with no MapParent, GetOrGenerateMap added a Settlement
with NO faction - a Base_Faction ruin map (~110 hostile pawns) and a NullReferenceException per
frame drawing it on the world layer. The fix creates a Settlement-class parent itself, with a
resolved faction (default Player), BEFORE GetOrGenerateMap, and refuses an empty or unknown one.

The behaviour needs a running game; this pins the SOURCE shape offline (the companion is
compiled by build.py, which needs Windows dotnet). Mutation probes prove each check can fail.
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "JawaBench.BridgeTools" / "JawaBenchSocietyTools.cs"


def method_body(text: str) -> str:
    start = text.index("public static async Task<object> WorldTileMapGenerate(")
    end = text.find("[Tool(", start)
    return text[start:end if end > 0 else len(text)]


def problems(body: str) -> list[str]:
    out = []
    sig = body[: body.index("{")]
    if not re.search(r'string\s+faction\s*=\s*"Player"', sig):
        out.append("no 'faction' parameter defaulting to \"Player\"")
    gen = body.find("GetOrGenerateMapUtility.GetOrGenerateMap(")
    dry = body.find("if (dryRun)")
    if gen < 0 or dry < 0:
        return out + ["GetOrGenerateMap call or dryRun branch not found"]
    pre = body[:gen]
    if "typeof(Settlement).IsAssignableFrom" not in pre:
        out.append("no Settlement-class test before GetOrGenerateMap")
    if "MapParentAt(" not in pre:
        out.append("no standing-MapParent check before GetOrGenerateMap")
    if not ("SettleUtility.AddNewHome(pt, parentFac)" in pre and ".SetFaction(parentFac)" in pre):
        out.append("parent is not created WITH the resolved faction before GetOrGenerateMap")
    head = body[:dry]
    if "'faction' is empty" not in head:
        out.append("empty faction is not refused before the dryRun return")
    if "No FactionDef '" not in head:
        out.append("unknown FactionDef is not refused before the dryRun return")
    if "parentFaction" not in body[gen:]:
        out.append("result does not report parentFaction")
    return out


def main() -> int:
    body = method_body(SRC.read_text(encoding="utf-8"))
    bad = problems(body)
    for p in bad:
        print("FAIL", p)
    # sanity probes: each mutation of the fix must be caught, or the checks are blind
    mutations = {
        "default_faction_dropped": body.replace('string faction = "Player"', 'string faction = ""'),
        "faction_not_set": body.replace(".SetFaction(parentFac)", "").replace("SettleUtility.AddNewHome(pt, parentFac)", ""),
        "class_test_dropped": body.replace("typeof(Settlement).IsAssignableFrom", "true || X"),
        "empty_refusal_dropped": body.replace("'faction' is empty", "faction blank"),
    }
    for name, m in mutations.items():
        if m == body or not problems(m):
            print("FAIL probe", name, "not detected")
            bad.append(name)
    if bad:
        return 1
    print("PASS world_tile_map_generate creates a Settlement parent with a faction (default Player); 4 probes caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
