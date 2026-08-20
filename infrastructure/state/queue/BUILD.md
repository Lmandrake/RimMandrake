# BUILD inbox.

## 🔴 OWNER RULINGS, 2026-08-19 — the queue triage, taken in the BUILD window

Eight rulings, given as a Q/A walkthrough of every live item. They supersede any
line below that says otherwise.

1. **The worlds on disk are THROWAWAY and the freeze is STILL AHEAD.** `world/WORLDMAP_gen.rws`
   (seed `pumpkin`) and `world/WORLDMAP_sub7b_source.rws` (seed `consortium`) are both
   `TidallyLocked` and both carry the seven Jawa factions — and **none of that counts.**
   Owner: *"Neither — still iterating."* ⇒ nothing has expired by being already-in-a-save,
   and every bake-at-world-creation deadline is in front of us, not behind.
2. **Bake-in correctness FIRST**, ahead of the roster, the faith text and the deploys.
3. **The roster is ALL ELEVEN FACTIONS. No cuts.** B40–B52 all stand.
4. 🔴 **B53 is built ALONGSIDE the roster, not after worldgen** — this REVERSES the
   2026-08-15 "SEQUENCED AFTER WORLDGEN" ruling recorded on that item. Reason accepted by
   the owner: pawn kinds and FactionDefs reference each other, so building them together
   avoids authoring every `pawnGroupMaker` twice.
5. **B54 is all eleven faiths, before the freeze.** Not player-faith-only, not a named few.
6. **The painter wins: biome-GENERATION edits are void, the runtime weather half stands.**
   Independently identical to DECIDE's D29, landed in `44cdb94` while this walkthrough was
   running. ⇒ `cut-the-boiling-biome-reference-4e2b90` is VOID by the same logic.
7. **B58 and B55 both move.** B55's world-independent half is unblocked; B58's
   `Jawa_Patches` half is owed and needs no game.
8. **The batched deploy pass runs** — it unblocks CHECK's D-CHK2 generator fix.

### ⛔ Messaging, restated by the owner in his own words, 2026-08-19

*"All that was meant is that Agents should not talk to each other. The User may send out
messages and be heard by Agents, but that is all (`/broadcast` skill). Sub-agents should
function normally."*

🔑 **`.claude/settings.json` ALREADY implements this and MUST NOT be "corrected".**
`crossSessionInbound: "accept"` is **deliberate and load-bearing** — `broadcast.py` reaches
windows through that same inbound path, so flipping it to `"refuse"` would silence the
OWNER's own game-state announcements, which are the one thing that is supposed to get
through. The outbound half is what enforces the ruling: `permissions.deny` lists
`SendMessage` and `ListAgents`, so no agent here can send to a peer.
⚠️ **`CLAUDE.md`, `POLICY.md` and the four seat files all claim the setting is `"refuse"`.
They are WRONG about the config, right about the intent.** Do not edit the setting to match
the docs; the docs get fixed.
✅ **Subagents are unaffected and fully authorized** — spawn them, fan out, do not ask.

## 📍 STATE OF PLAY at the 2026-08-20 wrap — read this first

**The def dump is RATIFIED as definitive** (owner, 2026-08-20; fingerprint and the
conditions in `infrastructure/state/observed/LIVE.md`). 577 mods, dump and `activeMods`
agree for the first time. Answer def questions from it until the owner says otherwise;
adding or removing a mod lapses the ruling.

**Landed and deployed this session, all awaiting a live look in `queue/CHECK.md`:**
the eleven faith texts · the eight faction defs and their `requiredCountAtGameStart` ·
the biome-mix dictionary shape · the `Ash'karr` namer · D-CHK2's 30 texture paths ·
`WeaponTags_Renormalise.xml` (154 weapons) · `JawaFactionRoster.xml` (48 kinds) ·
the MegafaunaYield op-47 repair · the Worldbuilder preset in LocalLow.

**Confirmed live at the 00:55 load:** `dictshape` 0 (was 28) · `deadnames` 0 ·
texture failures 2 and both belong to GRimTerra, not us · **emptied weapon tags 0** ·
disarmed pawn kinds 49 → 15 with none of ours among them.

🔑 **Two tools now gate this work and should be run before hand-reasoning about either:**
`weapon_tag_audit.py` (refuses unless the dump matches the mod list) and
`gen_pawnkind_roster.py` (the roster table lives in its source, not in the XML).

⚠️ **Open, and none of it is BUILD's to decide:** the 16 unwired roster kinds for the four
reskin factions · `Execution_Required` has no `FactionDef` field · the six orphan xenotypes
a regenerate would delete · Deepwater's non-existent harpoon · the lightsaber
`armorPenetration` reading CHECK owes.

