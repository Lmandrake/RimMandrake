# RimWorld 1.6 — Jawa scavenger clan on a desert world

**Read `infrastructure/agents/CHARTER.md`** — the whole process rulebook — and your
own window file: `infrastructure/agents/BENCH.md` (with the owner) or
`infrastructure/agents/FOUNDRY.md` (autonomous queue). Game cycle:
`infrastructure/GAME_STATE_WORKFLOW.md`. **Models: the ladder lives in
`infrastructure/agents/Agent_Policy.md` and nowhere else; never restate it.**

This file holds RULES and POINTERS only. Each rule's full text, the incidents behind it
and its measurements live in the file it points at:

| topic | full text |
|---|---|
| biome, roster, sea, naming-tier rulings | `design/RimMandrake/biome_rulings.md` |
| north star, LLM transport, pits, DLC, git, code review, art, bridge, savegame options | `design/RimMandrake/standing_rulings.md` |
| instruments that return a confident wrong number | `infrastructure/state/facts/instrument_traps.md` |
| tools with surprising side effects | `infrastructure/state/facts/tool_traps.md` |
| creature flight (stat, race flags, flip-book) | `skills/rimworld-modding/references/flight.md` |
| ticking, `MayRequire`, csproj, patch behaviour | `skills/rimworld-modding/references/project-engine-facts.md` |

## How we debug — owner, 2026-10-01

*"I really do mean stop and start working a new way."* Every mod gets a functional script
and is debugged through it; every live poking session ends by writing what it learned —
including informative false theories — into that script. Agents write and approve those
scripts; the owner's hash-bound `## north star` bars stay his. The 2026-10-01 build pause was
**lifted by the owner 2026-10-02** (*"Build pause is lifted."*); every new mod still ships with
its first script. Process: `design/RimMandrake/debug_process.md`.

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

## 🔴 A BIOME WITH ZERO TILES IS NOT A DEFECT — owner, 2026-09-20, said repeatedly

> *"Correct we will repaint the whole world when all the biomes are in. **You don't need
> to keep rediscovering this.**"* · *"Don't worry about worldmap painting. Once we have
> all the biomes in mods we will do the painting once and for all."*

- **The planet is painted ONCE, at the end**, after every biome's content is mod-migrated.
  A BiomeDef of ours on 0 tiles is the EXPECTED state: not a finding, not a defect.
- ⛔ Never repoint owned content at a donor def to make it appear on today's map; ⛔ never
  cite a tile count as evidence that something is or is not built. Keep the paint list
  (`BIOME_PAINT_ONCE_AT_THE_END_1`). **About to report one of our biomes on zero tiles? You
  have rediscovered this. Stop.** (It cost three reconciliation passes.)
- 🔴 **`world/ASHKARR_WORLDMAP_tiles.csv` is a RECORD, not the planet** — *"It is a RECORD of
  the planet, not a rival to it."* It tells you the planet on its export date; the live
  system is the only instrument for "right now".

Full text and incidents: `design/RimMandrake/biome_rulings.md`.

## Biomes, rosters and seas — owner rulings (full text: `design/RimMandrake/biome_rulings.md`)

- 🔑 **Search `src/` and the roster before FILING or designing — this project keeps having
  already built it** (four of six "new" mechanisms already existed, 2026-09-23).
- **Say which greatbole you mean:** `RM_Greatbole` (fellable tree) · `RUT_GreatboleHeartwood`
  (the mineable blob) · `RUT_GreatboleCore` (1×1 bookkeeping marker).
- 🔑 **An animal belongs to ONE biome unless there is an IN-GAME reason** — *"Animals sound be
  biome-specific unless there is an in-game reason"*; *"I meant pick one arid home."* A hole
  in a roster is filled with a NEW creature. 🔴🔴 **But EVICTIONS ARE STOPPED** — *"Let's stop
  evictions right now"*; *"This is a human review process issue."* No pass edits a roster to
  enforce this; multi-homed species are rows on that biome's own sheet at its sitting.
  🔑 **If consecutive questions to him each add a clause to a procedure, STOP** — it is review work.
- 🔑 **A sea biome describes BOTH its floor and its catch** (*"what you encounter as an animal
  there … as well as what you can FISH out"*); only fish-sized creatures owe a catch, and
  *"All the fishables should also be alive and moving around in the depths (this is true for
  ALL seas)."*
