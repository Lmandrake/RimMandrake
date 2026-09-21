# SWBESTIARY_UNPREFIXED_DONOR_DEFS_1 — donor names and dead bodies left in a shipping mod

## resolved — 2026-09-21, FOUNDRY

Re-measured both lists by parsing every XML under `src/` (`xml.etree.ElementTree`),
never by grep-and-assume. Re-measured counts differed from the filed estimate in
both directions, and the fix ended up bigger than "rename 7 defNames" once the
real reference graph was traced.

### Art-in-flight check (the item's own watch-out)

`infrastructure/artpipe/pending/` and `infrastructure/artpipe/active/` — zero
jobs mention any of `SWClaws`, `SWTailAttackTool`, `SWHornAttackTool`,
`SWLeftHoof`, `SWRightHoof`, `SWLeftArmClawAttackTool`,
`SWRightArmClawAttackTool`, `Bogwing`, `Dewback`, `FlyingAvian`, `Reek`,
`RSW_Mynock`. Clear to proceed. `MYNOCK_FLIGHT_ART_FIRST_1` (the item this one
said to check before touching `RSW_Mynock`'s body) is already CLOSED
(`c75ee26b8`) — its resolution gave the live `RSW_Mynock` ThingDef a vanilla
`Bird` body, not this file's `RSW_Mynock` BodyDef, so deleting the latter needed
no new coordination.

### What was actually true, once parsed (not what the item guessed)

**The un-prefixed BodyPartGroupDef/BodyPartDef names were not orphan-free
originals — they were UNDETECTED DUPLICATES of already-shipped, correctly
`RSW_`-prefixed defs from an earlier wave** (`RSW_MlieWaveB_BodyParts.xml`):
`SWClaws`/`SWTailAttackTool`/`SWHornAttackTool`/`SWLeftHoof`/`SWRightHoof`/
`SWLeftArmClawAttackTool`/`SWRightArmClawAttackTool` exactly duplicate
`RSW_SWClaws`/`RSW_SWTailAttackTool`/`RSW_SWHornAttackTool`/`RSW_SWLeftHoof`/
`RSW_SWRightHoof`/`RSW_SWLeftArmClawAttackTool`/`RSW_SWRightArmClawAttackTool`
(identical labels, identical fields). The item's title also said
"BodyPartDef/ToolCapacityDef-family" but only listed 7 BodyPartGroupDef names;
re-measuring found the file **also** carries 7 un-prefixed BodyPartDefs
(`SW_Club`, `SW_FrontHorn`, `SW_LeftHorn`, `SW_RightHorn`, `SW_RightWing`,
`SW_LeftWing`, `SW_DexterousTail` — "SW_" prefixed, not "RSW_") that are
likewise exact duplicates of `RSW_SW_Club`/`RSW_SW_FrontHorn`/etc. in the same
Wave-B file. The item's own **verify** criterion ("No defName in
`src/RimStarWars/SWBestiary/` lacks its tier prefix") is stricter than its
"what is wrong" list and catches these too, so they were fixed in the same
pass rather than left standing on a technicality.

Simply prefixing any of the 7 named BodyPartGroupDefs with `RSW_` (e.g.
`SWClaws` → `RSW_SWClaws`) would have **collided** with the pre-existing
Wave-B def of that exact name — a real collision, the same failure class the
item warns about. So the fix was **not** rename-in-place: it was delete the
duplicate and repoint every real reference at the pre-existing canonical name.

**`Bogwing` (bare, in `RSW_DesertPortA_Bodies.xml`) was the one genuinely
LIVE reference, not an orphan** — `RSW_Sketto.xml`'s `<body>Bogwing</body>`
resolves to it right now (confirmed via `jawa/get_defs` in the prior,
already-closed `SWBESTIARY_BODYPART_LIVE_VERIFY_1`, and via RimSage: zero defs
named `Bogwing` exist anywhere on the machine, so it is not vanilla Core —
`RSW_Sketto.xml`'s own header comment claiming "vanilla Core Bogwing body, no
port needed" was wrong, the same mistake already caught once for
`FlyingAvian`/`PekoPeko` in `RSW_MlieWaveC_Bodies.xml`). A correctly-prefixed
`RSW_Bogwing` BodyDef already exists (`RSW_MlieWaveC_Bodies.xml`, used live by
`RSW_Dactillion` and `RSW_Uvak`) with an identical body plan (same
`HeadAttackTool`/`Teeth`/`FrontLeftPaw`/`FrontRightPaw` groups `RSW_Sketto`'s
tools need). Fix: repoint `RSW_Sketto` to `RSW_Bogwing`, correct its stale
comment, delete the duplicate.

**`Dewback`, `Reek`, `RSW_Mynock`, `FlyingAvian`** (bare, in
`RSW_DesertPortA_Bodies.xml`) — confirmed genuinely orphaned by parsing every
`<body>` tag in every ThingDef under `src/`: the live races use differently
-named, already-`RSW_`-prefixed bodies from other waves (`RSW_Dewback` from
`RSW_MlieWaveB_Bodies.xml`, `RSW_Reek` from `RSW_MlieWaveC_Bodies.xml`,
`RSW_FlyingAvian` from `RSW_MlieWaveC_Bodies.xml`, and the live `RSW_Mynock`
ThingDef uses vanilla `Bird`). No ThingDef, PatchOperation xpath, or C# source
references any of the four. Deleted outright — no rename target needed since
nothing points at them.

**`RSW_DesertPortB_Bodies.xml`'s 19 `RSW_Body_*` BodyDefs** (re-measured as
**19, not 18** — the item's own count was relayed, not re-measured, and was
off by one) — all confirmed orphaned the same way: every live species
(`RSW_Cannok`, `RSW_Clodhopper`, `RSW_GraniteSlug`, `RSW_GreaterKraytDragon`,
`RSW_Horax`, `RSW_Jakobeast`, `RSW_KowakianMonkeyLizard`, `RSW_KraytDragon`,
`RSW_Krykna`, `RSW_Pikobis`, `RSW_Qormot`, `RSW_Shaak`, `RSW_Strill`,
`RSW_Varactyl`, `RSW_Voorpak`, `RSW_WarWyrm`, `RSW_Grank`) uses a
differently-named `RSW_<Name>` body from `RSW_MlieWaveC_Bodies.xml` instead of
this file's `RSW_Body_<Name>`; `RSW_Body_Bogwing`/`RSW_Body_FlyingAvian` have
no species consumer at all (those body plans are covered by `RSW_Bogwing`/
`RSW_FlyingAvian` in Wave C). The same file also carries **9 un-related but
equally dead BodyPartDefs** (`RSW_BodyPart_SW_Club`,
`RSW_BodyPart_SW_DexterousTail`, `RSW_BodyPart_SW_DorsalTentacle`,
`RSW_BodyPart_SW_LeftHorn`, `RSW_BodyPart_SW_LeftWing`,
`RSW_BodyPart_SW_RightHorn`, `RSW_BodyPart_SW_RightWing`,
`RSW_BodyPart_SW_SerpentTail`, `RSW_BodyPart_SW_Spikes` — a third naming
variant of the same Club/Horn/Wing concepts, already `RSW_`-prefixed so not a
naming violation, but referenced by nothing except the 19 orphaned BodyDefs
being deleted) — confirmed via the same full-`src/` parse and deleted
alongside them as dead weight.

