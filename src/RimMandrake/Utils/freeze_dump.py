#!/usr/bin/env python3
"""
freeze_dump.py — append a freeze entry to dumps/REGISTRY.jsonl. OWNER ONLY.

WHY THIS EXISTS. `refresh.py`'s own header has promised since 2026-08-20 that
"`--freeze` refuses without an explicit `--by owner`". There is no `--freeze` flag
in its argparse and there never was — so the one act the whole registry is built
around had no command behind it, and the owner would have been left hand-editing
an append-only JSONL by eye. Naming a capability is not handing it over.

⛔ IT REFUSES ANY SEAT BUT THE OWNER, and that is the point, not a formality. An
agent that re-freezes to clear a REPLACED warning silently moves the design target
everyone is authoring against — the exact failure dumps/README.md was written to
prevent.

🔑 It reads `capturedUtc`, `gameVersion` and the mod count OUT OF manifest.json
rather than taking them on the command line, because a freeze whose numbers were
typed by hand is a claim nobody measured.

    python3 src/RimMandrake/Utils/freeze_dump.py --by owner --note "..."
    python3 src/RimMandrake/Utils/freeze_dump.py            # dry run; prints, writes nothing
"""
import argparse, json, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
REGISTRY = os.path.join(ROOT, "infrastructure", "state", "dumps", "REGISTRY.jsonl")
DUMP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/DefDump")


def _dump_sha(dump):
    """sha of the mod set the CAPTURE saw, via refresh.py — never a second method."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import refresh
    except ImportError:
        return "see manifest.json"
    fp = refresh.dump_fingerprint(dump)
    return (fp or {}).get("hash") or "see manifest.json"


def _manifest(dump):
    p = os.path.join(dump, "manifest.json")
    if not os.path.exists(p):
        sys.exit("no manifest.json at %s — there is no capture to freeze." % p)
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _entries():
    if not os.path.exists(REGISTRY):
        return []
    out = []
    with open(REGISTRY, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                # ⚠️ REPORTED, never skipped. A registry that quietly drops a line
                # lets a frozen dump lose its immunity, and the symptom points
                # nowhere near the cause.
                sys.exit("REGISTRY.jsonl line %d is not valid JSON. Fix it by hand "
                         "before freezing; refusing to append past a broken line." % n)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--by", default="", help="must be exactly `owner`")
    ap.add_argument("--dump", default=DUMP)
    ap.add_argument("--id", default="", help="default OFFICIAL-<capture date>")
    ap.add_argument("--note", default="")
    ap.add_argument("--known-damage", default="",
                    help="what this capture is known to be missing; omit if clean")
    a = ap.parse_args()

    m = _manifest(a.dump)
    captured = m.get("capturedUtc") or m.get("captured") or ""
    if not captured:
        sys.exit("manifest.json carries no capturedUtc — refusing to freeze a "
                 "capture that cannot say when it was taken.")
    day = captured[:10]
    prior = [e for e in _entries() if e.get("kind") == "official"]
    cur = prior[-1] if prior else None

    if cur and cur.get("capturedUtc") == captured:
        sys.exit("OFFICIAL is already frozen at capturedUtc %s (%s). Nothing to do "
                 "— this capture IS the design target." % (captured, cur.get("id")))

    entry = {
        "id": a.id or "OFFICIAL-%s" % day,
        "kind": "official", "frozen": True,
        "modlist_count": m.get("modCount") or m.get("activeMods") or m.get("mods"),
        # 🔑 RECOMPUTABLE, and that is the whole point. OFFICIAL-2026-08-21 was frozen
        # with modlist_sha e0f11692cf69e516, which reproduces from NOTHING — not the
        # dump's own mod set (5ef6eec3daf6c325) and not the live load set
        # (49b83562b10df31c). A freeze is a claim about an artifact, and a claim
        # nobody can recompute cannot be checked, only believed.
        "modlist_sha": _dump_sha(a.dump),
        "path": "RimWorld by Ludeon Studios/DefDump",
        "by": "owner", "at": day, "capturedUtc": captured,
        "gameVersion": m.get("gameVersion", ""),
        "note": a.note or ("the design target — build to this. A differing live mod "
                           "count, greater OR lesser, is NOT staleness. Only the "
                           "owner re-freezes."),
    }
    if cur:
        entry["supersedes"] = cur.get("id")
    if a.known_damage:
        entry["knownDamage"] = a.known_damage

    line = json.dumps(entry)
    if a.by != "owner":
        print(line)
        print()
        print("DRY RUN — nothing written. Only the OWNER re-freezes: re-freezing is "
              "how the design target moves, and it must be a decision, not a way to "
              "clear a warning.")
        if cur:
            print("  current: %s  capturedUtc %s" % (cur.get("id"), cur.get("capturedUtc")))
            print("  on disk: %s%s" % (captured,
                  "   <- THESE DIFFER; refresh.py reports REPLACED" if cur.get("capturedUtc") != captured else ""))
        print()
        print("To write it:")
        print("  python3 src/RimMandrake/Utils/freeze_dump.py --by owner")
        return 1
    with open(REGISTRY, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print("froze %s at capturedUtc %s" % (entry["id"], captured))
    if cur:
        print("supersedes %s" % cur.get("id"))
    print("appended to %s" % REGISTRY)
    return 0


if __name__ == "__main__":
    sys.exit(main())
