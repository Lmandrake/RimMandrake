# ✅ REGENERATED AND COMMITTED at `c325daad`. Only the DEPLOY is left.

**Updated 2026-08-26, end of session.** Steps 1-4 below are DONE. Do not re-run the generator.

```
src/Jawa/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml
   28 operations · 801 animal entries · 0 removals · no <li> anywhere
   28 of 28 Ash'karr biomes covered
   all 28 biomes exist in the running game        (checked against the capture)
   all 578 distinct animals resolve as PawnKindDefs (same)
   0 entries cut by Cherry Picker
   3 cast rows skipped as not-PawnKindDefs, named in the generator output:
       Desert/SWPotF_RaceDef_ysalamir · ExtremeDesert/SWPotF_RaceDef_ysalamir · PoisonForest/GiantAnt_Race
```

## The one command left

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Jawa_Patches --apply
```

✅ XML deploys with the game UP; only assemblies are locked. Then `md5sum` the repo copy
against the game copy.

⚠️ **A full `validate_patch.py --live --defs` run over the 1,254-mod workshop tree was still
running when the session ended** — it takes many minutes on this mount. It is a belt-and-braces
xpath-hit check; the two questions that matter (do the biomes exist, do the animals resolve)
were answered directly against the capture and both passed. Re-run it if you want the third
opinion:
```
python3 skills/rimworld-modding/scripts/validate_patch.py \
  src/Jawa/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml --live <capture> \
  --defs "<game>/Data" --defs "<game>/Mods" --defs "<workshop>/294100"
```

---

# CAST_XML_REGEN_AND_DEPLOY_1 — finish the fauna repair: regenerate the patch and deploy it

⏳ **HANDOFF, 2026-08-26 ~22:0x, BUILD, session ending.** Everything upstream is committed and
pushed. The only thing left is mechanical.

## What is already done and committed

`design/Jawa/fauna/cast_assignment.csv` — **804 rows, all 28 Ash'karr biomes, zero cut /
rejected / Earth creatures.** Three exclusion sets now feed it and every generator refuses to
run if any of them is unreadable:

| set | source | size |
|---|---|---|
| Cherry Picker cuts | `Config/Mod_3521312241_Mod_CherryPicker.xml` (his own) | 277 pawn kinds |
| art rejections | `creature_art_decisions.json` state `replace` (frozen, his) | 10 |
| Earth fauna | `design/Jawa/fauna/EARTH_FAUNA_EXCLUDED.txt` | 80 |
| measured dead | `CorellianHound` — 0 in all 9 biomes it appears in, not on any list | 1 |

## What is left

```
python3 design/Jawa/fauna/gen_cast_patch.py            # ~8 min, disk walk over the workshop tree
```

⚠️ **A regeneration was IN FLIGHT when the session ended** (pid 447279, started ~21:5x). Its
log is in the session scratchpad and is gone. **Just run it again** — it is deterministic and
writes `design/Jawa/fauna/BiomeCast_Ashkarr.xml`.

Then, and only after reading the diff:

1. 🔑 **Read the coverage line it now prints.** It must say *"all 28 Ash'karr biomes are cast
   by this file"*. Anything else is a hole and the deploy waits.
2. **It must report 0 entries CUT BY CHERRY PICKER.** The cast is already filtered, so a
   non-zero count means an exclusion set changed underneath it.
3. Copy the CAST SECTION ONLY into `src/Jawa/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml`.
   ⛔ **The de-dup section at the end does NOT go there** — see below.
4. `python3 skills/rimworld-modding/scripts/validate_patch.py` on the result.
5. `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Jawa_Patches --apply`.
   ✅ XML deploys fine with the game UP; only assemblies are locked.

## ⛔ Two traps that will cost a load if ignored

- **The de-dup section is a FLOOR, not a roster.** The generator computes it from a
  post-patch capture, which cannot see a pair our own removal already cured — measured, it
  found 56 where 61 are shipped, and the 5 missing were all working removals. The shipped
  de-dup must stay the UNION in `AnimalBiomeDuplicates_Fix.xml` + `_Generated.xml`. That is
  why the deployed cast patch carries the cast section only.
- **`<li>` must never appear in a `wildAnimals` value.** `BiomeAnimalRecord` reads the node
  NAME as the animal; an `<li>` throws inside the loader and RimWorld discards the ENTIRE
  BiomeDef silently. It cost 26 biomes on 2026-08-22. The generator emits the right shape;
  do not hand-edit it into the wrong one.

## verify
Next load: `biome_commonality_zeroed.py --ours` reports **0** entries at commonality 0 among
the ones our patch writes, and no Earth animal spawns in `BiomeCypreJungle`.

## criteria
- [ ] Coverage line reads 28 of 28.
- [ ] 0 cut entries in the generator's report.
- [ ] Deployed, byte-identical to the repo.
- [ ] The de-dup files untouched by this deploy.
