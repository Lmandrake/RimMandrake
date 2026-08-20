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
`Lightsaber.dll` computes penetration in C#. The reading comes back from CHECK first —
`lightsaber-armour-penetration-...-6a91d3` in `queue/CHECK.md` asks for ONE number off the
weapon info card. The AP-2.0 patch was built and deleted; regenerating it is minutes.

**Later on 2026-08-20, after the state block above was written:**
- 🔴 **The game had been loading a RETIRED Empire patch.** A peer renamed
  `ImperialDesertDirectorate.xml` to `GalacticEmpire.xml`, but a rename is a delete plus an
  add and `deploy_custom_mods.py` will NOT delete on its own — it reports the orphan as a
  `-` line and keeps it. The old file sat in the Steam copy while the new one had never
  shipped. Fixed with `--prune --apply`. 🪤 **Check for a `-` line after every rename.**
- ✅ **Skills are SYMLINKS, not installs.** `.claude/skills/<name>` points at
  `skills/<name>` — same inode. Editing the repo folder IS installing it; the `.skill` zips
  are for handoff and a fresh clone only. I claimed the opposite three times before
  checking. `rimbridge-companion` was the one skill with no symlink and never invocable;
  linked now, 27 of 27.
- ✅ Everything deploys clean: `deploy_custom_mods.py` reports **"Everything in sync"**
  across all 22 mods, only the 17 deliberate `DEPLOY_HOLD` entries held.
- ✅ The dump still matches the live list (577 = 577). Bringing the game down does not
  lapse the ratification; only a mod-set change does.

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
          🔴 **CORRECTION 2026-08-20, read out of `PawnWeaponGenerator.TryGenerateWeaponFor`
          after this item was filed. The rule is a CEILING, not a bracket.** The engine
          rolls `weaponMoney.RandomInRange` once, then keeps every weapon pair whose
          `Price` is **not greater than** that roll:
              `if (!(w.Price > randomInRange) && <tags match> && ...)`
          ⇒ **`min` is not a floor on eligibility.** It only shifts the roll. What empties
          the pool is `max` sitting below the cheapest tagged weapon. So the fix is to
          raise `max` above the cheapest candidate — raising `min` as well is a
          separate, cosmetic choice about how rich the tier looks.
          ⚠️ And the engine compares `ThingStuffPair.Price`, which includes STUFF cost, not
          the bare `MarketValue` the numbers below are taken from. Treat them as a floor:
          the real price of a stuffed weapon is higher, never lower.
          (a) RAISE `weaponMoney` (the `max` especially) to clear the real weapon values.
          Measured off the
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

## GRIMTERRA_TEXPATH_TYPOS_1 Three broken texPaths in GRiNDTerra Biomes, juveniles only
row:      unassigned
from:     CHECK, 2026-08-20. Found in the load harvest after the owner's terrain/worldmap
          mod swap; diagnosed to the exact line.
spec:     `GRiNDTerra Biomes` (`GRimTerra.Biomesmod`, workshop `3537211820`) ships three
          `texPath`s pointing at folders that do not exist. **The art is all present** —
          only the paths are wrong, and every one of them is in the SECOND `<li>` of
          `<lifeStages>`, i.e. the JUVENILE stage. Baby and adult stages are correct.
            `1.6/Defs/ThingDefs_Races/Races_Animal.xml:301`
               is   Things/Pawn/Animal/TortoiseGRim/GRimTortoiseA
               want Things/Pawn/Animal/GRimTortoise/GRimTortoiseA        (words transposed)
            `1.6/Defs/ThingDefs_Races/Races_Animal.xml:305`
               is   Things/Pawn/Animal/Tortoise/Dessicated_GRimTortoiseA
               want Things/Pawn/Animal/GRimTortoise/Dessicated_GRimTortoiseA
               ⚠️ points at VANILLA's Tortoise folder. Logs nothing until a dessicated
               corpse exists, so it is invisible in the load harvest.
            `1.6/Defs/ThingDefs_Races/Races_Animal_Birds.xml:64`
               is   Things/Pawn/Animal/GRimPinkBird/GRimPinkbird
               want Things/Pawn/Animal/GRimPinkbird/GRimPinkbird          (capital B)
          🔑 The capital-B one is the instructive case: **Windows' filesystem is
          case-insensitive but RimWorld's content index is NOT**, so the file resolves
          perfectly from a shell and still fails in game. Never settle a texPath question
          with `ls`.
          FIX: a `PatchOperationReplace` in `Jawa_Patches` on those three `texPath` nodes.
          ⛔ Do NOT edit the workshop folder — Steam overwrites it on the next update.
