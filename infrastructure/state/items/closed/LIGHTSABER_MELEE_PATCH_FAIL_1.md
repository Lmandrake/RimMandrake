# Armoury_MeleePower.xml's lightsaber PatchOperationSequence fails against the live lightsaber mod

## spec
`src/RimStarWars/Armoury/Patches/Armoury_MeleePower.xml` (mod display name
"Jawa Armoury Rebalance", packageId `mandrake.rsw.armoury`) has a
`PatchOperationFindMod` block (line 106) gated on
`Star Wars : The Force - Lightsaber` (`lee.theforce.lightsaber`, active),
wrapping a `PatchOperationSequence` of ~15 `PatchOperationReplace` calls
retuning `tools/li[label=...]/power` on `Force_Broadsaber`,
`Force_Darksaber`, `Force_LightsaberBase`, `Force_Lightsaber_Crossguard`,
`Force_Lightsaber_Curved` and others. Player.log logs the WHOLE
`PatchOperationFindMod` as `failed` (2 identical lines, confirmed present in
`Player-prev.log` too — pre-existing, NOT caused by tonight's
`WEAPONS_DONOR_RETIREMENT_1` work; unrelated donor, unrelated file).

## 2026-09-01 — diagnosed and fixed

**Root cause, confirmed by reading the live donor XML directly**
(`lee.theforce.lightsaber`, workshop `3466124712`,
`1.6/Defs/ThingDefs_Misc/Lightsaber.xml`): the donor mod restructured at
some point since this patch was generated. Today, exactly ONE `<tools>`
list exists in the entire file — on the abstract
`ThingDef Name="Force_LightsaberBase"` — and all 12 named variants
(`Force_Broadsaber`, `Force_Darksaber`, `Force_Lightsaber_Crossguard`,
`_Curved`, `_Custom`, `_Dual`, `_Inquisitor`, `_Shoto`, plus 3 more not
touched by this patch) have `ParentName="Force_LightsaberBase"` and declare
**no `<tools>` override of their own** — pure inheritance.

This patch's 21 `PatchOperationReplace` calls targeting
`/Defs/ThingDef[defName="Force_X"]/tools/li[label="..."]/power` were
therefore guaranteed 0-match on every one of the 7 non-base variants (7
variants × 3 tools) — RimWorld's XML patcher only sees a ThingDef's own
literal XML, never its inherited fields, so a Replace against a node that
exists only on the parent can never match. This was **not** one bad xpath;
it was the entire per-variant half of the block, all dead the same way.
Most of these were harmless no-ops even when they DID once match (their
comments show `X -> X`, e.g. `92 -> 92` — reasserting the same value,
implying the donor mod used to give each variant its own tools override
that mirrored the base, and later collapsed them all to pure inheritance).
The 3 operations targeting the base itself
(`[@Name="Force_LightsaberBase"]`) are real, unchanged tuning (`12 -> 15`,
`28 -> 35` ×2) and still match fine today.

**Fix applied**: removed the 21 dead per-variant operations, kept the 3
valid base-level ones, left an inline note (the file is generated,
"do not hand-edit" — same exception-with-a-note pattern used earlier
tonight on `WeaponTags_Renormalise.xml`, for the same reason: a safe
regenerate needs a pre-patch dump, and reconstructing a full defunct
per-variant `<tools>` override with the right `capacities`/`chanceFactor`/
`armorPenetration` for 7 weapons is real balance-design work, not a bug
fix — not attempted here). `validate_patch.py --defs` (Data + Mods +
Workshop): 0 errors, 0 warnings. Deployed
(`deploy_custom_mods.py --mod Armoury --apply`).

**Consequence worth flagging, not fixed here**: since the donor mod
dropped per-variant tools, all 7 named lightsaber variants now share the
SAME hilt/point/edge power (base's 15/35/35) regardless of what distinct
value each used to carry (Broadsaber 35, Darksaber 56, Crossguard 64,
etc.) — the original per-weapon tuning intent this file encoded is already
gone upstream, independent of anything this fix did. Restoring distinct
per-variant power would need a design call (worth the numbers again?) plus
a `PatchOperationAdd` of a full `<tools>` list per variant, not a Replace —
a follow-on item if the owner wants it back, not filed here.

## verify
`validate_patch.py --defs <Data> --defs <Mods> --defs <Workshop>`: done,
0 errors, 0 warnings. **Not yet cold-load-verified** — deployed but no
restart has happened since (defs only parse at startup); ride the next
restart for any reason and confirm zero `[Jawa Armoury Rebalance] Patch
operation ... failed` lines.

## 2026-09-01, second sitting — a twin bug in the SAME donor's OTHER file

The first restart to verify the `Armoury_MeleePower.xml` fix showed
`patch operations failed` drop from 7 to 6 (not to the 5 baseline) —
`Armour_Penetration.xml` has the exact same
`PatchOperationFindMod(Star Wars : The Force - Lightsaber)` gate wrapping
its own per-variant `armorPenetration` tuning, same root cause (8 variants
× 3 tools = 24 `PatchOperationConditional` blocks whose `nomatch` `Add`
targets a `tools/li[label=...]` that doesn't exist on any of them either).
`Force_ImbuedBlade` is NOT part of the dead set — it's a genuinely separate
weapon (`ParentName="BaseWeapon"`, not `Force_LightsaberBase`) with its own
real `<tools>` list, so its 3 armorPenetration ops still work. Removed the
24 dead blocks the same way, kept `Force_LightsaberBase`'s 3 (all target
`0.00`, lightsabers deliberately ignore armor per the file's own header
comment). `validate_patch.py`: 0 errors, 101 warnings. Deployed.

## criteria
- [x] Bad xpath(s) identified and fixed (or gated) — 21 dead operations in
      `Armoury_MeleePower.xml` removed (first pass) + 24 more in
      `Armour_Penetration.xml` (second pass, same donor mod, same root
      cause), the valid base-level ones kept in both, `validate_patch.py`
      clean on both files.
- [x] Cold-load confirms zero patch-failure lines for this mod — confirmed
      2026-09-01: `patch operations failed` back to baseline 5 (3 Intimacy +
      1 Mining Outpost + 1 Biomes! Caverns, all pre-existing/unrelated).
      Both files clean.