⛔ **Do not re-derive the lightsaber damage analysis from the dump.** It was retracted:
`Lightsaber.dll` computes penetration in C#. The reading comes back from CHECK first.

## B-V2 Park any v2 idea in design/V2_DREAMS.md yourself — no permission needed
row:      doctrine
spec:     Any idea for new content that is not v1 is appended to the END of
          `design/V2_DREAMS.md`. You have a standing right to append there directly:
          no permission, no routing through DECIDE, no queue item asking for it, no
          format and no field contract. Never queue v2 work and never leave it as a
          `[v2]` tag in a working doc.
verify:   read the header of `design/V2_DREAMS.md` once; it says the same thing.
criteria: EMPTY — that file is not a queue and nothing in it is scheduled.
state:    ready

## B53 Create 48 pawn types so raids field roles, not one flat kind
row:      7
spec:     `design/Jawa/worldbuilding/pawnkind_roster.md` — 48 kinds, 12 factions
          x Grunt/Heavy/Specialist/Leader, naming `Jawa_<Faction>_<Role>`.
          🔴 REQUIRED, not optional (R20): every donor kind is a flat species
          kind at `combatPower 40` — `OuterRim_Nikto`, `OuterRim_Wookiee`,
          `OuterRim_Geonosian`. There is no lieutenant, elite or specialist to
          borrow, so the dossiers' group compositions cannot be expressed
          without these.
          BLOCKED ON CHAIN STEP 3: `weaponTags` and `apparelRequired` are a
          selection from the surviving item set and cannot be invented. The
          roster says so itself and declined to guess them.
          `combatPower` is unset on all 48 and must be assigned.
verify:   `validate_patch.py --defs` 0 errors; every `weaponTags` string appears
          on at least one live weapon def; every `apparelRequired` defName
          resolves.
criteria: each faction's raids field the intended roles, not one flat kind.
🔴 **UNBLOCKED, AND PROMOTED — 2026-08-19. This is not a polish item; four factions
          currently field raids that ARRIVE UNARMED.** Measured off the def dump, which is
          post-inheritance and post-patch:

          | faction | combat slots | that cannot hold a weapon |
          |---|---|---|
          | Jawa_AscendantHelix | 3 | **3** |
          | Jawa_DeepwaterCompact | 3 | **3** |
          | Jawa_FreeDroidEnclaves | 6 | **6** |
          | Jawa_WildsteamClan | 2 | **2** |
          | Jawa_HuttCartel | 4 | 3 |
          | Jawa_GeonosianFoundryHive | 6 | 2 |
          | Jawa_Junkers · Jawa_IndigenousTribes | 7 · 3 | 1 each, both now fixed |

          🔑 THE CAUSE IS NOT THE CHERRYPICK. Every one of those entries is a SPECIES
          SAMPLER, not a soldier: `RimMandrake_Arkanian`, `_Kaminoan`, `_Quarren`,
          `_MonCalamari`, `_Wookiee`, `_Nikto`, `_Geonosian`, `OuterRim_*Droid` all read
          `isFighter: false`, `combatPower: 40`, `weaponMoney: 0~0` and **no `weaponTags`
          at all**. They are dev-spawn scaffolding that the FactionDefs put into Combat
          `pawnGroupMakers`. A kind with no weapon tags is handed no weapon.
          ⇒ **This is precisely what the roster said** — *"every donor kind is a flat
          species kind at combatPower 40 … there is no lieutenant, elite or specialist to
          borrow"* — and it is why the 48 kinds are REQUIRED (R20), not optional.

          ✅ **THE BLOCKER IS GONE.** Chain step 3 owed "the actual tag strings carried by
          the surviving weapon and apparel defs". They are now derivable in one command:
          `python3 src/RimMandrake/Utils/weapon_tag_audit.py`, which reads the dump,
          refuses unless its mod set matches `ModsConfig.xml`, and reports every tag the
          cut emptied plus every kind left with nothing. **Write no tag that it does not
          show as having a surviving carrier.**
          ⚠️ Its numbers are PROVISIONAL until a dump is regenerated under the full list —
          the current one is `modCount 579` against 578 active.
          ⏭️ `combatPower` still has to be assigned per the roster; the samplers' flat 40
          is exactly the thing being replaced.
