# NEXT_RELOAD — ARCHIVE. Run sheets for loads that have already happened.

**Nothing here is a plan.** Every block below was the run sheet for a load that has since
been launched, harvested and closed. They are kept because a run sheet records what was
BELIEVED before a load, which is the only way to judge what the load actually proved.

🔴 **THIS FILE ROTS ON A CYCLE AND THIS IS THE SECOND CLEARANCE.** `NEXT_RELOAD.md` is a
queue for ONE event, so every load leaves its brief behind and the next reader cannot tell
plan from history. §0's own preamble records the first pass — *"the previous brief was
written 2026-08-20 07:35 and described a load that has since happened… ten items it listed
as pending are already done"* — which closed `RUN_SHEET_REASSEMBLE_AFTER_LOAD_1`. It then
grew back to 911 lines against a 400 budget in two days.

⇒ ⭐ **The fix is a lifecycle, not another sweep:** the run sheet should carry per-load
blocks with an index, the way `EXPECTED_FAILURES_next_load.md` does, so a spent load is
marked spent in place instead of being indistinguishable from the live one.

⛔ **MOVED, not deleted.** Blocks are byte-identical to how they stood.

---

## Archived 2026-08-23 — the 2026-08-22 EVENING load

It ran. Its score is in `EXPECTED_FAILURES_next_load.md` §5: **7 of 8 signatures passed and
F6 failed at 3,037 cross-reference failures against a baseline of 25**, because 26 BiomeDefs
had been discarded at load. That failure is closed as `MAP_BIOMES_REMOVED_LIVE_1`.

---

