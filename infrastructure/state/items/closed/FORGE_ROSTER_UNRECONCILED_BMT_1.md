# FORGE_ROSTER_UNRECONCILED_BMT_1 — four rosters still name a retired donor, and the Forge is the worst

## what is wrong

Found 2026-09-21 while assessing `ROT_ROSTER_DEAD_DONOR_NAMES_1`
(`Transient/dead_roster_refs_assessment.md`, `cbd2deb85`). Four biome roster JSONs still
carry `BMT_` names from **Biomes! Caverns**, with **zero live wiring**:

| roster | unreconciled `BMT_` names |
|---|---:|
| **`RUT_TheForge`** | **27** |
| `RUT_Miasma` | 10 |
| `RUT_FeverWood` | 9 |
| `RUT_Greentide` | 3 |

`biomesteam.biomescaverns` is **confirmed NOT in the active mod list** (parsed, not
scanned). So these name species that cannot spawn.

## 🔑 read the Rot's assessment before touching any of them

The Rot had the identical shape, and the answer there was **not** what it looked like:
**51% of its whole roster was species we ALREADY OWN under `RSW_` names and had simply
never wired.** Only ONE row was a genuine port-or-drop call.

⇒ ⛔ **Do not commission ports for these 49 names.** Check ownership first, exactly as
the Rot assessment did. ⚠️ Many donor species were ported under **renamed** defNames, so a
`RSW_<donorName>` prefix test **cannot find them** — the mapping lives in source comments
like `<!-- AA_Cactipine -> RSW_Spinerat -->` under
`src/RimStarWars/SWBestiary/Defs/DesertPort/`. A false "we don't own this" commissions work
already done.

Two further classes the Rot turned up, both worth checking for here:
- rows **already ruled** elsewhere and merely stale in the JSON (the Rot had `BMT_GlowBat`,
  ruled CUT by the owner 2026-09-10) — ⛔ re-porting one throws his ruling away;
- rows **already moved** to another biome under our name (`BMT_BovineBeetle` →
  `RSW_BovineBeetle`, "grabber", in the Lantern Deeps).

## spec

For each of the 49 names, in the Rot's pattern: is it already owned (under any name)?
already ruled? already moved? If none of those, it is a real port-or-drop call for the
owner. Produce the same table shape, then wire what we own.

## verify

Every `BMT_` name in the four rosters is either wired to an owned def, removed with a
recorded reason, or listed as an owner decision. No roster's *effective* composition
differs silently from its written one.

## criteria

`RUT_TheForge`, `RUT_Miasma`, `RUT_FeverWood` and `RUT_Greentide` play the roster they
declare.
