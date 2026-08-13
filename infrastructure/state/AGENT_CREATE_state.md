# AGENT_CREATE_state.md — where CREATE is

**Cross-session address:** `uds:/run/user/1000/cc-socks/88223.sock`
_(Session started 2026-08-13 after the seat reboot that killed session `538`.)_

Identity: `infrastructure/agents/CREATE.md`, injected automatically. Queue: `infrastructure/state/queue/CREATE.md`.

---

## 0. 🔴 The ruling that reshaped my queue — owner, 2026-08-13

> **"Each mod that we fix art in should get its own fix patch, so we could in
> theory upload it for others to use."**

**One art-fix mod per DONOR mod.** Own `packageId`, `loadAfter` + `modDependencies`
naming the single donor, and an `About.xml` description documenting **every** file —
that text is the Workshop description a stranger reads, not a note to ourselves.
Doctrine written to `src/Jawa/README.md`; `106bc63`.

It answered four queue items at once (C3 closed, C5/C6 unblocked, C11 opened) and
**convicted an existing mod**: `MissingArtFixes` is one bucket spanning several
donors and must split. It is **live and deployed**, so unlike the sled that split
changes what the game loads.

## 1. Dog sled — FINISHED and now LOADABLE; only art review is left

All three facings built and validated PASS clean, each with a tint mask from known
geometry, in `src/Jawa/DesertVehicleReskin/`. Review sheet:
`Source/REVIEW_all_three.png` (original beside new, plus a true-in-game-size strip).
No facing mirrors another — south is head-on abreast, north is a rear view with no
snout and rigging down, east is a side profile with the pair stacked vertically and
rigging left.

✅ **The `About.xml` blocker is GONE** (`106bc63`): `mandrake.desertvehiclereskin`,
`loadAfter sarg.alphavehiclesneolithic` — packageId read off the donor at ws
`3028675048`, not taken from a doc. `deploy_custom_mods.py --mod
DesertVehicleReskin` now reports the packageId and `in sync (0 files, 7 held)`; the
old **"no packageId in About.xml"** flag no longer fires.

⏳ **Held for ONE reason now: the owner has not reviewed the art.** `DEPLOY_HOLD.txt`
says exactly that, so the next reader knows approval is the only thing left.

⚠️ **`loadAfter` is load-bearing here and was nearly missed.** Alpha Vehicles
Neolithic ships its vehicle art as **loose PNGs**, and between two loose files at
one path RimWorld resolves by load order — so without that line the donor's own art
wins and the reskin is invisible. That is the **opposite** of `MissingArtFixes`,
whose donors bundle their art in AssetBundles, where a loose file wins regardless of
order. The two cases look identical and are not.

