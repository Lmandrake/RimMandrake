
## spec
`PLANT_CHERRYPICK_PASS_1` closed on the owner's walk, 2026-08-23. **The decisions exist; they
do not reach the game.** `design/Jawa/mods/plant_decisions.json` (`savedBy: plant_review.html`,
`savedAt` 2026-08-23T10:10:35Z, 192 rows, 77 touched) carries **4 cuts**, and the live Cherry
Picker config still carries **zero plants of any kind**:

    Config/Mod_3521312241_Mod_CherryPicker.xml   1347 entries: 1295 ThingDef, 28 BiomeDef,
                                                 8 IncidentDef, 7 PawnKindDef, 5 HediffDef,
                                                 2 RecipeDef, 2 GeneDef — no plant

The four to add — the key format is `<DefType>/<defName>`:

| defName | label | mod |
|---|---|---|
| `Plant_TreePine` | pine tree | Core |
| `Plant_TreeBirch` | birch tree | Core |
| `Plant_TreePoplar` | poplar tree | Core |
| `RG_Plant_Raspberry` | raspberry bush | ReGrowth 2 |

⛔ **Do not hand-edit the XML.** `src/RimMandrake/Utils/cherrypick_build.py` exists precisely
because Cherry Picker fails silently in three of its four failure modes — read its docstring
before touching the file. 🔴 **A key with no `/` throws inside `DefUtility.ToDefName` OUTSIDE
`RemoveDef`'s catch, and every remaining removal in the list is lost.** One typo and none of
the 1,347 existing picks apply.

## verify
`cherrypick_build.py`'s own offline validation, then in game: the four plants are absent from
a `Volcano` and an `AridShrubland` map, and **a spot-check that an unrelated existing pick
still applies** — that is what proves the list did not silently die at entry 1.

## criteria
- [ ] 4 keys added, file written by the script, existing 1347 entries intact.
- [ ] An unrelated pre-existing pick still applies in game.

## Watch out
✅ **Both resource consequences are RULED and neither blocks this.** `Volcano` (23 tiles) goes
wood 3 → 0 — intended; `VOLCANO_LOST_ALL_WOOD_1` is **dropped** because the owner ruled the
volcano does not need wood. `AridShrubland` (709 tiles) loses `RawBerries` — he accepted it.
⚠️ **`RG_Plant_Raspberry` may yet be withdrawn.** The owner described his cuts as *"only the
ones that affect volcanoes"* and this one affects `AridShrubland`; it is a real `touched`
decision of his and it stands, but **confirm before deploying** rather than after.
⚠️ **The repo copy is never what the game loads.** Diff the deployed config against the repo
copy; do not grep one and conclude about the other.

---

## 🔴 OWNER'S RULING, 2026-08-23, on the one entry this item told BUILD to confirm

> *"Cut the three trees. Do not cut raspberries, they can just be renamed."*

⇒ **Three keys were written, not four.** `Plant_TreePine`, `Plant_TreeBirch` and
`Plant_TreePoplar` are ratified and live. **`RG_Plant_Raspberry` is NOT cut and must not
be** — it stays in `AridShrubland`'s 709 tiles, keeping `RawBerries` there, and gets a
Star Wars LABEL instead. The rename is `RASPBERRY_RENAMED_NOT_CUT_1`.

⚠️ `design/Jawa/mods/plant_decisions.json` still records raspberry as a cut. It is the
owner's saved review artifact and was deliberately NOT rewritten; this ruling overrides
that row. `cherrypick_build.py` never reads that file, so nothing acts on it.
