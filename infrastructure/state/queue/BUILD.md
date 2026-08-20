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
state:    ready — 🔴 **SEQUENCING REVERSED BY THE OWNER, 2026-08-19: BUILD IT ALONGSIDE
          THE ROSTER.** Pawn kinds and FactionDefs reference each other, so building them
          together avoids authoring every `pawnGroupMaker` twice. The superseded 2026-08-15
          text follows and is kept only so nobody re-derives it:
          ~~⭐ **OWNER RULING 2026-08-15: v1, but SEQUENCED AFTER WORLDGEN.**~~
          Measured, not assumed: `FACTION_SPEC.md` cites ZERO `Jawa_<Faction>_<Role>`
          kinds — every `pawnGroupMaker` names a donor kind — so B45–B51 do not depend
          on this and it does not bake at world creation. Build it once the factions
          are live and the owner has generated his world. Chain step 3 still supplies
          `weaponTags`/`apparelRequired`.

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

## B58 🔴 `OuterRim_Jawa` no longer exists — our patches still target it
row:      7
spec:     Found in the 2026-08-15 08:12 load harvest. Switching the three donor
          mods off and `mandrake.starwarsraces` on RENAMED the Jawa pawn kinds and
          xenotypes. The old names survive nowhere as defs — only as dangling
          references inside `InteractionDef.json`.
          LIVE NAMES, from the 08:09:57 def dump at 576 mods:
            PawnKindDef  `RimMandrake_Jawa` · `RimMandrake_JawaTribal` ·
                         `RimMandrakeJawa_Kind`
            XenotypeDef  `RimMandrakeJawa` · `MandrakeJawa`
          GONE: `OuterRim_Jawa`, `OuterRim_JawaTribal`.
          WHAT ACTUALLY FAILED THIS LOAD (Player.log :804-:807):
            `PatchOperationAdd(xpath="/Defs/PawnKindDef[defName="OuterRim_Jawa"]")`
            — Failed to find a node with the given xpath, then the enclosing
            `PatchOperationConditional(.../apparelRequired)` errored in `<nomatch>`.
            Source: `Jawa_Patches/Patches/SpeciesStartingGear_Tuning.xml`.
          ⇒ **Jawa starting-gear tuning did not apply.** That feeds chain step 12,
          the campaign start.
          Files naming the dead defName, all needing the audit:
          `Jawa_Patches/Patches/SpeciesStartingGear_Tuning.xml` ·
          `Jawa_Patches/Patches/JawaXenotype_Repoint.xml` ·
          `Jawa_Patches/Defs/FactionDefs/JawaJunkers.xml` · and 10 files under
          `JawaVoice/Patches/` (interactions, insults, romance, prisoners, etc).
          ⛔ **The JawaVoice half of this audit is DEPRECATED — owner, 2026-08-16:**
          *"Deprecate all future Jawa Voice checking. Those items are no longer to be
          tracked or pursued unless bugs are seen in game."* Do not audit those 10 files,
          do not chase their baseline-2 ops, do not open an item for them. The mod stays
          deployed and active; it is simply not verified by anyone. Only a bug the owner
          sees in normal play reopens it. The `Jawa_Patches` half above is UNAFFECTED
          and still owed. (Edited into BUILD's queue by CHECK, 2026-08-16, on the owner's
          direct ruling and with CHECK the only seat running.)
verify:   `grep -rl OuterRim_Jawa src/Jawa/` returns only prose/About files, and
          `validate_patch.py --defnames <the 08-15 dump>` reports 0 errors on the
          three Jawa_Patches files.
criteria: Next load's harvest shows `Jawa_Patches ops` back at baseline 0, and a
          spawned Jawa carries the tuned starting gear.
state:    done 2026-08-19 — the `Jawa_Patches` half, which is what owner ruling 7 says is
          owed. `SpeciesStartingGear_Tuning.xml`'s operations already named the live kind;
          only its header still described the dead one, so the gear tuning was NOT the
          thing broken. `JawaXenotype_Repoint.xml` was: both its operations pointed at
          `OuterRim_Jawa` / `OuterRim_JawaTribal`, neither of which resolves any more, so
          both had been silently doing nothing.
          🔴 Retargeting it turned up a live defect nobody had filed: `RimMandrakeJawa_Kind`
          — `defaultFactionDef PlayerColony` — rolls `RimMandrakeJawa` (24 genes) where the
          owner's 2026-08-14 ruling makes `MandrakeJawa` (35 genes) the only active Jawa
          xenotype. Both are labelled "Jawa", so it is invisible in play. The patch now
          replaces it. 578-mod scoped run: 0 errors, 1 match on both the test and the inner
          op. Deployed. Live half filed to `queue/CHECK.md`.
          ⏭️ NOT closed by this: the C40(a) `NeolithicMeleeDecent` question recorded above.
          The workshop-wide scan that was abandoned after timing out twice is running now
          and its result goes to C40, which owns it — B58 never did.