- 🔴 **The ship is the only way down and back** — *"It's ship or nothing."* The ship flies to
  its own planet layer, `RM_SeabedLayer`; `RM_SeaDiveHatch` is a leftover
  (`SEA_DIVE_HATCH_REMOVE_1`).
- **Every BiomeDef with a roster sets `animalDensity`** (unset = 0 = no animals ever spawn).
  Parse `<wildAnimals>`/`<wildPlants>` as XML ELEMENTS, never by counting `<li>`.
- 🔑 **A review sheet's `cut` is scoped to THAT SHEET'S BIOME, never the planet.**
- 🔴 **An `RM_` twin's real cast is PATCH-ADDED** (`UtinniPatches/Patches/WildAnimals_<Biome>.xml`);
  reading BiomeDefs alone sees the wrong half.

## 🔑 "Star Wars style" naming is NOT Star Wars IP — owner, 2026-09-22 (Q11a)

*"The fact that we will use "star wars style" naming doesn't mean they have to live in the star
wars layer."* An **invented** exotic name lives in the franchise-free `RM_` tier; only a
**genuine canon** name is IP and routes through the Utinni patch layer. A `RM_` roster is rich
enough to stand alone — never a thin fallback. 🔑 When a tier or provenance question starts
generating sub-questions, **ask whether the CATEGORY is needed at all** before adjudicating
inside it. A donor mod's defName is not a canon source; verify canon with the Wookieepedia
search API. Authority: `biome_mod_architecture.md` §7 Q11a; detail in `biome_rulings.md`.

## Facts you cannot guess

- **The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`,
  never this repo.** Writing a file is not deploying it.
- **A cold load is ~15 minutes on the full list; a quicktest map is ~90 s.** Never
  "restart and see". *(MEASURED 2026-09-07, second launch of a session; a first launch
  after a reboot may run slower.)*
- **`ModsConfig.xml` is the live mod list**, at
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
  🔴 **Parse it** (`ET.parse(p).find("activeMods")`) for the active count — never `grep` it,
  and never cite a mod count written in a doc. ModsConfig describes the NEXT load.
- **Never guess a defName, field, or namespace.** RimSage (`mcp__rimsage__*`, Windows
  Desktop only), the def, the About.xml, or `measure` — and 🔴 **a number about a large
  artifact comes from `measure`, never from a scan** (`block_blind_scan.py` refuses).
  `0` means measured zero; ignorance answers `UNMEASURED`.
- 🔴 **A count that is round, zero or alarming is a query bug until a sanity probe proves the
  instrument can see.** Measured traps (ledger key is `id` not `item`, `python.exe` CRLF,
  `grep -c` exit 1, zsh no word-split, `ls|wc` on a missing dir, `*south*` mask glob, creature
  census by description not defName, "is there a mod for X" across BOTH mod roots incl.
  inactive …): `infrastructure/state/facts/instrument_traps.md`. When the owner says a thing
  exists and your instrument says it does not, **suspect the instrument**.
- 🔴 **`Plant` only ticks `TickLong()`** — a comp on a plant overrides `CompTickLong()`.
  🔴 **`MayRequire` on a top-level `<Operation>` is IGNORED** — guard with
  `PatchOperationFindMod`/`Conditional`; a composed member's packageId never loads. A patch
  that matches nothing logs nothing. Detail: `skills/rimworld-modding/references/project-engine-facts.md`.
- 🔴 **`modcheck run <Mod>` REWRITES the live `ModsConfig.xml`** (expensive list). When a new
  game won't start, read the **FIRST** exception in `Player.log`, not the loudest. More
  (600 s subagent watchdog, mid-session hooks, card gates, `handoff.py` and two BENCH
  windows): `infrastructure/state/facts/tool_traps.md`.
- **A gate cited by NAME outlives the item it names — check the item's state** (owner: *"That
  file may be VERY old… do not accept stale info."*).
- **Dumps and harvests decay** (owner, 2026-08-27): trust one only after its fingerprint
  matches the live mod set; the frozen `official` dump is the sole design target.

## North-star validation — owner, 2026-09-17

The validated-hash covers the WHOLE `## north star` section, prose included. *"Change no code —
you just re-validate when prose is corrected."* So: correct false text, then re-validate on his
word the same sitting; write only state-independent prose there. Validation state is never
written as prose — `modcheck floor --all` measures it. Walk-finding traps and the rest:
`design/RimMandrake/standing_rulings.md`.

## In-game LLM access is the Claude Code CLI, never a hosted API key — owner, 2026-09-05