verify:   `validate_patch.py --defs` 0 errors; the xpath reports 3 hits, not 0. A patch
          that matches nothing logs nothing.
criteria: a load whose `Player.log` carries **0** `Failed to find any textures at
          Things/Pawn/Animal/TortoiseGRim` or `.../GRimPinkBird` lines. Baseline today is 2.
          ⚠️ ABSENCE IS A WEAK SIGNAL and this is one of the cases where it is the only one
          available. Strengthen it by spawning a JUVENILE tortoise and looking — adults
          render fine and prove nothing. `jawa/set_pawn_age` cannot help: DebugSetAge is
          FORWARD-ONLY and refuses to walk a debug-spawned adult back to a juvenile.
state:    ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔴 `Inhabited` — SHIPPED TO BUILD 2026-08-20. The code is v1 now.

**Owner, 2026-08-20, in the DECIDE window:** *"Please ship the Inhabited spec to BUILD for
actual v1 construction, we have spare time tonight."*

⛔ **This REVERSES the standing ruling you may remember** — *"v1 for the DESIGN, v2 for the
code. Do not file BUILD items for the code."* That sentence is struck in place at the head
of `design/Jawa/bridge/INHABITED_DESIGN.md` and in `queue/DECIDE.md`. Build from the eight
items below; the design doc is the spec and it has not otherwise changed.

**The spec is `design/Jawa/bridge/INHABITED_DESIGN.md` (564 lines).** Read §2, §3, §4 and §6
before starting. Two corrections to it, found 2026-08-20 while filing these and NOT yet
folded into the doc's prose:

🔴 **The doc names `GiveQuest_Beggars`. NO SUCH SYMBOL EXISTS.** The real class is
`RimWorld.QuestGen.QuestNode_Root_Beggars`, and it (a) hard-requires Ideology via
`ModLister.CheckIdeology("Beggars")` at `:44`, and (b) builds a **hidden generated faction**
from `FactionDefOf.Beggars` at `:73` — beggars do not belong to an existing faction. That
changes `INHABITED_BEGGARS_FROM_POOL_1` from "draw from the pool" to "draw from the pool AND
reassign faction". See that item.

⚠️ **The casts are PROSE, not data.** 269 characters across 11 files, fields
`Name · race · gender · age` / `traits:` / `childhood:` / `adult:` / `hook:`. Only `traits:`
holds real defNames. There is no xenotype, pawnKind, faction defName, apparel or skill on
any entry. ⇒ `CAST_ROSTER_MACHINE_READABLE_1` exists because of this and everything that
instantiates a named person depends on it.

**Order.** `INHABITED_MOD_SKELETON_1` → `INHABITED_WORLD_OBJECT_CORE_1` →
🔴 `ROSTER_SURVIVES_OFFMAP_PROOF_1` (**stop here until it passes — it can invalidate the
architecture**) → the rest in any order.

## INHABITED_MOD_SKELETON_1 The mod folder, About.xml and csproj
spec:     Create `src/Jawa/Inhabited/`, mirroring `src/Jawa/JawaPlantGrowth/` exactly —
          that mod is the working reference for this toolchain and its csproj comments
          carry the build line.
            `src/Jawa/Inhabited/About/About.xml`
               `<packageId>mandrake.inhabited</packageId>`, `<name>Inhabited (local)</name>`,
               `<author>mandrake</author>`, `<supportedVersions><li>1.6</li>`.
               `<modDependencies>`: `Ludeon.RimWorld`, `brrainz.harmony`.
               `<loadAfter>`: `brrainz.harmony`, `Ludeon.RimWorld`.
            `src/Jawa/Inhabited/Source/Inhabited.csproj`
               `<TargetFramework>net472</TargetFramework>`, `AssemblyName`/`RootNamespace`
               `Inhabited`, `<OutputPath>..\Assemblies\</OutputPath>`,
               `<AppendTargetFrameworkToOutputPath>false`,
               🔴 `<CopyLocalLockFileAssemblies>false</CopyLocalLockFileAssemblies>` —
               three mods in this load set shipped the base game's assemblies into their
               own folder and caused silent chaos. Harmony must come from
               `brrainz.harmony` at runtime, never from us.
            `src/Jawa/Inhabited/Defs/` — empty for now, created so deploy sees it.
          Build with the WINDOWS-NATIVE dotnet; it cannot take a `/mnt/d` path:
            `"%USERPROFILE%\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\Jawa\Inhabited\Source\Inhabited.csproj -c Release`
          ⛔ Do NOT deploy while the game is running — the OS locks assemblies. Everything
          else in this mod (Defs, About) deploys game-up.
