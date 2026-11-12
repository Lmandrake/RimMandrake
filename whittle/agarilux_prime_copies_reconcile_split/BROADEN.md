# BROADEN — AGARILUX_PRIME_COPIES_RECONCILE_SPLIT (2026-11-11, CLAUDE_ARCHMAGI_OFFLINE2)

Second model: GPT via `src/RimMandrake/Utils/gpt_consult.py` (model gpt-6.1-sol, job consult-20261111-204536-2238573-2d2c97), given STATEMENT.md.

## The question (verbatim)

> You are a second model asked to BROADEN testing of a small RimWorld-mod change. Statement of done is attached (STATEMENT.md).
> 
> What I found and did:
> - RM_AgariluxPrime (a huge 20-cell "grath elder" fungus tree, Graphic_Single) is defined only in TheRot (packaged in the composed mod mandrake.rm.biomes).
>   Its base def named the retired donor slot Things/Plants/AB_AgariluxPrime; a TheRot PatchOperationConditional/Replace repointed it to RotSpecies/AgariluxPrime.
> - There were THREE PNGs: TheRot RotSpecies/AgariluxPrime.png (4096x4096, v3, owner-approved 2026-09-20: what the game draws),
>   TheRot Things/Plants/AB_AgariluxPrime.png (256px, art-eval ACCEPT), UtinniPatches Things/Plants/AB_AgariluxPrime.png (384px, art-eval REGEN).
>   The two art-eval-judged copies were BOTH never drawn (shadowed by the repoint). Root cause: the art-sheet tool reads src texPaths without applying patches.
> - Live def dump of a real full 317-mod game load (2026-11-02): RM_AgariluxPrime texPath = RotSpecies/AgariluxPrime from mandrake.rm.biomes; AB_AgariluxPrime (donor) not loaded; no dumped def names the old slot.
> - Change: base def texPath -> RotSpecies/AgariluxPrime, repoint op deleted, both donor-slot PNGs retired through the art ledger (archived bytes + ledger event).
> - Tests: resolver script (base def + every patch naming the def -> 0 touch texPath -> exactly one PNG across our src mods); validate_patch.py on the
>   touched patch + def files against the full 316-mod load set (0 errors; texPath existence checked); selftests alpha_plants_renders / hugethings footprint+lint PASS;
>   art_guard worktree 0 unledgered texture changes; art.py status: old slot has no live file, RotSpecies slot live and bound to RM_AgariluxPrime body;
>   art-sheet's src resolver now agrees with the dump; the hourly donor-render installer's plan does not re-install the retired copy (0 mentions; it sees 104 dregen jobs);
>   unproven_adjudicate --check passes; deploy dry-run for UtinniPatches says --apply prunes the stale deployed copy; repo-wide git grep for the slot path,
>   file paths and art-eval subject keys: 0 live readers (rest are append-only ledgers, dated records, donor-def rows, my own comments).
> - No game can be run (offline lane). No deploy allowed.
> 
> Question: what would a real user (new player, experienced modder, someone trying to break it, a messy real case) try that I have NOT tested,
> which could show the player sees something other than exactly this one PNG, or that the change broke something? Give the 3-5 most revealing
> concrete checks, ranked, each with what result would mean failure. Be concise.

## The answer (verbatim)

> 1. **Resolve the surviving path across the entire installed content stack.** Check `RotSpecies/AgariluxPrime` in every enabled mod, including version-selected folders, Workshop/local duplicates and packaged resources, using actual load precedence. **Failure:** another provider wins, or the winning bytes differ from the approved 4096px PNG. Uniqueness across *your src mods* doesn’t establish this.
> 
> 2. **Run the complete patch pipeline before/after and compare resolved defs.** Include patches with broad XPath selectors, inherited defs and conditional/sequence wrappers—not only patches mentioning `RM_AgariluxPrime`. Compare all affected defs and patch errors. **Failure:** the final graphic changes, a new patch failure appears, or removing the operation changes whether sibling operations execute.
> 
> 3. **Inspect projected fresh and dirty installations of the complete composed mod.** Compare a clean install with an upgrade containing both retired PNGs, using final manifests and file hashes without deploying. Cover TheRot and UtinniPatches together. **Failure:** either retired file still ships, the surviving PNG is omitted/changed, or cleanup removes a file still required by another installed component.
> 
> 4. **Repeat resolution under supported alternative loadouts.** Try the smallest supported TheRot configuration, the composed biomes package, and configurations with optional UtinniPatches/compatibility mods absent or reordered where permitted. **Failure:** any supported setup resolves a different texture, produces a missing texture, or depended on the deleted repoint operation.
> 
> 5. **Verify approval by image identity, not slot/name.** Match the surviving PNG’s hash to its approval evidence and the gptredo decision subjects. Your account says the ACCEPT judgement covered the retired 256px image. **Failure:** the surviving 4096px image inherits that ACCEPT solely through naming. That would leave the judgement requirement unresolved, even if rendering remains identical.