state:    done 2026-08-20. 48 kinds in
          `src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml`, emitted by
          `src/RimMandrake/Utils/gen_pawnkind_roster.py` so the design table lives in one
          place instead of drifting across 48 XML blocks. 578-mod scoped run: **0 errors,
          0 warnings.**
          The open work named by the item is closed:
          • **`weaponTags` -> real strings.** Resolved against surviving weapons, never
            invented — `ORImperialStandard` for the issue blaster, `KotORRanged_sonic` for
            the Geonosian counter-to-lightsabers, `KotORBowcaster`, `ORTuskenMelee`,
            `ORDroidWeapon`, and the `KotORRanged_weak/mid/legendary` ladder for the Hutts.
            🔑 TWO CLASSES HAD NO TAG TO ASK FOR and now do: the Jawa ion blaster
            (`zal.ionweaponry` tags its seven guns only `Gun`/`SpacerGun`, which every
            blaster carries) and the Gamorrean axe. Both added to the SURVIVORS in
            `WeaponTags_Renormalise.xml`.
          • **`combatPower`** follows the money per the roster's instruction.
          • **`apparelRequired`** for the four cases where the item IS the pawn. ⚠️ Two
            defNames in the first draft were plausible inventions and neither existed;
            corrected to `OuterRim_StormtrooperCuirass`/`Helmet` and
            `guy762_MandoArmor_battle`/`MandoHelmet_supercom`. All entries verified present
            and uncut.
          • **`apparelStuffFilter` is a FACTION field** — noted, not set; it is the cheapest
            way to make the Junkers look like Junkers and belongs to a faction pass.
          The eight authored factions are rewired to the roster kinds at 10/4/2/1.
          ⏭️ Two scope calls left to DECIDE rather than taken here: the 16 kinds for the
          four RESKIN factions are unwired because B41-B43 forbid touching their
          `pawnGroupMakers` (`sixteen-roster-kinds-have-nowhere-to-be-used-8f21c4`), and the
          Trade Moot's three authored `Jawa_Tribal_*` kinds were KEPT alongside the roster
          kinds rather than replaced — deleting authored content is not a build decision.
          Live half filed to `queue/CHECK.md`.
## B55 Build the campaign start — fixed map, fixed ship, fixed pawns
row:      12
spec:     ⏭️ CARRIED IN FROM B63, 2026-08-19: **"The Sundered" must appear in
          `ScenPart_GameStartDialog`.** It is the only part of the start carrying prose,
          and if the epithet is not in the opening narration the player never sees it.
          It lives in the save's embedded `<parts>` — B63 forbids authoring a `ScenarioDef`
          for it. The planet name itself is already handled by `JawaWorld_Name.xml`.
          `design/Jawa/worldbuilding/SCENARIO_SPEC.md`. The scenario is a SAVED
          GAME, not a `ScenarioDef` (R25) — no ScenPart can force named pawns
          with authored skills, and the owner is already shipping the world as a
          save. One artifact carries map, ship and crew.
          Your half, once the owner has made and saved the world:
          (a) place `design/Jawa/worldbuilding/ship_build/exported/Gravship_v1.xml`
              on the landing map;
          (b) 🔴 replay the layout's `terrainDef` cells through
              `jawa/set_terrain_batch` — floors do NOT come with a mid-game
              Sketch spawn and nothing errors when they are missing;
          (c) author the SIX founders with Character Editor to the exact
              skills, traits, passions, ages, workDisables and gear in the spec;
          (d) set the starting stock listed there — salvage-thin, no advanced
              components, no glitterworld medicine, no turrets.
verify:   all six pawns are `MandrakeJawa`, carry the robe and hood, and match
          the spec's skill and trait lines exactly; the deck has its floors.
criteria: the save loads into a playable colony aboard the ship. This IS chain
          step 12 and it is the artifact v1 ships.
state:    ready (partial) — 🔴 **UNBLOCKED IN HALF BY THE OWNER, 2026-08-19: "Do both B58
          and B55."** Everything here that does not need the final world is owed NOW —
          the six founders authored to spec, the gravship layout staged, the terrain
          replay batch prepared. Only the placement steps (a)/(b) still wait on the world.