verify:   the build produces `src/Jawa/Inhabited/Assemblies/Inhabited.dll` and
          `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Inhabited` plans a
          copy with no `-` lines. ⚠️ A mod with no About.xml or packageId is not
          deployable and deploy will say so rather than failing loudly.
criteria: the mod appears in RimSort / the in-game mod list under `mandrake.inhabited`.
state:    done 2026-08-20, `f0a9f6c`. Built at `src/Jawa/Inhabited/`, deployed, in sync.
          ⚠️ **Two deviations from the spec text, both deliberate and both mine to make:**
          (a) `<name>Inhabited (local)</name>` as specified, but the mod carries a real
          `Defs/` tree already rather than an empty one — the core landed in the same pass.
          (b) `EnableDefaultCompileItems` is left ON rather than listing every `.cs`
          explicitly as `JawaPlantGrowth` does; this project grows files weekly and an
          explicit list is a silent-omission machine. `CopyLocalLockFileAssemblies` is
          `false` as required and `Assemblies/` holds **only** `Inhabited.dll`.
          verify output:
            `Inhabited -> ...\Assemblies\Inhabited.dll   Build succeeded. 0 Warning(s) 0 Error(s)`
            `deploy_custom_mods.py --mod Inhabited` -> 6 `+` lines, **no `-` lines**,
            then `--apply` -> `-> VERIFIED in sync`
          ⚠️ It is **not in ModsConfig.xml**, so the game will not load it until it is
          enabled. That is a start-prep step, not a deploy step.

## INHABITED_WORLD_OBJECT_CORE_1 `WorldObject_Inhabited` — the roster is real pawns
spec:     `src/Jawa/Inhabited/Source/WorldObject_Inhabited.cs`. Model on `RimWorld.Planet.Caravan`,
          which is the settled shipped pattern for people held off-map — do not invent a
          persistence layer. §3 of the design doc.
            `class WorldObject_Inhabited : WorldObject, IThingHolder, ILoadReferenceable`
            fields, all through `Scribe`:
               `ThingOwner<Pawn> roster`   🔴 ACTUAL `Pawn` OBJECTS, never records. Names,
                                          skills, relationships, scars and memories then
                                          survive with no serialisation of ours, and §3.2
                                          ("sell a pawn and they stay") falls out free.
               `PlaceDef placeDef` · `CastDef castDef`   archetype + parameters
               `InhabitedState state`     enum: `Inhabited · Abandoned · Looted · Squatted`
               `ThingOwner<Thing> stock`  trade goods AND the larder (§2.1)
            `WorldObjectDef` in `Defs/WorldObjectDefs_Inhabited.xml` with
               `worldObjectClass="Inhabited.WorldObject_Inhabited"`, an expandingIcon, and
               `canHaveFaction=true` — faction is inherited from `WorldObject`.
            `GetInspectString()` renders the census line from §3.3:
               `12 souls . oil . will trade`  /  `9 souls fled . stock spoiling`
          ⛔ **No death record, no memorial, no ledger, no counter** (§3.1, owner verbatim:
          *"eaten and forgotten"*). The roster simply IS the survivors; the absence is the
          memory. Do not add a `died` int because it would be easy.
verify:   `dotnet build` clean; the def loads with 0 errors in a def-dump refresh
          (`python3 src/RimMandrake/Utils/refresh.py`) and `WorldObjectDef` `Inhabited_*`
          appears in the dump.
criteria: a `WorldObject_Inhabited` spawned on the world map via the bridge draws its icon
          and its inspect string on the planet view.
