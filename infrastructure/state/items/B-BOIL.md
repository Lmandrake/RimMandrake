## spec
Two files deployed to
          `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\Patches\`.
          (1) `JawaWorld_BiomeMix.xml` — `RG_BoilingForest` entry CUT (owner
          2026-08-15: *"WE ARE NOT USING BOILING BIOME"*, `df642a1`).
          (2) `SpeciesStartingGear_Tuning.xml` — **not my edit; it rode along.**
          It is committed BUILD work from `5bb9f5c` (B58) that had never been
          deployed, so the GAME COPY still carried the dead defName
          `OuterRim_Jawa` while the repo has said `RimMandrake_Jawa` since B58.
offline verify (BUILD, passed):
          ```
          validate_patch.py JawaWorld_BiomeMix.xml \
            --defs <workshop> --defs <Mods> --defs <Data> --live <DefDump>
          OK - 0 errors, 0 warning(s)

          deploy_custom_mods.py --mod Jawa_Patches --apply
          ~ Patches/JawaWorld_BiomeMix.xml
          ~ Patches/SpeciesStartingGear_Tuning.xml
          -> VERIFIED in sync
          ```
          29 `scoreOffset` entries remain in the biome mix; `boiling` survives
          only inside the explanatory comment.

## verify
_not recorded in the source queue_

## criteria
A Jawa pawn generated from `RimMandrake_Jawa` spawns wearing the
`apparelRequired` this patch sets, and `Player.log` shows **no**
`PawnKindDef named OuterRim_Jawa` / `found no matches` line for
`SpeciesStartingGear_Tuning.xml`. Separately, confirm the worldgen
biome list offered to the owner contains **no** boiling-forest entry —
that is an eyes-on at the world screen, not a log line, and it is the
owner's screen since worldgen is manual.

## notes
**from:** BUILD, 2026-08-15, shutdown window

**notes:** · **The boiling cut is deliberately UNOBSERVABLE and that is the point.**
  `regrowth.botr.boilingforest` left the list in the 585→575 descope, so
  the entry was already scoring a def that does not load. It validated
  **clean** against the dump — which still carries 576 mods — and matched
  nothing in game. Removing a no-op changes no behaviour. **Do not spend
  a live check trying to see this one**; the offline evidence above is
  the whole proof, and "nothing happened" is the expected result.
· **(2) is the half worth a live look**, and it is a real fix, not
  cosmetic: until this deploy the shipped patch pointed at
  `OuterRim_Jawa`, a pawnkind that no longer exists, so its two ops
  matched nothing and Jawa pawns got no `apparelRequired` from us.
· Restart required — defs parse at startup only; a save reload will not
  pick either up.

**Imported from `queue/CHECK_CLOSED.md`. Its `state:` read, verbatim:**

✅ DONE — CLOSED 2026-08-15 on evidence collected this session, owner approved.
This load's harvest read **Jawa_Patches ops = 0 failed, at baseline**, and
**zero** `Exception loading def from file Jawa*.xml` across the whole log.
