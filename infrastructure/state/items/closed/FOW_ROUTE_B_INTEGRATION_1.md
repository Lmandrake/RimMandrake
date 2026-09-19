# Route B fog-of-war integration — CAI combat AI + NWN fog, S&D dropped

Filed thin (no spec/verify/criteria) — FOUNDRY decided the shape below and
proceeded per CHARTER (*"the filer may know something you do not... decide it
yourself and write down what you chose"*). Full evidence trail:
`design/Jawa/mods/cai_fog_deep_dive_2026-08-31.md`.

## spec
Enable `Krkr.rule56` ([1.6] CAI 5000) + `Mlie.NWNRealFogOfWar` on the live mod
list, CAI's own fog toggle **off** so NWN drives fog (the owner-ruled Route B),
drop `memegoddess.searchanddestroy` (documented CAI incompatibility, #86).
Load order: both after `Ludeon.RimWorld[.Royalty/.Odyssey]` and `brrainz.harmony`
(CAI's declared `loadAfter`), placed right after the DLCs and before content
mods — satisfies the constraint without contending for "load at end".

## verify
- **Minimal-list quicktest** (21-mod FoW test list: the 19-mod minimal set +
  both new mods), two independent cold boots: zero `combatai|krkr|nwnrealfogofwar|realfow`
  exceptions in `Player.log` either time. Pre-existing droidworks/OuterRimCore
  errors unrelated to this item were present on both and are not this item's.
- **Fog visuals**: screenshot evidence — NWN's own "Not visible area" overlay
  renders (smooth diagonal fog front), not CAI's 16×16 blocky shader,
  consistent with CAI fog off / NWN driving.
- **Combat AI**: 3 debug-spawned `Pirate`s pathed ~9 tiles toward the colony
  over 2000 stepped ticks, no CAI errors. `jawa/fire_raid` itself produced
  zero arrivals on this quicktest world — a known bridge trap
  (`skills/rimbridge/references/traps.md`), not a Route B defect; direct
  debug-spawn substituted.
- **Full-list ride**: the owner's live mod list (592 → 593: + CAI + NWN − S&D),
  ordered the same way, written to `ModsConfig.xml` and updated into
  `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (was stale at 585
  — now matches what was actually live before this item touched it, plus
  Route B). FOUNDRY cold-booted the full 593-mod list to confirm before
  handoff — see `notes` for the result.

## criteria
- [x] CAI + NWN active, S&D inactive, on both the test list and the live list.
- [x] Two clean minimal-list boots, no CAI/NWN/Krkr exceptions.
- [x] Fog visibly renders (NWN's system, not CAI's).
- [x] CAI's combat AI observed actively pathing hostiles.
- [x] Full 593-mod list boots clean — cold-booted, bridge up, zero
      `combatai|krkr|nwnrealfogofwar|realfow` errors, no `incompatib*` warning.
      The 64 error/exception lines present are all pre-existing (signs,
      translation report, PregnancyUtility/Jewelry patches, etc.) — none name
      CAI, NWN or Route B.

## notes

### 🔴 Open finding for whoever builds the dive lamp — not this item's to close
`CompProperties_Sighter` (CAI's fixed-radius reveal comp — the mechanism the
underwater lamp-cone plan named) did not visibly reveal fog around a spawned
`CombatAI_TribalPoleCCTV` with CAI's fog off. Two explanations, neither ruled
out: (a) Sighter's reveal only runs through CAI's own `MapComponent_FogGrid`,
which doesn't run when `FogOfWar.Enable` is false — i.e. it may be inert
exactly when Route B is active; or (b) the freshly spawned building had 0 fuel
(`CompProperties_Refuelable`) and wasn't "in use" yet. **Not chased further —
`depths_build_spec_v1.md` §0.2 already routes the lamp-cone through NWN's own
glow model instead of Sighter**, so this doesn't block anything; it just means
Sighter is unproven, not proven, under Route B. Settle (a) vs (b) first if
anyone still wants to lean on it.

### CAI's fog-off setting — inferred, not Scribe-confirmed
`FogOfWar_Enabled.15` was added to `Mod_3673768803_CombatAIMod.xml` set to
`False`. The field name was read off the DLL's own string table (exact match,
same `FogOfWar_<Attribute>` family as the three fields the default-settings
dump already wrote) — not confirmed by reading a live C# field back through
the bridge, since no reflection tool exists on it. The two clean boots plus
the NWN-style fog rendering (screenshot) are consistent with CAI's fog engine
being off; nothing observed contradicts it.

### The `ModsConfig.FULL.LATEST.xml` snapshot was stale before this item
592 active mods were live but the stored `FULL.LATEST.xml` (the file
`modlist_swap.py --restore` uses) still held 585 — a 7-mod drift from before
this item, unrelated to it. Refreshed as a side effect of building the Route B
full-list config, since the correct base for that config was "the owner's
current 592", not the stale snapshot.