state:    built 2026-08-20, `f0a9f6c` — offline verify passes; **the def-dump half is owed
          and needs a load.** Filed to CHECK as `INHABITED_DEFS_LOAD_CLEAN_1`.
          🔴 **THREE DEVIATIONS FROM THE SPEC, and DECIDE should overrule any it dislikes:**
          (a) **`InhabitedPlaceDef` / `InhabitedCastDef`, not the bare `PlaceDef` / `CastDef`
              the spec wrote.** A def type name IS the XML element name and is shared across
              the whole load order; this build set carries 577 mods. `PlaceDef` is a
              coin-flip collision and a collision here is silent.
          (b) **`stock` is an `InhabitedStock` sub-holder, not a second `ThingOwner<Thing>`
              on the world object.** `IThingHolder.GetDirectlyHeldThings` returns exactly
              one owner, so a second one has to hang off a child holder. This is the shape
              `Caravan` uses for `pather` / `needs` / `beds` / `trader`.
          (c) **the larder and the trade goods are one container**, as the spec asked, and
              the census line reads them: `12 souls . oil . will trade`.
          ⛔ No death record, no memorial, no ledger, no counter exists anywhere in the mod.
          Checked by grep before commit.

## ROSTER_SURVIVES_OFFMAP_PROOF_1 🔴 THE ARCHITECTURE GATE — do this before the rest
spec:     §3.4 names this as *"the one that could invalidate the architecture. Do it first."*
          `Caravan` is designed to be TRANSIENT and we are using its shape for something
          PERMANENT. Pawns in a `ThingOwner` off-map are not ticked — which is exactly what
          "frozen until visited" wants — but vanilla never stress-tests it across years.
          BUILD writes the harness only:
            a dev-mode gizmo on `WorldObject_Inhabited`, `[DebugAction]`, that
            (a) generates 3 pawns into `roster`, one with a named social relation to a
                colonist and one with a scar and a trait,
            (b) prints each pawn's `ThingID`, name, age, relations count and hediff count.
          ⛔ Do not fix anything you find here. Report it — if pawns do not survive
          intact, §3's container choice is wrong and DECIDE re-specs before more is built.
verify:   offline: the gizmo compiles and the debug action is listed.
criteria: 🔴 CHECK's, and it is a soak, not a glance. Stuff the roster, **save, quit to
          desktop, reload**, let **100+ in-game days** pass without visiting the tile, then
          print again. PASS = same `ThingID`s, names, relations and hediffs; ages advanced
          by 0 days (frozen) or by exactly the elapsed time (ticked) — **either is
          acceptable, but which one it is must be reported**, because §3.4 promises frozen
          and a ticking roster changes the design.
          FAIL = any pawn missing, any relation dropped, any `Could not load reference to`
          in `Player.log` naming a pawn.
state:    harness built 2026-08-20, `f0a9f6c`. **The soak is CHECK's and is not done.**
          Filed as `ROSTER_SOAK_100_DAYS_1` in `queue/CHECK.md`.
          🔴 **TWO OF THE THREE WAYS THIS COULD HAVE FAILED WERE FOUND ON DISK AND FIXED
          BEFORE THE SOAK, so the harness is now testing a different question than the
          item assumed.** Read off the 1.6 decompile:
            1. `WorldObject.DoTick` walks its child holders and calls `ThingOwner.DoTick`
               on each, skipping only owners that are `is Map` or `is Caravan` — a
               hardcoded type test a mod cannot join. **The design's "pawns held in a
               ThingOwner off-map are not ticked" is FALSE for a custom holder**; the cast
               would have starved in a box. Opt-out is `IThingHolderTickable` with
               `ShouldTickContents => false`, and it is in.
            2. `Caravan.pawns` is `LookMode.Reference`, safe only because caravan pawns are
               in `WorldPawns` AND `WorldPawnGC.GetCriticalPawnReason` carries an explicit
               `p.IsCaravanMember()` test. A custom holder matches **none** of that
               method's tests, so the collector would have taken the whole roster between
               visits. Ours is `LookMode.Deep` and stays out of `WorldPawns`.
          §3.4 of the design doc has been corrected in place.
          ⇒ **The soak now proves the remaining question, which is the interesting one:**
          does a deep-held, deliberately un-ticked pawn survive save/quit-to-desktop/reload
          and 100+ days with relations and hediffs intact. Debug actions, category
          `Inhabited`: `Create place at current tile` · `Stuff roster (3 pawns)` ·
          `Report roster` · `Report displaced pool` · `Absorb roster into pool` ·
          `Draw 3 from pool`. `Report roster` prints ThingID, name, age in years AND ticks,
          relation count, hediff count, trait count, dead flag and faction, per pawn.
          🔑 **The age line is the one that answers §3.4's open question** — frozen reads
          the same tick count twice, ticked reads exactly the elapsed time.