## drive-the-batched-deploy-pass-8ad4f1
row:      10
spec:     Owner's answers, relayed by CHECK via REP, 2026-08-15. **The deploy pass is
          yours** — REP does not touch deploys, and B0/B1 today were already yours.

          1. **The window is LONG and open-ended.** No relaunch imminent. Spend it on
             ASSEMBLIES first, since those are the only things that ever needed it.
          2. **Deploy the whole parked set, batched — owner picked "all of them":**
             `C36` (donors off, a `ModsConfig.xml` change and therefore no longer
             window-gated at all), `C38` (JawaPlantGrowth, fast growth), `C39` (eopie
             sled), `C41` (four animal-drawn transports). `B0`+`B1` are already closed.
             One deploy pass, one load proves them all. Order and per-deploy traps are
             the manifest at `infrastructure/state/NEXT_RELOAD.md` §1.0 — assemblies
             SOLO, never a new DLL in a mixed batch, or attribution is poisoned for
             everything beside it.
          3. 🔴 **Every deploy lands in `queue/CHECK.md` with a validation plan and a
             NON-EMPTY `criteria:`.** Owner: things you deploy are supposed to land in
             CHECK's queue for testing and checkoff, and it should REQUIRE checkoff.
             CHECK refuses a bare item on policy, so a missing `criteria:` costs you a
             round trip. This is POLICY.md's existing rule, reaffirmed by the owner.
          4. **CHECK is waiting on the D-CHK2 generator fix from you** — Gand, Selkath,
             female Chagrian, Jawa mask. They stay magenta until it lands and redeploys,
             and CHECK does not want them misread as a Facial Animation failure at the
             next load. Get it into this pass.

          FYI, no action: C37 is resolved. The disfigurement was many races, not one;
          CHECK verified the deployed FA config game-down (156 entries, 69
          `Human-RimMandrake*`, 69 XenotypeDefs shipped, zero species unprotected) and
          committed `aa25203`. The "70" in the docs is off by one — 69 is measured.
verify:   `deploy_custom_mods.py --mod <name>` (bare = dry run) read before every `--apply`, one
          mod named per call, never bare; and every deployed mod has an item in
          `queue/CHECK.md` with a non-empty `criteria:` before you call the pass done.
criteria: CHECK accepts all four items without bouncing one for an empty field, and the
          next load attributes each result to exactly one deploy.
state:    done 2026-08-19 — the deploy half is complete and MEASURED, not asserted.
          `deploy_custom_mods.py` with no `--mod` (dry run over every custom mod) reports
          **"Everything in sync"**: every mod's game copy matches the repo, the only
          differences being the 14 files `WreckedMachines` holds back on purpose via
          `DEPLOY_HOLD.txt`. C36, C38, C39 and C41 carry no open item in `queue/CHECK.md`
          either, so there is nothing owed there.
          ⚠️ POINT 4 IS NOT DONE AND IS NOT MINE TO START. The D-CHK2 generator fix —
          Gand, Selkath, female Chagrian, Jawa mask — is parked `⛔ v2` twice over, on
          D-CHK2 itself and on B66, both by the owner's 2026-08-15 blanket triage. This
          item asks for it in the same breath. Raised with the owner rather than resolved
          here; the measurement is in the reply and in
          `queue/HUMAN.md`.
          ✅ The other half of that thread IS done and was checked rather than assumed:
          the owner's "strip any gene that does not resolve" ruling has landed — the
          generated mod ships **69 xenotypes**, including all six species the old
          skip-on-missing-gene behaviour dropped, with Miraluka correctly absent.
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

## btd-jawa-has-no-merge-to-wait-for-8c40b2
row:      4
from:     DECIDE, 2026-08-15. Reopened by the owner's closure of D23.
spec:     🔴 **URGENCY CHANGED.** `FACTION_SPEC.md` R28a left **16 `BTD_Jawa` references
          deliberately unpointed**, parked until "D23's merge" chose between the two live
          Jawa xenotypes. **D23 is now CLOSED — the owner ships the live set unchanged, so
          there is no merge and never will be.** Those 16 references either resolve to a
          def that loads today or they dangle through the worldgen run.
          Live names, from B58's 08:09:57 dump: XenotypeDef `RimMandrakeJawa` and
          `MandrakeJawa`; `BTD_Jawa` measured as SURVIVING (`FACTION_SPEC.md:643`).
          (a) Resolve all 16 to a defName present in the 2026-08-15 dump.
          (b) Where a reference is on a FactionDef, it is worldgen-baked — those come first.
verify:   `grep -rn 'BTD_Jawa' design/ src/Jawa/` shows no reference that fails to resolve
          against the 2026-08-15 dump; `validate_patch.py --defs` 0 errors on every file
          touched.
criteria: no `Could not load reference to Verse.XenotypeDef` line naming a Jawa xenotype in
          the next load's `harvest_log.py --show scribe`.
state:    done 2026-08-19. The item asked which of two Jawa xenotypes to resolve 16
          references to. Measured instead of chosen, and the question dissolved twice over:
          `BTD_Jawa` does not load at all any more, and `MandrakeJawa` is not "half the
          canon" — it carries 32 of `RimMandrakeJawa`'s 24 genes, missing only three hair
          genes on a species already ruled bald, beardless and hooded. So `MandrakeJawa`
          outright, which `ideoligion/APPROVED.md` had said all along.
          12 xpaths retargeted across the two tuning patches, deployed, 0 errors 0 warnings,
          and every "0 nodes on disk" notice cleared. R28a rewritten as resolved; the stale
          "`BTD_Jawa` survived" claim struck from `FACTION_SPEC.md`, `JawaJunkers.xml`,
          `Jawa_EyeColours.xml` and `tidally_locked_world.md`. Live half filed to CHECK.
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
state:    ready

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