> ## ✅ THE HOLD CONDITION IS MET — BUILD, 2026-08-22
>
> `CAST_ROSTER_SKILLS_DISCARDED_1` has landed. **The owner's 10:58 hold is discharged and
> this load may be launched when he is back.**
>
> 🔑 **The cause was the opposite of what the item said, and the XML half was already
> fixed a day before it was filed.** `SkillGain` carries `LoadDataFromXmlCustom`, so the
> ELEMENT NAME is the skill and its TEXT is the amount. The rosters had been emitting
> `<li><skill>X</skill><amount>N</amount></li>`, where the name is "li" and `FirstChild`
> is the `<skill>` element whose `.Value` is null — `float.Parse(null)` throws and the
> whole def is discarded. The log this was diagnosed from carries the proof in one line:
> `Could not resolve cross-reference: No RimWorld.SkillDef named li found`. `c6060ae8`
> converted all twelve files on 2026-08-21 16:07; the Player.log quoted at 08:40 the next
> day is from a session that STARTED BEFORE that commit (the file is appended for the life
> of a run; its mtime is the last write, not the launch). **What was still live is that
> `cast_to_xml.py` STILL EMITTED THE OLD SHAPE** and would have reverted the fix on its
> next run. Fixed at `b24dde99`; re-emitting now reproduces all twelve committed files
> byte-for-byte.
>
> ### ✅ ALREADY VERIFIED OFFLINE, 2026-08-22 — do not spend the load re-checking these
>
> | checked | result |
> |---|---|
> | every custom mod deployed | **in sync**, 14 files held on purpose (`WreckedMachines` + 1 genebank texture, owner parked to v2) |
> | JawaBench companion | rebuilt and deployed; game copy **byte-identical to HEAD**. It is not a mod — RimBridgeServer loads it from `<RimWorld>/BridgeTools/JawaBench/`, only at startup |
> | `The Salvation.rid` · `MandrakeJawa.xtp` | both byte-identical to the repo |
> | ModsConfig | 578 listed, 578 resolved, **0 missing**; fingerprint `49b83562b10df31c` matches the frozen OFFICIAL entry |
> | load ORDER | every patch loads after what it patches — DesertVehicleReskin 547 > Alpha Vehicles 534; Jawa_Patches 571 > StarWarsRaces 567 and > Big and Small core 536; JawaIonWeapons 570 > Outer Rim Core 539 |
> | all **69** `Patches/*.xml` | re-validated against the real load set after a validator bug was fixed: **0 errors** across 69 files. Exactly one dead xpath and it is harmless (`HeadSetForFA_Revive` targets a def Facial Animation generates at runtime). The 1,883 warnings are the add-if-missing idiom, already triaged. `validate_patch.py` now has a selftest (`selftest_validate_patch.py`, 8/8) proved to fail without the fix |
>
> ⚠️ **`mandrake.phytokinbarkheadfix` and `mandrake.kotorbandoliernorthfix` are STILL out of
> ModsConfig and that is correct** — the owner's 2026-08-14 baseline-shot ruling (B1, B2)
> wants the donors' unmodified art. `mandrake.cereanmanefix` is out because its target mod
> is inactive. ⛔ Do not "fix" the mod list by adding them.
>
> ### 🔴 WHAT THIS ONE LOAD MUST PROVE — everything BUILD landed 2026-08-22
> Grouped by where to look. ⚠️ **53 items across BUILD and CHECK cannot move until the
> game is up** — 23 BUILD, 30 CHECK, counted 2026-08-22 from the `needs:` lines in
> `queue/*.md` (`bridge`, `game-up` or `harvest`). The older "thirteen" here counted
> only one seat's and only one day's. Recount rather than trust it:
> ```
> grep -c "^needs:    \(bridge\|game-up\|harvest\)" infrastructure/state/queue/*.md
> ```
>
> **In `Player.log`, before touching anything:**
> ```
> measure count-errors "C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log" --top 12
> ```
> - ⭐ **`[JawaBench] ready: N tools, build <hex>`** — 🔴 **N must be 121.** Its ABSENCE means the
>   companion did not load, which used to be indistinguishable from a healthy run.
>   Expect **121** with `--gm`; **119** means the GM flag was not set, and any other
>   number means tools did not register. ⚠️ **This line said 119 and contradicted line 109
>   of this same file, which already said 120.** Measured 2026-08-22: 120 distinct
>   `jawa/…` names in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs`, of which
>   exactly two (`jawa/fire_incident`, `jawa/send_letter`) are the GM pair compiled in
>   only under `-p:JawaGmTools=true`. Recount rather than trust either number:
> ```
> grep -rhoE '"jawa/[a-z_0-9]+"' src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs | sort -u | wc -l
> ```
> - ⭐ **`jawa/vehicle_components` is the 121st and is NEW this load** — it was 120 before
>   `726d8386`. It reads a Vehicle Framework vehicle's component health, which is NOT in
>   `health.hediffSet`, so `jawa/pawn_health` reports a wrecked vehicle as undamaged.
>   Fold it into the L5 row, which already spawns four vehicles:
> ```
> jawa/vehicle_components                     # no args: lists every spawned vehicle
> jawa/vehicle_components pawn=<thingId>      # one vehicle, component by component
> ```
>   Expect a non-empty `components` list with `key`, `label`, `health`, `maxHealth`,
>   `efficiency`. ⛔ **An empty list is NOT a pass** — the tool is built to REFUSE when its
>   reflection chain breaks precisely because empty reads the same as undamaged. On a
>   non-vehicle pawn it must answer `isVehicle: false` and point at `jawa/pawn_health`.
> - ✅ **The companion was rebuilt and deployed 2026-08-22 and the game copy is now
>   byte-identical to HEAD.** It is NOT a mod: RimBridgeServer loads it from
>   `<RimWorld>/BridgeTools/JawaBench/`, outside ModsConfig, and only at startup.
> - **`[Inhabited] ready: … 294 characters …`** — not 193. That is the cast fix.
> - **Zero** `Exception loading def from file CastRoster_*` and **zero**
>   `SkillDef named li`.
> - ⚠️ `measure count-errors` is itself new and validated against this same log's known
>   answers (101 and 101). A `grep -c` on that log gives 148, 1007 or 122 depending on the
>   pattern; only one of those is the number of distinct errors.
>
> **🔴 THE DUMP PRODUCER IS NEW THIS LOAD — check it FIRST, before anything else.**
> `RimDefDump.dll` was rebuilt and deployed 2026-08-22 (`b9d3e8b0`) and has never run.
> `dump_request.txt` still reads `all`, so this load WILL take a capture, and it will be
> the first one written under the dated layout.
> ```
> [RimDefDump] starting, mode=all, capture=<id>, out=…/DefDump/captures
> [RimDefDump] capture published: …/DefDump/captures/<id>
> ```
> - Both lines must appear. **`capture published` is the one that matters** — everything
>   is written under `captures/.writing/` and only an atomic rename makes it a capture, so
>   its absence means the capture did not happen, not that it half happened.
> - Then, from the repo:
> ```
> python3 src/RimMandrake/Utils/game_paths.py            # `current capture` = the NEW id
> python3 ~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py build
> python3 ~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py count RimWorld.AbilityDef
> ```
> - ⚠️ **`measure build` must be re-run before any count is believed.** `defs.sqlite` sits
>   at the DefDump ROOT and is derived from whichever capture is current; after a new
>   capture lands it describes the OLD one, and nothing about the file says so.
> - ⛔ **`captures/2026-08-21T22-44-59Z/` must still be there afterwards.** It carries a
>   `.keep` marker because it is the frozen OFFICIAL, and retention must never prune it.
>   If it is gone, the keep-marker path is broken and the frozen design target is lost.
> - A leftover `captures/.writing/` after the load means the capture died mid-write. That
>   is safe by construction — no reader will match it — but it wants looking at.
>
> **⭐ EVERY BIOME'S WILDLIFE IS REPLACED THIS LOAD — new, and the biggest content change here.**
> `BiomeCast_Ashkarr.xml` shipped at `c60cd9b1`: **26 biomes, 754 records**, replacing
> shipped `wildAnimals` lists that held ~1,024 records almost all at commonality 0.
> - Expect **~29 creatures per biome** on the pyramid 4 tiny · 8 small · 8 med · 5 large ·
>   3 huge · **1 super-huge**, at 1.0 / 0.7 / 0.4 / 0.18 / 0.07 / **0.012**.
> - 🔑 **581 creatures appear in exactly ONE biome and NONE appears in four or more** —
>   the ubiquity the owner objected to. If one creature turns up everywhere, that is the
>   finding.
> - **458 dormant creatures are brought to life.** Seeing unfamiliar fauna is the expected
>   result, not a bug.
> - ⛔ **`animalDensity` is untouched.** `AB_RockyCrags` still runs 1.8 over what is now a
>   29-creature cast rather than 14, so it should read very differently — that is known and
>   is `CREATURE_DENSITY_PER_TILE_1`, not a new defect.
> - Backing it out is one command:
> ```
> rm "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml"
> ```

> **⭐ 37 CREATURES ARE RENAMED — the Latin binomials are gone.** `c4a50c96`, deployed.
> `Andrewsarchus` reads **krondar**, `Dinornis`'s clade-mate reads **kessik**, and so on;
> the coinages share morphemes by clade so the ecosystem reads as evolved.
> - 🔴 **LABEL ONLY — no `defName` changed.** If a quest, incident or another mod's patch
>   breaks, this is NOT the cause and looking here wastes the load.
> - ⛔ **Four names in the doc did NOT ship and that is measured, not a miss:**
>   `Protovermes` and `Compsognathus` are not in the dump at all; `Dinornis` and
>   `Sivatherium` exist but are not in the cast, so no rename was generated. Filed as
>   `CAST_MISSES_TWO_NAMED_BEASTS_1` for DECIDE. Seeing those two still Latin is EXPECTED.
> - Mythic Ages names (`dunbear`, `duskhorn`, `manehound`, `hellboar`) are deliberately
>   untouched — the bestiary wants that English-compound register as contrast.

> **Body size is REAL now — one bridge read settles the whole thing:**
> ```
> jawa/spawn_pawn xenotype=RimMandrakeWookiee   then read its BodySize
> jawa/spawn_pawn xenotype=MandrakeJawa         then read its BodySize
> ```
> - Wookiee **1.75**, Jawa **0.65** — a **2.7x** ratio in carrying capacity, food, melee
>   and health scale, not in the sprite alone. 1.00 on either means `BodySizeIsReal.xml`
>   no-opped.
> - A species in the -0.20 band (`RimMandrakeBothan`, `RimMandrakeSullustan`, …) reads
>   **0.80** — our own `RimMandrake_BodySizeGene_small`, mechanical since `1c3a673f`.
> - ⚠️ **BOTH Jawa xenotypes must read 0.65.** The Star Wars pack ships its own
>   `RimMandrakeJawa` beside our `MandrakeJawa`, and until `1c3a673f` only ours was
>   patched — two Jawa standing side by side at different sizes. If they differ, the
>   `RimMandrakeJawa` operation in `BodySizeIsReal.xml` did not match.
> - The small genes also got their metabolism (`_small` +1 → **+3**, `_smaller` +2 → **+5**),
>   so small species genuinely eat less. That shows in the gene assembler, not on a pawn.
> - ⛔ **Nothing may read 2.00 or over.** That is Big and Small's giant-weapon threshold
>   and anything at or above it silently gains the 23 `BS_GiantWeapon` weapons. The
>   ceiling is `HalfJotunFrame` at 1.75 on purpose.
> - `RimMandrakeHerglic` reads **1.75** and carries exactly ONE gene with the `BodySize`
>   exclusion tag — it used to get `Outland_BodyScale_Large` plus `HalfJotunFrame` and
>   they fought.

> **On the Configure Factions page — the owner's eyes, nobody else's:**
> - all **eight** authored `Jawa_*` factions listed, sorted above vanilla's rows.
>   Seven of them read `maxConfigurableAtWorldCreation −1` until `b95556a3`.
>
> **Through the bridge, once CHECK has it:**
> - `jawa/faction_leader_get` — all twelve authored factions show their AUTHORED
>   `effectiveTitle`. The Junkers' Scraplord, not `Awoken Cheese`.
> - `jawa/ideo_of` the Junkers — **4** memes and `structureMeme AM_Structure_Scavenger`.
> - a raid from `TribeCivil`, `Pirate` and `Empire` — **zero vanilla kinds**; then a trade
>   caravan and a settlement from each, to prove the non-combat groups survived.
> - `jawa/damage` a `Mech_Scyther` with the ion blaster — `stunned=True`, far fewer than 13
>   hits. Then a `Tribal_Warrior`: still down alive at ~6 hits with zero injuries.
> - the 48-kind armed sweep, and a 5-roll sweep of `Scavenger`, `Town_Trader`,
>   `Mercenary_Sniper`, `Hunter` and `Mechanitor`.
> - 20 spawns each of the eight Empire/Blackstar kinds — zero violence-disabling
>   backstories; the other ten families within noise of 13/180.
> - six spawns of `Jawa_Colonist` — robe and hood, no jeans.
> - 🆕 **the cache audit, added 2026-08-22 in the game-down window.** One command:
>   ```
>   python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\prove_world_cache_audit.py
>   ```
>   ⭐ **Read `[JawaBench] ready:` for 121** *(this line said 120 until 2026-08-22 21:5x;
>   a peer added `jawa/vehicle_components` at `9e79e3d2` and the DLL was rebuilt to md5
>   `1b24c77e`)* — `jawa/world_cache_audit` is new this
>   load, so **120 means `vehicle_components` is missing and 106 means the whole
>   2026-08-22 build never landed**. ⚠️ 119 is a DIFFERENT fault — it means the `--gm`
>   flag was not set, so the two GM-gated tools are absent. The harness arms a cache, repaints
>   under it and requires a non-zero stale count; **its last step needs a SECOND load** (save,
>   reload, expect `staleTotal == 0`) and it says so rather than pretending.
>
> ⚠️ **THE SCENARIO IS THE ONE THING THAT CANNOT BE TESTED BY A QUICKTEST.**
> `Jawa_UtinniStart` could not start a game at all before `6b9a79b9` — `ConfigErrors`
> wanted `playerFaction` and `surfaceLayer`, and with no config-page part the game walked
> to `InitGameStart` with **zero colonists**. It now inherits `ScenarioBase` and configures
> six `MandrakeJawa` through a xenotype part. **Proving that means starting a game from it
> and stopping at the pawn page**, which is the owner's act, not a bridge call.
>
> 🔑 **Nothing below this block has been re-checked against today's work.** The 2026-08-20
> sheet has since been REASSEMBLED by DECIDE (2026-08-22 13:05); `RUN_SHEET_REASSEMBLE_AFTER_LOAD_1` is closed.


> ✅ **DISCHARGED 2026-08-22 — the condition below was MET. Kept for provenance; do not
> read the ⛔ as live.** `CAST_ROSTER_SKILLS_DISCARDED_1` has landed (`c6060ae8` +
> `b24dde99`), so the hold has done its job and the load may be launched.
>
> 🔴 **OWNER RULING 2026-08-22 10:58 — THE COLD START WAS HELD.** Asked what the next load
> is for, he chose: *"Both — hold until the cast fix lands, then one load."*
>
> ⛔ ~~**Do not launch until `CAST_ROSTER_SKILLS_DISCARDED_1` has landed.**~~ The five things
> already deployed and unproven (Flamebow off the kill list, `Flamebow_TagWiden.xml`,
> `JawaIon_FieldOurOwnGun.xml`, and the two assemblies deployed 10:30) are NOT urgent
> enough to buy a load of their own — they ride along with the cast fix. **One load
> answers everything; launching now costs two.**
>
> 🔑 **The reason is the architecture gate, not the deploys.** `ROSTER_SOAK_100_DAYS_1`
> measured against 193 of 294 people produces a baseline that has to be thrown away and
> re-measured, and a re-measure is another ~25 minutes.
>
> ✅ **BUILD owns the cast fix.** The owner confirmed the item stays filed where it is;
> CHECK does not take it.

> ✅ **REASSEMBLED — DECIDE, 2026-08-22 13:05. The staleness banner that stood here is GONE,
> not struck: a banner left on a corrected file trains everyone to ignore banners.**
> §0 below now describes the load that is actually about to happen. `RUN_SHEET_REASSEMBLE_AFTER_LOAD_1`
> is closed. **Ten items the old brief listed as pending were already done** — that is what made
> it dangerous rather than merely old, and they are named in §0 so nobody re-adds them.

> 🔴 **STANDING OWNER RULING — 2026-08-15. THERE IS NO WORLDGEN FEATURE, IN ANY VERSION.**
>
> Verbatim: *"There is no auto worldgen we are building. The world will be user-made and
> frozen. We are NOT enabling worldgen, we will provide players a savegame with a fixed
> world, period. That's it. True worldgen is OUT of any version, even v2."*
> Clarified moments later: *"(but designing worldgen by hand and design documents to
> guide that are in)"*
>
> **OUT, permanently — this is not a deferral:**
> - Any automated or programmatic worldgen we build. No tool, script, DLL or bridge verb
>   that generates a world as a product.
> - Worldgen as a player-facing capability. **Players never generate anything.** They
>   receive a savegame containing the fixed world.
> - Any v2 worldgen item. ⛔ **v2 is NOT a parking space for this** — mark such work
>   dead, do not move it to `design/V2_DREAMS.md`.
>
> **IN, unchanged and still wanted:**
> - The owner building the world **by hand, once**. That is how the fixed world exists.
> - **Design documents that guide him doing it** — `WORLDGEN_FACTION_CHECKLIST.md`,
>   `SCENARIO_SETTINGS_SPEC.md`, the faction, biome and terrain specs. Keep writing them.
>
> 🔑 **The consequence, and it got stronger rather than weaker:** one hand-made world,
> frozen, then shipped to every player. **A faction, ideoligion or setting absent when he
> builds it is absent from every player's game forever, with no regenerate to fall back
> on.** That is why the faction roster and the faith text stay v1.


_A cold load costs **~23–30 minutes**. It is the scarcest resource in this project.
This file exists so a load is never spent on one question._

**Read top to bottom. It is ordered.** Down-window → call #1 → batches → release.
**Every item names the CALL that produces its evidence.** If a check has no call it
is in §7 (cannot be collected) and you do not attempt it.

Assembled by DECIDE from `infrastructure/state/queue/<SEAT>.md`. Harvest and clear
afterwards — a closed item is deleted. How to spend a load:
`skills/rimworld-load-round/SKILL.md`. What v1 is:
`infrastructure/state/V1_CHAIN.md`.

🔴 **Worldgen is the owner's and it is done by hand.** He builds a world, saves it,
and we ship it as a fixed resource. **No seat runs campaign worldgen, and nothing
in this file schedules it.**

⛔ **Do not add art-fix work.** Standing owner directive: art *fixing* is stopped
until the owner personally verifies art is broken. Art *observation* is welcome —
§5's eyes-on rows are observation, and nothing here schedules a fix.

## 0. ⏱️ PRE-LOAD BRIEF — reassembled 2026-08-22 13:05 by DECIDE

_Closes `RUN_SHEET_REASSEMBLE_AFTER_LOAD_1`. The previous brief was written 2026-08-20 07:35 and
described a load that has since happened (08-22 08:40, 578 mods, rev591, harvested and closed as
`NEXT_LOAD_LOG_HARVEST_1`). **Ten items it listed as pending are already done** — that is what
made it dangerous rather than merely old._

### State at reassembly — ⛔ RE-MEASURE ALL OF THIS IMMEDIATELY BEFORE LAUNCHING

| check | reading at 13:05 | consequence |
|---|---|---|
| game | **DOWN** — CHECK 11:25, 341 processes, no RimWorld, bridge port silent | the deploy window is open |
| deploys | 🟢 **everything in sync**, checked 12:50 — not assumed | nothing waits on the window |
| companion | deployed at **`7be4d084`** | had been one commit behind at `43d24a6e` |
| mod list | **578 active**, `factioncontrol` absent, `FULL.LATEST` clean | 🔴 the ~25-minute load, not the 22-second minimal one |
| cast fix | landed `c6060ae8` · `b24dde99`; regenerates byte-identical | **the reason the hold is discharged** |

🔑 **Why re-measure:** four seats share one working tree. The 2026-08-20 brief was written while
a peer was mid-commit and three of its rows were wrong within twenty minutes. **A measurement
taken at the top of a session describes a repo that has stopped existing.**

### What this load is FOR, in priority order

**1. 🔴 Prove the cast fix.** `[Inhabited] ready:` must read **294**, not 193. It is why we
waited, and every §10 number is void without it. → `CAST_ROSTER_SKILLS_DISCARDED_1`,
`MECH_AND_ARCHER_ARMED_1`. ⚠️ **269 is a dead number** and several item titles still carry it.

**2. 🔴 `WORLD_PORT_SURVIVES_BRIDGE_1` — the owner's own gate, named 2026-08-22.** Step 2 of his
four-step sequence: *"we need to successfully show that it can survive a port into the game
through the live bridge."* ⭐ **Until this passes, nothing downstream about the planet is real.**
Rank it above everything except the cast number.

**3. Things that BAKE AT WORLD CREATION and can never be retrofitted.** Step 3 of the owner's
sequence — these do **not** wait for the map, they run in parallel with it.
  - **The 82 ideoligion precepts.** No offline route exists: `validate_ideoligion.py` reads
    IdeoPresetDef and FactionDef XML and answers *"no religions found"* on a `.rid`.
    **Decision string: none — this is a DIALOG, not a log line.** Load `The Salvation.rid` and
    read the precept list on screen; PASS = all 82 present by defName.
    ⚠️ *"71 missing"* was a scrape bug — the block nests `RitualBehavior` / `RitualOutcomeEffect` /
    `RitualObligationTargetFilter` names, which are not `PreceptDef`s. **Do not re-derive it.**
  - **`LEADER_TITLES_ON_THE_IDEO_1`.** 36 of 37 leader titles come from the generated ideo, not
    the def — the Junkers' Scraplord reads **`Awoken Cheese`**. 🔴 **Live-only, and on the world
    that will actually be frozen**: every offline instrument reads `def.leaderTitle`, which is
    correct and unused, so an offline pass reports success while the defect is fully present.
  - **`PRESET_ONSCREEN_CHECK_UNVERIFIED_1`** — Configure Planet must read **Scale 7 / Coverage
    100%**. If it reads Scale 10 the preset lost its parameters: **ABORT, do not generate.**
    Generating on a stub is unrecoverable.

**4. The pawn-equipment rulings of 2026-08-22 — all quicktest-able, no world needed.**
⚠️ Ride each **only if BUILD has landed it**; an unbuilt item proves nothing and wastes the slot.
  - ✅ **`ION_MACHINE_TIER_MISSING_1` — BUILD shipped it (`9bca7ee3`), so it rides.** A
    `Mech_Scyther` must read `stunned=True` in far fewer than 13 hits; a `Tribal_Warrior` must
    **still** go down alive at ~6 hits with zero injury hediffs. 🔴 **A regression on the flesh
    half is a failure, not a bonus** — the owner's LOCKED SPEC D1 requires both tiers.
  - `BLACKSTAR_NAME_MUST_NOT_LEAK_1` — on a generated world, **exactly one** faction may read
    `Blackstar Company`, and **exactly one** `Galactic Empire`.
  - `AUTHORED_KINDS_MUST_FIELD_1` — every combat pawn from `TribeCivil`, `Pirate` and `Empire`
    must be a `Jawa_*` kind, **and** each faction must still send a trade caravan.
  - `EMPIRE_BLACKSTAR_ALWAYS_WILLING_1` · `BLACKSTAR_DEEPDESERT_POOLS_EMPTY_1` ·
    `VANILLA_KINDS_GET_BLASTERS_1` · `BARE_HANDS_REMEASURE_AFTER_LOAD_1`.

**4b. 🆕 THE WORLD AND ITS FAUNA — authored 2026-08-22 afternoon, AFTER this sheet was
reassembled at 13:05.** ⚠️ **It is the largest untested block riding the load.**
  - **The map changed substantially.** `HorrorWastes` (1,200 tiles), `IceSheet` (80) and
    `SeaIce` (277) are NEW biomes that **have never generated on this planet**. Meridian water
    halved, the Grey Sea given a brine halo, shore zonation applied, `VEE_SaltPlains` on 389
    dried-seabed tiles. 🔴 **`WORLD_PORT_SURVIVES_BRIDGE_1` is now testing a far bigger delta
    than it was written for.**
  - 🔑 **`SeaIce` and `IceSheet` were UNLOCKED in the live Cherry Picker config** (kill list
    1341 → 1339, backup `.bak-2026-08-22` alongside). **If either fails to generate, suspect
    the unlock before suspecting the tiles.**
  - **`BIOME_CAST_APPLY_1`** — 754 `BiomeAnimalRecord`s across 26 biomes, proposed at
    `design/Jawa/fauna/BiomeCast_Ashkarr.xml`. ⛔ **BUILD must wrap the 26
    `PatchOperationReplace`s and re-validate with `--defs` before it ships** — the validator
    gives 0 errors but 26 warnings, and an unwrapped replace against an absent mod logs a red
    error every launch.
  - **What to look for in game:** does each biome field the cast it was given · is the
    super-huge genuinely rare · does any creature turn up everywhere (only `jellybird` should
    reach 4+ biomes) · and **is `HorrorWastes`' ground sand-coloured between black rock and
    ice** — its terrain is still `Sand`/`Soil`/`SoilRich` and that is a known, unfixed defect
    (`HORROR_WASTES_ON_NIGHTSIDE_1`).

**5. The remaining live checks** — §5's batch, plus `LAKE_LINT_NARROWED_NOT_OFF_1`,
`FACTION_NAME_CHECK_TRUSTWORTHY_1`, `JUVENILE_AND_ASHSTORM_UNRUN_1`, `LIGHTSABER_AP_FROM_HAND_1`,
`DROID_ENCLAVE_FIELDS_DROIDS_1`, `JAWA_FARM_AND_DRILL_LIVE_1`.
⚠️ `QUICKTEST_VISUAL_ROUND_1` is **already `doing`** — CHECK owns it; do not start a second one.

### ✅ ALREADY DONE — do NOT put these on the load
The old brief listed several as pending. Verified against the ledger at 13:05:
`NEXT_LOAD_LOG_HARVEST_1` · `CLASSIC_IDEO_ERASES_FAITHS_1` · `FACTION_LABELS_ONE_LOOK_1` ·
`IDEO_ABILITY_DEFS_UNREAD_1` · `LOAD_ABORT_IS_FACTIONCONTROL_1` · `SETTLEMENTS_OFF_IMPASSABLE_1` ·
`INHABITED_ACTION_BRIDGE_CONFIRM_1` · `IONBUILDUP_ACCRUES_ON_FLESH_1` · `DEPLOY_SALVATION_RID_1` ·
`THE_SCALD_LOST_ITS_WATER_1` (superseded).

### ⛔ NOT riding this load, so nobody re-derives it
- **The worldmap edits the owner ordered 13:04** — halve the meridian water
  (`MERIDIAN_WATER_HALVED_1`) and the Grey Sea brine halo (`GREY_SEA_BRINE_PATCHES_1`). They are
  authored into `world/ASHKARR_WORLDMAP_tiles.csv` and reach the game over the **bridge**, not
  through a load — and he ruled them explicitly *after* the reload work.
- **The plant cherrypick.** Nothing is cut (owner, 12:52: *"keep ALL of these plants initially…
  let's run around the world and see how it looks before we actually cut anything"*).
  ⭐ **But walking the world IS a legitimate use of this load** — that is observation, not an art
  fix, so it is permitted under the standing art directive.
- **`ROSTER_SURVIVES_OFFMAP_PROOF_1` needs TWO loads** — save → quit → reload. Do not expect to
  close it on this one.

### Which list each item rides
**578 (this load):** everything above. The cast fix, the ideoligion dialog, the faction/leader
work and the world port all need the content mods.
**Minimal 13 (22 seconds, any time):** the ion tiers, the pawn-equipment spawns and the tag
audits — none of them needs a real world. 🔑 **If BUILD lands more equipment work after this
load, do NOT wait for another cold start; a minimal swap answers it in about a minute.**

### At launch, while it grinds
```
python3 src/RimMandrake/Utils/whats_new.py --seat <SEAT> --mark
```
**Launch, not close** — close is when work lands, so the deltas are not written yet.

### After it
```
python.exe src/RimMandrake/Utils/harvest_log.py
```
You paid for a full load; harvest the WHOLE log, not only what you changed.
⚠️ **`harvest_log.py` changed under the old sheet** — it was counting the load-time patch manifest
as evidence and reporting `303 / 5252 / 2224` RED for MegafaunaYield, `Jawa_Patches` and
`JawaVoice`. All three now read `0 / 0 / 2`. **Any number quoted from the old tool is suspect.**

---