## INHABITED_DISPLACED_POOL_1 The placeless, per faction
spec:     §4. `src/Jawa/Inhabited/Source/DisplacedPool.cs`, a `GameComponent` so it is
          saved with the game and reachable from anywhere.
            `Dictionary<Faction, ThingOwner<Pawn>> pools`  — people who lost their place
            `void Absorb(Pawn p, Faction f)`               — on FATE:flee
            `List<Pawn> Draw(Faction f, int count)`        — removes and returns up to
                                                             `count`, oldest-displaced first
          🔑 **Any cast being instantiated draws from the pool BEFORE generating anyone
          new.** That single ordering rule is the whole recurring-character effect.
          🔑 **This does NOT violate "frozen until visited"** — redistribution happens at
          cast INSTANTIATION, when a map generates, never on a background tick. Do not add
          a `GameComponentTick` that moves people around.
          ⛔ The dead never enter the pool (§3.1).
verify:   `dotnet build` clean. A `[DebugAction]` that absorbs 5 pawns and draws 3 returns
          3 distinct pawns and leaves 2, across a save/load.
criteria: raid a cast, leave, land on a second place of the same faction, and at least one
          pawn there is a survivor of the first — same name, and RimWorld's own opinion
          system already knows what you did to him.
state:    built 2026-08-20, `f0a9f6c`. Build clean; the save/load half is CHECK's, filed
          under `ROSTER_SOAK_100_DAYS_1`.
          🔴 **ONE DEVIATION, and it is a save-correctness fix, not a preference.** The spec
          asked for `Dictionary<Faction, ThingOwner<Pawn>> pools`. **That container cannot
          round-trip:** a `ThingOwner` must be constructed with its `IThingHolder` owner,
          and `Scribe_Collections`' deep look has no way to hand one to a value it is
          reconstructing — the owners come back null and every pool empties on load.
          Shipped instead: ONE `ThingOwner<Pawn>` plus a faction QUERY. `Absorb(Pawn,
          Faction, reason, origin)` and `Draw(Faction, int)` are the specified API,
          unchanged, and `Draw` returns longest-waiting first as specified.
          ⛔ The dead never enter the pool; `Absorb` refuses them on the first line.
          ⛔ There is no `GameComponentTick` and there must not be one.

## INHABITED_GENSTEP_CAST_SPAWN_1 The GenStep that puts the company on the ground
spec:     §2. The link chain is entirely shipped and verified 2026-08-19:
          `TileMutatorDef.extraGenSteps` (`TileMutatorDef.cs:26`) → our `GenStepDef` →
          `LordMaker.MakeNewLord(faction, job, map, pawns)`. `MapGenerator.cs:158` is where
          mutator gen steps are concatenated, so the hook is real and needs no patch.
          Seven shipped GenSteps already call `MakeNewLord` in this exact shape —
          `GenStep_SitePawns` is the closest model.
            `src/Jawa/Inhabited/Source/GenStep_InhabitedCast.cs`
              on generate: find the `WorldObject_Inhabited` for `map.Tile`; pull `roster`
              out; if short of the cast size, `DisplacedPool.Draw` first, then generate
              fresh from `CastDef`; spawn and `MakeNewLord`.
              on map destroy: return SURVIVORS to `roster`. The dead do not return.
          🔴 **CAST SIZE — DECIDE's ruling, 2026-08-20, so this item is executable:**
            hive foundry (Geonosian)   14–22      fortified waystation   10–16
            refinery / worksite         8–14      nomad camp (Tusken)     6–12
            trade moot / post           5–9       homestead / farmstead    4–7
            droid enclave               3–6
          A faction's 25 authored characters therefore spread across 2–4 places, which is
          the intent — a cast is a subset of a roster, not the whole of it.
          🔴 **FARMING IS NOT ATTEMPTED AND THIS IS NOT AN OVERSIGHT.** §2.1: three
          independent shipped walls, the worst being `WorkGiver_GrowerHarvest.ShouldSkip`,
          which opens `if (pawn.GetLord() != null) return true;` — **any lorded pawn skips
          harvest, even a colonist.** Sustenance is PRESENT, not produced: give the place a
          larder in `stock` and leave it visible, stealable and destroyable. Owner: *"I
          like that their food stocks are exposed. Very realistic."*