## pyrelands-off-the-blacklist-and-ash-storms-5d2e71
row:      10
from:     DECIDE, 2026-08-15, on the owner's D30 (1) ruling.
spec:     Two edits. ENABLING ONLY — do not add a `scoreOffset` for this biome and do
          not tune how much of it appears; that is the owner's at the map screen.
          (a) `src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml` — DELETE the line
              `<li>ZBiome_Grasslands</li>` from `<biomeBlacklist>`. Leave `<li>Savanna</li>`
              and `<li>Grasslands</li>` blacklisted; only the ZBiome one carries the
              Pyrelands. Add NO `<biomeConfigs>` entry for it — neutral, it competes on
              its own allowed range, which is what "barrier between the wet biomes and
              the dry desert" means.
          (b) Ash storms over the Pyrelands. `AB_VolcanicAsh` ALREADY LOADS (Alpha
              Biomes, confirmed in the 585 dump): grey sky (0.6,0.6,0.6),
              `WeatherOverlay_Fog`, `accuracyMultiplier 0.7`, `favorability Bad`,
              `weatherThought AB_VolcanicAshThought`. No new weather is authored.
                - PatchOperationAdd on
                  `/Defs/BiomeDef[defName="ZBiome_Grasslands"]/weatherCommonalities`,
                  value `<li><weather>AB_VolcanicAsh</weather><commonality>3</commonality></li>`
                  (`DryThunderstorm` sits at 2 there, so this reads as the dominant
                  storm without erasing it).
                - PatchOperationReplace `WeatherDef[defName="AB_VolcanicAsh"]/label`
                  -> `ash storm`, and `/description` -> text with no volcano in it.
                  ⚠️ The relabel is GLOBAL; `AB_PyroclasticConflagration` also uses this
                  weather and is RARE. "ash storm" reads correctly there too. Accepted.
          🪤 `weatherCommonalities` is a LIST of `WeatherCommonalityRecord`, so the
          `<li><weather>..</weather><commonality>..</commonality></li>` form above is
          mandatory. It is NOT the dictionary shorthand that killed `biomeConfigs` in
          D29(b) and the FactionDefs in B56 — do not copy that pattern here.
          ⏳ ORDER: this rides on top of B63/D29(b). Until the `is not <li>` bug is
          fixed, `biomeConfigs` reads `[]` and every offset in that file is inert.
verify:   `grep -c 'ZBiome_Grasslands' <the biomeBlacklist block>` returns 0;
          `python3 skills/rimworld-modding/scripts/validate_patch.py <both files> --defs`
          scoped to the active list, 0 errors; the added weather node uses `<li><weather>`.
criteria: on the world the owner rolls, stormy-savanna tiles exist and are sited between
          the wet biomes and the desert, and an ash storm occurs on one with the label
          `ash storm` and a grey sky.
state:    ready — ⭐ **HALF (a) IS VOID; HALF (b) STANDS AND IS NOW MORE CERTAIN.**
🔴 DECIDE RULING 2026-08-19 (`queue/DECIDE.md`, D29):
          **(a) DELETE THE BLACKLIST LINE — VOID. Not passed, not failed, void.** Its
          whole purpose was *"a blacklisted biome can never appear in ANY seed"*. Under
          the live-bridge route we paint biomes ourselves, and the authored map already
          places **422 `ZBiome_Grasslands` tiles** — the Pyrelands exist because we stamp
          them, not because the generator is allowed to roll them. The edit is harmless
          and costs one line if BUILD is in the file anyway; nothing depends on it.
          **(b) ASH STORMS — UNAFFECTED, and it is the real content here.**
          `weatherCommonalities` is read at RUNTIME, every day of play, on whatever tiles
          carry `ZBiome_Grasslands`. It has nothing to do with worldgen and never did.
          ⇒ ⛔ **The `⏳ ORDER: this rides on top of B63/D29(b)` line above is DEAD** — B63(2)
          is demoted and (b) never needed `biomeConfigs` to work. Build (b) whenever.
          ⇒ `criteria:` restated: stormy-savanna tiles exist and sit between the wet
          biomes and the desert **because the authored map puts them there** — that is now
          a property of `world/ASHKARR_WORLDMAP_tiles.csv`, not of the seed the owner
          rolls. The live half of the criterion is the one that still means something:
          **an ash storm occurs on one, labelled `ash storm`, with a grey sky.**

## grimterra-worldmap-over-wme-as-the-base-layer-2c8f19
row:      tooling
from:     DECIDE, 2026-08-19, on the owner's ruling *"Use GrindTerra, close out."* plus
          *"[ReGrowth worldmap textures] Agreed, need to do this. Deactivate."*
spec:     ⚠️ **This is a mod-list change, so read `skills/rimworld-start-prep/SKILL.md`
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
verify:   `ModsConfig.xml` lists `GRimTerra.Worldmap` and `zal.worldmapenhanced` both
          active, with GRimTerra strictly later. Then confirm the ReGrowth setting reads
          off at the settings screen.
