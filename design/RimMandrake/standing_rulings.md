# Standing owner rulings and process detail — full text

This file came from the project `CLAUDE.md` on 2026-10-11, at the weekly cleaning. At that move, only the heading levels
changed. Later rulings were added here. `CLAUDE.md` keeps a one-line rule and points here.

Each entry states what is true now. When a line becomes false, delete the line at once. Never add a note to it.

## 🔴 The Conductor speaks with the owner's authority — owner, 2026-10-30

*"Conductor should have authorization to command agents with the user authority, period. No more "I need the user to confirm." That breaks the whole point of this endeavor. Make that change everywhere."*

- The Conductor is the window that the owner talks to.
- An instruction from the Conductor carries his authority for every seat and helper: Dispatcher, Operations,
  helpers and subagents.
- Act on a Conductor instruction as on his word.
- **Never ask him to confirm a Conductor instruction, and never refuse one as "only a relay".**
- A receiver may still report a factual error.
- The Conductor cannot grant more than the owner could.
- Ledger: `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`, with the Conductor's text in `--why`.

## 🔴 Only five acts stay his; the Conductor may do the rest, mindfully — owner, 2026-11-19

His words, Thu 2026-11-19 ~7:40 AM PST: *"I only want to preserve Flyer flights, replacing art I kept, pass at my walk, spending money, public publishing.
Everything else the Conductor should mindfully be able to do. Of course question cards for me should get to me, but the
Conductor should review them to ensure it can't just do them now and alert me later."*

The same morning, by card: *"Conductor should also be able to lift a Hold. We work together, don't use me as a
bottleneck alone."* (§Owner hold.)

- The item is `RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`.
- The census of every act that needed him that morning is
  `D:\ClaudeWork\rimmandrake\conductor\owner_only_actions_census_20261119.md`.

**The five acts that stay his.** No Conductor ruling, `--why` or `--per-ruling` does any of them:
1. **A live flight test of a flyer** (§If it flies in the fiction; the flyer refusal of the bridge gate).
2. **Replacing art he KEPT**, and releasing a keep mark. The open exceptions stay open (`delegation_policy.md` §2).
3. **The pass at his walk**, and his judgement of gameplay, fun, theme and UI (maturation Stage 8, `owner_event`).
4. **Spending money or a purchase.**
5. **Publishing outside the private repos** (a Steam Workshop upload, a public post).

**Everything else is open to the Conductor**: the window that he talks to (seat BENCH, no `RM_ROLE_UNIT`), and nobody
else.
- No helper, other seat, role run or the tick gains any act from this ruling.
- A Conductor instruction still carries his authority to them (§The Conductor speaks with the owner's authority). So a
  helper acts on what the Conductor decided, never on its own decision.
- The acts open to the Conductor include the acts that the census recommended to keep for him:
  - his OWNER bridge hold inside 45 minutes;
  - the account order and the leave line of the shared account;
  - deleting or overwriting work that is not ours.
- **Recorded as the Conductor's act, never as his words:** `--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS
  --why "<the act, and the reason>"`.
  - `rimflow` refuses that ruling outside the Conductor window.
  - `rimflow` refuses that ruling when the `--why` has fewer than four words.
  - `rimflow` writes the why as `delegated: conductor act: …`. So each such act is a line of his daily digest (class
    `conductor act`, `delegated_digest.py`).
  - A tool that writes no ledger event writes that note itself.
- **"Mindfully":** four acts must name two things in the `--why`. The first is what is lost if the act is wrong, as
  `lost: <…>`. The second is how to undo the act, as `undo: <…>`.
  - Each of the two has at least three words. The gate refuses an empty or one-word why.
  - The four acts:
    - cutting his OWNER bridge hold inside 45 minutes;
    - changing the account order or the leave line of the shared account;
    - deleting or overwriting work that is not ours;
    - loosening or removing a bar.
- **Code:** `src/RimMandrake/rimflow/conductor_acts.py` (the five, the window check, the why rules; page
  `design/specs/conductor-acts/boundary.md`).

**His cards: the Conductor reviews each one first.**
- Every question card bound for him passes the Conductor first.
- If the act of a card is not one of the five, and no concrete evidence goes against the obvious answer, the Conductor
  acts now. Then the Conductor alerts him after.
- The alert is one digest line with the undo. The `--why` of the act carries the undo.
- Only the other cards reach him.
- This rule sits beside §Evidence-for-Ask and widens it. A card's subject no longer stays his only because an older rule
  called it his.

**What it does not change.**
- The run that enacted this ruling changed neither his user-level instructions (`~/.claude/CLAUDE.md`) nor other repos.
  The ban in those instructions on `push --force` and history rewrites still binds every agent, the Conductor included.
- Physical acts stay physical. An agent still asks him in words for an interactive login, or for a screen that he must
  look at.
- His own words keep their own field. `--owner-said` and `--by-card` are only ever his. The `## his words` section of a
  Designer record is written only from those two fields.
- §No mod runs forward on a broken pipeline still applies. A mod whose readiness list is not READY still does not run.

**Test that it was applied:** `selftest_conductor_acts.py`, and the own selftest of each opened gate.
`selftest_conductor_acts.py` checks three refusals:
- a Conductor act on one of the five is refused;
- a helper is refused every act;
- a mindful act without `lost:` and `undo:` is refused.

## North-star validation state

- 🔴 **Validation state is never written as prose: `modcheck floor --all` measures it.**
- 🔴 **And the 81 walk findings are NOT rot:**
  - `doctor` derives the mod of a walk from the BASENAME of the walk, never from its `subject:` line.
  - So its 24 ORPHAN_WALKs and 10 SUBJECT_COLLISIONs are ONE phenomenon. **34 of 78 walks are deliberate per-feature
    walks that share the subject of a live mod** (MEASURED 2026-09-18).
  - Of the 33 failing walks, 25 have a fully live subject. In those 25 walks, the defect is a stale id inside a STEP.
    **0 are genuinely orphaned**.
  - Never "fix" a walk on an ORPHAN_WALK finding alone.
  - Do not rebuild the 43-row decision sheet. The owner ruled that the sheet was never his to adjudicate
    (*"this doesnt feel like a sheet I should be asked"*).
  - The data of that sheet was also wrong. The subject packageId of a walk is backticked in 28 walks, BARE in 34 and
    absent in 16. So a backtick-only regex reads None for 50 of 78.
  - `DETERMINISM_ASSESSMENT.md` §11a is the account.
  - The walk-model ruling landed 2026-09-18 (owner card): **per-feature walks are first-class via a `feature:` key**
    (`WALK_FEATURE_KEY_1`, done).
  - **The "modcheck status reads a stored field" bug is FIXED** (`fa27e1cab`, live-checked 2026-09-17; the account
    is in `design/RimMandrake/CLAUDE.history.md`).
  - Do not re-open that bug as a live defect without a new measurement. The stored field now appears only as a
    `[stored: ...]` drift annotation.
- Do not casually edit the `## north star` section of a mod.
  - The hash covers the **whole section including explanatory prose**.
  - So a correction of a stale caveat reverts the checklist to DRAFT (hit live 2026-09-16). Then the mod quietly stops
    being refused.
  - 🔴 **Owner ruled 2026-09-17 that this stays as it is** — verbatim: *"Change
    no code — you just re-validate when prose is corrected."*
  - Bar-scoped hashing is **declined, not deferred** (`NORTHSTAR_HASH_SCOPE_1` dropped).
  - So the remedy for false text in a hashed section is: correct the text, then re-validate, in the same sitting.
    Re-validate on his word, or as the Conductor's act under §Only five acts stay his.
  - Never leave false text standing to protect a hash. That trade is now ruled against.
  - Therefore **write only state-independent prose inside that section**. For example, never write "binds
    nothing until validated": that text is false the moment the mod is validated.
  - `modcheck/cli.py validate <Mod>` refuses unless BOTH `state:` and `validated-hash:` header lines exist. A blank
    value is fine.
  - Since 2026-09-17, `modcheck/cli.py validate <Mod>` also refuses a section that parses to **zero bars**. Before,
    a misformatted section recorded VALIDATED against an empty checklist, which bound nothing.
  - For a dry run that writes nothing, omit `--owner-said`.

## In-game LLM access is the Claude Code CLI, never a hosted API key — owner, 2026-09-05

- Every mod that calls an LLM shells out to **`claude -p "<prompt>"`** (Claude Code in non-interactive mode) as a
  subprocess. Such mods are the Oracle, the raid-redesigner and any future consumer.
- Such a mod never makes an HTTP call to an OpenAI-compatible endpoint.

Owner, verbatim: *"Claude Code in non-interactive
mode (`claude -p "..."`) authenticates via your claude.ai login and can be
called from a shell script without any API key."*

- **Supersedes `OracleClient`'s original HTTP/OpenAI-compatible design** (`design/RimMandrake/llm_ingame_wiring_spec.md`
  §1, and the `OracleHttpClient` of `src/RimMandrake/Oracle`).
  - No base URL, no model string, no API key field, no local Ollama fallback.
  - The two laws in that spec stay UNCHANGED: text/menu authority only; the game is whole with the LLM absent.
  - The async/timeout/kill-switch threading shape stays UNCHANGED.
  - Only the transport moves: HTTP → subprocess.
