## spec
The def dump changed layout — it is now `DefDump/captures/<ISO>/{defs/,manifest.json,animals.json}`
plus a top-level `defs.sqlite` — and **at least two tools still expect the old
`DefDump/defs/*.json` root**. Both fail in the worst way: they report something that reads as
a real finding about the game.

| tool | what it does when pointed at the DefDump ROOT | truth |
|---|---|---|
| `src/RimMandrake/Utils/cast_to_xml.py` | `FAIL: no TraitDef.json at …` and exits | the tool is fine; it wants `captures/<id>/defs` |
| `skills/rimworld-modding/scripts/validate_patch.py --live` | prints `no defs/ under …DefDump; live checks skipped` and **passes the patch anyway** | 🔴 the `--live` half of every verification silently did not run |

🔴 **The second one is the dangerous one.** Several queue items specify verification as
*"validate with BOTH `--defs` and `--live`"*. Pointed at the root, `--live` degrades to a
one-line notice in a wall of output and the run still ends `OK - 0 errors`. **Every `--live`
check run against the root since the layout changed proved less than its author thought**,
including one in this session (`HORROR_WASTES_COLD_TERRAIN_1`, worked around by querying
`defs.sqlite` by hand).

## fix
Teach both tools to resolve a DefDump root to its newest capture — `captures/*/defs`, picking
the highest ISO name — and to say which capture they chose. ⛔ **Do not just fix the call
sites.** The next person will pass the root too; the root is the obvious thing to pass.

⚠️ **Choosing the NEWEST capture is not automatically right.** Measured 2026-08-23: the newest
capture, `2026-08-23T07-12-04Z`, was taken with the Star Wars donor mods switched OFF, which is
why `gen_races_mod.py` refuses to write (it would ship 63 species against 69 on disk). A
resolver must report the capture's `modCount` and let the caller refuse it, not silently pick
the latest. The known-good full capture today is `2026-08-21T22-44-59Z` at 578 mods.

## verify
- `python3 src/RimMandrake/Utils/cast_to_xml.py --dump "<DefDump root>"` runs and names the capture it used.
- `validate_patch.py --live "<DefDump root>"` performs live checks, and **says so**, rather than skipping.
- 🔑 A deliberately wrong defName in a test patch is CAUGHT by `--live`. That is the only proof the live half ran.

## criteria
- [ ] Both tools accept the DefDump root and resolve it to a capture.
- [ ] Each prints the capture id and its modCount.
- [ ] `--live` never skips silently: no capture found must be a loud refusal, not a notice.

## Watch out
⚠️ **`defs.sqlite` is a THIRD shape**, and it is not a drop-in for either — it does not
serialise `Vector2`/`Color` (`drawSize`, `colorSpectrum` read null), nor dictionary-keyed
custom fields (`wildBiomes`, `wildPlants`, `terrainsByFertility` all read null), nor
`TerrainDef` bodies. Anything needing those must read the mod XML on disk.

---

## ⬅ HALF DONE 2026-08-23 by BUILD — `validate_patch.py` is fixed; `cast_to_xml.py` is not

✅ **`skills/rimworld-modding/scripts/validate_patch.py --live` now:**
- resolves a DefDump ROOT to its newest `captures/<ISO>/defs` and **prints which one**;
- when it cannot, prints `ERROR   --live: ... LIVE CHECKS DID NOT RUN` and the summary line
  says an `OK` covers the `--defs` half only — it no longer degrades to a quiet notice;
- **compares the capture's `modCount` against live `ModsConfig.xml` `activeMods` and warns.**
  Measured on the fix: `the live dump holds 578 mods but ModsConfig.xml now lists 580 active`.
  That is the reading that matters — the fingerprint is the mod set, not the clock.

⛔ **`cast_to_xml.py` still needs `--dump <capture>/defs`.** It fails loudly (`no TraitDef.json`),
which is the safe direction, so it was left for this item rather than fixed blind.

## 🔴 CORRECTION — `gen_races_mod.py`'s stated cause is WRONG, and it was repeated

`gen_races_mod.py` refuses to write with: *"the dump ... was captured with the donors switched
off, so their xenotypes are absent."* **Measured 2026-08-23: that is false.** All three
captures contain the guy762 donor xenotypes —

    2026-08-21T22-44-59Z  XenotypeDef.json  446,272 bytes, guy762_* present
    2026-08-23T05-05-29Z  XenotypeDef.json  447,124 bytes, guy762_* present
    2026-08-23T07-12-04Z  XenotypeDef.json  447,133 bytes, guy762_* present

— and all three report `modCount 578`. ⇒ **The 63-vs-69 shortfall has some other cause**, and
`pick_species` is still where to look, but "the donors are missing from the dump" is not it and
chasing that will waste the time.

⚠️ **This was repeated in good faith into `RACES_GENERATOR_DIVERGED_1` and into commit
`9ede4d4c`'s message**, both of which say Option 1 is blocked on re-taking a dump with the
donors active. **It is not.** The refusal is real and the guard is right to fire; only the
explanation is wrong. Diagnose it from `pick_species` directly.

---

# ✅ CLOSED 2026-08-23 — both tools now take a DefDump ROOT

`cast_to_xml.py` joins `validate_patch.py`. It resolves a root to its newest
`captures/<ISO>/defs`, **prints the capture and its modCount** (`dump:
captures/2026-08-23T07-12-04Z, 578 mods`), and works with `--dump <root>`, `--dump
<capture>/defs`, or no `--dump` at all.

🔑 **Resolved ONCE at the call site, not inside each loader.** The first attempt put it in
`load_traits`, and `load_skills` then went straight back to looking in the unresolved root —
`no SkillDef.json`. A per-consumer fix for a per-invocation problem leaves exactly as many
holes as there are consumers.

⚠️ The two tools still fail differently and that asymmetry is deliberate: `cast_to_xml.py`
DIES when it cannot find a dump, `validate_patch.py` now raises an ERROR that taints its
summary. Both are loud. The bug being closed was that one of them used to be silent and
still printed `OK`.

Verified: a full `--write` over all 12 cast rosters is a **NO-OP**.