verify:   a quicktest map on a tile carrying the mutator spawns the cast, and the Lord
          exists (`Find.CurrentMap.lordManager.lords` non-empty). Roster count before
          and after a map cycle with no combat is EQUAL.
criteria: land, leave, return: the same named people are there. Kill two, leave, return:
          the roster is short by exactly two and no record of them exists anywhere.
state:    ⭐ **MECHANISM BUILT, CONTENT MISSING** — 2026-08-20, `f0a9f6c`.
          `GenStep_InhabitedCast` + `GenStepDef Inhabited_Cast` (order 900) are in and build
          clean. Roster-out, `MakeNewLord`, spawn, and roster-back-in are all wired.
          🔑 **Return of survivors is a Harmony prefix on `Verse.Game.DeinitAndRemoveMap`,
          not a GenStep hook.** `Game.DeinitAndRemoveMap` runs
          `Notify_MyMapAboutToBeRemoved()` and then `MapDeiniter.Deinit`, whose FIRST act is
          `PassPawnsToWorld` — every pawn despawned and handed to `WorldPawns`. The prefix
          is the last instant the cast is still standing on its own ground;
          `MapComponentUtility.MapRemoved` fires afterwards and is far too late.
          ⛔ **BLOCKED ON CONTENT, and it is not BUILD's to invent:** DECIDE's cast-size
          table is in the spec above and is now expressible — `InhabitedCastDef.castSize` —
          but **no `InhabitedPlaceDef` or `InhabitedCastDef` instance exists yet**, and
          neither does any `TileMutatorDef` naming `Inhabited_Cast` in its `extraGenSteps`.
          Those need the 269 authored characters as data first, which is
          `CAST_ROSTER_MACHINE_READABLE_1` below.
          ⛔ Farming is not attempted, as specified. `InhabitedPlaceDef.larder` carries the
          present-not-produced sustenance and the reason is commented at the field.

## INHABITED_DAY_NIGHT_ROUTE_1 One toil that reassigns duty, and a sleep JobGiver
spec:     §6. ROUTE is barracks → worksite → barracks across a day.
          🔴 **DO NOT BUILD A StateGraph WITH TRANSITIONS.** `Lord.ExposeData_StateGraph`
          serialises toils by **positional index** and re-runs `CreateGraph()` on load, so
          changing toil ORDER silently corrupts existing saves. Vanilla's own graphs are
          safe only because they never change; ours will be re-tuned.
          ⇒ **ONE `LordToil` that reassigns duty on a tick.** The schedule becomes ordinary
          C# inside that toil and can be edited freely forever.
            `src/Jawa/Inhabited/Source/LordToil_InhabitedRoutine.cs`
            `src/Jawa/Inhabited/Source/JobGiver_SleepAtNight.cs`  (~30 lines, §6)
verify:   `dotnet build` clean; a save taken mid-routine reloads with the Lord intact and
          the same toil index.
criteria: watch a cast over one in-game day — they work by day and are in the barracks at
          night, and a save/load mid-day does not scatter them.
state:    built 2026-08-20, `f0a9f6c`. Build clean. The watch-a-day half is CHECK's, filed
          as `INHABITED_ROUTE_ONE_DAY_1`.
          🔑 **The graph is ONE toil and must stay one forever.** `LordJob_Inhabited.
          CreateGraph()` returns a `StateGraph` whose only toil is
          `LordToil_InhabitedRoutine`; there are no transitions and no `LordToilData`, so
          nothing in this job is index-serialised at all. The stance field is deliberately
          NOT scribed — on load `CreateGraph()` rebuilds the toil, the field returns to its
          default and the next reassess reassigns. Self-healing by construction.
          ⭐ **The ROUTE is the DUTY'S FOCUS moving, not the duty changing.** One `DutyDef`,
          `Inhabited_Resident`, modelled on Core's `DefendBase` from
          `Data/Core/Defs/DutyDefs/Duties_NonPlayerHome.xml`, with `JobGiver_SleepAtNight`
          inserted above the `SatisfyBasicNeeds` subtree. The toil moves the focus between
          the worksite (day) and the barracks (night) every 600 ticks, and pins it to the
          pawn's own position while `lord.lastPawnHarmTick` is recent — a cast under fire
          does not walk to the barracks because the clock said so.
          ⚠️ **`ThinkNode_Priority` takes its subnodes IN ORDER**, not by `GetPriority`, so
          the XML order is the behaviour: fight back -> turn in at night -> eat and rest ->
          keep warm -> wander. Re-tuning means moving a line in that file.