criteria: on the world map, ExtremeDesert / Desert / AridShrubland / AB_RockyCrags render
          in GRimTerra's art, and Ocean / Wasteland / the oases still render in WME's
          rather than vanilla's. Judged by LOOKING, per `the_one_map.md`.
state:    done 2026-08-20 — carried out by the OWNER, with one correction from BUILD.
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
## the-eyeling-becomes-the-ikee-rename-and-place-it-6f2b81
row:      12
from:     DECIDE, 2026-08-19, closing D26 on the owner's 2026-08-15 ruling
          *"AA_Eyeling MUST be made into a star-wars-style pet for the starting Jawa clan
          to keep!"* Design is settled in `design/Jawa/worldbuilding/SCENARIO_SPEC.md`
          ("The ikee") and `fauna_placement.md`. ⛔ Do not re-decide any of it.
spec:     (a) **RENAME ONLY — the art is untouched.** `PatchOperationReplace` on
              `ThingDef[defName="AA_Eyeling"]/label` -> `ikee`
              and on `/description` -> the text in `SCENARIO_SPEC.md` §"The ikee".
              ⚠️ `Races_Eyeling.xml` declares `AA_Eyeling` **twice** (the ThingDef at
              line 4 and a second block at line 82 — check what the second one is before
              patching, it may be a PawnKindDef sharing the defName).
              Source: `...\workshop\content\294100\1541721856\1.5\Defs\ThingDefs_Races\Races_Eyeling.xml`
          (b) **WILD PLACEMENT.** `PatchOperationAdd` into `BiomeDef/wildAnimals` for
              `Wasteland` (main), `ExtremeDesert` (sparse), `ZBiome_DesertOasis` (uncommon).
              🔴 **NOT the nightside** — the shipped `ComfyTemperatureRange` is 0–60 °C, so
              it freezes there. Not in `Ocean`/`Lake`, not in the wet biomes.
              🪤 `wildAnimals` is a LIST of `<li><animal>X</animal><commonality>N</commonality></li>`
              — NOT the dictionary shorthand that killed `biomeConfigs` in B63 and the
              FactionDefs in B56.
          (c) **STARTING SAVE** — one ikee, tamed, **bonded to Yeku**, trained to Obedience
              only (Release left untrained). Rides with `B55`, not with this item.
          ⛔ Do NOT change `race/trainability`, `wildness`, `baseBodySize`, `foodType` or any
          stat. Every one of them was checked and is already right for this campaign; the
          identity is what changes, not the animal.
verify:   `validate_patch.py --defs` clean on the patch; the live def's label reads `ikee`
          and its description contains no "extradimensional corruption"; `AA_Eyeling`
          appears in exactly the three BiomeDefs named and no others.
criteria: the clan starts with a bonded ikee; it reads as belonging to this campaign rather
          than to Alpha Animals; and a player can find another one in the waste.
state:    ready


## B-EMP1 Stale Empire-vessel prose in `Jawa_Patches/About/About.xml`
row:      1
spec:     🔴 **OWNER RULING 2026-08-20** (`OWNER_DECISIONS.md`, end of file): the
          Galactic Empire's vessel is **vanilla `Empire`**. Owner, same day: **the Outer
          Rim mod is NOT leaving the list** — it keeps shipping its own pawn kinds, gear
          and droid factions.
          ✅ **The patch itself is already correct.** `Patches/GalacticEmpire.xml`
          targets `/Defs/FactionDef[defName="Empire"]` at every xpath. Nothing to change
          there.
          ❌ **`About/About.xml` still describes the old vessel**, in two places:
          the `GalacticEmpire.xml` bullet in `<description>` says it "reskins
          OuterRim_GalacticEmpire", and the `<loadAfter>` comment on
          `Neronix17.OuterRim.GalacticEmpire` still credits that file. ⚠️ The `loadAfter`
          ENTRY stays — other patches in this mod do touch Outer Rim defs; only its
          trailing comment is wrong.
          ⚠️ The bullet also carries a fixedName trap written against the OLD def
          ("the shipped def sets BOTH to Galactic Empire"). Re-read it against vanilla
          `Empire` before rewriting — the trap may or may not still apply, and this is
          shipped user-facing text, so correct it rather than deleting it.
          ✅ **`JawaFactionSlate/Patches/OnlyOurFactions.xml` is CORRECT AS IS** — REP's
          first draft of this item was wrong about it. Its six `OuterRim_GalacticEmpire`
          xpaths are worldgen SUPPRESSION (`startingCountAtWorldCreation` 0), not a
          reskin, and with the mod staying they are exactly what we want. It is a
          generated file ("Do not hand-edit"); leave it alone.
