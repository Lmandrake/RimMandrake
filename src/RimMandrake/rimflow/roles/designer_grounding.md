# Designer packet: Stage 0, Read (grounding)

Injected with `designer.md` and `designer_scene_contract.md` when the concept is at stage 0.

## Bounded grounding

Start with the affected mod, its current specification, its proof script (`validation.py` or the suite that covers it),
and the neighbours it directly touches. Expand reading only to resolve a **named** uncertainty that could change scope,
feasibility or proof; write the uncertainty into `record.json` (`contradictions` or an `inventory` entry with `impl:
unknown`) before you go looking, and stop when it is settled. Completion is the bounded questions answered, never "read
enough source" or "walked every possibility". 🔑 Search `src/` and the roster before you treat anything as unbuilt: this
project keeps having already built it.

1. **His words on the mod**: the ledger (`--owner-said` events on its items), the walk's `## north star`, his rulings
   (`design/RimMandrake/standing_rulings.md`, `design/RimMandrake/mod_definition_lessons_2026-11-02.md`). Each one you
   use goes into `record.json` `scope` or `decisions` with its `OWNER:<tsn>` source.
2. **The inventory**: one `inventory` entry per capability, with `impl`, `proof` and `scope` set separately (see
   `designer.md`). "Unproven on the ledger" may only mean unrecorded: mark `exercised_unrecorded` when his words say he
   ran it.
3. **Neighbours and whatever already does this job**: name each neighbour doing part of it, which one owns it, and any
   service this mod must opt into (*"These need to brought in harmony with each other."*, 2026-11-03).
4. **Feasibility from real source**: only for a capability that is `absent` or `unknown` and in scope. Skill
   `rimworld-modding`; a Star Wars species or droid: `rimworld-canon-references`.
5. **Script audit**: for each scene the mod's proof script stages, record which of the scene contract's parts it lacks
   (asserted start, discriminating control, restoration, hold). The missing parts become build items at stage 3; you
   write no code.
6. **A vanilla or popular mod that does the same thing**: one, only when it could change a design choice.

Any count you cite about a def dump, save or log: skill `measuring-large-artifacts`, then
`infrastructure/state/facts/instrument_traps.md`.

## What we built comes first (owner, 2026-11-02)

GSS sitting 1 asked him whether to keep poles, styles and save removal, all already built: *"Those were very strange
questions given we already have these capabilities."* So the packet carries **What is already built**, which the launcher
reads, not you: the mod's `src/` tree, every done ledger item whose id starts with the mod's subject (its folder in capitals,
plus each `--alias` given at `init`, e.g. `GSS`), and each live proof (`infrastructure/state/live_proofs/<ID>.txt`) filed
under them. It also lists done items that name the mod only in their title, for you to read. Stage 0 is refused until each
required line is accounted for: an `inventory` entry that cites it (in `impl_evidence`, `proof_evidence` or `source`), or
a `record.json` `built_reviewed` row `{"ref": "...", "covered_by": "<inventory id>"}` or `{"ref": "...",
"not_a_capability": "<why>"}`. A ledger that cannot be read is UNMEASURED and refuses done (end `blocked`); it never means
"nothing built". A built capability is clarified, never put up for keeping: an ask whose wording offers to keep, cut,
drop or remove something is refused when it is about a `present` capability whose scope he has not opened, whatever its
`offers_removal` flag says, and refused outright when it names no inventory entry. Ask him only on a real fork: a
decision his words and the built code do not already settle.

## Ends

Stage 0 is `done` when the inventory is in `record.json`, accounts for everything in **What is already built**, and
`failure_modes` names the three ways this mod could fail him.
Asks you already see go into `record.json` `asks` with `status: draft`; they reach him only through stage 1-2.

## The first time an item names a mod (owner, 2026-11-03)

*"We do (2) but only for the mods we're touching recently. Baroque Biomes, GSS, FlowWorks, Solar. After that, it's "the
first time an item names a mod, it gets a deep Designer pass to read out its code/spec, expand the spec and validation
strategies, certifies it with the user/clarifies confusion, then writes it all out for Relentless. That way we learn as we
go, getting better and better at it incrementally rather than pretending we know what we're doing right now."*

The four recent mods get the pass now, and any other mod gets it the first time an item names it: read its code and
spec, expand the spec and the validation strategies (site prep and controls for each scene), certify with him and clear
up confusion, then write it all out for Relentless as build items. Filed: `BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS`,
`GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS`, `FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS`,
`SOLAR_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS`; the trigger is `FIRST_TOUCH_BUILD_DESIGNER_READS_FIRST`.

How the trigger works (`src/RimMandrake/rimflow/first_touch.py`): Relentless gives no worker to an unstarted item that
names a mod (its id, title or a `src/` path) while that mod has no pass on record, and files the pass once,
`needs=owner`, as `<FOLDER>_DESIGN_FIRST_TOUCH` (the four above, and every Baroque Biomes compose member, map to their
filed items in `src/RimMandrake/rimflow/designer_passes.json`). A pass is on record when its item closes `done`, or when
`design/concepts/<Folder>/tree.json` passes `gate`. So closing the pass item `done` is what releases the held work: close
it only after the build items are filed. `python3 src/RimMandrake/rimflow/first_touch.py status [<Tier/Folder>...]` reads
which mods are on record. The hold is the rule `first_touch_hold` in `relentless_rules.json`. A pass's concept folder
starts its stage state with `designer_stage.py init`.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
