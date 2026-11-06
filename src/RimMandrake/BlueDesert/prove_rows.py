"""Read a northstar_driver --out results file and exit 0 when every named row (`chain.component`) is PASS, 1 when any
is FAIL, 2 when any is missing or UNMEASURED. Used by BLUEDESERT_GPT_ENRICHMENT_1's live proofs A2 and A5, whose
driver run selects one chain with --chains (the other chains read 'chain not run', so the run's own exit is not
the clause's verdict).
    python3 src/RimMandrake/BlueDesert/prove_rows.py <results.json> cold_rack.rack_cools_loaded_room_only ...

A row the file lacks says MISSING, and the LAST line then says why, because the live tier keys its cause on that line
(relentless_live.exit_reason/cause): bare MISSING rows made a driver that refused on a half-loaded game and one that
refused on a site setting read as one cause on two games, a "proof or site defect"
(GAMEENV_FIX_PROOFSITE_22E336EE_ITEMS_WAIT: WASTELAND A2 at 08:56Z refused on a ZOMBIE game, passed 5/5 at 09:51Z).
  - the driver refused on a game-state preflight (RELOAD_PREFLIGHTS): `reload needed: ...`, so the tier restages;
  - it refused for any other reason: `UNMEASURED: the driver refused: <its refused field>`;
  - it ran but wrote no row of that id: `UNMEASURED: the results hold no row <ids>`.
"""
import json
import sys

# preflights whose FAIL says the running game is not a playable load: another load can change them, no proof edit can
RELOAD_PREFLIGHTS = ("game_loaded",)
RELOAD = "reload needed"            # relentless_live.RELOAD / asked_reload: the last line's prefix


def why_missing(doc, missing):
    """results doc, the ids it lacks -> the one line that says why (see the module doc)."""
    refused = str(doc.get("refused") or "").strip()
    if refused:
        bad = [p for p in doc.get("preflight") or [] if p.get("status") == "FAIL" and p.get("name") in RELOAD_PREFLIGHTS]
        if bad:
            return "%s: the driver refused on the running game: %s FAIL: %s (refused: %s)" % (
                RELOAD, bad[0]["name"], str(bad[0].get("evidence") or "")[:160], refused[:120])
        return "UNMEASURED: the driver refused: %s" % refused[:200]
    return "UNMEASURED: the results hold no row %s" % ", ".join(missing)[:200]


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as ex:
        print("UNMEASURED: results unreadable: %s" % ex)
        return 2
    rows = dict((r.get("id"), r) for r in doc.get("bars") or [])
    code, missing = 0, []
    for want in argv[2:]:
        r = rows.get(want)
        st = (r or {}).get("status")
        print("%-11s %s  %s" % (st or "MISSING", want, str((r or {}).get("evidence") or "")[:200]))
        if r is None:
            missing.append(want)
        if st == "FAIL":
            code = max(code, 1)
        elif st != "PASS":
            code = 2 if code == 0 else code
    if missing:
        print(why_missing(doc, missing))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