## What I tried, and what I found

Script: `whittle/agarilux_prime_copies_reconcile_split/evidence/broaden_checks.py`. Output: `whittle/agarilux_prime_copies_reconcile_split/evidence/broaden_checks.txt`.

1. **Check 1, whole installed stack (GPT's #1).** I walked every folder of all 316 mods in the full shipping list (`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`;
   316 of 316 located across src, RimWorld/Data, Workshop and the Steam Mods folder), including every loadFolder and version
   subfolder, looking for any file named `AgariluxPrime*` or `AB_AgariluxPrime*`. **Only `mandrake.rm.biomes` ships
   `RotSpecies/AgariluxPrime.png`.** Its deployed bytes (sha256 85779af9…) are identical to src's. No workshop or DLC mod provides
   the path, so nothing can out-rank it in load order. The only other hit is the deployed Biomes folder's stale
   `Things/Plants/AB_AgariluxPrime.png`. It is unread (no def names that slot), and the next deploy prunes it
   (`evidence/deploy_plan_biomes.txt`, `evidence/deploy_plan_UtinniPatches.txt`: "deleted in repo -- --apply prunes it").
   UtinniPatches is checked from src, where the file is gone, and its deploy plan prunes the deployed copy as well.
2. **Check 2, broad patches the deleted repoint used to override (GPT's #2; the most revealing one).** Deleting the repoint means any patch
   that had changed this def's texPath *before* the repoint ran would now win. I evaluated **every xpath in every Patches/ file
   of the 316-mod load set** (3,137 files, 69,187 xpaths) with lxml against the RM_AgariluxPrime def element. RimWorld patches
   run on the un-inherited XML, so the isolated element is a fair target. **0 xpaths reach its graphicData, texPath or graphicClass.**
   The only selections are our own three def-level operations (the HugeThings mod extension and the label/description/size block).
   That those three show up proves the instrument can see. One defect in my own check: its first run evaluated relative xpaths
   (`Defs/ThingDef[...]`, 39,542 of them) from the root element, where they can never match. RimWorld evaluates them from the
   document node. I fixed the check to anchor them at `/` and re-ran it: still 0.
3. **Check 5, approval by image identity, not by name (GPT's #5).** GPT was right that the ACCEPT in gptredo_03 covered a different image.
   `evidence/judgement_record.txt` shows the two gptredo_03 rows judged sha b0a767dc… (ACCEPT) and sha c93606ba… (REGEN).
   Both files are now retired. Neither row judged the survivor (sha 85779af9…). The survivor's git blob is byte-identical to the v3 landing commit
   9d83052dca (07:47 on 2026-09-20). The owner's blanket approval "The rot art is approved." is stamped 08:53 the same morning, on a sheet
   whose row shows that v3. So the judgement that stands is his, on these exact bytes. It is not an ACCEPT inherited through a shared name.
4. **GPT's #3 and #4 (clean and dirty installs; other loadouts).** The deploy plans cover the dirty upgrade: both retired files are pruned
   and the survivor needs no change. TheRot ships only inside the composed `mandrake.rm.biomes`, and UtinniPatches depends on it. Since
   the texPath is now on the base def and no patch in the full stack touches it (check 2), every loadout that has the def draws the same
   path. No loadout depends on the deleted operation any more.

What none of this shows: a live render in a running game. That is barred in this lane. The 2026-11-02 full-list dump is the
nearest live reading, and it already drew `RotSpecies/AgariluxPrime` before this change.
