# Designer packet: Stage 0, Read (grounding)

Injected with `designer.md` and `designer_scene_contract.md` when the concept is at stage 0.

## Bounded grounding

🔑 Before you treat anything as unbuilt, search `src/` and the roster: this project keeps having already built it. Start
with the affected mod, its current specification and its proof script (`validation.py` or the suite that covers it).
Also read the neighbours that the mod directly touches. Read further only to resolve a **named** uncertainty that could
change scope, feasibility or proof. Before you read further, write the uncertainty into `record.json`: in
`contradictions`, or as an `inventory` entry with `impl: unknown`. When the uncertainty is settled, stop. Grounding is complete when the bounded questions have answers, never when you "read enough source" or "walked every possibility".

1. **His words on the mod**: read the ledger (`--owner-said` events on its items) and the walk's `## north star`. Read
   his rulings (`design/RimMandrake/standing_rulings.md`, `design/RimMandrake/mod_definition_lessons_2026-11-02.md`).
   Put each one that you use into `record.json` `scope` or `decisions`, with its `OWNER:<tsn>` source.
2. **The inventory**: write one `inventory` entry per capability, with `impl`, `proof` and `scope` set separately (see
   `designer.md`). "Unproven on the ledger" may only mean unrecorded. When his words say that he ran it, mark it `exercised_unrecorded`.
3. **Neighbours and whatever already does this job**: name each neighbour that does part of the job. Name the neighbour
   that owns the job. Name any service that this mod must opt into (*"These need to brought in harmony with each other."*, 2026-11-03).
4. **Feasibility from real source**: only for a capability that is `absent` or `unknown` and in scope. Use skill
   `rimworld-modding`. For a Star Wars species or droid, use `rimworld-canon-references`.
5. **Script audit**: for each scene that the mod's proof script stages, record the scene contract's parts that it lacks.
   The parts are the asserted start, discriminating control, restoration and hold. The missing parts become build items
   at stage 3. You write no code.
6. **A vanilla or popular mod that does the same thing**: name one, only when it could change a design choice.

When you cite a count about a def dump, save or log, use skill `measuring-large-artifacts`, then
`infrastructure/state/facts/instrument_traps.md`.
- **A stage 0 inventory can carry a capability that was later CUT**, while its item stays closed-as-built. Example: a
  furnace-beast world migration was cut in 84cc81013d. The coverage judge then demands a scene for a removed feature.
  Before you scene a capability, run `git log -S` on its main class to see whether the class still exists.

## What we built comes first (owner, 2026-11-02)

GSS sitting 1 asked him whether to keep poles, styles and save removal. All three were already built: *"Those were very
strange questions given we already have these capabilities."*

So the packet carries **What is already built**. The launcher reads its sources, not you:
- the mod's `src/` tree;
- every done ledger item whose id starts with the folder in capitals, or an `--alias` given at `init` (like `GSS`);
- each live proof (`infrastructure/state/live_proofs/<ID>.txt`) filed under those items.

**What is already built** also lists done items that name the mod only in their title, for you to read. Stage 0 is
refused until each required line is accounted for. One of these accounts for a line:
- an `inventory` entry that cites the line (in `impl_evidence`, `proof_evidence` or `source`);
- a `record.json` `built_reviewed` row `{"ref": "...", "covered_by": "<inventory id>"}` or `{"ref": "...",
  "not_a_capability": "<why>"}`.

A ledger that cannot be read is UNMEASURED and refuses done (end `blocked`). An unread ledger never means "nothing built".
A built capability is clarified, never put up for keeping: an ask whose wording offers to keep, cut,
drop or remove something is refused when it is about a `present` capability whose scope he has not opened, whatever its
`offers_removal` flag says, and refused outright when it names no inventory entry. Ask him only on a real fork: a
decision that his words and the built code do not already settle. Put the evidence against the obvious answer on the
ask (Evidence-for-Ask, CHARTER §Decisions).

## Ends

Stage 0 is `done` when the inventory is in `record.json` and accounts for everything in **What is already built**.
Also, `failure_modes` must name the three ways this mod could fail him. Put the asks that you already see into
`record.json` `asks` with `status: draft`. Draft asks reach him only through stage 1-2.

## The first time an item names a mod (owner, 2026-11-03)

The first time an item names a mod, the mod gets a deep Designer pass. Read its code and spec. Expand the spec and the
validation strategies (site prep and controls for each scene). Certify with him and clear up confusion. Then write it all
out as build items for the Maturation Pipeline.

A pass item is `<FOLDER>_DESIGN_FIRST_TOUCH`. `src/RimMandrake/rimflow/designer_passes.json` maps mods to their filed
pass items. A pass is on record when its item closes `done`, or when `design/concepts/<Folder>/tree.json` passes `gate`.
Close the pass item `done` only after the build items are filed. `python3 src/RimMandrake/rimflow/first_touch.py status
[<Tier/Folder>...]` reads which mods are on record. A pass's concept folder starts its stage state with
`designer_stage.py init`. His words, the first four passes and the retired trigger: `design/RimMandrake/roles.history.md`
§designer_grounding.md: The first time.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