No PatchOperation anywhere targets any of these defNames by xpath
(`grep`-checked for `BodyDef[defName="..."]` patterns across `src/`, zero
hits), and no `.cs` file references any of them as a string literal.

### What was done

1. `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Sketto.xml`:
   `<body>Bogwing</body>` → `<body>RSW_Bogwing</body>`; header comment
   corrected from the false "vanilla Core, no port needed" claim to the true
   provenance.
2. Deleted outright (every def inside was either a duplicate, now-repointed,
   or already dead; each file's ENTIRE content — confirmed by parsing root
   children — was one of these two categories, so nothing salvageable
   remained):
   - `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortA_Bodies.xml`
     (5 BodyDefs: `Dewback`, `Reek`, `Bogwing`, `RSW_Mynock`, `FlyingAvian`)
   - `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortA_BodyParts.xml`
     (7 BodyPartDef + 7 BodyPartGroupDef, all duplicates of Wave-B defs)
   - `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Bodies.xml`
     (19 BodyDef + 9 BodyPartDef, all duplicates of Wave-C defs or dead
     support parts for them)
3. Also moved `SWBESTIARY_MISSING_BODYPART_DEFS_1.md` to `items/closed/` —
   it was closed in the ledger (`9c2c5fe22`) but never moved, so the live
   `items/` glob was misstating it as open. Content-only correction, not a
   scope change on another seat's item.

### Left alone, and why

Nothing else in `src/RimStarWars/SWBestiary/` was touched. The un-prefixed
names outside this exact file pair (e.g. donor ThingDef names still bare in
`canCrossBreedWith` lists, documented and deliberately left as-is by prior
passes per the FeralGrazer/Pass-7 precedent) are out of this item's scope and
still correctly flagged where they already are.

### verify

- `validate_patch.py` static (no `--defs`): `RSW_Sketto.xml` — 0 errors, 0
  warnings. Whole-mod static sweep: pre-existing 96 errors (texPath/art
  placeholders in files this item never touched — `RSW_Anooba`, `RSW_Gizka`,
  etc.) are unchanged in kind and file, none newly introduced.
- `validate_patch.py --defs <Data> --defs <Mods> --defs <Workshop 294100>
  --mods-config <live ModsConfig.xml>` (the real load set): `RSW_Sketto.xml`
  — 0 errors. Whole-mod sweep: 23 pre-existing errors, none naming any
  defName touched by this item (`Bogwing`/`Dewback`/`Reek`/`FlyingAvian`/
  `RSW_Mynock`/`SWClaws`/etc. — all clean).
- `run_selftests.py`: see commit for the N/N result.
- No defName in `src/RimStarWars/SWBestiary/` still lacks its tier prefix
  from this pair of files; every surviving BodyDef in the mod is referenced
  by at least one ThingDef (confirmed by parsing, not grep).

## criteria

Nothing we ship can silently win or lose a name collision with a donor mod.
**Met**: the one live collision (`Bogwing` silently overriding an absent
donor def via last-loaded-wins) is gone — `RSW_Sketto` now points at the
one canonical, already-shipped `RSW_Bogwing`.