## INHABITED_BEGGARS_FROM_POOL_1 The beggars at your gate are the people you burned out
spec:     §4.1 consumer 2. ⚠️ **Two corrections to the design doc before you start:**
          🔴 (a) The doc's `GiveQuest_Beggars` DOES NOT EXIST. The real class is
             `RimWorld.QuestGen.QuestNode_Root_Beggars`, and the pawns are made at `:103`,
             `quest2.GeneratePawn(new PawnGenerationRequest(beggar, faction2, ...))`.
             That is the Harmony target.
          🔴 (b) `faction2` is a **hidden generated faction** built at `:73` from
             `FactionDefOf.Beggars` — beggars do NOT belong to an existing faction. So a
             Hutt refinery survivor cannot simply be handed over; the patch must draw from
             the pool AND move the pawn into the generated beggar faction, keeping name,
             traits, backstory, relations and memories. `Pawn.SetFaction` does this.
          ⚠️ (c) `:44` is `ModLister.CheckIdeology("Beggars")` — **the whole quest is
             Ideology-gated.** If Ideology is off in the shipped list this item is inert
             and that is not a bug; confirm against `ModsConfig.xml` before debugging.
verify:   `dotnet build` clean; the transpiler/postfix reports a patch target found — ⚠️ a
          Harmony patch that matches nothing throws at startup, unlike an XML one, so this
          one is loud. Good.
criteria: burn out a cast, wait for a beggar event, and at least one beggar is a pawn from
          the pool by name.
state:    ready

## CAST_ROSTER_MACHINE_READABLE_1 269 prose characters become data
spec:     ⚠️ **The blocker nobody has looked at.** The eleven cast files hold 269 authored
          characters as PROSE. Measured 2026-08-20:
            present on every entry: name · race (a prose string, not a def) · gender
              (`m`/`f`/`none`/`f-presenting`) · age (int) · `traits:` (REAL `TraitDef`
              names, some with degree, e.g. `NaturalMood(Sanguine)`,
              `DrugDesire(ChemicalFascination)`) · `childhood:` · `adult:` · `hook:`
            absent from ALL of them: xenotype · pawnKind · faction defName · apparel ·
              skills. Weapons and genes appear only incidentally inside prose.
            ⚠️ `INHABITED_CAST_DROIDS.md` uses DIFFERENT FIELDS by owner ruling — `chassis`
              replaces race and `service-years` replaces age. Handle it, do not normalise
              it away.
          Write `src/RimMandrake/Utils/cast_to_xml.py`: parse the eleven files into
          `src/Jawa/Inhabited/Defs/CastRoster_<FACTION>.xml`, one `<Inhabited.CharacterDef>`
          per character, carrying the authored fields verbatim plus the parsed `traits` as
          real defNames.
          🔴 **DECIDE owes you the four fields the prose does not carry** — xenotype,
          pawnKind, apparel and skills. They are filed as `INHABITED_OPEN_QUESTIONS_1` in
          `queue/DECIDE.md`. ⇒ **Build the parser and the def for what EXISTS now**; leave
          those four fields optional and empty. Do not invent values for them — a guessed
          xenotype ships a wrong-looking person into a frozen world.
          ⚠️ **The twelfth faction has no cast file.** Deepwater Compact (*the Balance*) is
          tabled at `INHABITED_DESIGN.md:485-497` but has no `INHABITED_CAST_*.md`. That is
          DECIDE's authoring debt, not a parser bug. Make the tool skip it cleanly.
verify:   the parser emits 269 `CharacterDef`s across 11 files, and
          `python3 skills/rimworld-modding/scripts/validate_patch.py` reports every
          `traits` entry resolving to a live `TraitDef`. A trait that does not resolve is
          the ONE thing here that must fail loudly.
criteria: the defs load with 0 red errors, and a named character from the roster can be
          spawned by defName through the bridge.
state:    ready