- The game process (Mono/Unity on the owner's Windows machine) launches `claude -p` via `System.Diagnostics.Process`.
  - The game process uses the same off-tick `Task`-based async pattern that is already built.
  - The game process reads stdout instead of an HTTP response body.
- Whoever rebuilds `OracleHttpClient` against this ruling: verify the exact invocation and output shape against a real
  local `claude -p` call before you wire it. Do not assume flags or JSON structure from this note.
- **New environment dependency this creates**: the owner's machine must have Claude Code installed and logged in. Else
  no consumer works at all. This dependency is a fact about his machine now, not a config value in Mod Settings.
- The ruling affects `PLOT_MECHANISM_MODS_WAVE_1` Part 1. The Oracle calls of the raid-redesigner ride whatever
  `OracleClient` becomes.

## A pit is a SUPERDEEP cell, not a building — owner, 2026-09-17

*"I'm not really sure a pit is any different than a deep canal."*

- The ruling is made and fully specified. Its item holds the state of the build; read the state there, with
  `rimflow show PIT_SUPERDEEP_COLLAPSE_1`: `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`.
- A pit is depth 4 on the D/F primitive that rulings 18/19 already established. D/F is depth and fill: each cell
  has a dug depth (D) and a fill of liquid (F). Rulings 18 and 19 are in `design/RimMandrake/flowworks_mod_definition.md`
  (§20 and §21).
- So the fitting concept collapses to **spikes alone**. Oil and poison are FluidDefs. The oubliette is CUT.
- An enclosed superdeep area is a room. The room becomes a prison room once a bed is in it.
- The quote above is his opinion from the sitting before the ruling. The ruling is his 2026-09-17 message, whole in the
  item. Its "you can't climb out. Period." is replaced by his rulings of 2026-10-12 and 2026-10-23: a pit traps each
  creature by its own climb, and a ladder lets a creature out (`design/RimMandrake/relative_depth_climb_design_2026-10-12.md`;
  items `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` and `LADDER_PARITY_BUILD_NO_KEYS_REQUIRED`).
- `capture down` and `convert down` happen from the lip, because a creature that the pit traps cannot leave.
- TEMPERATURE is the softening mechanism.

🔴 **The ITEM is the authority, not the spec.**
- `design/RimMandrake/pit_superdeep_collapse_spec.md` (1127 lines) was written BEFORE three rounds of rulings. Those
  rulings changed ten of its answers. The item lists the revisions that the spec is owed.
- Do not read the spec and act on it without reading the item first. Else you build the version that he rejected.
- The door family shipped as `FLOWWORKS_DOOR_FAMILY_1` (done): **two** stuffable defs. The door family is never the
  three defs that he described and then talked himself out of.

## Shipping names are three-tier — owner, 2026-08-30

- Every NEW packageId, defName, C# namespace and mod folder uses the tier grammar in `design/NAMING_SCHEME_PLAN.md`.
- The three tiers:
  - **RimMandrake**: any RimWorld game;
  - **RimStarWars**: any Star Wars scenario;
  - **RimUtinni**: this campaign.
- The packageId is `mandrake.<tier>.<modname>`. The prefixes are `RM_`/`RSW_`/`RUT_`.
- C# namespaces nest: `RimMandrake[.StarWars|.Utinni].<Mod>`. Never use a bare `RimStarWars`/`RimUtinni` namespace.
- "Jawa" is lore text only. Dev tooling is exempt.

🔴 **The migration is DONE — there is no rename gate any more.**
- `NAMING_SCHEME_EXECUTION_1` closed **2026-08-31** at `54a8e28d`, on the owner's own word (*"Deploy the full
  rename."*). That closure is why the mod set already carries `mandrake.rm.*` / `mandrake.rsw.*`.
- So when a mod is RENAMED after that date, the rename is ordinary owed work. Do the rename. Do not defer it to a
  closed item.
- If a doc cites that item as a reason to wait, delete the citation.

## Every mod ships superb Mod Settings — owner, 2026-09-12

- Every mod that we ship carries a real settings screen, with:
  - an on/off switch per major feature/mechanic;
  - tuning where a number is the experience;
  - defaults that equal the shipped behavior;
  - a mod that degrades gracefully when every switch is off: the game still works;
  - a label on each toggle that acts only on a newly generated map.
- TESTING: a biome mechanic is tested in game only on its home biome. No test away from the home biome is owed.
- That testing ruling is the owner's, 2026-10-15, kept by his card of 2026-11-21:
  *"I would like to release the … requirement that the biome mechanics
  work in other biomes. That's too much of a lift. … We can't guarantee they will work
  in other biomes beyond our framework. They should… but we're not going to validate
  that at this time."*
- A mechanic works by its conditions (§Biome mechanics work by their conditions).
- The switch for a mechanic is a plain on/off, default on, with no biome in it. Each "Enable outside this biome" switch
  becomes such a switch when its mod converts (his card of 2026-11-21).
- Spec and retrofit of existing mods: `MOD_OPTIONS_RETROFIT_1`.
- This rule applies to every future mod, with no exceptions.

## Biome mechanics work by their conditions — owner, 2026-11-21

- The ruling: item `RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES`.
- The principles as entries: `GUIDING_PRINCIPLES.md` entries 1 to 5.
- What each existing mod converts: `design/specs/2026-11-21-guiding-principles/conversion_list.md`.

The ruling:
1. By default, a mechanic works by the physical conditions where it acts. A mechanic does not work by the biome that
   it is in. The conditions are sun angle, heat, water, fire, ground, roof, food, and the like.
   - A biome holds its data: its plants, animals, terrain, weather odds and map generation.
   - A biome depends on a mechanic or showcases it. Or the biome holds the materials or sources to make the mechanic,
     or to make it shine.
   - This rule is a default, not a prohibition. Many mechanics will in effect appear in one biome only, because only
     that biome has the conditions. Examples: tar where there are tar pits, unless a player carries tar; the tiny
     particulates of the Abyss.
2. The stated exception: a mechanic can be a heavy load even where it is not active. Such a mechanic may stay unloaded
   outside its parent biome. That case is the exception, not the rule. The mod's design states the exception with its reason.
3. Testing: a mechanic is tested where it matters, in game on its home biome. The ruling is his, of 2026-10-15, kept by
   card on 2026-11-21 (§Every mod ships superb Mod Settings). No foreign-map check and no offline test is owed for this
   rule.
4. The principle applies to all new design and code from 2026-11-21.
   - Each existing mod converts when it next advances, as a planned change for its next version.
   - No bar of a current version moves.
   - Pyrelands 0.1.0 is not reworked.
5. Six switches are named "Enable outside this biome". The six switches are in Greentide, Pyrelands, RustCathedral, Scarlands'
   Warscar, TerminalBiomes' Scald and TheRot. When its mod converts, each such switch becomes a plain on/off for its
   mechanic.
   The new switch is default on, with no biome in it.
6. A dangerous mechanic is on by default on every map. Its conditions decide where it acts. No default-off list by biome
   exists.
7. The hot water of the Scald is physics, not a biome exception. Water that hot scalds the same way on any map (§Direct
   Sun). The clock of the Scald is rewritten at its next version.
8. Vanilla and third-party biomes follow the same rule: conditions decide. No tag list and no master switch exist.
9. A visible effect with no meaning is removed, not confined. His case is the constant pale marked region round a steam
   geyser. The swirling steam stays.
10. `GUIDING_PRINCIPLES.md` binds.
    - `GUIDING_PRINCIPLES.md` holds at most 7 entries. Each entry has his words, one example that honours it and one
      example that breaks it.
    - Only his ruling adds an entry. Agents may only propose.
    - He adopted three entries on his third card:
      - a limit lives in the world;
      - an effect that implies harm is true;
      - mechanics justify their combined load.
    - He adopted none of these:
      - an offline test for new mechanics;
      - "a biome states how it earns a mechanic";
      - "a biome owns data, not laws";
      - "every effect is actionable".

His words, 2026-11-21 (the ledger's `file` event of the item holds the whole message): *"the white hazy blocks inside the pit I do not think were "TheForge" but yes the geysers were. I didn't mind the steam so much, but the meaningless pale region around steamgeysers I definitely did. And Biome mechanics in general do NOT stay confined to the biome of origin: they are universal, but that biome depends on them, showcases them, or has the materials or sources to make them or make them shine. For example, the Stillshade has nothing "special" about its long shadows and intense sun exposure effects: those should be planet-wide. But the Stillshade showcases them with a unique biome adaptation to them. Make sense? The Rot features a living floor covering that heats rooms and keeps life alive in the cold through food consumption. It works anywhere, but it's native to the Rot and must be tended and carried elsewhere. We should also make it die in direct Sun exposure to explain why the Rot hasn't spread over the whole surface. Please take the GENERAL lessons in this message as guiding principles for the whole game, Baroque Biomes, etc. But then take my specific examples and enact them as well in specific tickets. If there are conflicting rulings, please let's review them right now and correct them to avoid ambiguity. If there are specific conflicts (current mechanics that don't honor these principles) let's also rule on them. But remember: Form first, Specifics later, ok?"*

His three card answers, 2026-11-21 (the item's "What the card said"): (a) What should "universal" mean as a rule for the code? → **Conditions, never the place**: *"A mechanic reads only physical conditions (sun angle, heat, water, fire, ground, roof) and never which biome it is in; a biome keeps only its data."* (Not picked: universal unless a reason is written; only the elements are universal.) (b) How much do we test a mechanic away from its home biome? → **Home only, as ruled in October**: *"The code is written universal; only the home biome is tested."* (Not picked: home plus one foreign map; every mechanic on every biome.) (c) When should existing mods be converted? → **New work now; old mods as they advance**: *"The principle binds all new design and code from today; each existing mod converts when it next advances, as a planned change for its next version."* (Not picked: Pyrelands converts now; one campaign across all mods now.)

His second card, 2026-11-21 (answered 22:35 UTC; the item's notes): (d) What becomes of the six "Enable outside this biome" switches? → **Turn each into a plain on/off**: *"one switch per mechanic, no biome in it. When a mod converts, its switch becomes 'this mechanic: on/off', default on."* (e) Are dangerous mechanics on by default on every map? → **On everywhere; conditions decide**: *"this is the ruling taken at its word. Fire walks wherever the grass is dry."* (f) Under "conditions, never the place", is the Scald's hot water still an exception? → **Physics: hot water scalds anywhere**: *"the harm comes from the water's heat, not the map. Any water that hot, on any map, harms the same way; the Scald is simply where it is common."* (g) Which biome did you mean by Stillshade? His words: *"I accidentally mixed Stillsand and Long Shade. I just meant shade vs. direct sun."*

His words after that card, 2026-11-21: *"For example, if for some reason we put the Rot near the Scald, I would expect the Direct overhead sun to mercilessly overheat characters, burn out the fungus mats on the ground, and the plants would likely all die due to their intolerance of the ambient local heat. But all the mechanics would remain on, just a very different outcome."* (The Conductor read his typed "expend" as "expect".)

His third card, 2026-11-21 (answered 23:23 UTC): (h) Which proposed lines do you adopt? His words: *"A limit lives in the world, An effect that implies harm is true, Mechanics justify their combined load, "No offline testing, we test only where the mechanics matter. And many mechanics WILL effectively only be in a single biome (e.g. tar mechanics don't matter where there are no tar pits... unless the players bring tar somewhere of course). We don't test outside the source biome at this time. Perhaps in future versions, but not now. I also don't want to say it is FORBIDDEN to have a specific biome mechanic, that is not how the rule should be written. I mean to say all of the biome specifics mechanics so far stated are per condition, not by some magic in a specific biome. The Abyss is a good example. There are no tiny particulates on other maps for the mechanic to engage with, so it will never be seen there. If we made a creature with those tiny particulates present, it should still work as in the Abyss... but we're not doing that right now. Make sense? If a mechanic is a heavy load even when not "active" in all other biomes, we may make the call to simply not load it outside the parent biome... I want to preserve that capability. But that should be the exception, not the rule, and stated."* (Not picked: new mechanics owe the offline test.) (i) The three weaker lines → **Adopt none of the three**. (j) How do our mechanics treat biomes that are not ours? → **Same rule: conditions decide**: *"no special case. Fire walks on dry vanilla grass exactly as on ours."* (Not picked: act only on biomes we tagged; conditions decide, plus one master switch.) (k) How much authority does the principles file have? → **Binding, short, only your rulings**: *"At most 7 entries, each with your words, one example that honours it and one that breaks it. Only your ruling adds an entry; agents may only propose."*

## Direct Sun — one model, a pure function of geometry — owner, 2026-09-29 and 2026-10-19

The rule, as the root `CLAUDE.md` carried it:
- Direct Sun feeds **vanilla** heat (felt temperature → Heatstroke).
- The value is 55 °C at the zenith × sin(sun angle). The sun angle comes from the position of the tile on the planet.
- No biome has its own heat kind, number or exception.
- Shade gear is parasols and roofs. A tent is any quick roof.
- Volcanic/steam/fog heat is plain air temperature.
- And **no animal or pawn ever vanishes without a readable sign.**

2026-09-29 (Long Shade sitting): *"If we implement the heat load, then places like the Deep Desert
and volcanic biomes should absolutely roast you similarly. It can't be a new "kind" of heat."*
2026-09-30: *"The biome takes its sun angle from its latitude ok the planet not a region
description."*

2026-10-19, by question card on the design pass
(`design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`):

- Zenith value: *"55 C everywhere"*.
- Shade: *"This is too ornate. Keep only Parasols and Tents, and Tents are just a quick structure
  (any roof structure will do the same). Then we just need to think about where "shade vs not
  shade" is for the various maps, and that's a pure function of geometry, NOT biome. So: no
  biome-specific heat, no biome-specific sun. It's a matter of geometry (low sun is less intense AND
  produces longer shade, high sun produces only covered shade and much more intense effect).
  Ambient heat is normal Rimworld rules."*
- Volcanic, steam and hot-fog heat: *"Hotter air on the thermometer"*.
- Night: *"In Utinni this isn't possible: time of day = location, permanently. If these biomes are
  used on a day/night world, then of course it follows solar angle/geometry that is now a function of
  time of day. If that creates too much work, then drop sun heat (should actually be called "direct
  sun") when the day/night isn't constant anymore. That's not our primary deliverable target."*

- Tree shade (2026-10-19, after the pass): *"Only the day-side biomes with massive trees would have
  massive shade beneath them at a fixed angle, and we need to think about that. Most tree-dense maps
  will be mostly shade then (ambient heat yes, direct sun no). So that needs to be deeply thought
  though. If we have an excellent tree shade model working, then YES direct sun works the same
  everywhere on the day side. If we do not go that route, we may choose to turn it off on tree-heavy
  maps (this would be an inferior option)."*
  - The model and its adopt-or-fall-back test are in `design/RimMandrake/tree_shade_model_2026-10-19.md`.
  - The decision is `TREE_SHADE_DECIDE_CROWNS_OR_LIGHTS_OUT`.

What this means, and how to check that it was applied:
- **The feature is called Direct Sun.**
  - Felt heat = 55 °C × sin(sun elevation) × weather sun factor × the strength dial.
  - The felt heat goes into the vanilla felt-temperature → Heatstroke path. No new hediff.
- **Sun elevation comes from the map tile's position on the planet only.**
  - In Utinni the sun of every map is fixed (time of day = location).
  - On a world with a day/night cycle, the sun follows the clock, or Direct Sun switches off on that world. That world
    is not the primary target.
- **Shade is geometry.**
  - Roofs and parasols cover at every sun angle.
  - Structures and rock cast a shadow. The length of the shadow grows as the sun drops. So a low sun gives long shade,
    and a high sun gives almost no shade beyond covered cells.
  - No BiomeDef field, heat kind or per-biome number changes the shade or the sun's strength.
- **Shade gear is the parasol and roof structures.** A tent is any quick roof. The standing sun shield is not a shade
  item.
- **Ambient heat is vanilla air temperature**, shown on the thermometer. Shade never changes ambient heat.
- **Hot water is physics, not a Scald exception** — owner, by card, 2026-11-21: *"the harm comes from the water's
  heat, not the map. Any water that hot, on any map, harms the same way; the Scald is simply where it is common."*
  - His card of 2026-11-20 still says how hot water harms: *"yes keep the clock, AND it should be even worse in the Scald water
    itself (hot water is not the same as hot air"*.
  - So steam from hot water keeps its exposure clock (`RM_HediffComp_EnvironmentalExposure`). Ordinary heat armour
    answers that clock.
  - The water harms faster than that steam, on any map where such water is.
  - The clock of the Scald is rewritten to read those conditions at its next version
    (`design/specs/2026-11-21-guiding-principles/conversion_list.md` §TerminalBiomes).
  - The sun, air heat and heatstroke stay one kind everywhere.
  - Design: `design/concepts/TerminalBiomes/TheScald_design.md`.
- Test:
  - no BiomeDef or patch under `src/` carries `heatKind`, `heatOffsetC` or any per-biome sun field;
  - the selftest gives the same numbers at the same elevation in every biome
    (`DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL`).

## Every DLC is assumed — owner, 2026-09-19/25/26

🔑 **Design assumes every DLC is present** — owner, 2026-09-25, verbatim: *"Always assume all the dlcs."*
- No standalone-without-expansion fallback tier is owed.
- He said this when asked about the deluxe gear of the free mods without Odyssey.

🔴 **And that assumption covers the PLAYER, not just us** — owner, 2026-09-26: *"it is assumed
that future players will have all the Rimworld DLC's currently installed."* ⇒ **Every DLC is a
hard prerequisite of shipping, exactly like the base game.**
- Anything that we ship may depend outright on Royalty, Ideology, Biotech, Anomaly and Odyssey content. That includes a
  mechanic, a def, a biome roster, a quest, a scenario.
- **Do not design, build or file a DLC-less degradation path**.
- Do not raise "what if the player lacks X" as a defect, a risk or an open question. That question is answered: the
  player has it.
- **Do not spend a review, a test tier or a load round on proving a DLC-absent configuration.** No such supported
  configuration exists.
- `MayRequire` still goes on **mod** guards for load safety.
  - On a DLC, `MayRequire` is harmless but decides nothing.
  - So never read a `MayRequire` as evidence that a DLC-absent case is supported.

🔑 **ALL TEST MOD LISTS include ALL FIVE EXPANSIONS — no exceptions right now.** Owner ruling, 2026-09-19, verbatim:
*"Was Odyssey even loaded for this test? ALL TEST MOD LISTS should include ALL THE EXPANSIONS; we're not trying to
ablate expansions out of our list at this time."*
- All `modset_builder.py` tiers set `dlc: True`.
- The `want` list of a tier may still narrow which *mods* load, for isolation.
- The `want` list may no longer narrow which *DLC* loads.

## Biome art never blocks — owner, 2026-10-18

*"We are going to simply accept all art for the Biomes at this time and review them later, so there is no blocking. Art
review is now a secondary priority."*

- All biome art in game now is ACCEPTED as it is.
- Open review sheets stay open for later.
- No build, deploy, sprint gate or item waits on an art pick.
- Art review is a secondary priority. Art work itself is not stopped. (The rest of his message told the window of that
  evening to prepare the finish of FlowWorks. He put no order between FlowWorks and later art work. His later words
  keep the art pipeline running, 2026-11-07: "It's ok to keep the art pipeline going".)

## Draw order — owner, 2026-10-16 and 2026-11-08

- More south draws in front, for every large pawn, building and plant, game-wide.
- His words (owner 2026-10-16, 2026-11-08): *"if you are more south, you go in front."*
- The rule is built in `src/RimMandrake/MandrakePatches/Source/SouthDrawsFront/` (setting "Southern things draw in
  front").
- Its measured limits: `infrastructure/state/items/RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES.md`.

## Correctness outranks seat ownership — owner, 2026-09-19

*"It is WORSE to leave incorrect information that belongs to another seat than it is
to violate seats... ok? I keep saying this. MAKE IT SO EVERYWHERE."*

🔴 **A false statement in another seat's file is yours to fix, on sight.**
- The full rule is in `infrastructure/agents/CHARTER.md` §Correctness outranks seat ownership.
- `.claude/hooks/queue_lint.py` WARNS on a cross-seat item edit. `queue_lint.py` never blocks the edit.
- Pair this rule with the deletion rule in the next section: remove wrong content; do not annotate it.

## Inaccurate material is DELETED, not superseded-in-place — owner, 2026-09-09

*"Simply remove offending inaccurate material, don't leave it in and supersede
it."*

- Remove wrong or dead content outright. Git is the provenance.
- Fix every inbound reference in the same change.
- A one-line successor pointer at the top is only for content that MOVED somewhere else (owner, 2026-08-30). A pointer
  is never a banner over wrong content that stays in place.
- Entries state what IS, never what used to be.
- "Not my file" does not discharge this duty.
- Single-source only what a generator can enforce. Where only discipline enforces a duplicate, write a pointer instead.

## Git

**Operating doc: `design/RimMandrake/GIT_WORKFLOW.md`** — read it before you touch git.

- **Work in your seat clone**: `/home/mandrake/rm/bench`, or the helper clone that your brief names.
  - Each clone is on ext4, with one writer each.
  - The FOUNDRY clone was retired with its seat.
- `D:\Luke\dev\RimMandrake` is a **read-only mirror** of origin/main. The mirror has no `.git`, and the mirror is
  refreshed every 5 min. Never write it. Windows tools read it.
- **Land with the wrappers:** `./publish -m "subject" path…` or `land.sh <sha> <paths>`.
  - Each wrapper prints `PUBLISHED <sha>`. Pass that sha to `rimflow close --sha`.
  - To realign the clone, use `./sync`.
  - Never use `git pull --rebase`: it refuses on any dirty file. Never use a stash (`GIT_WORKFLOW.md`).
  - Put the pathspec on the `commit` (`git commit <paths> -F -`).
  - Never use `git add -A`/`.`/`-a` (hook-enforced). Never use `--force`. Never commit a file over ~50 MB.
- Committed *and pushed* is the only durable state. Commit each finished unit and push at once.
- Proof of publication is `git merge-base --is-ancestor <sha> origin/main`, not an empty `git log origin/main..HEAD`.
- The pre-push and PreToolUse hooks refuse a compound command whole. So keep file writes and commits in separate Bash
  calls.
- 🔴 **Worktrees are OFF** (owner, 2026-10-02, by card).
  - Never use `isolation: "worktree"`. Never use `git worktree add`. `block_worktrees.py` refuses both.
  - Writing helpers edit in the clone of the window, one at a time when paths could overlap.
  - The window commits explicit paths.
  - Tell each helper in its brief: `reset --hard`, `checkout --` and `stash` are forbidden, and a conflict is
    reported, never cleared.
- **Clone pool: 16 clones and a disk floor.** The owner's words:
  - by card, 2026-11-02 18:35 PST: "How hard should Relentless run this machine? → 8 workers, 16 clones / 70 GB", from
    10 / 40;
  - first approved 2026-10-31, for writers above 4: "I trust you, but please monitor them carefully. They seem to
    propagate prolifically.";
  - of the GB line, 2026-11-18: "You set the GB limit, so yes do as you think."
- The count line, 16 clones, guards against clones that multiply unwatched.
- The GB line is a disk floor, not a pool size.
  - `scratch_clone.py` refuses a new clone when the free space is under the disk floor.
  - Here the free space is the free space on `/`, less the largest clone in the pool.
  - The disk floor is `ops.disk_brake_free_gb` in `src/RimMandrake/Utils/slot_rules.json`.
  - That value is the `DISK_LOW` line: one worst day of scratch growth. The number lives in that file only.
  - The fixed pool size (70, then 80 GB) was removed on 2026-11-22. The fixed size had refused a launch at 83.55 GB
    with 433 GB free on `/`.
  - Danger, evidence and promises: `design/specs/2026-11-22-clone-pool-disk-floor/boundary.md`.
- `scratch_clone.py` reuses an idle pushed clone first.
  - `scratch_clone.py` sheds what the last run left in the clone: ignored files, publish checkouts, packed loose
    objects.
  - `scratch_clone.py` reports count, GB, free space, floor and oldest.
- The pool has one alarm, `disk.pool_breach`. The alarm counts three things:
  - a pool over 16 clones;
  - a pool under the disk floor;
  - any helper clone with unlanded work after an idle hour. The clone can be in the pool, in `rm/scratch` or in a
    session dir. PROTECTED is no excuse.
- The alarm does not count two kinds of commit:
  - a trailing lesson/ledger commit (the clone's return step at the end of a run bundles those into the orphans
    store, so they are not lost);
  - a commit whose content origin/main already holds under another hash.
- A pool clone with unpushed work is never reused.
- Revert the pool if a clone strands work, or if the free space on `/` goes under the disk floor. To revert the pool
  is to end the approval of reused clones for more than 4 writers, and to return to at most 4 writers at one time.
- **Per-writer state, nothing shared:**
  - Ledger shards are `ledger/events/<SEAT>.jsonl` (`merge=union`, `ledger_lint.py`). Never `checkout --ours/--theirs`
    a shard.
  - Queue views are rendered on read (`rimflow queue <SEAT>`).
  - Lessons are one file each under `infrastructure/state/lessons/`.
  - Review status records are under `infrastructure/state/code_review/`.
  - Artpipe state is outside git, at `D:\ClaudeWork\rimmandrake\artpipe\`.
- **Windows-side tools:**
  - Builds go through `winbuild.py <Mod|csproj>`.
  - `codex.exe` needs staging in `D:\ClaudeWork\rimmandrake\scratch\codex\`. `gpt_consult.py` and `codex_image.py` do
    that staging.
  - 🔴 A committed mod DLL carries a `.srchash`, and is pushed with it (hook `block_dll_source_mismatch.py`, on push).
  - After a merge that touches the `Source/` of a mod, rebuild. Never pick the DLL of one side.
- Drained historical work lives in `archive/*` tags on origin.
- Origin is SSH (`git@github.com:Lmandrake/RimMandrake.git`). A push that falls back to https can use a one-shot token
  header (`gh auth token`).
- A `cd` in one Bash call persists into later calls. Use absolute paths, or `cd` back. (For example, `modcheck` needs
  `python3 -m modcheck.cli <verb>` from `src/RimMandrake/Utils`.)

## Code is clean when its promises are tested — owner, 2026-11-19

His words (Thu 2026-11-19, about 3:55 PM PST, item `RIMMANDRAKE_ENACT_CLEAN_MEANS_PROMISES_TESTED_ONE_FIX_ROUND`):
*"Please adopt the Nov 18 rule to all code: we are redefining "clean" to be with respect to a stated design doc/promise
list with specified covering tests. If minor errors continue to be found, you get two rounds, then you're ignored. That
seems too much to be honest. If you find minor errors and fix them, that's it. That's the new rule, ok? Push back if
you disagree, but enough is enough."*

His words (Thu 2026-11-19, 5:27 PM PST, item `RIMMANDRAKE_AMEND_REVIEW_RULE_MINOR_FINDINGS_STAY_ON_POLISH`):
*"AGREED: minor nits and what doesn't have meaningful impact gets left alone, left on a "polish" list."*
His card (Thu 2026-11-19, 5:54 PM PST, item `RIMMANDRAKE_ENACT_REVIEWER_FIXES_ONE_REREAD_THEN_FLAG`). Who fixes a
significant finding? He picked *"The reviewer, on the spot (Recommended)"*. What checks a fix? He picked *"One blind
reread of the fix"*, and wrote: *"(2) Precisely one, yes. If it too finds a significant change and fixes it, the file
is flagged but left alone. Flagged files are examined to see if we need to change the definition of significant or
there is a real instability, but this is done infrequently, say weekly or so."* Should a standing scan run again? He
picked *"Quiet files only, when idle (Recommended)"*, and wrote: *"(1) yes, on Sonnet 5.5, and the Python to visualize
the clean/dirty codebase is ressurrected and included on the standard suite of Desktop visualizations to track.
(perhaps this should become tabs in a standing browser actually, along with FLEET_NOW and MATURATION_NOW in their own
windows)."* Who may take a line from a polish list? He picked *"Nobody; it is a record"*, and wrote: *"(3) for now. We
will later do experiments on Polish if we can/must. We're not close to polishing anything right now"*. The card also
stated two rows that he did not have to pick: the definition of significant, and the filing gate (below).
Reason (measured 2026-11-19, `D:\ClaudeWork\rimmandrake\conductor\review_instructions_old_vs_new_20261119.md`,
`review_loop_three_gaps_20261119.md` and `clean_rule_origin_20261119.md` in the same folder): the old FOUNDRY review
loop let the reviewer fix what it found, with the whole file in context, then sent one fresh reader. It fixed only
significant findings and converged on quiet files (median 0.75 commits in the week before a review): a first read
found 0 or 1 bug per mod file, and the fresh reread found 0. Reviews that fixed every finding wrote new code, and new
fix lines drew 14 to 25 claims per 1,000 lines, against about 3 for old code; on fast-changing pipeline files 8 of 11
and 9 of 15 later claims pointed at lines the last fix had just written.

- **For all code** (mods, defs, C#, tools, hooks and pipeline machinery), CLEAN is judged against a stated page of
  promises: `design/specs/<component>/boundary.md`, in the form of §A boundary page before pipeline code. A file is
  CLEAN when a page names it in its `Code:` line, each promise on that page has a test of the same name, and those
  tests pass. A later edit stays clean while those tests pass.
- **"A full-file review finds nothing" is not a pass condition, for any code.** A review record (`mark-clean`) does
  not make a file CLEAN.
- **Two meanings of clean, named apart.** PAGE-CLEAN: each stated promise has a passing test (`check`; this is what
  CLEAN means everywhere). READ-CLEAN: a cold read of these exact bytes found nothing significant (the review record,
  `mark-clean`, read by `check --record`). The standing scan writes READ-CLEAN; it never makes a file PAGE-CLEAN.
- **A finding is significant** when it is measured, or predicted with a concrete case (this input, this wrong
  result), to break a stated promise or cause a failure. A prediction with no concrete case is not significant.
- **The reviewer fixes a significant finding on the spot**, in the same job. The reviewer first writes a test and sees
  it fail, then fixes, then sees it pass. No ticket carries the finding to a separate builder.
- **Precisely one blind reread checks a fix in a code review.** (A mod fault fixed in a sitting: §Touching code has a
  cost; that reader reads only the fix.) One fresh reader who did not make the fix reads the fixed file once. The reader gets the file, not the diff and not the earlier findings. If the reader finds nothing
  significant, the review is over. If the reader also finds a significant thing, the reader fixes it (same test rule)
  and flags the file: `code_review_status.py flag <path> --why "…"`. Nobody reviews a FLAGGED file again. There is no
  third read.
- **Flagged files are examined about weekly.** Read the list with `code_review_status.py list --flagged`. For each
  file, ask one question: must the definition of significant change, or is this code really unstable? Record the
  answer with `code_review_status.py unflag <path> --why "<the answer>"`, or leave the flag with a note on its ticket.
  The Conductor does this until a timer does. Proposal, not wired: the Friday run of `rm-findings-judge.timer`
  (`src/RimMandrake/Utils/findings_judge_friday.md`, a weekly Opus `claude -p` that already reads patterns across runs
  and files rule candidates) takes this as one more step; the item
  `RIMMANDRAKE_WIRE_FRIDAY_JUDGE_TO_EXAMINE_FLAGGED_FILES_WEEKLY` holds the wiring.
- **A minor nit, or a claim that is not significant,** is one line on `polish.md` beside the page. Nobody fixes it. For
  now nobody takes lines from a polish list: it is a record (his words above).
- **Filing gate.** A new ticket must cite a broken promise or a failure. File one ticket per source event, never one
  per symptom.
- **A standing scan reads quiet files when the machine is idle** (his card above): files unchanged for 7 days or more,
  mod content first, when no mod step needs the machine. It follows the same method (significant, the reviewer fixes,
  one blind reread, flag). The clean/dirty view is back on the Desktop (`CODEBASE_NOW.html`). The scan is not built
  yet: the item `RIMMANDRAKE_BUILD_STANDING_SCAN_OF_QUIET_FILES_ON_SONNET` holds it.
- **A mod's locked bars are the page of every file inside the mod** (his card, 2026-11-19 evening: *"Locked bars are
  the page"*). The promises are `design/concepts/<Mod>/version/locked_bars.json`, and the tests are the test table
  rows that decide each bar. A mod with no locked bars reads NO PAGE. A bar with no test, or a red test, reads DIRTY.
  A bar whose test has not run on these bytes (in-game tests included) reads UNREADABLE. Detail:
  `design/specs/2026-11-19-clean-means-promises-tested/boundary.md`.
- **Code with no page reads NO PAGE, not DIRTY** (the Conductor's reading, delegated, told to him 2026-11-19). It gets
  its page when someone next changes it, or when it is on a mod's next-step path. Nobody writes pages for untouched
  code in a sweep. For pipeline machinery, Decision 1 of §A boundary page before pipeline code also says when a page
  is owed.

The commands (`check`, `check --record`, `mark-clean`, `flag`, `list --flagged`, `unflag`) and what each answers:
`python3 src/RimMandrake/Utils/code_review_status.py --help`.
`check` exits 0 CLEAN, 1 DIRTY (a promise has no test, or its tests file fails), 3 UNREADABLE (a page or tests file
could not be read or run, or a page is not registered in `boundary_check.py` `PAGES`), 4 NO PAGE; over several paths
the worst answer sets the exit. It runs each naming page's tests file once per call. Its own page:
`design/specs/2026-11-19-clean-means-promises-tested/boundary.md`.

- **Before you spend a review on a file, check that it is still reachable** — owner, 2026-09-03: old scripts sit
  around long after they stop mattering. A Python file with no importer, no `python3 <it>` in any doc, hook or script,
  and no CLI entry point is a DEAD-FILE candidate; a `.cs` file dropped from the `.csproj` or with no live caller
  (reflection-registered bridge tools included — grep the tool-name string, not just C# call sites) is the same. Say
  what you checked. **Don't delete on a grep alone — verify, then file it** (or drop it, if it's plainly gone) rather
  than spending a review on code nobody runs. A file only a human runs by hand can look unused to a naive grep and
  not be.
- **What this does not change.** The judge rule for mod work (§The judge refuses flaws, not polish: one full
  inspection, then one check of the repairs) is a separate ruling about mod judges. Codex and GPT
  may review pipeline machinery by this rule (§A boundary page before pipeline code). "The test is built
  with the item" and "The pipeline fixes its own defects" stand. A mod's Polish list in the Maturation Pipeline (the
  Design Version rule) is a separate list; the Conductor decides each move to it; "nobody takes lines" covers only the `polish.md` beside
  a code page.
- **Test that this was applied:** `code_review_status.py check` on a file that no page names reads NO PAGE; on a file
  whose page has every promise tested and passing it reads CLEAN, with no review record. A FLAGGED file reads FLAGGED
  in `list`, never DIRTY, and `mark-clean` refuses it. `roles/code_review.md` says that the reviewer fixes and that
  one blind reread follows.

## Touching code has a cost; if you see it, do it — owner, 2026-11-19

His words (Thu 2026-11-19, card answered about 6:28 PM PST; the card asked *"Which rule should govern the pipeline
tickets already filed?"*; item `RIMMANDRAKE_ENACT_TOUCHING_CODE_COSTS_SEE_IT_DO_IT`):
*"We JUST changed standing orders across this whole project. Please be advised and make the changes. This is standing
policy for all FIXERS that receive a ticket (is it really fixing something that anyone would care about?),
REVIEWERS/JUDGES (is this a significant comment/change), and pipeline monitors (are these tickets impactful,
meaningful, and worthy of action)? Basically we're introducing a new concept: TOUCHING code has a COST. It's DANGEROUS
at a low noise-level, so you must justify doing it, and that includes old tickets that didn't justify why. So by that
criteria, yes! Go and "judge" the tickets now to see if they are "worthy" the risk of their repair. Obviously the ones
with failing tests are a go. Maybe you can group them together to repair them in a single context more cheaply, that
would be welcome. I would also like to introduce the idea that ANYONE can be a fixer. If a ticket adjudicant in THIS
VERY EXERCISE picks up a ticket and can clearly see "yes this is valid and I can even see how to easily fix it"...
PLEASE DO. Don't make someone else go read everything and decide yet again... Just please do it! This is the "If you
see it, do it" rule. In essence, you have to have evidence that you should NOT do so. The assumption to just "set a
ticket down for someone else later with 'fixer' on their forehead" is false... the fixer is you unless you can prove
you don't have the resources or currently have other responsibilities that prevent you from investing. Feel free to
push back, but this seems very important and is very much in the spirit of the old successful Foundry process, even
now. Vital: OF COURSE you do, no debate. Any real chance of voiding a run is catastrophic."*
The same card's other question (*"Which of these should I build?"*, about why findings never stop) he answered *"Stop
rule in every judge brief (Recommended)"* and *"One fault, one ticket"*
(`RIMMANDRAKE_KEY_AUTO_FILERS_ONE_FAULT_ONE_TICKET`).
Why a touch is dangerous (measured 2026-11-19): new fix lines drew 14 to 25 review claims per 1,000 lines, against
about 3 for old code (§Code is clean when its promises are tested); tickets born of a review beget 2.5 times the
descendant tickets of tickets born of a live failure (0.78 against 0.31 per root), and the costliest retired-era
failure classes came from reviewers, judges and auto-filers with no stopping level
(`D:\ClaudeWork\rimmandrake\conductor\churn_vs_responsibility_specs_20261119.md` §3, §6 and §8).

- **Who this binds.** Every fixer that receives a ticket, every reviewer and judge, and every pipeline monitor
  (Operations, the ops alarm filers, the findings judge, the sweeps) before it files. It binds tickets
  filed before the ruling too: a ticket that does not show why its repair is worth the touch is judged now
  (`RIMMANDRAKE_JUDGE_OPEN_PIPELINE_TICKETS_WORTH_THE_TOUCH`).
- **Test 1, the worth of the touch, asked before the touch.** Change code, a def, a test, a hook or a brief only to fix
  something that someone would care about. The touch is worth it when one of these is true:
  - the finding is significant (§Code is clean: measured, or predicted with a concrete case, to break a stated
    promise or cause a failure) and ordinary operation reaches it (a call site, a documented command, a player's
    game or a later run produces the input);
  - a failure happened: a run, a test, a player-visible fault, or the owner's report;
  - its ticket has a red test that shows misbehaviour: a wrong result or a failure. That is a go. A red test that only
    restates the ticket proves no worth and is not a go; a judge reads each red test (his card answer, Thu 2026-11-19
    10:17 PM PST, *"When it shows misbehaviour (Recommended)"*; the card asked *"When is a red test enough to make a
    ticket a go?"*).
- **A real chance of voiding a run is always worth the touch** (his words: *"Vital: OF COURSE you do, no debate"*). A
  void is a run killed, timed out or never started, or a trial or a run's work lost (§No trial is spent by a system
  failure). "Real" means *"Happened, or ordinary use causes it (Recommended)"*: a failure that happened, or a concrete case in
  normal use (his card answer, Thu 2026-11-19 10:17 PM PST; the card asked *"How should 'a real chance of voiding a
  run' be read?"*). No repair for an imagined fault. A rare known fault may waste one run before it is fixed; that run
  is voided, so no trial is lost. A rare failure that a page
  lists under DOES NOT SURVIVE (§A boundary page before pipeline code, Decision 4) is not a real chance until it
  happens once. Then it is a failure and a new source event, and it is worth the touch.
- **A finding that fails test 1 gets no fix and no ticket.** Write it as one line on `polish.md` beside its page, or
  as one line in your report where no page exists. An open ticket that fails test 1 is dropped with the reason
  `not worth the touch: <why>`. That is not trimming work: §You do not trim work (`roles/conductor.md`) forbids cutting
  worthy work to save spend, and this rule says the unworthy touch is itself the cost.
- **Test 2, if you see it, do it.** Whoever judges a finding or a ticket worth the touch is its fixer, in the same run:
  write the test and see it fail, fix, see the test pass, publish. Never set it down for someone else without evidence
  that you should not do it. The evidence is one of these:
  - you lack the tools or the access (a read-only role; a live-only fault and no bridge);
  - the fix is not known;
  - it needs one of the owner's five acts (§Only five acts stay his);
  - it would change a north-star bar;
  - another live run holds the same files;
  - your verdict must stay independent of the work: a judge that fixed the work it judges would become
    its maker, and nobody would judge the fix;
  - your assigned work would not finish (name it).

  The ticket that you file carries that evidence, and the fix where you could see it.
- **Test 1 comes first.** "If you see it, do it" never licenses a touch that fails test 1.
- **A fault is fixed in the sitting; a wrong check is repaired or removed there; neither sends the mod back** (owner,
  2026-11-20, items `RIMMANDRAKE_ENACT_WRONG_CHECK_FIXED_IN_SITTING_NOT_RETURNED` and
  `RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION`; first ruling at item
  `RIMMANDRAKE_ENACT_WRONG_CHECK_FIXED_IN_SITTING_NOT_RETURNED`). His words (Fri 2026-11-20, about 4:10 AM PST), asked
  whether to extend the significance rule to tests: *"Agreed, modify standing rule in-place to include your extension
  for "inappropriate/insignificant test""*; asked whether the in-game driver should repair a wrong check in the
  sitting: *"YES! I'm really tired of "throwing things back" rather than fixing in-place. These should have been
  repaired in place I'm fairly certain, then re-run. We need to stop treating all agents as corrupt. They're not.
  Their reasoning just collapses to the fixes they make sometimes. But if there are strong checks to validate in place,
  that can be overcome."* Earlier (about 3:55 AM PST): *"I am distressed that judging events are still being used to
  slowly improve testing definitions rather than game content."* The cause (measured 2026-11-20): FlowWorks in-game
  visit 2 read 8 FAIL and 5 UNMEASURED of 31; the router filed all 13 lines and moved the mod back to the offline
  build; all six fixer runs that followed repaired checks, and none changed the mod. His further words the same
  morning: about 4:25 AM PST, *"Also, even if the "mod is wrong" should not throw the mod backwards! If the judge can
  just fix it right now with a before/after test, and thus show passing... just do it! If it needs a live game... ok,
  fine. But seriously, I'm almost about to say just spin up the game and do it right then. These loops are TOO LONG
  AND SLOW."*; about 4:40 AM PST, on the blind judge that fixes with one fresh reader of the fix: *"I agree with your
  blind judge -> fresh reader argument."*; about 4:50 AM PST, *"And yes... if a live game is available, of course a
  judge (or any role!) should be able to just grab it and use it to get something done! IT's an unused resource
  otherwise... the worst case."*; about 5:05 AM PST, on "set it aside": *"How does that help if there's a needless
  test present? The next judge will hit it again..."*
  - Class each failed or unmeasured check first: the mod is wrong (`class` MOD), the check is wrong (HARNESS) or the
    staged scene is wrong (SITE). These are the classes of skill `live-debugging-proof-harness`.
  - A wrong check or scene is worth repair only if a bar would go undecided without it. A check that no bar needs is
    removed: taken out of the test table (and deleted when nothing else names it), so that no later judge meets it
    again. One line on the polish list is the record of the removal. No ticket.
  - "A failure happened" (test 1) does not make a wrong check worth the touch by itself: the failure was the check's.
  - The agent that classes a check wrong repairs it in the same sitting and runs it again while the game is up. The
    reasons "my verdict must stay independent" and "my assigned work would not finish" (test 2) do not excuse a wrong
    check or scene: its repair does not touch the mod.
  - The guard that replaces distrust: a repaired check counts only after it is seen to FAIL on a planted fault (or on
    a state that is known bad) and PASS on the real build, in that sitting, with both readings recorded beside the
    row. A needed check whose repair cannot be shown both ways stays not counted (UNMEASURED), never PASS, and keeps
    an owner: the run that found it, or a filed item with the evidence. "Not counted" is for that case only. Plant with
    what exists: the planted cases of the blind challenge, a check's `--old` or mutant switch, or a save or state that
    is known bad.
  - A mod fault that the judge or driver can fix is fixed in the sitting: a before/after test (red on the parent,
    green on the fix), the fix, and the check shown passing on the fixed build (in a visit, the checks that the fix
    touches run again on that build). Then one fresh reader, a run that did not make the fix, reads only that fix, once, and writes its
    review (`fix_reviews.jsonl`); the steward run that reads the record is that reader. This replaces the whole new
    blind cycle that a fixed mod used to owe.
  - Only a mod fault that could not be fixed in the sitting goes down the road back, with the evidence why (no tools,
    the fix is not known, another run holds the files, one of his five acts, a north-star bar), and so does a bar left
    undecided. A wrong check or scene never moves the mod back. The driver or judge files each line that still goes
    back, before it ends; the router files only what they did not.
  - A fix that needs the live game takes it when it is free (§The bridge is passed through one file): any role, a
    judge included.
  - A resume never crosses a blind boundary (owner, 2026-11-20, about 5:30 AM PST: *"And of course blind judges and
    others don't inherit the builder's context, or anywhere else the whole point was NOT to inherit the context. I
    didn't mean that."*). A blind judge, the fresh reader of a fix, an examiner, a challenger and the coverage judge
    always start fresh; a run that keeps context (a continuation, a holder, the run that records its own red-seen
    proof) resumes only its own session, never the session of a run whose work it judges.
  - A run that edits a deciding test records its red run with `maturation.py red-seen` before it closes. Measured
    2026-11-20: two fixers (`44124fa343`, `345366aa49`) edited Gimme Some Slack's deciding test file and saw planted
    faults go red without recording it; the certificate then refused 18 of 26 bars on `red_seen`, and the mod sat
    from 2:14 AM to about 4:50 AM PST until a hand ran `maturation.py red-seen` (`509bca1964`).
  - In the blind challenge, a Problem `against` a check or scene that the judge repairs, shown both ways, owes
    nothing more. A Problem fixed in the mod owes its one fresh reader.
  - Enforced by `maturation.py` (`read_ingame_exit`: `line_class`, `repair_shown`, `mod_fix_shown`, `review_sound`,
    needless and undecided lines; `read_exit`: `check_repair`, `review_sound`) and carried by the blind-judge,
    in-game driver, steward, fixer and builder briefs (`WRONG_CHECK_RULE`, `RED_SEEN_RULE`).
    Page: `design/specs/2026-11-20-wrong-check-fixed-in-sitting/boundary.md`; test:
    `src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py`.
- **Group the repairs.** Tickets with one cause, or in the same files, are fixed in one run and one context.
- **A stopping level in every judging brief** (his pick on the same card, *"Stop rule in every judge brief
  (Recommended)"*, whose description read: *"Why: it hits the measured cause. About a dozen briefs (auditor, ops
  alarms, blind judges, art and coverage judges, sweeps) each get a look count and a 'good enough' level. Cost: each
  brief needs a calibration run, or the rule is only words."*). Each brief that reviews, judges, audits or files
  findings states three things: the level that is enough, when to stop looking, and the polish route that files no
  ticket. A count in such a brief names the danger it guards beside it (§No limit without the danger it guards).
  Until a calibration run checks a brief's stop rule, that rule is only words: the list of briefs and the runs owed
  are on `RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN`.
- **A small change is checked by the agent that made it, and never waits for a run** (two rulings of the owner,
  2026-11-05, merged here 2026-11-23). *"Please make a ruling: The pipeline is NOT to be used to "bless" any change in
  the game. That's a huge expenditure for a small validation that could be manually performed."* He said this of
  Relentless, which is now retired. *"We MUST stop this endless token burn by making little cute notes on tickets and
  letting the system totally restart each item once more time to do a check, ok?"* (He had just said *"NO! Do not write
  this diagnosis onto the item... YOU DO IT NOW!"* to a Conductor. That Conductor had diagnosed
  `MODCHECK_DONOR_ENVIRONMENTS_1` and had written the next step on the item.)
  - A small change is a change whose check is a quick manual validation: an installed picture equals his pick, a value
    reads back, a file is deployed. The agent that made it checks it on the spot (a hash, a read, a single bridge call)
    and closes it with that evidence in one command: `rimflow close <ID> --sha <sha> --evidence "<what ran and its
    result>"`. The command records the pass and the close together.
  - When a seat or helper finds why an item is stuck, that seat or helper does the fix and the remaining check at once.
    Then the same seat or helper closes the item with that evidence. Never write the diagnosis or a `NEXT:` onto the ticket instead.
  - Never queue, unhold or re-release an item for a check alone. An item goes back to the pipeline only when real build
    work remains.
- **How the rules fit.** §Code is clean when its promises are tested is this rule for code review (significant, the
  reviewer fixes, one blind reread). §The pipeline fixes its own defects is test 2 for the pipeline's own machinery,
  and its hand-off list is the list above. The CHARTER's "See it, fix it, then" (owner, 2026-11-05) is test 2 for a
  small fix; since this ruling, a fix that is not small is still yours unless the evidence above says otherwise.
- **Test that this was applied:** `src/RimMandrake/rimflow/selftest_touching_code_cost_rule.py` finds the two tests
  in the root `CLAUDE.md`, the CHARTER, the six `.claude/agents/rm-*.md` files and the fixer, judge and monitor role
  files, and a stopping level in each judging brief that it names.

## What is where

**Art is judged against the canon library, and canon is the target** (owner, 2026-09-15).
`design/RimStarWars/canon_references/` holds the canon entries (creatures, species, droid
chassis; count it, never cite a number) — each with sourced canon, a visual brief written against real reference images, a
`## Must show` checklist and `## Engine limits`. **An empty `## ruling` means canon stands
unopposed, not that the entry is unusable**; he rules on deliberate departures from canon;
ambiguity and contested regens go to the art judge first (`delegation_policy.md`). `AGENT_BRIEF.md` there is the operating doc. 🔴 Keep the
three defect classes apart — a **missing gene** is edited in the def, an **engine limit**
needs new art or more mask channels, and a **rig limit** (Ithorian neck, Kaminoan
proportions, Muun body, Lasat legs) cannot be fixed at all, so art chasing it is waste.
Art and cosmetic changes are delegated (owner, 2026-10-22, `delegation_policy.md`): a judge agent applies
`art_judge_brief.md`, which keeps the old rule's reason — a pawn cosmetic change must not break animated faces.
🔑 **Every art review sheet shows the canon reference images and the entry's `## Must show`
beside each row whenever the subject has a canon entry** (owner, 2026-10-04); a row without one
says so. Since 2026-10-04 art goes through the art ledger and its `art install` only
(`design/RimMandrake/art_ledger_design_2026-10-04.md`), and his rulings live in
`infrastructure/state/art_rulings/`, never only in `Transient/`.

The folder tree is in `CLAUDE.md` §What is where, and the Transient rule is in `CLAUDE.md` §Transient. Two facts
are only here. `Transient/` is untracked since 2026-10-18 (owner, by card: *"Stop tracking; pin to keep"*); pin a
file with `transient_pin.py add <path>` (`*.decisions.json` always stay tracked). `rimflow sweep --transient` lists by
age; it never deletes.

## Nothing reaches the owner unread — owner, 2026-10-22

> *"for a review sheet to be worth showing a human, YOU need to look at it yourself first to see if it passes muster
> on any item you can judge. That's just a general rule for RimMandrake from now on. No walkthrough maps unless you've
> zoomed in on every station and stared at the screenshot for potential issues related to the mod, ok? Typical
> graphics problems, connections, making sure each graphic objects is recognizable as what it is, etc. Use a naive
> Opus if you need to judge things, or a GPT consult if you want to make a bigger sheet and send it out. Now please
> work on this principle until it's a coherent, concise principle and implement it for all human review. Art sheets,
> lists of rules... it's all the same. Read it first and see if it's obviously broken, malfunctioning, or problematic
> before wasting a human's time to tell that to you."*

🔴 **Whatever we put in front of him to judge** — review sheet, art set, phone image, walkthrough map or save, list of
rules, report, a card's material — **the presenter first looks at every item an agent can judge**, itself or through a
naive judge (a fresh-context Opus that did not make it; `gpt_consult.py` for a big sheet), and **fixes or drops what is
obviously broken**: does not render, does not connect, is not recognisable as what it is, contradicts itself or its
spec, repeats something he already ruled. A walkthrough: a zoomed capture of every station, connection and path, each
stared at for the mod's faults. He gets what survived, items an agent cannot judge marked as such, and one line of
what was caught. **Test:** if his first comment is something we could have seen, it was not ready.
**Enforced** for sheets: `serve_gated.py`, `review_queue.py` and `sheet_to_artifact.py` refuse a sheet without a
complete `<stem>.prereview.json` (`src/RimMandrake/Utils/art/prereview.py`); maps, images and prose rest on the
presenter. **Unchanged:** who decides (`delegation_policy.md`), the scaled-review gate, a grader's score as evidence
only. The 2026-10-19 card *"Python command, no agent before you see it"* now means no agent COMPOSES the page; one
still reads it. Incident: 2026-10-22 FlowWorks walkthrough (hoses missing reels, under buildings, unreadable
connectors, a pawn over a pit cover), `skills/rimworld-live-review/references/traps.md`.

## Options he must LOOK at ship as a savegame — owner, 2026-09-02

*"Save user review options as save games."* A screenshot shows one angle of one
thing; a save lets him walk it, zoom it, and read the tooltips. So when a pass
produces options for him to judge in-world — structures, layouts, creatures,
gear on a pawn — **build them and save the game.**

- **One map, all options** (his ruling by card), laid out on a grid with enough
  pitch that nothing overlaps, plus an item file giving the **grid key**: which
  option is at which cell.
- **Saves stay until he says delete** while he may still judge them. Not overwritten by the
  next review. A save nothing reads any more is a leftover: archive, delete, list in his
  digest (owner card 2026-10-26, `delegation_policy.md` §2).
- 🔴 **Back up the Saves folder's keepers first and stat it afterwards.**
  `rimworld/save_game` has silently written the CURRENT slot instead of `saveName`.
  Confirm a NEW file appeared and no existing one changed size — never trust the
  path it hands back.
- ⚠️ Verify each option is actually THERE (`jawa/list_things` per slot) before
  calling it a review. A placement log's `thingsSpawned` is a NET count and goes
  negative when a build clears plants.

## Check for existing regenerated art before queuing more — owner, 2026-09-20

Before you file a `fill_queue.py` job, check whether art for that subject was **already generated and already ruled
on**. Do the same whenever a def or item is "missing art" or "owed new art". Generate only what the search does not
find. The artpipe daemon runs all the time, and its output often sits unused for days. The def or roster
work that would wire it in often has not happened yet.

- **Search the artpipe state dir by subject/defName first** —
  `python3 src/RimMandrake/Utils/artpipe/artpipe_state.py find <term>…` covers `done/`, `_artsrc/`,
  `registry.jsonl` and `art_status.json` in `D:\ClaudeWork\rimmandrake\artpipe` (outside git since 2026-10-02) and
  refuses rather than report 0 when that dir is absent — not just by job-id guesswork.
  A finished job's `rimflow_item_id` and `style_notes` often name the exact
  roster row or item it was generated for.
- **Check for a review sheet's `.decisions.json`** (`Transient/*.decisions.json`,
  a `port_tail_*`/`bulk_art_*` sheet, or similar) — if the owner already ruled
  on that art (kept/replace/improve), queuing a fresh regen throws that
  ruling away and spends a job for nothing.
- 🔑 **Caught live, 2026-09-20 (`BMT_FLORA_ABSORPTION_1`):** three plants
  (giant leaf, fire lavender, heatsink fungus) were about to get a fresh
  `fill_queue.py` job each. All three already had finished, validated art
  sitting in `_artsrc/` since 2026-09-12/13 — one traced straight to the
  exact roster row being fixed — found only because the owner said *"I
  actually already saw beautiful art for giant leaf somewhere in a review
  sheet"* and asked for a check across the rest of the missing set. Nothing
  in the workflow up to that point had prompted the check on its own.

## Spare capacity: finish, then strengthen, then explore — and a conditional pass is a pass (owner, 2026-10-25, by card)

When the planned work runs out, agents spend the rest in that order. His words on the card: *"(4) but
have some stopping criteria for both finish and strengthen. Zero bugs is NOT it... there will always be
imperfections. We're trying for "a human won't immediate get frustrated and produce bug reports" instead
of "no one will ever find anything wrong." Hours producing no issues, or only partial/weak issues that have
had multiple rounds of attempting to fix them already, produce a conditional pass... and that's ok."*
So finishing or strengthening a thing STOPS at a conditional pass: hours of testing that turn up no issues,
or only weak/partial ones already through several fix rounds. Record it as a conditional pass and move on;
never grind toward zero defects. Here "finish" and "strengthen" are kinds of spare work, and "(4)" is the card's
option 4. A conditional pass ends that spare work. A conditional pass never passes a mod's version: only his walk does
(§Only five acts stay his). His later ruling of 2026-11-20 says what fills a quota surplus: quality work queued ahead,
with the clean/dirty code review as the backup plan (`src/RimMandrake/rimflow/roles/operations.md` §Success test).

## Account and capacity budget (owner, 2026-10-25, by card)

*"Be aware of the account limits. the.mandrake.system and lukas.mandrake belong entirely to me and may be
fully consumed each week. Partition how much you can use per day (roughly), but it's really the weekly
reset. Always save some capacity for our interactive exploration together at night (predominantly).
There's also GPT capacity to monitor and exploit. Steven.lewis can be used once the others are depleted...
roughly half of it is available for our use."* So: budget against the WEEKLY reset; track GPT capacity too and use it.
The order of the accounts in that quote is replaced. His standard switching plan of 2026-10-28 (item
`ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING`) burns steven first inside its window after its reset, then system, then
lukas. It keeps "about half" of steven as the leave line. The order, the leave lines, and each dated exception (one is
in force from 2026-11-20) are in `src/RimMandrake/Utils/switching_plan.json`; obey that file.
He was answering the card question "How much should be kept free for you?". The share for his evenings and the rough
daily partition in that quote are ended (owner, by card Mon 2026-11-23 8:57 AM PST, item
`RIMMANDRAKE_ENACT_FOUR_CARD_ANSWERS_ON_HIS_TWO_WAY_RULINGS`). The card asked *"Must agents keep account capacity for
your evenings?"* He picked *"No, run to the line (Recommended)"*: *"Buys: the most work done unattended. Costs: on a
heavy day an account can be near its line when you sit down, and the sitting moves to another account or waits.
Recommended: later and more specific."* No share is kept. Each account runs to its line, at any hour. The order, the
leave lines and Steven's line do not change.
The fixed account order and the shared account's leave line may be changed by the Conductor as its mindful act
(owner 2026-11-19, §Only five acts stay his): its `--why` names what is lost if wrong (`lost:`) and the undo (`undo:`).
The money side stays his: nothing here buys capacity.

Live runs finish past the soft line; no account is driven to zero (owner, 2026-11-20 about 5:30 AM PST): *"And yes for
live runs finish past, absolutely. Actually 0.1% is even ok kept. We just don't want to crash to zero and get stuck.
Please make that true everywhere."* About 6 AM PST: *"Agreed for 1% at the moment"*. So:
- At an account's soft line (its line + 2%) no new run starts on it. At its line the switch or the stop waits while a
  detached run is live, and goes when the runs end or at the hard line, whichever is first.
- The hard line is max(1%, line - 2%): steven's 52% leave line gives 50% (his 2026-10-28 "use it until 50%"); every
  other account stops at 1%. The meter reads whole percents (8,749 readings to 2026-11-20, none fractional), so 1% is
  the lowest line it can see; a 0.1% line waits for a finer meter.
- A switch the priority pulls (above the line) waits for live runs too, at most 2 h.
- Do not stop runs or switch accounts by hand at the soft line; the plan drains them.
- The numbers live in `src/RimMandrake/Utils/switching_plan.json` and nowhere else; the page is
  `design/specs/2026-11-20-account-drain/boundary.md`.

## Nobody plays during development; only the canonical world saves are protected — owner, 2026-11-23

His words, by card, 2026-11-23, about 4:45 PM PST (item `RIMMANDRAKE_ENACT_NOBODY_PLAYS_NO_OWNER_GAME_OR_SAVES_TO_GUARD`):

- On "stop a broken ArchBig under his hold": *"I DO NOT PLAY. You keep making this mistake. No one is playing the game
  while we're developing it. I don't own any game."*
- On "removals on his saves": *"I DO NOT OWN SAVES. The only saves that are protected are canonical world saves that
  we're using to build the playable game itself. There are no players and no actual live games to protect, as long as we
  can rebuild the world. But currently the world painting is slow, so we have canonical saves. That's it."*

What follows from his words:

- No game is the owner's game, and no save is the owner's save. ArchBig is the game with the full mod list. He looks at
  staged work there.
- The canonical world saves (`infrastructure/state/CANONICAL_SAVE.md`) are the only protected saves. The reason is that
  to paint the world again is slow. A test may remove things on any other save.
- Each other save is disposable. A save that waits for his review stays until he rules
  (§Options he must LOOK at ship as a savegame). That rule keeps the look, not a save of his.
- A broken game is stopped at once, on any game, also while his hold stands. The stop is reported.
- His OWNER hold and `./pipe off game:ArchBig` guard a look at staged work. Both still bind. The game is never put in
  fullscreen or in focus, and he controls the clock in a sitting.
- The CAMPAIGN profile of the companion guards a loaded canonical world save, and guards nothing else
  (`design/RimMandrake/companion_handshake.md`).
- A rule, guard, test or question that protects his play, his game or his saves is false. Delete it.
- The census of 2026-11-23: `design/specs/2026-11-23-nobody-plays/census.md`.

## There are several live games; a busy game is not a reason to wait — owner, 2026-11-14 to 2026-11-20

His words, with their dates (Pacific):

- 2026-11-14 8:25 PM, by card on the in-game acceptance stage: "Which game gives scripted verdicts" → "Whichever game
  is free".
- 2026-11-16: *"don't forget we have two Rimworld games, so I don't want to hear any 'waiting for game'"*.
- 2026-11-20 6:20 AM: *"We can run two games you know..."*
- 2026-11-20 3:40 PM: *"You should not have been waiting for the game. there are two games"*.
- 2026-11-20 8:24 PM: *"There are two live games. Clearly some basic document needs to be changed. You keep getting that
  wrong. Find that top document and define both games as options. Ensure the bridge holder is well defined and the
  policies for using them. My god. Please stop saying waiting for the live game."*

The games. Each game has its own install, its own bridge and its own lock:

| game | where | lock (`--host`) | what it is for |
|---|---|---|---|
| ArchBig | Steam's install on Archmagi, `C:\Program Files (x86)\Steam\steamapps\common\RimWorld` | `archmagi` (the default) | his walks and looks, and every check that needs the full mod list |
| ArchSmall | its own install on Archmagi, `D:\ClaudeWork\rimmandrake\instances\b\game` (own Mods, BridgeTools, Saves) | `archmagi.b` | any work that a tier mod list can prove |
| Steve1, Steve2 | SteveDesktop, through `infrastructure/stevedesktop/RUNBOOK.md` | `stevedesktop`, `stevedesktop.b` | queued pipeline tests |

The names of the games (owner, by card, 2026-11-22 about 2:35 AM PST). His question: *"How should we call the
different games on each computer? A and b lower case are very hard to read and recognize. We should also remark them
for which computer they are on since stevedesktop can also run games."* His answer on the card: *"Let's go with
ArchBig, ArchSmall, Steve1 & Steve2."* (item `RIMMANDRAKE_RENAME_GAMES_ARCHBIG_ARCHSMALL_STEVE1_STEVE2_LETTERS_UNREADABLE`).

- ArchBig is the old `game a`, ArchSmall the old `game b`, Steve1 the lock `stevedesktop`, Steve2 the lock
  `stevedesktop.b`. The machine is still SteveDesktop; Steve1 and Steve2 are names of games only.
- Every line that a person or an agent reads names a game by its name. Every input takes the name in any letter case.
  The old inputs (`a`, `b`, `game:a`, `archmagi`, `archmagi.b`, `stevedesktop`, `stevedesktop.b`) stay valid as
  aliases, so live runs, old briefs and old ledger events keep working. An unknown name is refused by name, never read
  as a default game.
- A letter names a game on its own machine: `b` on Archmagi is ArchSmall, on SteveDesktop it is Steve2. A name of
  another machine's game is refused there by name.
- The internal keys do not change: lock keys, instance letters and folders, `RM_GAME_INSTANCE`, control-store scopes
  (`game:a`) and ledger history. One map, `src/RimMandrake/rimflow/game_names.py`, turns a key into its name. Its
  promises are on `design/specs/2026-11-20-per-game-hold-own-install/boundary.md`; its test is
  `src/RimMandrake/rimflow/selftest_game_names.py`.

The bridge holder:

- A bridge holder is the one process that drives one game: its lock names it. Two holders may drive two games at
  the same time; one holder never drives two games.
- `game_lock.py query|claim|release|run ArchBig|ArchSmall` and `rimflow bridge who|take|release --host <lock>` act on one game's
  lock; with no `--host` rimflow acts on ArchBig. `RM_GAME_INSTANCE=b` points a tool and the bridge client at ArchSmall.
- Every rule of "The bridge is passed through one file" (below) applies to each lock.

The policies:

- Choose the game by the work. Work that a tier mod list can prove goes to any free game. If ArchBig is busy or held,
  the work goes to ArchSmall or to SteveDesktop. A seat that needs ArchSmall starts it
  (`python3 src/RimMandrake/Utils/game_instance.py launch ArchSmall --wait`) and does not ask.
- Only a check that needs the full mod list must use ArchBig. The full list on ArchSmall beside ArchBig does not fit in
  Archmagi's memory (about 17.5 GB needed against 19.6 GB of headroom over a 12 GB floor, measured 2026-11-20). A wait
  for ArchBig names those checks.
- His walk holds ArchBig only (`./pipe off game:ArchBig`). In-game runs then go to ArchSmall.
- Never write or say "waiting for the live game", "needs the live game" or "the game is busy". Name the game. Say why no
  other game can take the work.
- A tick line, brief, refusal or status page that says work needs a game while a game is free, or while ArchSmall could
  take it, is a pipeline defect. Fix it in the same run (§The pipeline fixes its own defects).
- The pipeline picks the game with `pick_game` (`src/RimMandrake/rimflow/maturation_dispatch.py`): the in-game visit,
  the Stage 6 holder, and the holder on a spent offline road back of game-only items. Detail:
  `design/specs/2026-11-20-per-game-hold-own-install/boundary.md`,
  `design/specs/2026-11-20-tick-game-only-exit/boundary.md` and `design/RimMandrake/two_rimworld_instances_2026-11-07.md`.

## The bridge is passed through one file

**RELENTLESS** was the retired Relentless Pipeline's bridge holder (`model.bridge_identity`), not a seat: only old `bridge` events carry it.

One process drives each game at a time, not for ownership but for attributability. The one file is that game's
driver lock (owner, 2026-11-21, about 3:35 AM PST: *"A single point of reference and truth? And most importantly, a
token free lightning fast way to query, claim, and release."*). Design and measurements:
`design/specs/2026-11-21-one-game-lock/boundary.md`.

```
python3 src/RimMandrake/rimflow/game_lock.py query [ArchBig|ArchSmall|all]  who drives it, since when, for what
python3 src/RimMandrake/rimflow/game_lock.py claim ArchSmall --for "<what for>"  take it for this process tree
python3 src/RimMandrake/rimflow/game_lock.py release ArchSmall              the moment you stop
python3 src/RimMandrake/rimflow/game_lock.py run ArchSmall --for "<what>" -- CMD  hold it for CMD's life
```

Exit 0 free or done, 75 held, 3 his hold, 2 could not look. `rimflow bridge who|take|release` and `./bridge` read and
write the same lock, and write the ledger's history; nothing decides from the ledger.

🔑 **It errs toward ALLOWING, never toward mutual lockout** (owner, 2026-09-02). A holder whose process has ended holds
nothing. A live holder holds; `--force` cuts it and is recorded.

⭐ **The owner overrides both of you with `./bridge conductor|free`**, and his word
lands in the same file you already read.

🔴 **His presence at the machine is not an event** (owner, 2026-10-30, verbatim: *"I really, really need you to strip "when I come back to the machine" as an event for anything changing. It's causing so many problems and I don't need it."*). Nothing reads his
keyboard or mouse clock, and his touching, leaving or returning to the machine never gates, delays, yields,
requeues or aborts anything: a bridge take, deploy, restart, dispatcher ring, seat restart, arena lane, TestPilot or
runner. A seat MAY take the bridge, deploy and restart the game on its own when it is free or ours
(`rimflow bridge idle --for "<what>"` reports it;
`rimflow bridge take --idle-ok --for "<what>"` and `./game --idle-ok --why "<what>" ...` do it), and lists each act in his daily digest (class `bridge idle`). Still
binding: his OWNER hold (below) and `./bridge` override, never a flyer's flight (`--flyer` or flight wording refuses),
and the game is never fullscreened or focused, so it does not steal his screen. The arena lane config key `owner_playing` is ignored and dropped.

🔴 **Any role that needs the live game to finish a fix takes it when it is free** (owner, 2026-11-20, about 4:50 AM
PST: *"And yes... if a live game is available, of course a judge (or any role!) should be able to just grab it and use
it to get something done! IT's an unused resource otherwise... the worst case."*). A judge, a driver or a fixer
takes the bridge with `rimflow bridge take --idle-ok --for "<what>"` when it is free or ours, starts the game with `./game --idle-ok --why "<what>" up`, does the fix, and releases the bridge the moment the
work stops. A mod does not wait a stage for a game that sits unused. The briefs that carry it are the in-game driver's,
the blind judge's and the live fixer's (`FREE_GAME_RULE` in `maturation.py`). An offline-stage fixer gets only offline
items, because a game-only item goes back to Stage 6, so its brief keeps "Never take the bridge or a game". The same limits bind as above. Measured
2026-11-20: neither `cli.py bridge take --idle-ok` nor `./game --idle-ok` reads a role key; a BENCH take under the role
units of a driver, a blind judge and a coverage judge succeeded.

🔴 **His OWNER hold is takeable 45 minutes after his last interaction** (owner, by question card 2026-10-30, "Should
agents ever be allowed to take your hold?", typed: *"45 minutes after my last interaction, or I deliberately release
it"*). Interaction means his deliberate acts only: any OWNER-attributed ledger event (his `./game`, his
`./bridge conductor|free`, anything run on his words, card or ruling), a bare `./bridge`, his chat prompt to any
seat window (the human-input signal `block_agent_over_slots.py` uses), and the hold's own events. Never his keyboard,
mouse or presence. Until then every take refuses, `--force` included, naming his last interaction; an unmeasured
signal refuses. The one exception is the Conductor's mindful cut (owner 2026-11-19, §Only five acts stay his): from the
Conductor window, `rimflow bridge take|release --per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why
"<why>; lost: <what his sitting loses if this is wrong>; undo: <how he gets it back>"`, never for a flyer's flight. Code: `src/RimMandrake/rimflow/owner_interaction.py`, gate in `rimflow/cli.py` `_take_decision`.
Seat OWNER is his authority, not his activity: an agent's `--owner-said`, `--by-card`, `--per-ruling` or `--why`
restarts nothing (`is_his_act`). `host_guard` holds the same line across clones: a live OWNER lock takes no `--force`
without the cli's verdict.

🔴 **Holding the bridge is blanket authorization — never ask what to do with it** (owner,
2026-09-19, verbatim: *"Never ask that. If you have bridge, you may start steam, launch
game, anything you need."*). Once the lock says it's yours, starting
Steam, launching the game, running a cold load, anything the session needs — none of it
needs a question first.

`src/RimMandrake/Utils/broadcast.py` is the owner's tool and the Conductor's (owner 2026-11-19, §Only five acts stay
his; no other seat or helper runs it); the game-state relay above is its only other carve-out, and since 2026-09-29 that relay is STAMP-ONLY — a seat running it writes the
ledger event and messages no window (owner: game-state broadcasts between agents *"burn tokens
unnecessarily and rarely inform"*; `rimflow next` measures the game itself).
🔴 Run commands yourself — a `!`-prefixed paste handed to the owner is the defect
(hook-enforced on Stop); anything he must LOOK at comes with the complete native path.

## The Conductor has no closed sources — owner, 2026-10-31

*"I don't accept anything being closed to you. Don't make those designs. Conductor accesses everything. Redo that analysis."*

- "Those designs" are designs that close a source to the Conductor. He answered a report that the Dispatcher journal was
  closed to the Conductor and to its helper (record `conversations/2026-10-31-1440-7d9f8e12.md`).
- No design, gate or role file closes a journal, log, ledger, record or tool to the Conductor window. A page that shows
  no spend figure is not a closed source, because the Conductor reads the figures elsewhere.
- "Redo that analysis" was an order for that morning. It is done and binds nothing now.

## The Test Pilot is a permanent way of working — owner, 2026-10-31

*"Ok, so the "test pilot" agent is a real idea we should simply implement and accept, period."*

His earlier words: *"a "Test Pilot" type agent to sit down with the raiders and do a deep debug live with the game, trying things experimentally through bridge, rather than just code changes and long, slow testing procedures"*. Adopted regardless of the arena trial verdict. An item with 3 non-pass runs in a row, or a defect that needs live observation, goes to an `rm-testpilot` agent (`.claude/agents/rm-testpilot.md`) instead of more code-and-retest cycles. The rule and its measurement are in `src/RimMandrake/rimflow/testpilot_route.py`; `rimflow pilot` prints the ticket. Each sitting ends by writing what it learned, false theories included, into the mod's functional script.

## Retest only after a code change — owner, by card 2026-10-31

Card: "Retest rule → Retest only after a code change". An item is tested once per code version; a harness-invalid run is repaired, never counted. Two kinds of run repeat on one code version: the budgeted runs of a kind B scene and the steps of a kind C hunt (§Live tests have three kinds).

A code version is `gate.code_version`: the chain's runtime hash, the runtime hash of every mod composed with it, its code slice and its declared inputs, without the harness and without a driver's result files. Every kind of verdict counts, GAP included: a row owed a live check stays owed however often it runs. A chain the harness stopped gets no verify at all, and one `HARNESS_REPAIR_CAUSE_<HEX>` item per distinct cause holds it until the repair closes. A chain (a named group of checks in a mod's `validation.py`) can change its verdict with no code change. That chain is reported, not repeated: each run of the chain is classed by outcome (§Live tests have three kinds, section 2). `testq.py submit --retest-why REASON` is the human override, and a `--rows` job asks no permission. Code: `src/RimMandrake/Utils/testq/retest.py`, `gaps.settled`.

## No limit without the danger it guards; parallel work is the default — owner, 2026-10-31 to 2026-11-17

*"In general, any decision we make that is shown to simply limit progress, productivity, or parallel construction should be immediately attacked to force it to defend its requirement. Parallel subagent development must be maximized so long as it's reliable, work is fairly checked, etc. That's true of ALL architectural comparisons, ok? They MUST support this. And our handoff procedures and context management must be robust to this."* · *"Trial gets priority, not exclusion."* (2026-10-31.) The trial was the retired architecture trial of that week (card on
`ARENA_DAYZERO_PROVE_GAME_DEV_BAR_LIFTS`); that sentence binds nothing now. An architectural comparison that does not exercise parallel work does not decide which design is best. Review: `design/RimMandrake/parallel_review_2026-10-31/`.

**His test for any guard** (record `conversations/2026-11-16-0055-2020153c.md`, a session begun Sun 2026-11-15 4:55 PM
PST; said of deterministic checks before a model reads a ticket): *"I don't mean to create needless ceremony (and please
don't!) Each element must defend precisely what it's protecting against and have evidence that it actually happens...
but when it has... protect cheaply!"*

**His objections in the 14 days before this was written down**, verbatim from the conversation records (a record's
name is its session start in UTC; the PST start is beside it):
- `2026-11-06-0423-ff1dbc91.md` (began Thu 2026-11-05 8:23 PM PST), on the retired Relentless's pacing of 6 proofs every 30 minutes: *"I had no idea
  we had arbitrary pacing... of course we should drop all this pacing control crap... the LLM's pace things slowly all
  by themselves, we don't need to add to that."* And on its 5 run starts per tick (also retired): *"What's the reason to limit how many
  runs per tick can change? I don't get it."*
- `2026-11-06-0643-4d8425d6.md` (began 2026-11-05 10:43 PM PST): *"WHY must we wait 10 minutes?! All these arbitrary
  pauses cost us a lot of time! Please stop building arbitrary pauses into the system..."*
- `2026-11-06-2027-1f35a6cd.md` (began 2026-11-06 12:27 PM PST): *"I thought we just redesigned the system to eliminate
  a huge number of arbitrary rules. Now yu're describing a similar system again...?"*
- `2026-11-07-0444-79d5c12a.md` (began 2026-11-06 8:44 PM PST), on the test-tools grant that lapsed after 7 days: *"Why
  is there even such a grant and time limit?"*
- `2026-11-09-0336-eca4c96a.md` (began 2026-11-08 7:36 PM PST), on a 3-hour wall time given to a helper round: *"Why is
  10:45pm a limit? No time limits please. GPT might be slowing it down"* (`detached_helper.py` has launched with no
  wall time by default since).
- `2026-11-12-1751-23399ea2.md` (began 2026-11-12 9:51 AM PST), on Explosive Knockback's throw caps of 40 and 60:
  *"No caps please."*
- `2026-11-12-2150-a0f60432.md` (began 2026-11-12 1:50 PM PST): *"WHY would anything cut off text at 600 characters?!
  please get rid of these arbitrary cuts!"* (fixed for the text stores in `9fa4614958`,
  `RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS`).
- `2026-11-17-1807-c041be2c.md`: *"Drop 11-14 limits, old rule."*, quoted whole in §A limit from before the Maturation
  Pipeline is suspect, below.

Each limit was removed one at a time while new code kept adding new ones; Crystallize 2026-W47 adopted the rule below
as its one change (delegated: evidence-for-ask; report
`D:\ClaudeWork\rimmandrake\conductor\crystallize_2026W47\sweeps.md` §3 item 2, §5 cluster 8, §9 candidate 1).

**The rule, for every agent and every program.**
- **Scope:** every cap, pause, wait, timeout, wall time, retry or attempt bound, rate or per-tick count, concurrency
  count, grant expiry and text cut in our code, configs, role files and briefs. A limit inside a mod's gameplay is a
  design promise and is judged by that mod's design (his "No caps please" above removed one).
- **Each limit names two things where it is set** (the comment beside the number, the component's boundary page under
  LIMITS, or the brief): the **danger** it guards, meaning what goes wrong without it; and the **evidence** that the
  danger happens, meaning an incident, measurement, record or lesson, with its date or path.
- **A limit that cannot name both is removed, not tuned.** A bigger number is not a fix. When the danger is real but
  nothing measured supports the LEVEL, the level is the defect, and the launcher picks the bound for the job it is
  launching. Example: `detached_helper.py`'s default spend cap of $15, removed 2026-11-19: `launch` now requires
  `--budget-usd` and `--resume` carries the earlier run's cap
  (`RIMMANDRAKE_REQUIRE_HELPER_SPEND_CAP_FIFTEEN_STOPPED_FOUR_RUNS`, `design/specs/2026-11-19-launch-spend-cap/boundary.md`).
- **When the evidence exists, the guard stays and is cheap** (his "protect cheaply!"). This rule removes no guard that
  has its danger and evidence.
- **Found in the wild:** a limit with no named danger in pipeline machinery is a pipeline defect (§The pipeline fixes
  its own defects): file it with its acceptance test and remove it in the same run, or hand it off with the evidence
  when removing it is outside your tools.
- **Where limits are born:** a boundary page lists each limit the component enforces under LIMITS (§A boundary page
  before pipeline code), and a helper brief that sets a limit says what it guards
  (`src/RimMandrake/rimflow/roles/conductor.md`, helper launches).

**What this does not lift.** His own rulings already name their danger by his word, and change only by his act or the
Conductor's mindful act in their own sections: his holds (the six biome mods held on 2026-11-16, his OWNER bridge hold's
45 minutes, his stops such as the 8:22 PM stop of pipeline reviews on 2026-11-18); the hard per-run spend stop he
ordered (*"Don't let any burn go to 90M this time ok?"*, 2026-11-12, §No launched agent is told its spend; only a
DEFAULT level with no evidence is in scope); the account order and leave lines (§Account and capacity budget); the
machine-safety brakes (the clone pool's 16 clones and its disk floor, §Git); and no live flyer flight test without him.

**Measured, so any later date can judge it.** `python3 src/RimMandrake/Utils/owner_objections.py conversations <start>
<end>` reports `arbitrary_limit` **≤ 2 blocks** for the 14 days after 2026-11-19 (2026-11-20 to 2026-12-03).
Baseline: 8 blocks in 7 records for 2026-11-05 to 2026-11-19 [measured; pinned by
`src/RimMandrake/Utils/selftest_owner_objections.py` at `338b3cae50`]; the 14 days before that (2026-10-22 to
2026-11-04) read 2, so part of the spike belongs to the retired pipelines and a fall is not all this rule's doing.
Review date: 2026-12-03 (any 14-day window after adoption works).

## Wrap-up is a script, never a request — owner, 2026-11-03

🔑 *"asking an agent to do something will NEVER assure it gets done, so there will be debris that piles up if it leaves a trace. That's bitten us many times, and writing even more urgently "no really, please check" does nothing. We need a deterministic check that ALWAYS happens after the agent finishes to ensure that any wrap-up occurs. Period."* A wrap-up that matters is a scripted step or a check that runs after the agent, never an instruction to it. Mechanism: item `AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED`. Designer and debug-process wording: `design/RimMandrake/debug_process.md` ("Test disturbances").

## Every mod's test script matures at first touch — owner, 2026-11-03

🔑 *"We do (2) but only for the mods we're touching recently. Baroque Biomes, GSS, FlowWorks, Solar. After that, it's "the first time an item names a mod, it gets a deep Designer pass to read out its code/spec, expand the spec and validation strategies, certifies it with the user/clarifies confusion, then writes it all out for Relentless. That way we learn as we go, getting better and better at it incrementally rather than pretending we know what we're doing right now.""* 

- "(2)" is option 2 of the card question "How far should the Designer go?". The items below carry it out for the mods that
  he names: the Designer reads each proof script and names each scene's missing site preparation and control case.
- For every other mod, the deep Designer pass runs when the mod is first worked. The Designer reads the code and the
  spec, expands the spec and the validation strategies, and clears up confusion.
- "Certifies it with the user": the Conductor certifies the pass (his ruling of 2026-11-19, `delegation_policy.md` §2),
  and brings him only a question that carries its evidence (§Evidence-for-Ask).
- "Writes it all out for Relentless": Relentless is retired. The Designer writes for the Maturation Pipeline.

Items: `BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS`, `GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS`, `FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS`, `SOLAR_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS`; trigger `FIRST_TOUCH_BUILD_DESIGNER_READS_FIRST`. Role wording: `src/RimMandrake/rimflow/roles/designer.md`.

## A passing bar is an experience, never a tuning number — owner, 2026-11-16

*"Official ruling: Everything about the Coalescence is next version. Everything about the Grown Limbs is next version.
The mod passing bars should not specify flora and fauna yield rates! That would mean every time we renormalize every
mod must repass its bars... drop that! How do we get the Judges to not demand pendantic stuff like this? Who cares the
halfmade tree has more than one graphic? There's variants all the time. Defer Helix trade to next version."*
(OWNER.jsonl note on `RIMMANDRAKE_APPLY_CONTAGION_JUDGE_FIXES_EIGHT_REFUSALS_HALTED`, 2026-11-16T15:14:15Z, about 7:14 AM
PST, after reading the Contagion coverage judge's 25 refusals; "pendantic" is his phone's "pedantic".)

- **The rule, for every mod:** a passing bar states an experience a player would notice. It never pins a yield rate, a
  stat value or any other tuning number a renormalization pass changes, never an asset-variant count, and never "every
  field of every row" of a def.
- **The test, one sentence a judge applies:** would this bar have to be re-passed after we renormalize numbers or add an
  art variant? Then it is not a bar.
- **Named non-gaps** (the Contagion look, `design/concepts/Contagion/coverage_verdict.json` g16 and g18): "the selftest
  covers every rostered plant's ingestible and yield fields"; "the Halfmade Tree resolves more than one graphic
  variant"; "one row per inventory special, each with its field and expected value".
- **Enforced in code:** `src/RimMandrake/rimflow/bar_rule.py` (the rule text and the gate). The coverage judge's prompt
  carries it, every gap names its `bar_kind`, and only an `experience` gap blocks; a gap that pins a tuning number, a
  variant count or a declared field (by the judge's word, the second reader's or the gate's detector) is advisory:
  stored and shown, blocking nothing. A new gap at a later look on material that did not change is the earlier look's
  miss: advisory too (folds in `DESIGNER_GAPJUDGE_FIX_ONE_BATCH_PER_ROUND`). The Designer's leaf rule:
  `src/RimMandrake/rimflow/roles/designer_write.md`. Regression set: `selftest_bar_rule_tuning_numbers.py`.
- **What it does not change:** behaviour is still tested (a comparison a player sees, "gunfire leaves less mulch than a
  burn", is an experience); a mod's selftest may still read its declared numbers as a regression check, which is not a
  passing bar; north-star bars that already pin a number are his to change (census:
  `design/RimMandrake/bars_pinning_tuning_numbers_census_2026-11-16.md`, brought to him by the Conductor).
- **The rest of the same ruling is Contagion's scope:** the Coalescence, the Grown Limbs and the Helix trade move to
  Contagion's next Design Version (the re-scope of `design/concepts/Contagion/`).

Item: `RIMMANDRAKE_TEACH_JUDGES_BARS_HOLD_NO_TUNING_NUMBERS`.

## Aim at a playable version, and build on what already exists — owner, 2026-11-08

He said it of the retired Artisan loop, after a live sitting closed in hours what the loop had ground at for two days:
*"We've got to get out of the "endless checklists grinding against the last 20% closure" experience."* · *"we're
trying to get a Playable v1 right now, not determine the "ultimate perfect mod" right now."* · *"It also seems like
we're biased towards building our own solutions rather than building off of existing game infrastructure (e.g. sand),
open source projects, etc. We should more aggressively leverage existing work that's already proven whenever
possible."* Work one issue at a time to a look, against the version's promise, not against frozen thresholds; before
building a mechanism, look for a vanilla, DLC or proven open-source one to stand on. The judge rule below is the
pipeline's form of the first half. (Source: the Conductor's seed for `RIMMASTER_REDESIGN_ARTISAN_JUDGMENT_NOT_CHECKLIST_GRIND`,
`git show f2ce40bac8:design/RimMandrake/artisan_judgment_seed_2026-11-08.md`.)

## The judge refuses flaws, not polish — owner, by card 2026-11-17

*"We need judges that turn away incomplete work, but not work that isn't tuned just-so or, worse, forever needing more
tuning because we keep asking a judge 'how could it be better?'"* (2026-11-17 about 4:00 PM PST, after Pyrelands' stage
5 took nine recorded looks.) He then ruled by question card, answered about 5:17 PM PST: "Adopt the four rules
(Recommended)" (OWNER.jsonl tsn 1794964642498221334). GPT's nine rulings were not adopted.

- **Rule 1, three reasons to refuse:** a promise is not kept; nobody would notice if a promise were broken (no test, or
  a test that cannot fail; the judge describes the broken mod that would get through); or the test or paperwork is
  itself wrong. Every refusal quotes the promise it rests on. Anything else ("prove it more thoroughly", "test more
  cases", polish, tuning) is advice and does not block.
- **Rule 2, one full inspection, then one check of the repairs:** the second look checks only whether the listed
  problems were fixed, by reading the fix, never by whether a form was filed. It raises something new only when a
  repair itself broke something, quoting the changed passage. Then it stops; what is left goes to the owner as a short
  list, not to another judge.
- **Rule 3, a refusal creates no new requirement:** it binds only "close this hole". Its numbers, day counts, bearings
  and methods are one way to close it; a number binds only if the owner said it. The mod is never changed to hit a
  test's number: that is a question for the owner. (The 2026-11-12 path to pass stands, as a suggestion.)
- **Rule 4, only the owner's promises must be proven:** a Designer "must not read as" line ("it must not read as…") that is neither his words
  nor the plain opposite of the promise is a tip for finding broken mods, never a separate thing to test.
- **The two dials:** who must confirm a refusal (today only late findings get a second reader; one step up: every
  refusal), and the number of looks (starts at 2). A third, the Designer's tips per promise, starts at 1.
- **Two bug fixes land whatever else happens:** a finding the judge rated polish blocks nothing, and a carried gap the
  look found repaired closes without a claim form.
- **When it binds:** once the judge's and Designer's prompts are edited and the judge is recalibrated, not before. Until
  then the judge runs as it stands. The rules are not applied backwards: Pyrelands stays covered.

Full text: `design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md`. Item:
`RIMMANDRAKE_RETHINK_JUDGE_STRICTNESS_BARS_LOOSE_PROOFS_ORNATE`.

## The pipeline proposes a Fable Rescue; it never launches one — owner, 2026-11-16

Asked "Shall I file that as the next step of the work order, with its tests?" about the Conductor's criteria for when a
mod is going round the same ground (both rescues of 2026-11-16, Gimme Some Slack and Pyrelands, were launched by hand),
he answered *"yup. Then we'll watch stats to see if we need to tune that."* (about 10:10 PM PST). The Dispatch tick runs
`src/RimMandrake/rimflow/maturation_rescue.py`, which reads five criteria from records (a check flipping pass/fail
across builds; a tuning number changed twice in opposite directions; the same bar refused two cycles running; the stage
spend ceiling reached without a green certificate; a bar with no test that runs the real mechanic) and writes one
`RESCUE PROPOSED:` line per new piece of evidence to the Conductor log, marked RAISE FIRST. It never launches a rescue, it
proposes nothing for a mod the owner holds or one under or just out of a rescue, and a criterion it cannot read is
reported UNMEASURED. Its thresholds are one settings block, tuned only from the stats (`rescue_proposals.jsonl` in the
Dispatch state dir; `maturation_rescue.py status`). This supersedes "No stall detector" in
`RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY`. Item:
`RIMMANDRAKE_PROPOSE_RESCUE_WHEN_MOD_CIRCLES_BOTH_HAND_LAUNCHED`.

## Every mod builder builds the offline model from the first build — owner, 2026-11-17

*"Also, it feels like the Fable Rescuer again found that offline modeling is REALLY informative and useful. Sounds like
something that should be instructed to the mod builder in general, yes, from the get-go? I kinda thought we already
had, but maybe it hadn't had a chance to benefit from that yet."* (about 10:50 AM PST, after the Explosive Knockback
rescue; "Rescurer" in his words is "Rescuer".) Enacted by the Conductor.

- **What it says:** keep a mod's decision logic Verse-free so an offline test runs the shipped decision; before any
  fix or tuning, build a generator of the situations the mod can be in, read by the bars' own checks; declare the range
  (what it varies, how many cases, what it leaves out), never "every case"; a mod with no decision logic says so in one
  line. It extends his 2026-11-16 "Hunt parameter regimes and regions, not examples" from the rescue to every builder.
- **One source:** the `offline-model` block in `src/RimMandrake/rimflow/roles/fable_rescue.md` step 2. The rescue reads it
  in place; `maturation.OFFLINE_MODEL` reads it into the offline builder's brief (`brief_text`, from a mod's first
  build) and the road-back fixer's (`maturation_autonomy.fixer_brief`). Edit the block, never a copy.
- **What it does not change:** no spend, cap or budget goes in it; the bars, stages and judges are as before.

Item: `RIMMANDRAKE_TEACH_OFFLINE_MODEL_FIRST_BUILD`; selftest `selftest_offline_model_rule.py`.

## Broken tests are expected; an inability to measure is reported up, never read as broken work — owner, 2026-11-03

*"The checker was unable to measure something, and interpreted that as a wrong value rather than an inability that should
have been "reported up" for fix and repair."* · *"This is horrible. We must be tolerant to broken testing and acceptance
tests. This will be very common and expected. ... make our system more rigorously capable in terms of debugging test,
validation, and acceptance tests at the same time as testing code. ... Pretending that lower productivity and cyclic loops
is rigorous checking is self denial."* The proof, harness, site, sandbox and contract are suspects alongside the code;
a failure is attributed before any rework, and an instrument fault becomes repair work while the item waits without a
strike. A false close is still worse than a wait. Design input: GPT consult at
`D:\ClaudeWork\rimmandrake\conductor\test_tolerance_consult\`.

## Codex agents run with full machine access — owner, 2026-11-09

*"Please grant that authority to all agents immediately."* This answered the finding that on Archmagi, Codex's Windows
workspace-write sandbox cannot reach WSL (`Wsl/Service/E_ACCESSDENIED`), so a Codex-run agent (then a Designer, or a worker of the
Relentless, Whittle or Artisan loops, all since retired) can work on the ext4 clones only with `danger-full-access`. Every agent environment now carries
`CODEX_SANDBOX=danger-full-access` (`~/.config/environment.d/50-codex-sandbox.conf`, `~/.zshenv`, `~/.profile`; the
runner is `src/RimMandrake/Utils/agent_runner.py`). It changes nothing else: Claude stays the default runner, results are
still validated by the existing checks, and the quota gate and the rule against falling back to Claude still hold.

## The test is built with the item, offline and live — owner, 2026-11-13

*"Yes, from now on, we build the test at the same time as the item, both offline and online versions. then they get consolidated into the formal tests."*
The run that builds an item also writes its offline test (red-first selftest) and its live test (a bridge script that stages the case and reads state). A live test that could not be run is recorded on the item as UNRUN with its exact command. Both are later consolidated into the mod's formal tests (its functional script and north-star bars). Item: `RIMMANDRAKE_BUILD_TESTS_WITH_ITEM_OFFLINE_AND_LIVE`.

## Live tests have three kinds — owner, 2026-11-23

Item `RIMMANDRAKE_ENACT_THREE_TEST_KINDS_FORCED_COUNTED_HUNTED_NOT_STARS_ALIGNED`. He approved this text on 2026-11-23
(*"Approve updated draft 3."*). Sections 1 to 8 below are the approved text, with one later ruling of his in section 3 (a
scene short of its X of Y; his words are at the end). The reasons and the examples:
`design/specs/2026-11-23-three-test-kinds/draft.md`.

Two cases of 2026-11-23 started the rule. In Explosive Knockback visit 4, the spared-carrier scene failed once because
the carrier walked out of the blast; the one failure blocked the exit of the visit. In FlowWorks, a raider was lifted
out of a pit once in 18 free runs; when the rescue was ordered, the rescue happened 2 of 2 times, and the bug was fixed
that morning.

The Principle of Impactful Evidence is at the top of `infrastructure/agents/CHARTER.md`, in his exact words. Minimum
Force (section 7) is also in the live-testing skills: `skills/live-debugging-proof-harness/SKILL.md`,
`skills/rimworld-live-review/SKILL.md` and `~/dev/MandrakeWorkflows/skills/test-pilot-sitting/SKILL.md`.

### 1. Every live scene has a contract
Before its first run, a scene states:
- **the claim**: one sentence about what the mod does (example: "an ordered rescue carries this pawn out of the pit");
- **the entry point**: where the scene steps in, and which decisions of the mod it leaves to the mod;
- **a valid opportunity**: the state that must hold for the run to test the claim;
- **success**: game state that a program reads (who is where, who holds what), never only a message that the mod wrote;
- **forbidden effects**: what must not happen (a pawn lost or doubled, an exception);
- **the end**: when the program stops looking.
A program decides each run from the contract. An agent reads only a run that the program cannot decide.

### 2. A run ends in one of seven outcomes, kept apart
SUCCESS · MOD FAILURE · RANDOM MISS (a valid opportunity, an allowed miss) · ENVIRONMENT FAULT · APPARATUS FAULT
(our script, our tool or our staging spoiled the run) · UNRESOLVED (something went wrong and nobody knows why) · COULD
NOT LOOK (the run gave no reading).
- A run is an ENVIRONMENT FAULT only when the record shows that something outside the tested behaviour spoiled the
  opportunity. If the mod could have spoiled it, the run is UNRESOLVED.
- A forbidden effect is a MOD FAILURE in any run, even a spoiled one.
- Only SUCCESS speaks for the mod. No other outcome needs a later pass to cancel it.

### 3. The kind says how a scene is judged
A scene with no tag is kind A.
- **Kind A, deterministic.** The scene can make a valid opportunity on demand, and the result is not random. One valid
  run decides: PASS or FAIL. A count such as "4 of 5" is never used.
- **Kind B, stochastic.** After a sincere attempt at control, the opportunity is still uncertain, or the result is random
  by design. The scene looks for evidence of success.
  - A kind B scene passes on one SUCCESS, with no MOD FAILURE and no UNRESOLVED run (section 2) on the same claim and build.
  - That pass says "this was seen to work". That pass does not say how often the thing works.
  - How many runs to spend is a budget, written on the scene before the first run. When the budget ends with no
    SUCCESS, the verdict is INCONCLUSIVE, never PASS and never FAIL. (A scene with X of Y that ends short: below.)
  - Where the result is random by design (a yield, a drop chance), the scene passes on X successes in Y valid
    opportunities. X and Y come from the intended yield and from the testing budget, and are written before the first
    run. Check the rate itself offline where that is possible, because offline runs are free.
  - **Short of X of Y (his ruling, 2026-11-23).** A scene that ends with fewer than X successes escalates to the Conductor.
    The program raises it: one RAISE FIRST line in the Conductor log and a note on the item of the mod's in-game run, with
    the scene, X, Y, the count reached and the tag evidence. The Conductor decides whether the mod's function needs X of
    Y, or X was a guess that guarded against environmental fluctuation. The scene's pass is held until the call is
    recorded (`src/RimMandrake/rimflow/shortfall.py call`). "The mod needs X of Y": the scene reads MOD FAILURE, and
    the mod goes back to an earlier pipeline stage for a fix, as for any MOD FAILURE (the road back of Stage 6 in
    `design/specs/2026-11-13-maturation-pipeline.md`); the call stands while X of Y stands. "X was a guess": a new X goes on the scene before its next run, and
    the scene is judged again. The opportunities already run on the same build count. Nobody else changes X or Y. This
    changes nothing for a scene with no X of Y, and no rule of kind A or C.
- **Kind C, intermittent hunt.** A temporary hunt for a fault that shows only sometimes. A hunt looks for evidence of failure.
  A hunt is never part of a mod's final acceptance tests. A hunt may use kind A or B scenes to get exposure; their verdicts
  stay their own.

### 4. Tags B and C carry their evidence
- Tag B names the things that spoil the run, what was tried to control each, and why that was not enough.
- Tag C names the symptom, how often it was seen in how many opportunities, and where the trace is.
- The tester gives the tag. The Conductor, the owner or a Fable rescue run gives it when the tester does not see the need.
- A tag changes how a scene is judged. A tag never removes a recorded run.

### 5. An UNRESOLVED run, and the hunt
- One UNRESOLVED run is recorded and holds the scene's pass until someone classes it.
- A hunt opens when the fault is serious (one sighting is enough) or is seen again.
- **A hunt never opens silently.** The run that opens it tells the Conductor: what happened, why it matters, the next
  step that would tell two causes apart, and what that step costs. The Conductor may call a Fable rescue, add the hunt to
  a later rescue, or look itself.
- Each hunt step answers a named question. Before each step, state what the answer could change and what the step may
  spend. Count opportunities, not runs.
- A hunt ends as one of four: FIXED AND SHOWN · NOT A FAULT (the apparatus, or disproved) · STOPPED, UNRESOLVED ·
  HANDED ON.
- A trigger found is not a fix. A hunt stopped is not a fix.
- After a fix, the forced scene stays in the live tests only while the fault is likely to return. Otherwise its check
  goes to the offline tests, or is retired.
- A hunt that stops unresolved leaves a record: the symptom, how bad it is for the player, the trace and the save, the
  build and mod list, what was tried, and what would reopen it. A serious unresolved fault also needs a written decision
  at the mod's pass: the Conductor writes it, and the owner reads it in his digest.

### 6. A spoiled environment is repaired, in proportion
- When a run names a thing that spoiled it, the run tries to remove that thing: hold or place it inside the scene, use
  the calm test environment, use a smaller mod list, use a bridge tool, or build a bridge tool.
- Lean towards building the control. A control is rarely for one scene: it lowers the cost of this scene's later runs
  and of many later scenes. So weigh a control against the testing it makes possible, not against one proof.
- Trace a spoiled run to its source. Be inventive. What still cannot be controlled is the reason for tag B.
- The calm test environment is a named bridge profile: one name for a list of controls that the bridge switches on.
  The profile reports which controls it switched on and which it could not.
  A scene checks that the controls it needs are on. A line in a list is not proof.

### 7. Minimum Force (goes in the live-testing skills)
> **Use the least force that makes a scene affordable and reliable, and that leaves to the mod every decision the scene
> claims to test.** Whatever the force steps past is outside that scene's evidence.

The ladder, from most force to least, for "a raider crosses a covered pit": teleport it onto the cover; give it a path
over the cover; a corridor with no other way and bait beyond; a ring of pits round a base and a natural raid. Say which
step the scene uses and, in one line, why not a lighter one. Trying every lighter step first is not required. (The natural
raid is not to be had now: raid tests are paused, §The cheapest test that decides the bar.)

### 8. Verdicts keep, per scene
- A scene's verdict stands until a change touches what the scene reads or exercises. The record names the build that the
  game had loaded, not only the build on disk.
- No exit asks for every scene in one visit, or for one scene several times in a row.
- **The testing horizon.** State which claims are left to the owner's walk and to real play. Those gaps are accepted.

### His words, 2026-11-23

The order (about 11:35 AM PST):

> *"YES! Stochastic event testing requires the changes you pose. 0) We need to define three things to make this work. A: deterministic test (should always be reliably testable, the standard default, what we assume today). B: Stochastic test (testing a reliable capability with many input variables that make the test's outcome unreliable, thus requiring looking for evidence-of-success rather than guaranteed reproducable success on demand. Only justified due to large numbers of unreliable environmental variables or a capability that itself stochastic in yield/production by intention) C: Intermittent test (the test itself is deterministic, but it's seeking an intermittent bug that only occasionally manifests due to complex environments or unknown nature, thus requiring looking for evidence-of-failure amidst repeated apparent successes). We need to explicitly tag tests for their intention, so they can be repeated and judged appropriately. Approved explicitly: 1) Force the situation ALWAYS if possible, there are too many variables to control otherwise. 2) Broaden this definition of detection/success/failure to handle A, B, and C cases explicitly. 3) Required to handle case B. 4) Correct, a detected failed environment is not a mod failure and may or may not indicate a testing apparatus failure, depending on the level of our own control. Each time a failed environmental variable is identified, the testing environment (number of loaded mods, calm testing environment definition, use of or creation of new BRIDGE capabilities to remove the influences) should be explored and exercised if possible. There will likely always be some residual testing influences, but let's get VERY creative in trying to remove them to preserve sanity and not burn all our tokens on repeating large expensive test suites with low yields even if the mod is 100% correct. Push back and question card me, expand this prompt to make it excellent. This is a VITAL upgrade, immediate priority, work with me Fable right now! Then we send it to GPT afterwards for deep review, skeptical breakdown, and fix improvements, and finally work together on the final token-efficient simple bearing language version."*

Card answer 1, how kind B is judged:

> *"For Tests of Type A (intended for capabilities that should be reliable and reliably testable) you would not use "4 of 5" form of success. That would be inappropriate. If there are environmental variables that frequently confound an otherwise reliable capability (such as requiring certain pawns present in specific onfigurations), it becomes test type B where traced success & failures is important evidence but ANY demonstration of success may be as good as we're going to get. Then tuning the X out of Y numbers becomes art and resource balancing. Please push back if this doesn't seem appropriate or make sense or address your concern."*

Card answer 2, kind C and the pass:

> *"Intermittent bugs will be a transient hunt mode, usually by a test pilot, but possibly temporarily inserted into passing pipeline tests while they are still being hunted during the development (after having been seen once or twice). They are never intended to be left on for the final testing suite. As you say, once their source is detected, they may be converted into specific forced configurations (hopefully even deterministic at that point) to ensure it does not reoccur, but after the fix that requires proof of likely re-emergence (you don't want your basic acceptance suite turning into a littany of everything that was once wrong, it's too expensive for live game testing). Offline tests may be more receptive to holding a large number of "once wrong" recursion testing. If the bug is never or exceptionally rarely reproducable and cannot be transformed into a forced test, it is dropped from any mod acceptance testing to preserve efficiency. This should become a broad principle in our game: the Principle of Impactful Evidence: due to fixed resources, we must allocate testing only to what is likely to provide future value, never comprehensive coverage for its own sake, and that equation will change over time given evolving knowledge of an evolving system. [Please help me restate this answer before you record it verbatim, we want this to be superbly stated for the best impact on the game. That principle should be placed at the highest level within this project, I believe you made a place for that guidance recently?]"*

Card answer 3, who tags:

> *"It's not as hard as you say. Of course the User or the Conductor have authority to do this. If environmental variables beyond our control can be identified that preclude a Kind A test, even after sincere attempts to control them, it is reasonable to proceed to kind B testing. There is evidence for it, not a lazy tester. The tester should have to provide evidence that type B testing is required, after a sincere attempt to control the environment otherwise fails. The Conductor or a Fable Rescue would be ideal sources for this if the tester fails to recognize it. Debugging/diagnosing a failed pass is a perfect time to recognize this in an ordinary environment. PLEASE do try to control environment and/or upgrade the BRIDGE with skills to help provide a more stable testing environment first whenever possible. That too is evidence that type B testing is required."*

Card answer 4, forcing and natural runs:

> *"Agreed, forcing is dangerous, not simply preferred. It tests the basic, elemental capability but does not explore important configurations. Here is another Principle, this time for Debugging/testing skills in rimworld: the minimum force required for testing is optimal. Example: We are testing a raider walking over a large covered pit, but they rarely choose to walk over it in a real game. From least desirable/most elemental to most desirable/most complete: teleport raider onto middle of covered pit; pre-set raider walk path over the pit; place pit in narrow hallway without alternative route and place desired object/combatant as bait to draw them over it; place an array of covered pits entirely surrounding a natural base and allow naturally spawned raiders to find their own path across in their own time. [We will almost never be able to afford that final, natural test type due to the time and token cost of each test plus a potentially low yield due to environmental factors and other mod interactions] [Agreed that the player walkthrough can cover the most complex situations, but even still some will simply have to wait for real gameplay to discover, and that's ok. that is the "testing horizon" we can afford.]"*

Card answers of about 12:50 PM PST. Placement of Impactful Evidence: "Top of the Charter, pointer in CLAUDE.md
(Recommended)". Minimum Force: "My restatement, in the live-testing skills (Recommended)". The unexplained kind B
failure, typed:

> *"(1) repeated unexplained failures indicate deeper investigation is required, yes. I would also like to suggest that a Hunt be communicated to the Conductor as an opportunity for Fable Rescue (or at least to be included in such a rescue if it is called later), or the Conductor may choose to look and give a second perspective with its different context to assist. It should not be a silent conversion to a Hunt. It's a big deal in a mod's testing to need this."*

His comments on draft 3, about 1:25 PM PST (the last part of the message orders BRIDGE v2):

> *"1) agreed, but that was kind of covered. We are obliged to trace environmental causes to their source... and unexplained movement of colonists repeatedly out of the zone should show up... but I take your point. 2) Agreed... I had indicated that for stochastic testing you use X of Y successes, where X and Y are set by the intended yield plus the testing resources we have. That should cover this, should it not? 3) Yes... we know this... that's why the rule of minimum forcing. I feel this restates what we ourselves said. But if you find value in its version, so be it. Environment repair is proportionate: but biased towards the spend towards control. It is unlikely a single test will require a unique environmental control, so you are lowering the cost of much future testing (as well as reruns of this test in the future). So proportional here is biased towards testing capacity, not just "the cost of a single proof." Hunt opens on serious, yes surely. Serous faults must announce being dropped, agreed. These are my comments."*

The ruling on a scene short of its X of Y (about 3:00 PM PST; item
`RIMMANDRAKE_ENACT_SHORT_OF_X_OF_Y_ESCALATES_CONDUCTOR_CALLS_IT`):

> *"I can also rule too: It means escallation is required. Does the mod REQUIRE X of Y to be true, or was X of Y a guess and (X-1) of Y is just as good? Depends on whether the mod's actual function requires X of Y or whether X of Y was just guarding environmental variable fluctuation. That's a Conductor call."*

## The cheapest test that decides the bar — owner, 2026-11-23

Item `RIMMANDRAKE_ENACT_NO_RAID_TESTS_UNLESS_FORCED_CHEAPER_TEST_FIRST`. It extends the Principle of Impactful Evidence (top
of `infrastructure/agents/CHARTER.md`).

1. **The cheapest test that decides the bar is the test.** The designer of a test shows, on the scene or the check
   (`cheaper_why` in the test table), why a cheaper, faster, simpler test cannot decide the same bar. Without that evidence,
   the cheaper test is the test. From cheap to dear: an offline test; a state read; one spawned or held pawn and one order; a
   staged event; a scene with many pawns; a raid. A smaller mod list is cheaper than the full list.
2. **A test that we cannot afford is replaced.** When a test costs more time and tokens than its evidence is worth, replace
   it by a less expensive test of the same bar, or of the part of the bar that matters. Do not keep running it.
3. **No raid in a test unless the mod's own function is about raiders.** A raid is hostile pawns that attack by their own
   will: a raid incident, a mech cluster, or pawns under an assault or siege lord. A raid is the most complex stage that a
   scene can use. A hostile pawn that a scene spawns, holds or orders is not a raid.
   - **Raid tests are paused.** Until the test tools can hold a raid still (the Bridge 2 scene library,
     `design/specs/2026-11-23-bridge-v2/`), no pipeline run stages a raid. The switch is
     `src/RimMandrake/rimflow/raid_pause.json`. `raid_pause.py lift --why "..."` lifts the pause, and it is the Conductor's act
     or the owner's. The machinery, and what it does not stop: `design/specs/2026-11-23-raid-tests-paused/boundary.md`.
   - A test that stages a raid carries `stages_raid` (what it stages) and `cheaper_why` in its test table. While the pause is
     on, nothing starts that test. It reads `PAUSED: raid tests wait for the tools`, which is not PASS, not FAIL and not
     UNMEASURED. It spends no trial, turn, look or cycle, and it does not pause its mod.
   - The bar of a paused scene stays open on the mod's record. The mod may go on to its walk brief, which names the open bar.
     The version does not pass until the bar is decided, or the Conductor decides by name what becomes of the bar.
   - The work that builds the raid tools may stage a raid: its item is in the `allow` list of the switch, and its run sets
     `RM_RAID_FOR` to that item.
   - FlowWorks has a real need (raiders on ladders and at moats). Its raid scenes wait for the tools.
     Each part of their bars that one ordered pawn can decide has its own scene now (`sc_moat_walkers`,
     `sc_trench_cover_pawns`, `sc_islands_walker`).
   - Explosive Knockback did not need a raid: no row of `sc_walk_raid` read a raider. `sc_walk_blasts` replaced it, with no
     raid, on the small list. `sc_barrage_perf` does not need the full list either.

**What this does not change.** The bars (a bar about raiders is still a bar about raiders); the kinds of live test and the
seven outcomes; his walk, where he may play a raid; a live flight test of a flyer; offline tests of raid code.

**His words, 2026-11-23, about 9:15 PM PST** (his answer to a card):

> "Two principles. 1) no raid tests until we have better tools, pause them for now. 2) YOU LIKELY DON'T NEED RAID TESTS! That's almost like saying "make the test build a whole colony and then survive a raid." It's overkill for testing almost anything except a raid-centric mod capability. I would strongly urge you NOT to test using raids unless forced. Flowworks I know you want to test their ability to use ladders, attack moats, etc so that's a real need. Explosive Knockback... I do not think needs a raid. That's another testing principle revealed out of this: A test designer must provide evidence that any level of test cannot be satisfied with a cheaper, faster, simpler test. That's a corollary to the "every test should be weighed by its importance for the future divided by its cost in time and tokens." We should add an extension of that existing guidance principle: a test that we can't afford may simply need to be replaced be a less expensive test (simplify this language, improve it). SO... I CHALLENGE Explosive Knockback to defend its need for a raid test!"

Earlier the same evening:

> "Bringing in raiders for a test like Flowworks is doing is one of the most complex testing maneuvers possible. ... we may not be currently ready for complex raider testing until we upgrade our testing apparatus and methodology and BRIDGE and python harness"

## What Python cannot reach goes into the bridge's C#; tests stay in Python — owner, 2026-11-23

This ruling has two halves. Quote the two halves together.

**His words.** He typed these words on 2026-11-23, 5:49 PM PST (the time on the ledger event). His words answer
`design/specs/2026-11-23-bridge-v2/10_for_the_owner.md`:

> *"I am ok with 10_for_the_owner, except for one thing: ANYTHING we literally can't control or measure from Python today is authorized to be installed into the C#. Per-tick, accessing variables... whatever the Python CANNOT reach right now is grounds for more BRIDGE C# to make them accessible. Quote me on that."*

- **Half one: authorized without asking.** Python drives the game through the bridge. Some control or measurement is out
  of Python's reach through the bridge today. Examples: a capture or an act on each tick, a hidden or private value, a
  live write of a value, an event between two ticks. Each such wall is enough reason to add generic C# to the bridge.
  - No agent asks the owner or the Conductor first.
  - The agent that hits the wall builds the new bridge function, test first, or files a ticket for the new bridge function.
  - Do not poll from Python around the wall. A poll can miss an event that lasts one tick.
  - First check that no bridge tool reaches the thing already (`skills/rimbridge-companion/SKILL.md` §0).
- **Half two: unchanged.** Tests, scene steps and verdicts stay in Python. The C# that an agent adds is a generic
  instrument that any test can call. The C# is never a test, a scene or a check of one mod.
- **The question that tells an instrument from a test:** could a scene of another mod call the C# function unchanged?
  Yes: an instrument, so add it to the bridge. No: a test, so keep it in Python.
- **Not changed:** the driver lock, the gates of `build.py`, the live flight test of a flyer (one of his five acts), and
  the ordinary work on tools that Python can reach already.

**Where half two comes from.**

- 2026-11-06: his ask was for primitives of the bridge that Python calls: *"We were always supposed to implement more
  in-game testing built into Bridge to leverage from Python... let's get back into that!"* The Conductor wrote the
  direction on that ask: "Proofs stay in Python, and the game gains generic primitives, not C# test suites"
  (`design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md`; his whole ask is in `draft.md` beside it).
- 2026-11-23, 4:43 PM PST: *"ALSO, MAJOR NOTE: you have often proposed building tests into the C# itself. Each time I remind you that the Python calls to Bridge are lightning fast and take no real time, allowing us to modify tests IN PROGRESS and keep them as Python (cheaper, no DLL compile or conflicts). Then you back off and say I'm right. Let's make sure to go through that discussion early here. I don't want C#-coded tests if we can just as cheaply keep them in Python, that would be a big error."*
- 2026-11-23, 5:25 PM PST: *"Or if we're struggling to build what we need in Python but can't seem to and want to put it in C# suggests better "hands" functions in the BRIDGE. And as the evidence suggests, new BRIDGE capabilities (especially deep in-game access like hidden variable reads, per-tick captures and actions, etc.) make complete sense."*

Item `RIMMANDRAKE_ENACT_PYTHON_CANNOT_REACH_IT_AUTHORIZES_BRIDGE_CSHARP`.

## A cleansed design passes all three checks — owner, by card 2026-11-23

A cleansed design is a mod's design after the pass that strips out extras. The card (Mon 2026-11-23, 8:57 AM PST, item
`RIMMANDRAKE_ENACT_FOUR_CARD_ANSWERS_ON_HIS_TWO_WAY_RULINGS`) asked: *"Which checks must a cleansed design pass when the
held biome mods return?"* He picked *"All three, as today (Recommended)"*: *"Why: it keeps the strongest check before
any build. Buys: nothing changes in the pipeline, and no weak design slips through to a build. Recommended: your later
card kept both gates and did not withdraw the whole-mod check."* The three are the whole-mod check
(`designer_cleanse.py review`), the cold-reader exam (stage 4, `exam.json`) and the coverage judge (stage 5). No agent
switches one of them off for a cleansed design.

## Mod Design Versions use Semantic Versioning — owner, 2026-11-13

*"Each mod now needs an official Version we are building towards. This is not a "game version" but just of that mod. It is not the "current snapshot in git hash" but rather the version of the mod's design we are aiming at."* · *"Semantic Versioning it is."*
Every mod's Design Version is numbered `MAJOR.MINOR.PATCH` (semver.org), with this project's meaning:
- **MAJOR**: the mod's vision changed (a redesign).
- **MINOR**: Divergent additions: work that extends or shifts the vision, filed for the next version.
- **PATCH**: Convergent polish and corrections after a version has passed.
- A version before release is `0.x`; `1.0.0` is the version shipped to players. A judge round is a release candidate, `-rc.N`.
The rule is user-level since the same day (*"Semantic Versioning should be a Lodestar-level, User-level addition to all current and future projects, along with the Convergent changes and Divergent changes that are part of the same design."*): `~/.claude/CLAUDE.md`, terms in `~/dev/Lodestar/LEXICON.md`. Here the unit is the mod. His card answers, 2026-11-13:
- **Problem or Polish:** a refinement that fixes a Problem (a defect, or an experience a player would reject as strange or disappointing) stays in the current version; Polish goes to the mod's Polish list and is not part of passing. The Judge makes the call as best it can; the threshold is tuned with him.
- **Asked at filing:** the current-or-next question is decided when the ticket is filed as active, not when it is picked up. Once filed as current it moves to the next version only by Judge deferral.
- **The Conductor decides both in this repo, and tells him after** (owner, by card Mon 2026-11-23 8:57 AM PST, item
  `RIMMANDRAKE_ENACT_FOUR_CARD_ANSWERS_ON_HIS_TWO_WAY_RULINGS`). The card asked who decides Polish moves and
  current-or-next version in RimMandrake. He picked *"Conductor decides, tells you (Recommended)"*: *"Why: your
  2026-11-19 words say everything else, and you ruled you should not be the bottleneck. Buys: no filing waits for you;
  each call reaches your daily digest with its reason. Costs: a mod's scope can drift before you see it; you correct
  after the fact. Recommended: it matches your later words."* The Conductor logs each call with
  `--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why "<the call and its reason>"`. No filing waits: a helper or a
  Judge files the change with the class that it recommends and its evidence, and the Conductor decides. His user-level
  rule for other projects ("ask at filing", `~/.claude/CLAUDE.md`) is unchanged.
- **Judge deferral** of a bar is approved by the Conductor; he sees each one after.
- **The mods in the Designer enter as 0.1.0** at today's bars, their open gaps sorted into Problem, Polish and next version.
- **The Deep Desert Tribes are their own mod with their own Design Version** (card 2026-11-13 ~9:30 PM PST, "Own mod, own version, later", correcting the 4 PM "One mod, Tribes next version"): Pyrelands 0.1.0 is the biome alone and passes first. The Tribes mod (`src/RimUtinni/PyrelandsMechanics`, `mandrake.rut.pyrelandsmechanics`, design `design/concepts/PyrelandsMechanics`) gets its own Design Version 0.1.0, started only after the biome passes, and stays out of test mod lists until then. Design kept as written.
- **A new mod's first Design Version is 0.1.0, locked by the pipeline without asking him** (§Evidence-for-Ask, below):
  when its concept tree locks, `maturation_autonomy` writes VERSION.json `locked` 0.1.0, `locked_by: pipeline`, and a
  delegated record for his digest. It asks him only when it finds evidence against 0.1.0, quoted on the card.
- **Each passed version is tagged** (owner, 2026-11-20, about 4:10 PM PST: *"Make sure we TAG each finished version
  of a mod so we can easily come precisely back to it, please. This should become policy."*): every version that passes
  gets the annotated git tag `mod/<Mod>/v<MAJOR.MINOR.PATCH>` (for example `mod/GimmeSomeSlack/v0.1.0`) on the commit
  that records its pass, and the tag is pushed to origin. To return to a version, check out its tag
  (`git checkout mod/<Mod>/v<version>`, read-only, or `git switch -c <branch> mod/<Mod>/v<version>` to work from it).
  The pipeline does it: `maturation.py advance <Mod> passed` lands the pass files with `./publish`, tags the PUBLISHED
  commit and pushes the tag. A tag that fails is loud (`PASSED BUT NOT TAGGED`, exit 5) and is retried with
  `python3 src/RimMandrake/rimflow/maturation.py tag-pass <Mod>`; the pass itself stands. A tag name that is already
  taken refuses the pass before anything is written. A tag push whose commit is already on origin/main passes the
  ledger hook (`.claude/hooks/block_ledger_lint.py`). The seat and role clones keep the tags: `./publish` and `./sync`
  fetch with git's default tag following, and `mirror` fetches `refs/tags/*`. The pool clones and their store
  (`scratch_clone.py`) fetch with `--no-tags`, so a tag made after a pool clone was cut is not in it: run
  `git fetch origin tag mod/<Mod>/v<version>` there first. Page: `design/specs/2026-11-20-maturation-pass-tag/boundary.md`.
His words in full and the build plan (lock, next-version file, pass record), still a draft: `design/specs/2026-11-13-mod-design-versions.md`.

## A limit from before the Maturation Pipeline is suspect: act, or ask him first — owner, 2026-11-17

*"Drop 11-14 limits, old rule. Clear its limitations. We are remeasuring it for a brand new pipeline. Don't keep telling
me we can't do things when it's from pre-maturation pipeline decisions. Those old decisions are unlikely to be relevant
anymore. At least suspect it and ask before refusing."* (Tue 2026-11-17 ~11:00 AM PST.)

The incident: SteveDesktop's queue refused Pyrelands and Graffiti and the steward reported `IDLE_BY_RULE`, all on his
2026-11-14 card "Pipeline tests only" (spec 18c), a rule set while the pipeline (spec
`design/specs/2026-11-13-maturation-pipeline.md`) was still being specified. That limit is deleted
(`RIMMANDRAKE_DROP_STEVEDESKTOP_PIPELINE_ONLY_LIMIT`).

The rule, for every agent:
- A limit, gate or refusal that comes from a decision made before the Maturation Pipeline is suspect. Do not refuse on
  it: take the action, or ask him first, quoting the old decision's date and text.
- Tag such a limit "old decision (date)" in any "it cannot be done" claim, and challenge it before our own newer rules.
- What it does not change: his rulings made for the pipeline or after it (his 2026-11-16 hold on six biome mods, no
  flyer flight test, the machine-safety brakes); a limit he re-confirms becomes a new decision with today's date.

## Stops that the work did not cause: system failures, pipeline defects and asks for the owner

Three cases, each with his words and its full rule: §No trial is spent by a system failure, §The pipeline fixes its own
defects and §Evidence-for-Ask. A refusal at a gate is §A fault of form is repaired where it is found.

### No trial is spent by a system failure — owner, 2026-11-18

His words (Wed 2026-11-18, ~10:30 AM PST, about Graffiti, item `RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT`):
*"Ensure it didn't use up it's turns, trials, whatever... I will not accept ANY system that pointlessly expends such
statistical measurements based on failed system calls or behavior. You know that. Fix the system such that it's easy
to indicate this to it. And NEVER tell me "I can't that's frozen" or "it's a write only ledger" or bullshit like
that."*

- **No trial, turn, look or cycle is spent** by a run that died of a system cause (killed, timed out, the CLI exiting
  with no result of its own, a launch that never started) or that he or the Conductor stopped or declares void. A mod's
  real non-pass still counts. "Failed", "void", "zero" and "could not look" stay four answers in every record and line.
- **Automatic:** the tick classes such a run `void_system` from its record's own result (`run_void.py`) and moves its
  book entries to the mod's `voided` list; its faults go on the mod's own count, and at 3 since the last `clear` the mod
  reads `system_fault` (alarm `OPS_MATURATION_SYSTEM_FAULT_LOOP`): nothing launches, no trial is spent.
- **By hand, one verb:** `python3 src/RimMandrake/rimflow/maturation_dispatch.py void <unit>... | --item <ID> | --mod
  <Mod> --since <time> --why "..." [--owner-said "..."]`; `unvoid <unit> --why "..."` reverses it; `voids` lists every
  line. It takes the Designer runs and judges the run started, gives back a coverage look it applied (the grant stands
  again, the earlier verdict file is put back, the void one kept as evidence), and lands the files. An unknown run and
  a double void are refused. An append-only file is no excuse: the fold of its lines is what every reader honours.
- **Void spend is off the ceiling** (his card, 2026-11-18 11:06 AM PST, "Does not count (Recommended)":
  `design/specs/2026-11-18-pipeline-control-surface/03-merged.md`, Rulings 1): the stage ceiling counts what the mod
  cost on its merits; a void run's spend stays measured and is shown apart as void spend (`void_usd`), and the
  system-fault alarm catches a fault loop. The old killed-run refund is retired with it (nothing is charged to give
  back). A ceiling release a **void_system** run spent is given back (the Conductor's decision of 2026-11-18 1:05 PM
  PST, delegated by evidence-for-ask, in his digest; he may overrule); a hand void leaves the release spent.
- Census of every counter and what is not yet reached: `design/RimMandrake/pipeline_trial_counters_census_2026-11-18.md`.

### The pipeline fixes its own defects — owner, 2026-11-15

*"Fix the process wherever it didn't work, ok? Make the pipeline better, don't keep cleaning up after it and leaving it
alone"* (Sun 2026-11-15, on the ledger 12:42 PM PST), then minutes later: *"Please make this a principle of the Maturation pipeline:
the Pipeline fixes its own issues once detected. When there's a clear problem and a known fix... do it. It's not a
ticket for someone else, it's a ticket to file then do yourself."* (on the ledger 12:46 PM PST). Ledger: item
`RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP`, file event 2026-11-15T20:42:04Z and ruling note
2026-11-15T20:46:53Z (tsn 1794775613233596209).

The rule, for every pipeline agent and program (the tick `maturation_dispatch`, `maturation_autonomy`, the steward,
a judge, a fixer, a builder, the Designer's runs, a Conductor helper):
- A defect found in the **pipeline itself** (its code, tools, records, tests, status page) with a clear cause and a
  known fix: file the ticket with its acceptance test, then do the fix in the same run, tests first; publish; say so in
  the report (ticket id, sha). A program does the fix itself when it is deterministic and logs it; when it needs a
  model, the program files the ticket and launches a fixer on it itself, inside its own caps.
- Hand off only with the evidence that §Touching code has a cost; if you see it, do it lists: the fix is not known,
  is outside the agent's tools (it needs the game and the agent holds no bridge; it needs the owner under
  `delegation_policy.md` §2), would change a north-star bar, or touches files another live run holds. Then the ticket
  carries the evidence and what was tried. A defect must pass that section's test 1 (worth the touch) before anyone
  fixes or files it.
- A workaround by hand without the permanent fix is not allowed. Cleaning up after the pipeline and leaving it alone is
  the thing he ruled against.
- What it does not change: a MOD's gaps (its bars, its build work, its findings) keep going through the stages as
  designed; this rule is about the pipeline's own machinery. Ledger calls made under it: `--per-ruling
  RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP --why "delegated: self-fix: <what and why>"`.
- Where the tick still hands a line to the Conductor, and whether it self-fixes now: the prose of
  `infrastructure/state/items/RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP.md`. In the spec:
  `design/specs/2026-11-13-maturation-pipeline.md` §5 "The pipeline fixes its own defects".

### Evidence-for-Ask — owner, 2026-11-15

*"You are repeatedly asking me to rule on whether 0.1.0 is appropriate for a new mod. So far it is every single time.
You must have evidence why 0.1.0 is NOT appropriate to pause to query me from now on. For ALL questions and choices from
now on, Conductor must have evidence why it does not select the obvious answer before it pauses for the human, alright?
This is a RimMandrake-wide ruling for all pausing agents. Let's call it the Evidence-for-Ask rule."* (Sun 2026-11-15
~11:40 AM PST.)

The rule, for every agent and role that can pause for him:
- Take the obvious answer instead of pausing. Log it as a delegated call: `--per-ruling
  RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME --why "delegated: evidence-for-ask: <the call, and why
  nothing argues against it>"`. It reaches his daily digest (`delegated_digest.py`). It is ours, never stored as his.
- Pause only with concrete evidence against the obvious answer (a record, a measurement, his earlier words), and put
  that evidence on the ask. An ask without it is not sent.
- What it does not change: the five acts that stay his (§Only five acts stay his: his live walk among them) still wait
  for him, and a quotation of his words is written only from his words; each ask now carries its evidence. Every
  other card is reviewed by the Conductor first and acted on when nothing argues against the obvious answer.
- In code: `maturation_autonomy.version_evidence` / `autolock_and_land` (Design Version 0.1.0); `designer_stage`
  accepts a root or a flagship pick approved this way (`delegated: "evidence-for-ask"`, `CONDUCTOR:<tsn>`), and an ask
  whose `evidence_against` is filled still waits. The other places that still pause, with the obvious answer for each:
  `infrastructure/state/items/RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME.md`.

## A fault of form is repaired where it is found; it never stops the work — owner, 2026-11-20

*"That is a categorical error. A mod generating a too long name, even if that were a problem, should be given the chance
to just fix it right there and continue without loss of context or really any time at all. Confusing "errors" and
"refusals" of naming conventions with mod errors is stupendously unacceptable. The ultimate pedantry. "We are here to
judge whether you killed someone or not, but since your shoes aren't properly tied, I'm forced to render a mistrial and
say inconclusive." I really really need you to stand back and look at how we do things now. Any agent doing "something
wrong" should be given the chance to fix it and redo it right now without any delay. Period. No more large
consequences for trivialities. What is going so wrong here?"* (Fri 2026-11-20 about 11:50 PM PST; on the ledger as the
file event of item `RIMMANDRAKE_REPAIR_AT_THE_REFUSAL_NO_STOP_FOR_UNTIED_SHOES`, 2026-11-21T08:28:51Z.)

Definitions:
- **A fault of form** is a fault in how work is presented: a name, a flag, a missing paste, a missing section, a stale
  stamp, a file that a tool can make, a format, a count of the wrong slots.
- **A fault of substance** is a fault in the work: the mod is wrong, the test is wrong, the run died, the machine or an
  account failed without a plan. Waits that end by themselves (a planned account drain, a held bridge, his hold on a
  game) are neither: they wait, and count nothing.

The two repair routes, in this order:
1. **Repair and continue.** The tool repairs the input itself, prints one `NOTE (form, repaired): <what> -> <how>`
   line, records the note on its event, and the act goes on (exit 0).
2. **Return to the agent.** When only the agent can repair it, the refusal reads `REFUSED (form): <what>` with a
   `REPAIR: <the command, or the text to add>` line. The agent's run does the repair and repeats the act at once, with
   its context. Every launched brief carries the line: "A refusal that names its repair is an instruction: do the
   repair and repeat the act; never stop or hand off for it."

For a program caller (the tick): it never sends a refused input again unchanged. It applies the named repair itself,
or it launches one small repair run with the refusal as its brief, and the mod's line reads `repairing: <what>`. A
refusal of form never counts as a system fault, pauses a mod, voids a run, spends a trial or waits for a hand. What
happens when a repair did not hold is promised and tested in the boundary page below.

The fault loop counts substance only. Every refusal that reaches it carries a class; an unclassed one counts as form
and is logged for the census, so a new gate cannot bring the old behaviour back unseen. When the loop trips on
substance, it starts the repair itself (the boundary page below).

What still refuses, because it is substance by his standing rulings: his five acts, his holds, his OWNER bridge hold,
a `./pipe` stop, the per-run spend stop he ordered, the account order and leave lines, and the machine-safety brakes.

Mechanism: `src/RimMandrake/rimflow/form_fault.py`. Promises and their tests:
`design/specs/2026-11-21-repair-at-the-refusal/boundary.md`. The census of refusal sites:
`design/specs/2026-11-21-repair-at-the-refusal/census.md`.

### 🔴 His word and the Conductor's act are not refused — owner, 2026-11-20

*"I need you to make the system less fussy about user comments. When I say something I don't want to hear it sounded
like a question or that the card needed a user statement. You work for me. The conductor works for me. It does things
for me. The system should not be refusing needed items. The system should not be in our way. Make it so."* (Fri
2026-11-20 ~5:48 PM PST.) Item `RIMMANDRAKE_STOP_GATES_DEMANDING_OWNER_WORDS_HE_ALREADY_SPOKE`; census of every site:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\owner_words_gates_census.md`; page:
`design/specs/2026-11-20-owner-words-not-refused/boundary.md`.

- When he states something in the Conductor window, or the Conductor acts for him, no gate, hook or tool refuses the
  act for lack of a quote, a card text, a card answer or a provenance flag of a particular kind. The act goes through
  and is recorded. A missing piece of provenance becomes a recorded note or a self-repair.
- `--owner-said` records his words as he typed them. A quote that ends in "?" is recorded; a bare "yes" is recorded
  (add `--why` to name what he agreed to).
- What each gate now does instead of refusing, with its test: the page above
  (`selftest_owner_words_not_refused.py`). The gates themselves: the census above.
- **What stays:** his five acts (§Only five acts stay his); his OWNER bridge hold and its 45 minutes; his mod holds
  for helpers; `./pipe` stops. No helper, tick or other seat gains his authority or the Conductor's. Nobody writes
  words he did not say into `--owner-said`: an act without his quote is recorded with `--per-ruling` or `--why`.

### A refusal carries its path to pass; a criterion nothing could pass is an alarm — owner, 2026-11-12

*"We MUST ensure that we don't get trapped letting poorly tuned Judges refuse everything forever, burning tokens, and
providing no signal to improve upon. ANY refusals must be as detailed as the evidence they are rejecting and include the
fixes and paths towards passing that are attainable and reasonable. It also MUST include assessment of the acceptance
criteria themselves. If they are found to be flawed, we need a process to immediately bring a neutral fixer in to repair
them independent of the Judge itself so as not to bias towards pass = success and repair the demonstrated flaws or
insufficiencies. Evidence that "this item doesn't pass" is not valuable. Evidence that "nothing could ever pass" is
grounds for immediate, swift action. Then the item is immediately rejudged once the acceptance criteria are repaired.
Agreed? This is VITAL. No more repeated loops for the sake of ceremony! No more broken acceptance tests causing judges to
destroy my account uselessly."*

- **Every refusal is a record** (`refusal_contract.py check`): its evidence, what it shows, `would_pass`, the
  `smallest_fix` (attainable, cost) and a `criterion_verdict` on the clause itself. A refusal without them is refused
  itself: re-asked once, and never counted against the item or sent back to the builder. Two malformed answers mark the
  brief FAILED.
- **A flawed or unattainable criterion goes to the neutral fixer** (`roles/criteria_fixer.md`, `refusal_contract.py
  repair`), never to the builder; `diffguard` refuses any undeclared loosen, and an owner bar is never repaired: it is a
  card for him.
- **Only a CALIBRATED brief's refusal has a consequence** (`infrastructure/state/judge_calibration.json`); an edit to a
  brief resets it to UNTESTED, and an UNTESTED brief's refusal is stored and shown only.
- **Loops stop:** the third refusal of one clause triggers repair; the fourth refused verdict on one item, or a family
  refusing most of what it sees, raises `REFUSAL_NOTHING_COULD_EVER_PASS` to the Conductor. The Designer's coverage
  judge stops at its second not_covered, parks on a second refusal while he is away, and parks at twice the item's cap.
- **A judge does not grade its own criterion** (owner 2026-11-16, below): the Contagion judge marked all 25 of its own
  criteria `sound`. The coverage judge's `criterion_verdict` is kept as its opinion (`judge_criterion_verdict`); the
  binding one comes from a second reader that did not judge (`coverage_judge.second_read`, one fresh Opus call), and
  with no second read the refusal is stored and shown only. A judge confessing its own criterion flawed still reaches
  the neutral fixer.
Spec: `design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md`. Item: `RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS`.

## After a change, only the checks that the change touches run again — owner, 2026-11-21

His words, 2026-11-21 about 1:00 AM PST (item `RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203`), when the
steward wrote that all 203 in-game checks of Gimme Some Slack 0.1.1 had to run again after one feature (the power
switch lamp) landed: *"No all 203 checks should NOT have to be rerun it should only be the ones pertaining to the
switch. This is so stupid! We've already agreed that when you change code only the tests that relate get run. Extend
that logic everywhere! Please get efficient! No more ceremony and over completeness!"*

The earlier agreements he cites: his card of 2026-11-12 (rule 2d, `design/specs/2026-11-13-maturation-pipeline.md`):
*"Piecemeal revalidation of specific touched line items is crucial"*; his live-run ruling of 2026-10-25 (its words are
below); and
`run_selftests.py --only <tests>` with `pipeline_tests.json` (only the tests for what you changed).

**The live-run ruling of 2026-10-25, merged here 2026-11-23.** *"Targeted runs should always have been policy."* Then:
*"When we're building out content we should be focusing aggressive testing only on the highest value informative tests
not rerunning other tests that happen to be nearby or ahead of it."* A live run after a change runs only the chains and
rows that the change touches: `modcheck run <Mod> --item <ID>`, `--chains` or `--rows`; the whole suite needs `--full`.
Run the rows that can change what we do next. Never re-run a row only because it shares a chain with, or runs before,
the row you need. A brief that asks a live helper for the whole suite to prove one fix is the defect. The design of the
code that does this: `design/RimMandrake/focused_testing_plan_2026-10-25.md`. The daily full sweep that the ruling once
allowed is gone (2026-11-23): a full pass is a named act with its reason, below.

**What it narrows.** The build-match change of 2026-11-17 (item `RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO`).
The text is ours, as `build_match.py` records it: "A verdict whose mod hash or game build differs from the build he walks
does not count; its check is re-run." He approved it, 2026-11-17: *"Leave it as is, I justed wanted to understand. I
approve your changes to the Step 6->Step 7 transition and preparation."* This ruling narrows it to the checks the change touches. A game build that differs still
re-runs the row (the game itself changed). A mod hash that differs re-runs the row only when the change touches its
check.

**The rule.**
- It applies at every stage: the offline certificate, a blind cycle, an in-game visit, the walk build match, the
  nightly and `./publish`.
- A check relates to a change when the change touches something that the check reads or exercises. One program answers
  that for every stage: `src/RimMandrake/rimflow/rerun_relation.py` (page
  `design/specs/2026-11-21-rerun-only-related/boundary.md`). A check declares its `exercises`, `reads` and `file`; a
  declaration beside a locked table goes in `version/exercises.json`. A Python file relates by top-level name, a JSON
  file by the check's own entry, a C# change by source file (the DLL is derived), every other file by file. A full-list
  check, or one that declares `"*"` (a log budget, a load-without-errors check), relates to the whole mod.
- A row made on an earlier build still counts when nothing that its check reads or exercises changed. A whole table is
  never sent back because the build hash moved.
- When the relation cannot be read for a check, that check runs again, and it is listed so that someone can declare it.
  The others still count.
- A full pass is a named act with its reason, never a default: `maturation.py certificate <Mod> --run --all "<why>"`;
  `--run` alone runs only the stale, red or unstamped deciders. The blind judge's reproduction of the recorded offline
  runs is the blind stage's own independent check, not a rerun after a change; after a fix of its own it reruns only
  the deciders the fix touches.
- Never tell the owner that all checks must run again after a small change. Name the checks that the change touches
  (`maturation.py next <Mod>`, `build_match.py check --mod <Mod>`).

**Where it is in force.** The in-game build match and Stage 6 exit (`build_match.py`, `maturation.py`), the visit brief
and `next` (they name only the checks to run), the walk identity, the offline certificate (`ran_on_this_build` hashes
each test's own reads; `--run` keeps green-on-this-build tests), `./publish` (it runs only the pipeline tests whose
inputs the change touches; every test only when the change set cannot be read), and the nightly (finished mods only).

**Risk, stated once.** A change can break a check that no declaration connects to it. The guards are the whole-mod
checks, the next visit of the related checks, and his walk. No full rerun is added to cover it.

## No mod runs forward on a broken pipeline — owner, 2026-11-19

His words (Thu 2026-11-19 ~6:05 AM PST, item `RIMMANDRAKE_ENACT_NO_MOD_RUNS_ON_BROKEN_PIPELINE_RULING`): *"Ok:
standing rule. You offered to run GSS on a broken pipeline. We're not running mods forward until the pipeline is fixed,
ok? So now you don't have to ask me anymore for that."* Half an hour earlier, by card (item
`RIMMANDRAKE_PROVE_PIPELINE_READY_BEFORE_SLACK_CEILING_RELEASE`, answered 5:35 AM PST), he had released GimmeSomeSlack's
ceiling *"but ONLY if we have repaired all tickets remaining for the pipeline stages it's about to engage, including the
judges etc. The pipeline's ready, right?"*

The incident: after his "One mod at a time" the Conductor switched GimmeSomeSlack on (`./pipe log`, act ct_000066, 5:28
AM PST). A readiness check then found three open faults on its path, each able to give a stuck stage, a lost trial or a
ghost run (`D:\ClaudeWork\rimmandrake\conductor\pipeline_ready_for_gimmesomeslack_20261119.md`, verdict NOT READY), and
the Conductor offered him to run it anyway. GimmeSomeSlack was switched off again (act ct_000070, 6:00 AM PST).

The rule, for every agent and program that can move a mod:
- No agent switches a mod stage on, releases a ceiling for a mod, or launches a build, fix or in-game visit of a mod
  while any open Maturation Pipeline ticket classed BLOCKS lies on that mod's path.
- **The check is a readiness list for that mod**, like the GimmeSomeSlack one: every component the mod will touch, in
  path order, judges and the road back included; each open pipeline ticket on it classed **BLOCKS** (can give a wrong
  verdict, a lost trial, a ghost run or a stuck stage on this run), **RARE** (a rare failure listed, not fixed, under
  §A boundary page before pipeline code, Decision 4) or **NOT ON PATH**; and for each component whether it was looked
  at. "Could not look" is never counted as clean: a component not looked at keeps the list from reading READY.
- **"Fixed" is measured by that list: it reads READY for that mod** (no BLOCKS row open, no component unlooked). Then
  the mod runs under the usual rules: his holds, his newest word on how many mods run at once, the stage ceiling. His
  one-mod-at-a-time words of 2026-11-17 and 2026-11-19 are replaced: two mods (2026-11-20), then three, while the
  pipeline shows no sign of breaking (2026-11-20 4:12 PM PST, item `RIMMANDRAKE_BURN_STEVEN_FULLY_NEXT_NOT_LUKAS`; three
  again on 2026-11-23).
- No agent asks him whether to run a mod before its list reads READY: the answer is already his, and it is no.
- What continues: pipeline repair (the BLOCKS tickets first, each under §The pipeline fixes its own defects), design
  text, investigations, read-only checks and readiness lists.
- What it does not change: his holds and his other rulings (a ceiling above the stage's still needs his word or the
  Conductor's act, §Only five acts stay his); the tick
  keeps running.
- **The switch that holds it is one per mod:** `./pipe off <Mod> --why "no mod runs on a broken pipeline (owner
  2026-11-19): readiness <path> NOT READY"`, lifted by `./pipe on <Mod>` only with a READY list's path in its `--why`.
  It refuses every launch the tick makes for that mod (they carry the mod, `RM_CONTROL_MOD`); a helper the Conductor
  launches by hand carries no mod, so for that the rule binds by itself. `./pipe off all` is the wrong switch: every run
  is in scope `all` (`control.run_scopes`), so it would also stop the repair helpers this rule wants. Ledger calls made
  under it: `--per-ruling RIMMANDRAKE_ENACT_NO_MOD_RUNS_ON_BROKEN_PIPELINE_RULING`.

**This section replaces the rule of 2026-11-03** (the Conductor's decision, 2026-11-23: the later ruling wins). Then he said of
Relentless, which is now retired: *"Relentless fixes operations or conductor or designer or any other part of the system
before continuing content creation yes."* The pipeline's form of *"Yes relentless fixes itself first."* is §The pipeline
fixes its own defects. The health verdict, its budgets and its pauses are deleted; his other words of those days are in
`design/RimMandrake/CLAUDE.history.md`.

## Mods keep their own state; all other work goes in the one list; the pipeline works the list — owner, 2026-11-22

*"Foundry and Bench WORKED. But they were using the human as many aspects of what we now call the Maturation Pipeline
manually. Because the pipeline wasn't working for a bit, we seem to be reverting back towards Bench and Foundry. But
that's the wrong way, making it more and more efficient to ask me to judge things via a walk and through constant
talking. Instead we need to improve the pipeline to take over more of these capabilities in a semi automated fashion,
know when it's in trouble and needs a human, but also recognize when it's not. THAT's the motivation for all the
modifications to the pipeline. ... We're still trying to make a pipeline that can handle this stuff, and that's ok, as
long as we're converging. What we've found is that we're great at capturing needed work that's generated by the
pipeline itself, but poor at capturing and integrating and pursuing additional work made when you consult the human,
or that questions the pipeline itself. Conversely, when we focus on that, we tend to start dropping the routine work
of the pipeline. It seems to be a focus of attention problem. ... one place to write things down, one place to close
them... seems useful. It's ok to have mods track their own state, that I understand. The point of agents and
pipelines. But anything outside that context seems like it should then go into a single "holds everything else" list
to me."* (Sun 2026-11-22 10:27 PM PST; on the ledger as an OWNER note on item
`RIMMANDRAKE_STUDY_ONE_PLACE_FOR_OWED_WORK_HE_ASSUMED_IT_EXISTED`, 2026-11-23T06:27:55Z.)

- **Two kinds of state.** A mod's open work (version, bars, gaps, polish, next version) lives in the mod's own folder,
  and the Maturation Pipeline works it. All other work lives in one list, the rimflow ledger: one place to write it
  and one place to close it.
- **Nothing else holds open work.** A handoff, a log, a status page, a memory file, a run's result file and a reply to
  him may describe work. None of them is where the work is owed. A debt that is only in one of those is not recorded.
- **The pipeline works the list.** The motive of every change to the pipeline is that the pipeline takes over more and
  needs him less. A seat or role that works the list by hand, with him or the Conductor window as its memory, is the
  reversion that he names. The list's worker is the pipeline's own clock.
- **The pipeline knows when it needs a human and when it does not.** Each kind of list work states the evidence that
  sends it to him. Everything else proceeds and reaches his daily digest. His five acts stay his. A trouble report
  names the outcome at risk, why the pipeline's own recovery was not enough, and the smallest act that clears it.
- **A view is not a store.** A page for him is built from the list by one rule. Beside it stands a count of needs that
  started somewhere and have no home in the list, because a view built from the list alone cannot show what never
  reached the list (his words, 2026-11-22 7:05 PM PST: *"if you show me JUST from the ledger... I will never know what
  was dropped"*).
- **No gate for it.** No hard stop makes an agent reconcile a record before it ends (§A fault of form is repaired
  where it is found). Where a program can check an outcome, the check decides that the work is done, and a note does
  not. Not every remark is work (§Touching code has a
  cost).

### The list's worker is a pipeline in its own right, and it must not need the Conductor to run — owner, 2026-11-22

*"I need to become aware of "the smaller copy of the pipeline" that you use for "some work different than mods." This
is the key. That is the piece that isn't working yet. We can fix this! Please include it now on the Maturation Pipeline
sheet as its own pipeline, with whatever modules/stages it has within it, along with what's running and why. THAT is
the thing that needs to be held accountable for "what are you doing now, what's next, what closed, what remains open
and why, what's been escalated for help, what is ready for human review"... all of that. That seems like the piece
that would own much of this. When we say "the pipeline should be repaired," it is the smaller pipeline that processes
that request, as it is not mod work, if I understand it. Let's make it as formalized as the mod-based pipeline."*
(Sun 2026-11-22 10:47 PM PST.)

*"And I agree, the Conductor should NOT be constantly required just to keep a pipeline running... that means we DO
have things that still need fixing. The conductor monitors, works with us, and rescues/repairs what MUST be done...
but if we're always in that mode, the pipeline is incomplete."* (Sun 2026-11-22 10:48 PM PST; on the ledger as an OWNER
note on item `RIMMANDRAKE_RESUME_PLAN_RUN_WITH_HIS_SECOND_PIPELINE_DIRECTION`.)

- **Two pipelines.** The Maturation Pipeline works mods. A second pipeline works the list (the plan calls it the List
  Pipeline; the name is his to change). A request to repair the pipeline is work for the second pipeline.
- **The second pipeline has stages, and it is shown on the Maturation Pipeline page** beside the mod pipeline. It, not
  a seat, answers six questions: what it is doing now, what is next, what closed, what remains open and why, what is
  escalated for help, what is ready for human review.
- **It is as formal as its work needs, not as heavy as the mod pipeline.** A small fix with its test passes in
  seconds through the stages that are programs.
- **The Conductor's place:** it monitors, works with him, and rescues and repairs what must be done. A stage that
  needs the Conductor window to keep it running is a defect of the pipeline, and the page shows which stages are
  still worked by hand.

Study, plan and build order: `design/specs/2026-11-22-coordination-every-agent-must-use/` (`plan.md`). The ancestors
and what they did wrong: `plight.md` §10 in that folder.

## The nightly checks finished mods only — owner, 2026-11-15 (card)

Asked what should happen to the nightly run (evidence: `D:\ClaudeWork\rimmandrake\conductor\nightly_reds_report_20261115.md`
§5), he chose *"Pause nightly and fixers until a mod passes"* and typed: *"(3) because I think Nightly tests should check
mods with finished versions, not mods in production. Code is too fluid otherwise. Wrong phase."* (Sun 2026-11-15, on the
ledger 4:10 PM PST: item `RIMMANDRAKE_PAUSE_NIGHTLY_SWEEP_WRONG_PHASE_UNTIL_MOD_FINISHED`, file event tsn
1794787827067966182). He then asked *"Keep nightly tests for Pipeline elements perhaps though?"*; the Conductor's answer,
his to overrule: the pipeline's machinery is the most fluid code there is, so it is checked at the door instead.

- **The nightly set** is the tests of mods with a passed Design Version (`design/concepts/<Mod>/version/stage_record.json`
  at `passed`, or a kept older record that is): `src/<tier>/<Mod>/**/selftest*.py` and
  `src/RimMandrake/Utils/selftest_<mod>_*.py`. A mod in production is never in it; process machinery is never in it.
  None passed: the run says "nothing finished yet", green. `python3 src/RimMandrake/Utils/nightly_scope.py show`.
- **The nightly runs now.** He chose the hold until a mod passed; the first mod passed and the hold lifted itself (measured
  2026-11-23: `nightly_scope.py show` reads 41 tests from 1 finished mod, and `timers_held.json` is empty). So a missing
  nightly is a fault. A hold would come back only by `timers_guard.py hold --until finished-mod`, a recorded,
  ruling-backed stop.
- **When it runs**, it runs on a clean clone of origin/main (`/home/mandrake/rm/nightly`) with `~/.local/bin` on PATH, and
  no fixer launches on a red until it has been rerun red on current origin/main (the build cop's RerunGate files the item
  only then; red_dispatch launches only on filed items).
- **The pipeline's own tests run at the door:** a publish touching a Maturation Pipeline file runs the pipeline tests whose
  inputs it touches and refuses on a red (`src/RimMandrake/Utils/pipeline_tests.json`, `publish.py pipeline_checks`);
  tests that read live state are listed there and excluded. `"nightly": true` in that file puts them back in the nightly.
- **What stays:** the 13 publish tree checks; agents run the tests for what they changed before a commit; every item is
  built with its tests (2026-11-13); no test is deleted.

## Spend in weighted tokens; the live game is never held for his look while he is away — owner, 2026-11-16

His words (Mon 2026-11-16, ~1:08 PM PST, on the ledger 21:10Z under `RIMMANDRAKE_ENACT_TOKENS_NOT_DOLLARS_NO_LIVE_HOLD`):
*"Please speak in terms of weighted tokens not money. The money quotes don't translate meaningfully. Do not hold live
testing when I can't go to the desktop such as now."*

- **Weighted tokens, never money.** Every line a person reads states spend in weighted tokens: the DETACHED RUN ENDED
  lines and notes, `maturation_dispatch.py` status, pause, release and `releases` lines, the maturation status page,
  `maturation_hands.py list`, and the Conductor's own words to him.
  List dollars stay only inside, where a tool needs them (`spend_watchdog.py --cap-usd`, the run record's `cost_usd`, the
  stage ceiling and caps); a line about a dollar-kept limit converts at `maturation_dispatch.WT_PER_USD` (exact: one
  list dollar is 1e6 / the reference input price) and marks the figure `≈`. Moving the ceiling and caps themselves into
  tokens: `RIMMANDRAKE_KEEP_STAGE_CEILING_IN_TOKENS_NOT_LIST_DOLLARS`.
- **Weighted by model too** (his words, ~10:03 PM PST: *"I want you to properly weight tokens by the model as well so
  they are more comparable. That's how I always want us to measure"*; item
  `RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT`). The unit is `weighted_v2`: each usage field (input, 5-minute and
  1-hour cache writes, cache reads, output) at that model's own list price, divided by the list price of one uncached
  Opus 5.5 input token (= 1). The one table is `role_launch.MODEL_PRICES`, from Anthropic's published list prices; a
  model missing from it fails by name, never a fallback weight. A run is weighed from its result's `modelUsage` (the
  whole process, subagents included), else its usage and model. A `weighted_v1` figure (relative to the same model's
  input, no model weight; Opus reads counted at 0.1 where the list says 0.05) is converted by
  `role_launch.tokens_v2` before it is compared with a v2 one; limits set in v1 were converted at the measured
  Opus v2/v1 ratio so they keep meaning the same real spend for Opus runs.
- **No live hold for his look while he is away.** A staged owner look is never a reason the pipeline holds, parks or
  pauses the game: the look is kept as a save, the game goes back to the tick, and the look is re-staged from that save
  when he sits down. Stopping a live run to stage a look is a kill, which the tick retries like any kill
  (`maturation_dispatch.retriable` counts kills, not launch faults), and `maturation_dispatch.py clear` lifts the stop
  an ended automatic run left. The in-game driver's brief keeps every `*OWNER_LOOK*` save. His own OWNER bridge hold
  while he is walking a look stays his (§The bridge is passed through one file).

## No launched agent is told its spend; the hard cap is enforced from outside — owner, 2026-11-16

His words (Mon 2026-11-16, ~6:25 PM PST, watching a live builder; item `RIMMANDRAKE_HIDE_SPEND_FROM_BUILDERS_CAP_NAGGED_EVERY_TURN`):
*"I don't like how you're telling the agent how much it's spent. This has been shown to reduce their creativity and
obsess on cost savings..."* and *"You're telling it constantly"*.

- **The agent is blind to its spend.** No launch states its spend, cap or what remains: not a harness flag, a brief, a
  footer, a hook, a packet, a resume prompt or a tool's output the agent reads. `claude --max-budget-usd` is banned in
  every launcher: it makes the harness inject `USD budget: $used/$cap; $left remaining` every turn (attachment
  `budget_usd`; 143 in one 11-16 builder run), and Claude 2.1.311 has no switch that keeps the cap without the
  reminder (`CLAUDE_CODE_DISABLE_ATTACHMENTS` drops every attachment, hooks included).
- **The hard per-run stop stays** (owner 2026-11-12: *"Don't let any burn go to 90M this time ok?"*), enforced from
  OUTSIDE by `src/RimMandrake/rimflow/spend_watchdog.py`: it wraps the claude argv, pins the session, reads the
  transcript usage (`role_launch.transcript_usage`, each message weighted_v2 at its own model's prices), and at the
  cap stops the run and writes the result claude writes at its own cap (`error_max_budget_usd`,
  `stopped_by: spend_watchdog`), so the run is recorded as stopped on cap, raises the same alarms and stays
  resumable. Its rate is the list price itself (weighted_v2 x the reference input price), and a model not in the
  table stops the run by name.
  Launchers call `spend_watchdog.wrap(argv, cap_usd)`; `selftest_spend_blind_agents.py` sweeps the tree for the flag.
- **Humans still see spend**, in weighted tokens: run records, the DETACHED RUN ENDED lines, the status page. An
  Operations run is still told the ACCOUNT's reading (its job), never its own budget or spend.

## The pipeline's pause switch and its "up next" forecast — owner, 2026-11-18

His words (Wed 2026-11-18, ~10:27 AM PST, item `RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED`): *"I think we may
need to have Dispatch have a "pause all pipeline items" setting we can easily toggle (non-code-editing) for situations
like this. We really don't want work starting (or failing to start) when we expect otherwise. And perhaps some kind of
"up next" feature we can ping that says what WILL happen in some amount of time if we do nothing, so we can confirm
using its own code..."*

- **One switch, no file editing:** `python3 src/RimMandrake/rimflow/maturation_dispatch.py pause [<Mod>] --why "..."
  [--until <time>|--until-release] [--stop-live]`, `resume [<Mod>] --why "..."`, the same as `rimflow pipeline
  pause|resume` and as `./pipe off|on all|<Mod>`: a switch in the one control store (next-but-one section), binding the
  moment it commits. `pause.json` is retired (still read, so an old entry would still hold).
- **What it stops:** every `systemd-run` launch in `src/RimMandrake` (`control.launch_unit`; the census is
  `control.call_sites`). A live run finishes unless stopped with `./pipe stop` (three modes, next-but-one section) or
  `--stop-live` here, which stops it and records it in the control store; a stopped run spends no trial (next section).
- **A planned stop:** class `planned`, on no idle, paused or stalled reading, so no alarm; `enabled: false` reads the
  same. `status` and the maturation page lead with PIPELINE PAUSED, its why, who and until; an expired `--until`
  resumes by itself and says so. A pause store that cannot be read reads PAUSED, never running.
- **Up next:** `maturation_dispatch.py next [--within 30m]` (`rimflow pipeline next`) runs the tick's own decision code
  dry on a moving clock: what WILL start, when, on which model and by which rule, what is blocked and by what, and
  "nothing will start" said outright. A live run's end and a Designer chain cannot be forecast: they read UNMEASURED.
- **The Conductor's journal hold** stays a launch block in the tick, binding once its commit is in the dispatch clone.

## One control store and `pipe` — owner, 2026-11-18

His words (Wed 2026-11-18): ~10:40 AM PST *"I want to be able to trivially have you submit a command to change consumable
resources like looks, runs, etc. to modify the record when it fails due to other reasons or even if we want to make an
exception. ... This should be a one-line bash command, ok? Build that immediately. No more wasting time and tokens on
trivial pipeline commanding. ... Individual items should be trivially switchable on and off. Queues should be trivially
editable. Make all of this deterministic, easy, traceable, reproducable, testable... this stuff isnt hard, so let's make
sure we're doing it right."* ~11:02 AM PST *"we are going to have. System that is instantly responsive by the time we are
done here. This is not beyond our technology to achieve."* By card (asked 11:04 AM, answered by 11:25 AM PST): a void
run's spend does not count toward the stage ceiling (shown apart; the system-fault meter and its alarm catch a fault
loop); stopping is three specific commands: *"Each of these should be specific commands. "Stop work immediately and
write where you are." "Stop work at the next easy spot and write where you are." "STOP NOW without write." Defaults for
the system are nice, sure... should be Stop work at the next easy spot and write where you are" should be the default
always. But we shouldn't rely on defaults. The agent should be precise in its instruction and use the right option. We
don't need to prethink this."* ~11:28 AM PST: *"there should even be an option just to force kill the agent, period. Not
just send it a nudge to die swiftly."* Design: `design/specs/2026-11-18-pipeline-control-surface/03-merged.md`.

- **The store** is `~/.local/state/rimmandrake/control/control.db` (SQLite, WAL, ext4, outside every clone;
  `src/RimMandrake/rimflow/control.py`; `RM_CONTROL_DB` for tests, and a test process never reaches the live one).
  Control state never needs git, a clone, a publish or a tick: every launch reads it at the moment it starts.
- **One admission point:** every `systemd-run` that starts pipeline work goes through `control.launch_unit`, which
  admits (switches by scope: all, mod, stage, item, family, role; accounts; a duplicate unit name) in one transaction,
  and gives the unit an `ExecCondition` that re-checks at start (a run cancelled by a `pipe off` after admission exits
  REFUSED, never "running") and an end receipt. `selftest_control` fails on any unrouted site. Relentless (retired) is
  routed and its family is OFF.
- **His hold** (`mod_owner_hold.json`) is imported into the store with his words; the file is its published mirror.
  `pipe on all` never lifts a mod's hold; `mod_owner_hold.py lift` lifts store and mirror, and binds at once.
- **Stopping:** `pipe off` blocks new starts only and names the live runs. `pipe stop <scope> --write-now |
  --at-easy-spot | --kill`: all three block new starts on the scope, void the live runs' trials, and print each unit and
  the mode. The two writing modes reach the running agent through its Claude Code PostToolUse hook (`control.py hook`,
  carried in its `--settings`); `--write-now` escalates to `--kill` at its deadline (5 min by default). `--kill` is
  SIGKILL to the whole cgroup and the claude scope, verified dead with its milliseconds; a survivor is reported and
  nothing is recorded killed. A killed detached run's record and clone return are done by the command, so a relaunch
  needs no hand step. With no mode the default is `--at-easy-spot`, and `pipe` says it was the default.
- **Consumables are reservations, not counters:** the owner-granted coverage look is reserved before its judge runs and
  charged only at a valid verdict; no verdict, a raise or a dead holder releases it as a system fault (meter and alarm
  `control:system_faults:<mod>`). `pipe void <run>` gives a run's charges back once and tells the dispatch books
  (`run_void.py`); a void never moves a stage, and `pipe show` flags a stage advanced on a voided run.
- **Unreadable store:** nothing launches, and `pipe show` says `CONTROL UNREADABLE: <cause>`; `pipe doctor` names the
  fix. `pipe stop <unit> --kill` still works by unit name.

## A boundary page before pipeline code — owner, by card 2026-11-18

Three decisions by question card (Wed 2026-11-18, answered 11:19 to 11:25 PM PST; three `--by-card` notes on
`RIMMANDRAKE_DESIGN_REVIEW_TREADMILL_FIX_COUNT_WAS_FLAT`). He picked the recommended option each time. Why he was
asked: four Codex reviews of the control store made 15, 11 and 15 claims with 2, 0 and 2 real problems, and each
repair drew new claims [measured, `design/specs/2026-11-18-review-growth-cycle/00-problem.md`]. Design:
`design/specs/2026-11-18-review-growth-cycle/01-design.md`, section 5.

"Pipeline machinery" below means a file matched by `pipeline_files` in `src/RimMandrake/Utils/pipeline_tests.json`.

- **Decision 1, the page comes before the code.** Card: *"Before a helper writes new pipeline code, what do we do
  first?"* He picked *"Write a one-page list (Recommended)"*: *"The page lists what the code accepts, which failures
  it does not handle, and what it promises. Each promise gets a test. A reviewer can only report a broken promise."*
  The page is `design/specs/<component>/boundary.md`, with the parts ACCEPTS, DOES NOT SURVIVE, PROMISES, LIFE
  CYCLES when the component keeps state between calls, and LIMITS when it enforces any limit. LIMITS lists each limit
  the component enforces (a cap, pause, timeout, retry bound or text cut) with the danger it guards and the evidence
  that the danger happens; a limit that cannot name both is removed, not tuned (owner 2026-11-16, the guard test in the
  limits ruling of 2026-10-31 to 2026-11-17 above; LIMITS added by Crystallize 2026-W47, delegated). Entries are named
  with words, and a promise's test carries the promise's name. Pipeline machinery owes a page when it is new, or when a change adds a state, an input form, a
  read of the outside world, or a verb that kills, deletes, locks or launches. A one-line fix owes none. An existing
  component gets its page when it is next extended, never in a sweep. One fresh reader that did not write the page
  reads it before code is cut to it. The cost he accepted: *"New code that kills runs goes live in half a day, not
  one hour."*
- **Decision 2, when code is clean**, is now his ruling of 2026-11-19 for all code: promises tested; the reviewer
  fixes a significant finding, and one blind reread checks the fix (§Code is clean when its promises are tested).
- **Decision 3, the open complaints of 2026-11-18.** Card: *"What do we do with these 18?"* He picked *"Fix only
  real problems (Recommended)"*: *"A complaint that breaks a promise on the list gets fixed. The others go on a
  'later' list."* A claim outside the page goes to `polish.md` or `next_version.md` beside the page as one line: no
  ticket, no repair. For pipeline machinery with no page yet, a claim is a Problem only if a call site in the repo or
  a documented command produces the input. This replaces his "Fix all 24" of 7:47 PM the same evening.
- **Decision 4, a rare failure that breaks a promise (owner, by card Thu 2026-11-19, answered 5:27 AM PST,
  13:27:48Z, session f95c29f3).** Card: *"Each piece of pipeline code now has a one-page list of promises. A promise
  says what the code always does. A blind reader and Codex each say 21 of 35 old review complaints break a promise.
  The earlier analyst said 4. Most of the 21 are rare failures, such as a crash during a crash. What do we do with a
  rare failure that breaks a promise?"* He picked *"Page says 'not handled' (Recommended)"*: *"Why: keep the code
  small and stop the review cycle. The page lists each rare failure it does not survive. No fix is built. Cost: those
  failures stay possible, and you must trust the list. Recommended: fixing all 21 is the review cycle again by
  another door."* (Not picked: "Fix every one", "Fix only what happened".) So a complaint is a Problem only when it
  breaks a promise in ordinary operation. A rare failure is not: it goes under DOES NOT SURVIVE as one plain line,
  the promise's words are narrowed until the page is true, and no fix is built. Where the code already survives a
  rare failure, the line says "handled today, not promised", so the page stays true and no review asks for more.
  Our reading of "rare" (the Conductor's helper, delegated, not his words): it needs something to go wrong that the
  broken promise does not itself name (a failed call, kill or read; a locked, corrupt or lost store; a crash), or a
  second failure while the first is handled, or two events in the same instant, or an input or code shape no call
  site produces. Ordinary is any input inside ACCEPTS at the pace a person or a timer sends it, with the world
  answering, plus the one failure a promise names as its own subject, met alone (`probe-never-lies` names a failed
  `systemctl` call; without this such a promise would promise nothing). The same card's second question, *"May I run
  one more Codex test?"*: he picked *"Yes, after the page rule (Recommended)"*: *"Why: the page rule above changes
  which complaints count as real. I relabel the 35 by your rule, then run one test. Cost: one Codex run, and a short
  wait for the relabel. Recommended: a test against wrong labels tells us nothing."* That answer allows one run; it does not
  turn Codex reviews of pipeline machinery back on (his card of 2026-11-23 below did).
  Applied: `src/RimMandrake/rimflow/roles/code_review.md`, the control page's DOES NOT SURVIVE, and the relabel in
  `design/specs/2026-11-18-review-growth-cycle/05-three-way-labels-20261119.md`.
- **Changing a page after it has passed** is next-version work: a new accepted input, survived failure or promise is
  written for the next Design Version and never added to the current one's bars. Moving a failure to DOES NOT SURVIVE
  accepts a risk: the Conductor decides it (delegated, logged) and he sees it in the daily digest.
- **What this does not change.** "The test is built with the item" and "The pipeline fixes its own defects" stand.
- **Codex and GPT reviews of pipeline machinery are back on (owner, by card Mon 2026-11-23 8:57 AM PST, item
  `RIMMANDRAKE_ENACT_FOUR_CARD_ANSWERS_ON_HIS_TWO_WAY_RULINGS`).** The card asked whether his stop of 2026-11-18 8:22
  PM PST (*"Go ahead and stop the review growth cycle now. I don't want to pay for that anymore."*) still stood. He
  typed: *"Codex reviews back on. We found the problem. Modern code review instruction includes the significance
  requirement. The old ones didn’t. It was the forced working of any finding no matter how small. Push back if that is
  not your understanding but I felt we resolved this."*
  - Each review uses `src/RimMandrake/rimflow/roles/code_review.md`, or a prompt that carries the same significance
    rule, the same stop level (one full read, one fresh read of a fix, never a third) and the same polish route (one
    line on `polish.md`, no ticket). A finding that is not significant is one line on `polish.md`, never a ticket
    and never worked.
  - A Codex or GPT reviewer that cannot write the clone returns its Problems. The run that launched it fixes each
    Problem, test first, and one fresh reader reads the fixed file once.
  - UNMEASURED: that Codex obeys the significance rule on real code. To measure it, read the first three reviews:
    count the findings, and count the significant ones. The one measured reading is a sort of 35 old claims, not a
    review of code (2026-11-19): 1 of 9 agreed polish claims called a Problem, and 2 of 3 agreed real ones caught.
    The row `code_review` (the review brief's calibration) in `infrastructure/state/judge_calibration.json` reads
    UNTESTED. An UNTESTED row does not stop a review; an UNTESTED brief's refusal sends no work back by itself.
- **First page (the pilot):** the control store, `design/specs/2026-11-18-pipeline-control-surface/boundary.md`.
- **Test that this was applied:** a new pipeline component has a `boundary.md` committed before its first code
  commit; a review finding on pipeline machinery quotes a page entry or sits on a later list.

## Owner hold: six biome mods stop, Pyrelands stays — owner, 2026-11-16

His words (Mon 2026-11-16, ~5:20 PM PST, on the ledger 01:22Z 11-17 under `RIMMANDRAKE_HOLD_SIX_BIOME_MODS_ONLY_PYRELANDS_STAYS`):
*"And stop the new biome mods work. Only Pyrelands as a biome mod right now. They are poorly defined builds right now
and the system choked at their lack of precision I think."*

- **Held:** Contagion, Cauldron, FeverWood, GelatinousSlime, LeaningScrub, Stillsand: the biome mods that were in the
  pipeline that day. **His words cover every biome mod but Pyrelands** ("Only Pyrelands as a biome mod right now"). So do
  not start a biome mod that is not on the list either; first put its row in the list. The hold does not touch mods that
  are not biome mods.
- **One list, one file:** `src/RimMandrake/rimflow/mod_owner_hold.json` (code `mod_owner_hold.py`). A held mod: the Dispatch
  tick launches nothing on it (no builder, judge, live driver, steward, fixer or holder, and a discovered concept is not
  seeded); the Designer and DesignerCodex chain sweeps, the harvest chain and a pending run-now skip it; it is on no
  idle, paused, stalled or Designer-stall reading, so it raises no alarm and no incident; `maturation_dispatch.py
  status` and the maturation page print **HELD BY OWNER** with his words and date. A run already live on it finishes.
- **He or the Conductor lifts it** (owner, by question card, Thu 2026-11-19 ~6:50 AM PST, item
  `RIMMANDRAKE_ENACT_CONDUCTOR_MAY_LIFT_HOLD_NOT_HIM_ALONE`; picked "Yes, let it finish" on the hold-mirror run, his words:
  *"yes... but Conductor should also be able to lift a Hold. We work together, don't use me as a bottleneck alone."*).
  His lift: `python3 src/RimMandrake/rimflow/mod_owner_hold.py lift <Mod> --said "<his words>"`. The Conductor's lift,
  from the Conductor window (seat BENCH, not a launched run): `... lift <Mod> --per-ruling
  RIMMANDRAKE_ENACT_CONDUCTOR_MAY_LIFT_HOLD_NOT_HIM_ALONE --why "<the Conductor's reason>"`; it is recorded as the
  Conductor's act (never as his words) and writes a `delegated: scope` ledger event, so it reaches his daily digest. A
  lift with neither is refused; no helper, other seat or the Dispatch tick lifts a hold, and `pipe on` never does. Then
  publish `mod_owner_hold.json`; `mod_owner_hold.py show` lists the holds. A lifted mod still does not run while its
  readiness list is not READY (§No mod runs forward on a broken pipeline, owner 2026-11-19). A new hold is a row in the same file, with his words,
  then `./pipe init --import` (safe to repeat), so that every launch refuses the mod and not only the tick.

- **Design text on a held mod is allowed; the held mods will return** (owner, by question card, Thu 2026-11-19 ~5:35 AM PST, after six hand-launched helpers wrote design tickets for FeverWood, whose briefs named no mod so the hold never checked them). Picked "Design text is allowed"; his words: *"Design text is allowed, and we WILL return to the mods... they're not going to be deprecated, don't worry."* The option's description, verbatim: *"Why: design is cheap and loses nothing if the mod never ships. Only builds, tests and live runs stay held. Cost: tokens go to mods you set aside, and designs drift from what you last read."* So: the hold above binds the PIPELINE (its launches, chains, alarms); a helper may write design text on a held mod; builds, tests and live runs on it stay held; no mod is deprecated; no hold is lifted by this (a hold is lifted only by `mod_owner_hold.py lift`, his or the Conductor's). Item `RIMMANDRAKE_ALLOW_DESIGN_TEXT_ON_HELD_MODS_THEY_RETURN`.

## Resetting a test scene is harness housekeeping, never a mod deliverable — owner, 2026-11-17

His typed answer to a Conductor card (Tue 2026-11-17) on the proposed Pyrelands polish entry
`RIMMANDRAKE_RESTORE_PYRE_WIND_SCENE_GROUND` (put the scene's ground back after the wind-burn scene):
*"This is dumb. It's not even an item at all. Just save the test in a file and reload... We shouldn't be judging Test
Reset as a mod deliverable."*

- **The decision:** resetting or cleaning up after a test scene is the harness's job: it saves the game before the scene
  and reloads that save after. It is never a mod deliverable, never a build item for the mod, and never a coverage gap,
  Problem or Polish finding. No judge (coverage, blind Judge, scene look) refuses, fails or files anything for how a
  scene is reset.
- **Why:** reset is the same for every scene and every mod, so it belongs once in the harness; judging it per mod spends
  rewrite, exam and judge rounds on work no player ever sees.
- **What it does not change:** a scene still writes a `restore` line and the runner still records recovery
  (`designer_stage.py scene-begin` / `scene-end`), so an interrupted run is still put back before the next one; the
  asserted start and the control are still judged; a mod effect that persists in a real game (a scar that never fades,
  terrain a mod corrupts) is still a mod finding, since that is play, not test reset.
- **Owed:** the harness saves before and reloads after each scene where it does not yet
  (`RIMMANDRAKE_SAVE_RELOAD_AROUND_EVERY_TEST_SCENE`).

## Todoist is for to-do lists only, never an alert route — owner, 2026-11-19

*"So Todoist is officially retired as any kind of alert: it just doesn't work in a timely manner. It's really only to
maintain to do lists, as it says."* (typed into a card, 2026-11-19 6:10 AM PST). To "May we close our own old alarm
tasks there?" he picked **"Close them, and stop posting"** (*"Why: fix the source too. We close ours and switch the three
senders off until the new alerts are built. Cost: until then no alarm reaches the phone at all, not even as a silent
task."*).
- No program, hook, unit or agent posts an alarm, alert, page or "ring his phone" message as a Todoist task. The
  Todoist posts of `ops_core/phone_push.py` (deadman_check, login_watch, switching_plan) and `windows/heartbeat.ps1` are
  off by default: `RM_TODOIST_ALARM_POSTS=1` / `-TodoistAlarmPosts` is the switch, and nothing sets it.
- The route that replaces it is decided (owner, 2026-11-19, item
  `RIMMANDRAKE_DESIGN_PUSHOVER_ALERTS_CRITICAL_ONLY_TWO_SENDERS`): Pushover, for CRITICAL needs only, sent by the
  Conductor or Operations only. The program is `src/RimMandrake/Utils/pager.py`.
- Until that item closes, **no alarm reaches his phone** (`pager.py status` read "last sent: none" on 2026-11-23). Each
  alarm still goes to its own log, alarms file and ledger.
- To-do lists synced into Todoist (Lodestar Burning, Hestia) are unaffected.

## The root CLAUDE.md holds rule lines and pointers only — owner, 2026-11-19

Asked by card (2026-11-19 ~12:58 PM PST) how far to drain the project `CLAUDE.md` (41,213 characters, loaded into every
session and helper), he picked option (1), "Drain to rule line plus pointer", and typed: *"I have no idea why it says
regroup, cut nothing. Old likely obsolete guidance. (1) and use Simplified Technical English when rewriting Claude.md
entries please. No more oracular oddities. No provenance either, that's for git."*
- Each `CLAUDE.md` entry is a plain heading, the rule in Simplified Technical English (no sentence over 20 words, active
  voice, one idea per sentence, the same word for the same thing) and a pointer to the file that holds its full text.
- `CLAUDE.md` carries no provenance: no dates, no "by card", no quoted owner words, no incident stories, no
  measurements kept for history. Those live in the rule's home (this file, `biome_rulings.md`, `CLAUDE.history.md`, a
  facts file).
- No emphatic riddles or emoji shouting. A warning keeps its force by stating what the wrong move costs.
- **Superseded:** the 2026-09-23 spring-cleaning ruling for `CLAUDE.md`, "regroup, cut nothing". It no longer binds the
  root `CLAUDE.md`. What still holds from it: evidence moves to a home, it never vanishes (the Crystallize merge gate,
  `checkable.py compare`).

## 🔴 There is no worldgen feature, in any version — owner, 2026-08-15

- **OUT, permanently:** any automated or programmatic worldgen; worldgen as a
  player-facing capability. ⛔ v2 is not a parking space for it — mark such work
  dead, never deferred.
- 🔑 **Players never generate anything. They receive a savegame holding the fixed
  world** — one hand-made world, frozen, shipped. A faction, ideoligion or setting
  absent when it freezes is absent from every player's game forever.
- ⛔ **Do not build anything that produces ALTERNATIVE planets** (owner, 2026-08-18).
  No seed sweeps, no variants, no knobs that could roll a second world. ✅ Author
  THE map, judged by realism first, iterated by LOOKING (`worldview.py`); target and
  references: `design/Jawa/worldbuilding/the_one_map.md`.

## 🔴 The pipelines before the Maturation Pipeline are retired — owner, 2026-11-13 and 2026-11-18

*"Nothing of that era should remain. No more collisions or confusion."* (2026-11-18). Builds run in the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md`); the Conductor launches helpers (`src/RimMandrake/rimflow/detached_helper.py`); design goes to the Designer (`src/RimMandrake/rimflow/roles/designer.md`), ops alarms to Operations. Every retired era, what was removed and what still carries an old name (no `relentless*` module is left; some live paths and names still say relentless, FOUNDRY or pulse, and each rename is a ticket listed there): `design/RimMandrake/retired_eras_index_2026-11-18.md`; `selftest_retired_era_gone.py` refuses a remnant at `./publish`. The daily findings judging and the Friday memory sweep are `rm-findings-judge.timer`. FOUNDRY is not a seat: `rimflow` maps it to the Conductor's key (`RETIRED_SEATS` in `cli.py`), as does the FlowWorks lane (`infrastructure/state/flowworks_lane.json`, field `seat`).

## Facts you cannot guess — the root CLAUDE.md list, with its rulings (owner, 2026-08-27 and 2026-10-24)

This is the list as the root `CLAUDE.md` carried it until 2026-11-19, word for word. The detail behind each fact is in the file the fact names.

- **The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`,
  never this repo.** Writing a file is not deploying it.
- **A cold load on the full list costs many minutes; a quicktest map is ~90 s.** Never
  "restart and see". The measured figures, which grow with the mod list, are in
  `design/RimMandrake/CLAUDE.history.md` and the `rimworld-load-round` skill.
- **`ModsConfig.xml` is the live mod list**, at
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
  🔴 **Parse it** (`ET.parse(p).find("activeMods")`) for the active count — never `grep` it,
  and never cite a mod count written in a doc. ModsConfig describes the NEXT load.
- 🔴 **Never restore the owner's mod list; only canonical world saves are precious** (owner, 2026-10-24):
  *"Never worry about my mod list restoration! … Until I start playing (months from now likely) you never need
  to "restore" mods to anything or worry about harming save games other than canonical world saves."* Leave
  ModsConfig on whatever tier serves the work; no "restore before release" step. Every save except the canonical
  world saves (`infrastructure/state/CANONICAL_SAVE.md`) is disposable.
- **Never guess a defName, field, or namespace.** RimSage (`mcp__rimsage__*`, Windows
  Desktop only), the def, the About.xml, or `measure` — and 🔴 **a number about a large
  artifact comes from `measure`, never from a scan** (`block_blind_scan.py` refuses).
  `0` means measured zero; ignorance answers `UNMEASURED`.
- 🔴 **Instrument-blindness is a user-level rule.** Measured traps here (ledger key is `id` not `item`, `python.exe` CRLF,
  `grep -c` exit 1, zsh no word-split, `ls|wc` on a missing dir, `*south*` mask glob, creature
  census by description not defName, "is there a mod for X" across BOTH mod roots incl.
  inactive …): `infrastructure/state/facts/instrument_traps.md`.
- 🔴 **`Plant` only ticks `TickLong()`** — a comp on a plant overrides `CompTickLong()`.
  🔴 **`MayRequire` on a top-level `<Operation>` is IGNORED** — guard with
  `PatchOperationFindMod`/`Conditional`; a composed member's packageId never loads. A patch
  that matches nothing logs nothing. Detail: `skills/rimworld-modding/references/project-engine-facts.md`.
- 🔴 **`modcheck run <Mod>` REWRITES the live `ModsConfig.xml`** (expensive list). When a new
  game won't start, read the **FIRST** exception in `Player.log`, not the loudest. More
  in `infrastructure/state/facts/tool_traps.md`; the 600 s subagent watchdog, mid-session hooks and card
  gates in `infrastructure/agents/Agent_Policy.md`; `handoff.py` and two Conductor windows in
  `skills/using-rimflow/references/traps.md`.
- **Dumps and harvests decay** (owner, 2026-08-27): trust one only after its fingerprint
  matches the live mod set; the frozen `official` dump is the sole design target.

## The weekly Crystallize pass improves the agents and carries the skill proposals — owner, 2026-11-02, 2026-10-29, by card 2026-11-23

Crystallize is the consolidation pass (the `crystallize` skill of MandrakeWorkflows). For this project it has two jobs.

- **Crystallize improves the agents and the skills.** His words, 2026-11-02: *"Every day we should ask if each agent can be
  improved based on our evidence. That's the beauty of making them agents. Same with reusable skills not agent
  specific."* By his card of 2026-11-23 ("Stop it, weekly does it") the weekly pass does this work. The daily improvement
  pass was deleted. Each pass asks, for each role file and each skill, if the evidence since the last pass improves it.
- **Crystallize carries the skill and tool proposals.** His words, 2026-10-29: *"This is a good thing to discuss with the user and
  a positive outcome."* By his card of 2026-11-23 ("Weekly, in one report") a proposal for a new skill, or for a move of a
  skill or tool up to the user-level tools, goes in the weekly report, not on a daily card. Each entry gives its name,
  what moves, why it is general, and the measured evidence. He decides each one. First entry owed:
  `RIMMANDRAKE_PROPOSE_PROSE_CHECK_TO_USER_TOOLS_BELOW_TWELVE`.
- The report is `CYCLE_REPORT.md` in `D:\ClaudeWork\rimmandrake\conductor\crystallize_<year>W<week>\`.
- Measured 2026-11-23: the pass runs and applies edits, but it has not been weekly. Its last two runs were 31 days apart
  (2026-10-19 and 2026-11-19). `RIMMANDRAKE_REVIVE_WEEKLY_CRYSTALLIZE_RAN_31_DAYS_APART` holds the repair.

## Sittings with the owner keep the advanced-zoom mod — owner, 2026-11-03

*"there was a standing rule that the advanced zoom capabilities were always to be included in mod lists where the human sat with Conductor, so I can zoom in and study things."* Any mod list built for a sitting with him includes it.

## If it flies in the fiction, it flies in the game — owner, 2026-09-19

*"Standing rule: we make flyers flyers when we can, ok?"* Real flight, triggered by touching
the def, not a sweep. Flight is the **`MaxFlightTime` STAT** (Core, not a donor); the animation
is a **whole-body directional flip-book** (`flyingAnimationFramePathPrefix`), ⛔ never a Spastic
wing render-tree. Mechanics: `skills/rimworld-modding/references/flight.md`.

🔴🔴 **NEVER live-test a flyer's flight without the owner present** — *"For the third time, do
not do live testing of flyers without a human present. It doesn't work."* and *"Don't try to
capture images of flight. It doesn't work."* Verify flight by a deterministic STATE read of
`Pawn_FlightTracker`; a visual check is a joint session or it waits.

## Owner authority on the ledger — one field per kind of authority (owner, by question card 2026-10-11)

`--owner-said` = his words (typo fixes and joining his own sentences are fine, meaning unchanged) · `--by-card "<question → option>"` = a decision he took by card (the label is our text; the whole card, the picked option's description included, is stamped from the card store: `src/RimMandrake/rimflow/card_capture.py`) · `--per-ruling <item-id|event>` = a standing ruling cited by reference (it stands until he changes it) · `--why "…"` = your own words. No transcript proof runs; nothing checks a quote but its shape.

## 🔴 Never send him to a computer you can reach yourself — owner, 2026-10-31

User-level rule; here the route is Tailscale.