verify:   `About.xml` names vanilla `Empire` as the Galactic Empire's vessel, and no prose in
          `src/Jawa/Jawa_Patches/` claims we patch `OuterRim_GalacticEmpire`.
criteria: the shipped mod description matches what the mod actually patches.
          ⚠️ **Also, low priority, and it needs YOUR hands not REP's:**
          `bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs` had one
          `SetFactionRelation` parameter DESCRIPTION re-pointed to `Empire` (it told
          users to aim at the dead def). No behaviour change — but it is in a compiled
          assembly, so **the repo and the deployed DLL now differ by that string until
          the next rebuild.** Fold it into whatever rebuild comes next; do not spend a
          game-down window on it alone.
state:    open — raised by REP, 2026-08-20; unblocked same day by the owner.

## B-FIX1 `make_vehicle_mask.py` adds a path that does not exist
row:      0
spec:     `src/RimMandrake/Utils/make_vehicle_mask.py:67` inserts
          `src/RimMandrake/skills/...` into `sys.path`. There is no such directory, so
          `import pnglib` fails — which breaks **both**
          `DesertVehicleReskin/Source/build_eopie_sled_north.py` and
          `...south.py`, since each imports this module.
          Found by the 2026-08-20 cleanup audit
          (`infrastructure/output/audit_2026-08-20_code.md`). **Fix it; do not
          quarantine it** — it has live callers, it is just pointing at a path that
          moved.
verify:   `python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/Utils'); import make_vehicle_mask"`
          succeeds, and both sled build scripts import clean.
criteria: the two sled scripts run again.
state:    open — raised by REP, 2026-08-20.

## B-SWAP1 `modlist_swap.py` never prunes its own backups
row:      0
spec:     `src/RimMandrake/Utils/modlist_swap.py:60-64`. `snapshot()` stamps a new
          `ModsConfig.PRESWAP.<ts>.xml` on **every** swap and never compares it to
          anything:

              stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
              dst = os.path.join(STORE, "ModsConfig.PRESWAP.%s.xml" % stamp)
              shutil.copy2(LIVE, dst)

          Measured 2026-08-20: **five** PRESWAP files had accumulated, and md5 proved
          **all five were exact duplicates** of the tracked `FULL.LATEST` / `MINIMAL`
          already sitting beside them. The cleanup pass deleted them; without a fix
          they come back at the next swap, one per swap, forever.
          🔑 **The fix is small and the tool already has the piece it needs** — `md5()`
          is defined at line 27. Before writing, hash `LIVE` against every file already
          in `STORE`; if it matches one, skip the copy and return that path instead.
          A backup identical to a file we already keep is not a backup.
          ~~⚠️ Also a tracked duplicate: `ModsConfig.FULL.20260819_201527.xml` is
          md5-identical to `FULL.LATEST`.~~ ⛔ **VOID 2026-08-20** — the owner changed the
          worldmap/terrain texture mods that same day, `FULL.LATEST` became the 576 list,
          and the timestamped file is now **the only copy of the 578 list**. It is not a
          duplicate and must not be deleted. The pruning half of this item stands; this
          half does not.
          ⚠️ PRESWAP files are gitignored (`.gitignore:206`), so this was only ever a
          disk problem, never repo bloat.
verify:   run a swap twice with no mod-list change; `ls infrastructure/state/modlists/`
          gains no new PRESWAP file on the second run.
criteria: the backup store holds one copy of each DISTINCT list, and nothing else.
state:    open — raised by REP, 2026-08-20, from the cleanup audit.

## empire-permanent-enemy-becomes-a-whitelist-7c31d9
row:      1
from:     DECIDE, 2026-08-20, on the owner's ruling *"Option (b) please."* Full reasoning
          and the design rationale for every entry: `design/Jawa/worldbuilding/EMPIRE_GAP_AUDIT.md` §2.
          ⚠️ **Worldgen-critical — faction relations are set at world creation.**