**Still owed: 4 of 5 vehicles** — Chariot, WarChariot, CoveredCarriage, OxCart.
Geometry already measured in `Source/GEOMETRY.md`, so this is execution, not
investigation. 24 PNGs (4 × 3 facings × art+mask). Source art:
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3028675048\Textures\Things\Vehicles\Land\Tier0\`
— one folder per vehicle, each `AV_<Name>_{north,south,east}.png` plus `…m.png`
masks. ⚠️ Mask suffix is `AV_DogSled_southm.png`, **not** `_south_m.png`.

⚠️ **The donor's own `About.xml` says 11 vehicles; `TODO_v2.md` §0c says 12.** Not
resolved, does not affect the reskin (only 5 have an animal), but do not quote 12 as
measured.

## 2. Gravship — build-ready; the radius question is CLOSED, offline

`design/Jawa/worldbuilding/ship_build/ship_bridge.json`, regenerated `--center 250,250`.
Origin +81,+57, hull 86×133 at x82–167 / z58–190. One foundation call laying 4,057
cells, 4 terrain, 26 spawn, 1,053 things. Selftest ALL PASS; BRIDGE rehearsed it on
a scratch map, 1,045/1,045 in 5.6 s.

✅ **Open question 1 is ANSWERED — see queue C4.** 34/30/12/85 match the stored
config floats exactly; the solver is right. **The def literals disagree by design**
(Odyssey 16.9 → VGE 12.9 → Bigger Gravships stamps it from C# after all XML
patching, winning regardless of load order), so "verify the radius against the def"
is not a check that can be run. BRIDGE's owed `get_def GravFieldExtender` drops to
confirmatory (`infrastructure/state/queue/BRIDGE.md` B3).

🔴 **What that pass actually caught:** `src/RimMandrake/mapsynth/ship_designs.py` claimed
`EXT_SUPPORT = 500` came from the settings file. **That key does not exist there** —
500 is Bigger Gravships' compiled default. Right value, wrong reason, and at VGE's
100 or vanilla's 250 the cap would have been below the 4,057-tile hull and the build
would have failed on *capacity* with every radius correct.

⚠️ **It flies only on the owner's mod settings** (34/30/12/85). Bigger Gravships'
own defaults are 25.9/25.9/8/25.9 — needs reach 74.46, defaults give 51.80. If that
config is lost or "Restore Mod Defaults" is clicked, the design silently stops being
liftable and **nothing logs it.**
⚠️ **Margin is 0.28 of a cell**: extender (56,8) sits at 84.72 against the 85 cap.

**Open question 2 stands:** two heatsinks held back as footprint conflicts —
(26,126) Mincer and (66,126) Neutro Synth, both HOT wings. Fixing regenerates
`build_sheet_15.json`, trips BRIDGE's `SHEET_SHA256` pin and moves five machines to
sorted orientation. **The ship builds with 6 of 8 meanwhile.**

⚠️ `design/Jawa/worldbuilding/` now belongs to **VISION** — ship *design* is no longer CREATE's;
CREATE builds from spec. `player_maps/` is still CREATE's.

## 3. What is owed, in the order the v1 gate wants it

**I own four of the eight burn-down rows** (`V1_SCOPE.md`), and **two close offline**:

| row | state | blocked on |
|---|---|---|
| 3 · one `QuestScriptDef` that fires | ⬜ **literal 0** — grepped, no `QuestScriptDef` anywhere in `src/` | nothing |
| 4 · three terrain/resource overrides | ⬜ **literal 0** — no authored `TerrainDef` | nothing |
| 8 · gravship, DEEP | design complete, build 0 | wants the game; I anchor that session |
| 1 · Empire reskin | ✅ seen live | done |

⚠️ **Rows 3 and 4 are at zero because nobody saw they were closable**, not because
they are hard. Both pure XML. **Author offline, deploy with row 2, verify in ONE
session** — never one row per load at ~23–30 min.

🟡 **Unanswered by the owner: which I build first** — rows 3+4, or the 4 remaining
Bantha vehicles they reassigned me overnight (`TODO_v2.md` §0c), or `check_sprite.py`
(C8) first so every later vehicle validates for free. I asked; the answer did not
land before the wrap. **Ask again rather than picking** — the reassignment was the
owner's call and rows 3+4 are v1.

## Art facts worth keeping — not in any skill or traps file

- **Cerean sibling registration:** in every healthy pair (Long, Pony, Male/Female
  head) the south shares the north's x-range and top edge and is only shorter.
  **Measure the sibling set before drawing a missing facing.**
- **Byte-identical facings exist:** `CereanTuft_east` and `CereanTuft_south` are
  identical files — the donor reuses one facing for that style. **Hash the sibling
  set before assuming a missing facing needs drawing.**
- **Loose beats bundled, order beats loose.** A loose PNG overrides an AssetBundle
  asset at the same path *regardless of load order*; between two loose files, load
  order decides. **So whether `loadAfter` is required depends on how the donor
  ships its art**, and you cannot tell by looking at the path.
- **`bodySize` is a gameplay MASS stat and says nothing about sprite proportions.**
  The Massiff/Eopie call went the other way once measured on pixels (0.720 vs
  0.618 against a 0.57 slot). Same failure shape as reading a def and inferring
  what the renderer does.