Every in-game LLM call shells out to **`claude -p "<prompt>"`** as a subprocess. Owner,
verbatim: *"Claude Code in non-interactive mode (`claude -p "..."`) authenticates via your
claude.ai login and can be called from a shell script without any API key."* The spec's two
laws (text/menu authority only; the game is whole with the LLM absent) stand. Detail:
`standing_rulings.md`; spec: `design/RimMandrake/llm_ingame_wiring_spec.md`.

## A pit is a SUPERDEEP cell, not a building — owner, 2026-09-17

*"I'm not really sure a pit is any different than a deep canal."* 🔴 **The ITEM
`infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md` is the authority, not the 1127-line
spec**, which predates ten changed answers. Summary in `standing_rulings.md`.

## 🔴 One Direct Sun, a pure function of geometry — owner, 2026-09-29 and 2026-10-19

*"It can't be a new "kind" of heat."* · *"no biome-specific heat, no biome-specific sun. It's a matter
of geometry (low sun is less intense AND produces longer shade, high sun produces only covered shade
and much more intense effect). Ambient heat is normal Rimworld rules."* Direct Sun feeds **vanilla**
heat (felt temperature → Heatstroke), 55 °C at the zenith × sin(sun angle), the sun angle from the
tile's planet position; no per-biome heat kind, number or exception. Shade gear is parasols and roofs
(a tent is any quick roof). Volcanic/steam/fog heat is plain air temperature. And **no animal or pawn
ever vanishes without a readable sign.** 🔑 **Running it on every day-side map depends on tree
shade:** *"If we have an excellent tree shade model working, then YES direct sun works the same
everywhere on the day side."* Without one, it is turned off on tree-heavy maps, which he calls
inferior. The model: `design/RimMandrake/tree_shade_model_2026-10-19.md`. Full text:
`standing_rulings.md` §Direct Sun; design and migration:
`design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`.

## 🔑 Every DLC is assumed — owner, 2026-09-19/25/26

- *"Always assume all the dlcs."* and *"it is assumed that future players will have all the
  Rimworld DLC's currently installed."* ⇒ **Every DLC is a hard prerequisite of shipping**, like
  the base game. ⛔ No DLC-less degradation path, no "what if the player lacks X" defect, no test
  tier proving a DLC-absent configuration. `MayRequire` stays on **mod** guards for load safety;
  on a DLC it decides nothing.
- **ALL TEST MOD LISTS include ALL FIVE EXPANSIONS** — *"ALL TEST MOD LISTS should include ALL
  THE EXPANSIONS; we're not trying to ablate expansions out of our list at this time."* A tier
  may narrow which mods load, never which DLC.

## Shipping names are three-tier — owner, 2026-08-30

Every NEW packageId, defName, C# namespace and mod folder follows `design/NAMING_SCHEME_PLAN.md`:
**RimMandrake** / **RimStarWars** / **RimUtinni** — packageId `mandrake.<tier>.<modname>`,
prefixes `RM_`/`RSW_`/`RUT_`, namespaces `RimMandrake[.StarWars|.Utinni].<Mod>`. "Jawa" is lore
text only; dev tooling is exempt. 🔴 **The migration is DONE** (*"Deploy the full rename."*,
2026-08-31) — a later rename is simply owed work; delete any doc still citing a rename gate.

## Every mod ships superb Mod Settings — owner, 2026-09-12