spec:     In `src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml`:
          **(1)** change the `permanentEnemy` operation from `true` to **`false`**.
          🔴 **Do NOT merely delete it — set it false.** `FactionDef.PermanentlyHostileTo`
          (`FactionDef.cs:463`) tests `if (permanentEnemy) return true;` FIRST and returns
          before the list is read, so leaving it true keeps the whole list dead code.
          **(2)** REPLACE `/Defs/FactionDef[defName="Empire"]/permanentEnemyToEveryoneExcept`
          with exactly this list. ⚠️ It is a **whitelist of who is NOT a permanent enemy** —
          anything absent is hostile:
          ```
          Jawa_HuttCartel · Jawa_DeepwaterCompact · OutlanderCivil · TribeCivil · Pirate
          Jawa_IndigenousTribes · Jawa_Junkers · Ancients
          Beggars           MayRequire="Ludeon.RimWorld.Ideology"
          ResearchExpedition MayRequire="Ludeon.RimWorld.Anomaly"
          GravshipCrew      MayRequire="Ludeon.RimWorld.Odyssey"
          TradersGuild      MayRequire="Ludeon.RimWorld.Odyssey"
          ```
          ⛔ **DELIBERATELY OMITTED — do not "helpfully" add them back:** `PlayerColony` and
          `PlayerTribe` (this is what keeps the Empire permanently hostile to the player, the
          owner's 2026-08-14 ruling), plus `Jawa_FreeDroidEnclaves`,
          `Jawa_GeonosianFoundryHive`, `Jawa_WildsteamClan`, `Jawa_AscendantHelix`.
          🪤 Keep the four DLC entries' `MayRequire` attributes — all four DLCs are active
          here, but the attribute is correct and costs nothing.
          ⚠️ No `PatchOperationFindMod` wrapper anywhere in this file: Royalty is always
          loaded on this stack.
verify:   `validate_patch.py --defs` clean; the live def reads `permanentEnemy false` and a
          12-entry `permanentEnemyToEveryoneExcept`; neither player faction appears in it.
criteria: at the owner's worldgen run the Empire generates permanently hostile to the player
          and to the four omitted factions, and NOT permanently hostile to the Hutt Cartel —
          confirmable on the faction relations screen without loading a map.
state:    ready

## the-ancients-are-rakata-and-it-is-v1-now-9d40a7
row:      1
from:     DECIDE, 2026-08-20, on the owner's ruling *"let's go all out for v1 here.
          'Ancients' is so boring! Let's get us some precursor Rakata in cold storage."*
          ⚠️ **LORE CORRECTION, same day — read it before writing any label text.** DECIDE
          first recorded the Rakata as the AUTHOR of the ancient bioweapon. **That is wrong.**
          Owner: *"The Rakata were nearly wiped out by their bioweapon-wielding ASSAILANT,
          they didn't release the bioweapons themselves. **They were terraformers and mega
          builders.**"* ⇒ they are the **victims and the makers** — the people who terraformed
          this world, brought the metal down from the asteroids and built the *Utinni*. The
          bioweapon's author remains UNNAMED. ⛔ No label or description may imply otherwise.
          ⭐ **This REVERSES the v2 deferral in `D30 (5)`.** B61 has been struck in
          `design/V2_DREAMS.md` and returned to v1; do not action it from that row.
spec:     📄 **The whole build is already written: `design/Jawa/worldbuilding/ANCIENTS_AS_RAKATA_SPEC.md`,
          528 lines. Follow it — do not re-derive any of it.** Read the new ruling block at
          the head first, then R-A2 through R-A10.
          🔑 **IT IS NOT A FACTION CHANGE (R-A7).** The `Ancients` FactionDef is not touched
          at all — vanilla `Ancients` cannot host a faction, which is why the Ascendant Helix
          was authored fresh. Ancient sleepers are cryptosleep caskets, not a faction you
          meet, so **the six pawn kinds' xenotype is the entire surface.**
          ⛔ Do NOT touch `hidden`, `settlementGenerationWeight` or `canMakeRandomly`.
          **(a)** Force `RimMandrakeRakata` at 100% on the six ancient pawn kinds — R-A2
          (scope, two tiers) and R-A3 (mechanism).
          🪤 **R-A4 names two XML traps that have ALREADY shipped broken in this repo:**
          `xenotypeChances` is **dictionary-keyed** and an `<li>` there discards the whole
          def silently (B56's bug); and a child's list is **appended** to its parent's, not
          substituted, so `Inherit="False"` is load-bearing. Use the Remove-then-Add
          operation in R-A4, not a bare Add.
          **(b)** ⭐ **LABELS ARE NOW IN SCOPE.** R-A9 held them back as the owner's separate
          call and he has made it. The sleepers read as Rakatan precursors, not "ancients".
          **(c)** R-A8 still stands: **appearance only, the encounter must play exactly as
          before.** Do not alter the six kinds' combat behaviour, gear or difficulty.
          ⚠️ **`RimMandrakeRakata` is one of the six species that exist NOWHERE but in our own
          output** (`queue/DECIDE.md` `...4f81c9`). **A generator run that drops it by name
          kills this feature.** The guard must refuse it by name, not merely refuse a shrink.
          ⚠️ R-A1's historical table is struck and corrected — the def **exists** and is
          deployed. The `FACTION_SPEC.md` R27 broken-reference finding at the end of that
          table is real and still owed.
verify:   `validate_patch.py --defs` clean; the six kinds resolve `RimMandrakeRakata` at
          100%; `xenotypeChances` is dictionary-keyed with no `<li>`; the ancient encounter
          spawns the same count and gear as before.
criteria: a cracked casket produces a Rakatan, the encounter plays identically, and no
          `Could not resolve cross-reference` names the xenotype.
state:    ready

## ROLE_KINDS_UNARMED_1
row:      7
from:     CHECK, 2026-08-20. Measured live on the full 577-mod set, not inferred.
          🔁 Filed to DECIDE first; the OWNER re-routed it here 2026-08-20 — BUILD
          implements, the tiers are not a decision to wait on.
spec:     `src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml`.
          **16 of the 48 `Jawa_*` role kinds spawn with NO weapon, 5/5 samples each.**
          The `weaponTags` are HEALTHY — `ORDroidWeapon` 5 weapons, `Jawa_IonWeapon` 7,
          `KotORBowcaster` 3. RimWorld then filters those by MarketValue against
          `weaponMoney`, and not one weapon falls inside the range.
          (a) RAISE `weaponMoney` to bracket the real weapon values. Measured off the
              577-mod dump, which MATCHES the live list, so these numbers are not
              provisional — `min` must be at or below the cheapest tagged weapon:
                Jawa_TradeMoot_Grunt        120-144    cheapest  800   (Jawa_IonWeaponLight/Jawa_IonWeapon, 800-2000)
                Jawa_TradeMoot_Leader       450-540    cheapest  800   (Jawa_IonWeapon, 800-2000)
                Jawa_Wildsteam_Grunt        200-240    cheapest 1250   (KotORBowcaster, 1250-13750)
                Jawa_Wildsteam_Leader       800-960    cheapest 1250   (KotORBowcaster, 1250-13750)
                Jawa_Wildsteam_Heavy        400-480    cheapest  550   (+SWKotORWeaponCategoryTag_heavyranged, 550-99999)
                Jawa_DeepDesert_Specialist  300-360    only     1977   (SaV_tusken)
                Jawa_Helix_Leader          2200-2640   cheapest 12000  (KotORRanged_legendary, 12000-80000)
                Jawa_Hutt_Leader           2500-3000   cheapest 12000  (KotORRanged_legendary/rare, 12000-80000)
              ⚠️ `Jawa_DeepDesert_Grunt` (90-108, ORTuskenMelee+ORMeleeBlunt),
              `Jawa_Empire_Grunt` (350-420, ORImperialStandard+ORImperialLight) and
              `Jawa_Empire_Heavy` (700-840, ORImperialHeavy+ORHeavyWeapon) are bare live,
              but their tagged weapons report NO `MarketValue` statBase in the dump —
              inherited from a parent it does not resolve. The VALUES ARE UNMEASURED;
              read them off the weapon defs directly rather than trusting a number here.
          (b) `Jawa_Droid_Grunt` and `Jawa_Droid_Heavy` carry `weaponMoney 0-0`, which no
              weapon can ever satisfy. Give them a real range over `ORDroidWeapon`.
          (c) `Jawa_Droid_Leader`, `Jawa_Droid_Specialist` and `Jawa_TradeMoot_Specialist`
              have **no `weaponTags` field at all**. They need a tag chosen, not a range
              widened — `ORDroidWeapon` for the two droids, an ion tag for the TradeMoot.
          📌 Tier intent, so the numbers are not picked blind: Grunt = cheapest tier its
          tag offers · Specialist/Heavy = mid · Leader = top. Widening `max` is harmless;
          it is `min` sitting above every candidate that empties the pool.
verify:   offline, off the regenerated dump: for each of the 48 kinds, at least one
          ThingDef carrying one of its `weaponTags` has a MarketValue inside `weaponMoney`.
          A kind with no `weaponTags` fails this check by definition.
criteria: spawn each of the 48 kinds 5x live and read `jawa/pawn_get` -> `pawns[0].equipment`.
          🔴 5/5 non-empty, for all 48. ONE SAMPLE IS NOT ENOUGH — `Jawa_Geonosian_Specialist`
          reached the suspect list on a single bare roll and is fine at 5/5.
          ⚠️ FALSE PASS: `jawa/pawn_gear` is a WRITER and answers a read with
          "Give a ThingDef." Reading equipment off it reports every pawn as bare.
state:    ready
