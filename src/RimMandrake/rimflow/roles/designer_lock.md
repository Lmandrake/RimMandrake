# Designer packet: Stage 5, Lock

Injected with `designer.md` at stage 5. One versioned order, no avoidable rework:

1. **The root is already his.** Stage 1 recorded his approval of the exact root text and its OWNER event. If the walk's
   root is not yet VALIDATED, that is his word only:
   `python3 src/RimMandrake/Utils/modcheck/cli.py validate <mod> --owner-said "<his words>"`. If it was not validated
   before stage 3 wrote the tree, the `write` that stamps `root_hash` changes the tree, and the launcher reopens stage 3
   and 4: `return` to stage 2 with the decision "root validation" rather than rewriting here.
2. **The artifacts are frozen.** The tree, sheet, scenes and floor are those stage 3 wrote and stage 4 examined; the
   launcher refuses a done result here if any of them changed since.
3. **The Arbiter signs coverage** against those hashes: `concept_tree.py sign <dir> --by Arbiter [--item ID]`, run
   inside an Arbiter role run (it refuses any other writer). It writes a `rimflow note` on the concept's item (stage.json
   `item`) naming the tree and sheet hashes, then the stamp in tree.json; the gate wants both, so commit the ledger shard
   with tree.json (the signature does not change the tree hash the launcher tracks).
4. **The gate**: `concept_tree.py gate <dir>` passes, and `designer_stage.py showcases <dir>` accepts the showcase set:
   the lock is refused while a record.json inventory capability is exercised by no showcase and no scene, and the
   scenes the set names are rechecked against the scene contract (a scene added since stage 3 is not trusted by id).
5. **File the mod item**, `--kind mod`, with `## verify` citing `design/concepts/<Mod>/tree.json` and the accepted tree
   hash. A new mod under another kind escapes the gate. The Producer admits it. Relentless runs `gate` at the pool, at the
   lease, and at `enrol`. FlowWorks and GSS go to Relentless like every other mod. Every scene's missing entry point,
   control or restoration step is a filed build item before this one.
6. Write `result.json` `done`. The launcher then marks the concept `locked`.

Changing a locked tree: his word only, for an edit, removal or waiver (a `locked_change` decision with his OWNER event); a
new concept comes back through the Designer as an amendment. Either gives a new hash and a new signature. A wrap-up that
matters is a scripted step or a check, never an instruction (owner, 2026-11-03, `AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED`).

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
