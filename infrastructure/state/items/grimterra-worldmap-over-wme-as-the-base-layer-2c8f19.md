## spec
⚠️ **This is a mod-list change, so read `skills/rimworld-start-prep/SKILL.md`
first** — RimWorld, RimSort and Steam do not tell each other anything, and a
change made in the wrong order does not take.
(a) **ACTIVATE `GRimTerra.Worldmap`** — already subscribed at
    `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3546956014`.
    No Steam subscribe needed. ⚠️ It is **GRimTerra**, not GRiNDTerra, and it is
    NOT `grimterra.biomesmod` (3537211820), which is a different mod and already
    active — do not confuse them.
(b) 🔴 **KEEP `zal.worldmapenhanced` ACTIVE, loaded EARLIER than GRimTerra.**
    DECIDE ruling: WME is the base coat, GRimTerra is the top coat. RimWorld
    resolves textures per file and the later mod wins per file, so GRimTerra's 40
    PNGs win where it has an opinion and WME's 231 cover the rest. **Do not
    deactivate WME** — GRimTerra covers only 76.1% of our authored planet, and
    the 23.9% gap is Wasteland 7.8%, **Ocean 6.7%**, PoisonForest 2.9%,
    ZBiome_DesertOasis 2.1%, Lake 1.4% and five smaller. Without WME those render
    in VANILLA art, including every sea on the planet.
(c) **ORDER.** `GRimTerra.Worldmap` must load after `zylle.MoreVanillaBiomes`,
    `sarg.alphabiomes`, `grimterra.biomesmod`, `regrowth.botr.core` **and**
    `zal.worldmapenhanced`. Its two `<texture>` repoints (AridShrubland ->
    `World/Biomes/AridShrubland1`, Tundra -> `Tundra1`) target the same two fields
    ReGrowth's patch rewrites, and last patch applied wins.
(d) 🔴 **TURN OFF ReGrowth's `RG_WorldmapTextures`** — owner's explicit ruling.
    It defaults **True** and repoints AridShrubland and Tundra to ReGrowth's own
    art. AridShrubland is **9.1% of our planet**. ⚠️ **There is no config file to
    edit** — it is a ModSettingsFramework option under category
    `RG_RetexturesSettings`, has never been saved (no `RG_WorldmapTextures`
    anywhere in `Config\`), so it exists only as an in-game toggle. **This one
    needs the owner at the settings screen, or a bridge action.** Do not write a
    file and assume it took.

## verify
`ModsConfig.xml` lists `GRimTerra.Worldmap` and `zal.worldmapenhanced` both
active, with GRimTerra strictly later. Then confirm the ReGrowth setting reads
off at the settings screen.

## criteria
on the world map, ExtremeDesert / Desert / AridShrubland / AB_RockyCrags render
in GRimTerra's art, and Ocean / Wasteland / the oases still render in WME's
rather than vanilla's. Judged by LOOKING, per `the_one_map.md`.

## notes
**from:** DECIDE, 2026-08-19, on the owner's ruling *"Use GrindTerra, close out."* plus
*"[ReGrowth worldmap textures] Agreed, need to do this. Deactivate."*

**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20 — carried out by the OWNER, with one correction from BUILD.
He swapped the texture mods himself and asked for the new set to be recorded:
OUT `zal.worldmapenhanced` + the three `noxilie.regrow.wmb.*`; IN
`grimterra.terrainretexturemod` + `grimterra.worldmap`. 578 -> **576**, archived
as `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`.
⚠️ **(b) IS OVERTURNED BY THE OWNER'S OWN ACTION.** This item said KEEP
`zal.worldmapenhanced` as the base coat and NOT to deactivate it. He deactivated
it. His action is the later decision and it stands — but the measured consequence
recorded here should not be lost: GRimTerra covers **76.1%** of the authored
planet, so the remaining **23.9% now renders in VANILLA art** — Wasteland 7.8%,
**Ocean 6.7% (every sea on the planet)**, PoisonForest 2.9%, ZBiome_DesertOasis
2.1%, Lake 1.4% and five smaller. `grimterra.terrainretexturemod` is a TERRAIN
retexture and does not fill a world-map gap. ⇒ if the seas look vanilla when he
looks at the planet, this is why, and re-activating WME below GRimTerra is the
one-line fix.
🔴 **(c) WAS WRONG ON DISK AND BUILD FIXED IT.** `grimterra.worldmap` sat at
**442** with `regrowth.botr.core` at **460** — eighteen slots too early. ReGrowth
rewrites the same two `<texture>` fields GRimTerra repoints (AridShrubland,
Tundra) and **last patch applied wins**, so as ordered, ReGrowth won and
GRimTerra's repoint of AridShrubland — **9.1% of the planet** — was being
overwritten. Moved to 460, directly after ReGrowth at 459, and after
`sarg.alphabiomes` (50), `grimterra.biomesmod` (162) and `zylle.morevanillabiomes`
(234) as this item requires. Pre-change list archived as
`ModsConfig.PRESWAP.grimterra_order.xml`; undo is one move back.
⏭️ **(d) IS STILL OPEN AND IS THE OWNER'S**, unchanged: ReGrowth's
`RG_WorldmapTextures` defaults TRUE, has never been saved to any config file, and
exists only as an in-game toggle under `RG_RetexturesSettings`. It cannot be
written from outside. Removing the three `noxilie.regrow.wmb.*` mods did NOT
address it — those are separate mods from `regrowth.botr.core`, which is still
active at 459.