On/off per major feature, tuning where a number is the experience, defaults = shipped
behaviour, all-off degrades gracefully, worldgen-affecting toggles labelled. Applies to every mod,
no exceptions. **Biome mechanics are promised inside OUR biomes only** (owner, 2026-10-15: *"We can't
guarantee they will work in other biomes beyond our framework. They should… but we're not going to
validate that at this time."*): build no new cross-biome switch; existing ones stay, off, labelled
unsupported.

## If it flies in the fiction, it flies in the game — owner, 2026-09-19

*"Standing rule: we make flyers flyers when we can, ok?"* Real flight, triggered by touching
the def, not a sweep. Flight is the **`MaxFlightTime` STAT** (Core, not a donor); the animation
is a **whole-body directional flip-book** (`flyingAnimationFramePathPrefix`), ⛔ never a Spastic
wing render-tree. Mechanics: `skills/rimworld-modding/references/flight.md`.

🔴🔴 **NEVER live-test a flyer's flight without the owner present** — *"For the third time, do
not do live testing of flyers without a human present. It doesn't work."* and *"Don't try to
capture images of flight. It doesn't work."* Verify flight by a deterministic STATE read of
`Pawn_FlightTracker`; a visual check is a joint session or it waits.

## Queue items are NAMED, not numbered — owner, 2026-08-20; grammar 2026-10-10

New items are **`SUBJECT_INTENT_TWIST`**: what it is, one intent word from the bank
(what it set out to do at filing — never live state), then a **true, kind, specific**
comic aside on how it is going: `BRIDGE_HANG_UNSTICK_THIRD_TIME_LUCKY`. No trailing
`_1`. `rimflow namecheck <NAME>` shows the parse; `file`/`spawn` refuse the rest. Rules
and bank: `design/RimMandrake/ticket_naming_2026-10-10.md`. Legacy `…_1` and
`B*`/`C*`/`D*`/`W*` IDs are never renamed; B-style ones are always cited with their
title attached — `B58 (the dead Jawa pawnkind)`, never bare.

## Correctness outranks seat ownership; wrong material is deleted

- *"It is WORSE to leave incorrect information that belongs to another seat than it is to
  violate seats... ok? I keep saying this. MAKE IT SO EVERYWHERE."* (2026-09-19) — fix a false
  statement in any seat's file on sight, commit it at once by explicit path, and say what was
  WRONG. Correcting is not redirecting. Full rule: CHARTER.
- *"Simply remove offending inaccurate material, don't leave it in and supersede it."*
  (2026-09-09) — delete wrong content, fix every inbound reference in the same change; a
  one-line pointer only for content that MOVED.

## 🔑 Agents decide nearly everything, art included — owner, 2026-10-22

*"Nearly everything including art. An agent can absolutely ask another agent for an art ruling based on some prose
constraints and requirements we can draft."* Taste calls go to a judge agent (not the maker); every delegated call is
logged `--why "delegated: <class>"`, never as his approval, and reaches him in a daily digest. Only the short list in
`design/RimMandrake/delegation_policy.md` §2 still needs him (north-star bars, irreversible acts on others' work,
replacing art he kept, changing his rulings, outward/paid acts, flyer live tests).

## Owner authority on the ledger — one field per kind of authority (owner, by question card 2026-10-11): `--owner-said` = his words (typo fixes and joining his own sentences are fine, meaning unchanged) · `--by-card "<question → option>"` = a decision he took by card (the label is our text) · `--per-ruling <item-id|event>` = a standing ruling cited by reference (it stands until he changes it) · `--why "…"` = your own words. No transcript proof runs; nothing checks a quote but its shape.

## Git

**Operating doc: `design/RimMandrake/GIT_WORKFLOW.md`** — read it before touching git.
Work in your seat clone (`/home/mandrake/rm/bench` or `/home/mandrake/rm/foundry`);
`D:\Luke\dev\RimMandrake` is a read-only mirror. Commit explicit paths (never `git add -A`/`.`/`-a`,
never `--force`, never a file over ~50 MB), push at once (`./publish` prints `PUBLISHED <sha>`),
and keep file writes and commits in separate Bash calls (hooks refuse a compound command whole).
🔴 **Worktrees are OFF** (owner, 2026-10-02, by card; `block_worktrees.py`). A committed mod DLL
travels with its `.srchash`. More: `standing_rulings.md` §Git.

## Code isn't clean until a review says so

Every file is DIRTY until `python3 src/RimMandrake/Utils/code_review_status.py check <path>`
says CLEAN (content-hash based; `mark-clean` only after a full-file review finds nothing).
Check a file is still reachable before spending a review on it. Procedure:
`standing_rulings.md` §Code review.

## What is where

```
src/                    mods, defs, C#, art            FOUNDRY owns
design/                 campaign specs (Utinni)        the owner's, via BENCH
skills/                 tooling + how-to               curated in fresh-context passes
infrastructure/state/   ledger, items, facts/, V1.md   written only through rimflow
  items/<ID>.md         LIVE item prose only — this glob is the live set
  items/closed/         prose of done/dropped/superseded items (moved on close)
  handoffs/             reboot handoffs — NOT queue items, never greppable queue state
Transient/              output to LOOK AT, then bin    UNTRACKED (pins only), ~14 days
```

**Transient rule**: a human reads it once → `Transient/`; a program reads it →
`/tmp`, never the repo; anyone-later → the repo, committed outside `Transient/`.
Shelf life ~14 days: never the only copy of anything, and never cited by a committed doc.
🔴 **Untracked since 2026-10-18** (owner, by card: *"Stop tracking; pin to keep"*): an unpinned file
lives only in the clone that wrote it (not on `D:\`, GitHub or the other seat). `*.decisions.json` always
stay tracked; pin anything else with `python3 src/RimMandrake/Utils/transient_pin.py add <path>`.

**Art is judged against the canon library, and canon is the target** (owner, 2026-09-15):
`design/RimStarWars/canon_references/` (`AGENT_BRIEF.md` is the operating doc; count the
entries, never cite a number). Art and cosmetic changes are judged by a second agent against
`design/RimMandrake/art_judge_brief.md` (delegated, below). Art goes
through the art ledger's `art install` only. **Check for existing regenerated art before queuing more:** search
`artpipe_state.py find` and sheets' `.decisions.json` first (*"I actually already saw beautiful art for giant
leaf somewhere in a review sheet"*). Detail: `standing_rulings.md`.

**Options he must LOOK at ship as a savegame** — *"Save user review options as save games."*
One map, a grid key, saves kept until he says delete; back up the Saves folder first.

## Tools

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <name>   dry run; --apply writes
python3 src/RimMandrake/Utils/winbuild.py <Mod|csproj>           C# build, staged on D:\ClaudeWork\rimmandrake\build
./mirror sync | status                              D:\…\RimMandrake as a writer-free origin/main export
python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>...  ask GPT via codex.exe; files inlined
python3 src/RimMandrake/Utils/refresh.py            rebuild the offline def dump
measure count <DefType>                             one line; never a bare number
python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs ...
./src/RimMandrake/Utils/show.sh <path>              open it in Explorer
./game --said "<his words>" up|down|loading         the moment he says it; bare ./game measures
./game --why "<your reason>" down|loading|up        🔴 a REBOOT is yours to call, no asking
                                                     (owner 2026-09-02) — bridge free first
./bridge [bench|foundry|free]                       OWNER ONLY — bare ./bridge says who has it
rimflow …                                           the ledger: file/claim/close/drop/verify
python3 src/RimMandrake/Utils/run_selftests.py --only <tests>   before a commit: only the tests for what you changed;
                                                     the FULL sweep runs nightly 03:00 (rm-selftests-nightly.timer,
                                                     Transient/selftests_nightly.log) — owner by card 2026-10-14
python3 src/RimMandrake/Utils/system_screenshot.py <out.bmp>   OS desktop capture — always OK,
                                                     no asking (owner 2026-09-09)
python3 src/RimMandrake/Utils/system_click.py <x> <y>          OS-level click for dialogs a
                                                     bridge call can't reach
```

## The bridge is passed through one file

One window drives the live game at a time. Who holds it is `infrastructure/state/BRIDGE`,
written only by `rimflow bridge who | take --for "<what for>" | release` (release the moment
you stop). It errs toward ALLOWING: a hold with no event for 45 minutes is stale and simply
taken; `take --force` always works. ⭐ The owner overrides with `./bridge bench|foundry|free`.
🔴 **Holding the bridge is blanket authorization** — *"Never ask that. If you have bridge, you may
start steam, launch game, anything you need."* Game-state relays are STAMP-ONLY (*"burn tokens
unnecessarily and rarely inform"*). Detail: `standing_rulings.md`.

## Skills

Roster: `skills/README.md`. Most reached for: `rimworld-modding` · `rimworld-deploy`
· `rimworld-load-round` · `rimbridge` · `efficient-subagents` ·
`generating-rimworld-sprites`. Lessons go to `infrastructure/state/lessons/` (one file each:
`python3 src/RimMandrake/Utils/lessons.py add "…"`); skills are edited only in fresh-context
curation sessions.

## Compact Instructions

When this conversation is compacted (idle or not), the summary MUST preserve, verbatim where
quoted:

1. Every open `NEXT:` pointer, with its item ID (`` `ID` — state; NEXT: <action> ``).
2. Lessons learned this session that are not yet filed with `lessons.py add`.
3. Every owner ruling quoted verbatim this session, with its date — his exact words, not ours.
4. Bridge holds (who holds `infrastructure/state/BRIDGE`, and for what) and the game state.
5. Running subagents: name/ID, task, and what they write where.
6. Uncommitted or unpushed paths.
7. If no **HANDOFF READY** was said since the last commit, write the line **HANDOFF OWED**,
   so the resumed session writes the handoff (from the transcript on disk if needed) first.
