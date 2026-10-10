# Weeping Stones sheet — independent verification 2026-10-10

Read-only check of commits 53a55b750 (enact), 721d86974 + a03876497 (the 19 TODO rows) against the owner's
`Transient/biome_ffar/weepingstones_sheet_2026-10-05.decisions.json` and the snapshot he ruled on
(`infrastructure/state/art/sheets/weepingstones_sheet_2026-10-05.snapshot.json`, id fb9db321a6e6c4fd, built 07:03,
ruled 07:06–07:50). Nothing was fixed.

**Method.** A pick counts as installed if its bytes OR its decoded pixels match a file in `src/**/Textures`
that the def's texPath binds to (the fish items are re-encoded, so a byte check alone fails them). Redo rows were
checked against the artpipe job JSONs in `D:\Luke\dev\_artpipe` (state, `canon_reference`/`reference`). Descriptions
and labels were diffed from `53a55b750^` to HEAD. Rosters were checked inline and through the `WildAnimals_WeepingStones.xml`
xpath. Changed patches and defs passed `validate_patch.py` against the full mod roots: 0 errors, plus 1 advisory
warning (the Reeds patch is not wrapped in a FindMod guard).

**Totals.** 51 rows. 4 were never clicked (RSW_Bantha, RSW_Dewback, RSW_Eopie, RSW_Jamel have no `at`; they
are prefill only), so 47 were ruled. **PASS 14, FAIL 33.**

## Systemic causes (these explain most of the FAILs)

1. **`enact` silently counts a by-name or render pick as "already live" when the def's texPath points at
   the donor.** It hits the branch at `src/RimMandrake/Utils/art/enact.py` ~L582: `def_points_at(src, rel)` →
   `installed_already ("def texPath (donor art)")`. As a result:
   - **Creatures still render as vanilla animals.** Burrak = Warg, Gorrask/Ivvol = Tortoise, Karrek = Cobra,
     Sillik = Squirrel, Tirbak = Muffalo. Each PawnKindDef still points at the vanilla texPath, and no file of his
     pick exists anywhere in src.
   - **Plants still show the old A picture.** For "pick B" on Bladderquill, Dewblade, Dewgourd, Dripfringe,
     Rockfinger, Salvecomb and Shadefern, `Things/Plant/RM_X/` still holds only `RM_X_a.png`, the old A.
2. **Explicit "+ variant" ticks are never installed.** Enact only protects variants; it does not ship them. Not
   shipped: Bladderquill B, Shadefern B, Steamfrond B, Verdimoss B, Weepmat B, Fanback C.
3. **Enact marks a redo note as "followed" as soon as an art job exists, which drops the def half of the note.**
   No description or label change was made, and the notes are now off the open list, for:
   - Ambrosia (beef up description)
   - Huldu (regenerate and expand description)
   - Loomu (beef up)
   - Skarrin (enhance)
   - Ssurr (expand)
   - Vhakk (new description)
   - Kirruk (rename "Dewglider")
   - Vizhik (rename "Fan Eel" and beef up)
   - Vellak (redo description after the art; nothing tracks it)
4. **The catch jobs ignored "generate AFTER the source is settled, blocking until".** All 8 were filed at 14:58Z
   with no dependency and no reference to the source creature. HulduCatch, LoomuCatch, IvvolCatch, KarrekCatch,
   SkarrinCatch and VizhikCatch(east) have already rendered. MurrinCatch is failed and re-pending, with its old A
   catch as its only reference.
5. **Several redo jobs carry the very art he rejected as their reference.** The commit message says "redo jobs
   carry no reference to rejected art", but:
   - Ambrosia references A (fa6e5ce7), the art he said "Drop the art currently here" about.
   - Loomu references the vanilla tortoise (2875a03b) although his note says "Remove the turtle art".
   - Vizhik references the cobra (8cf333e0) although his note says "Drop all this art".
   - Murrin and Skarrin also use the cobra as reference on "redo completely" notes.
   - Huldu v1 used the tortoise rather than (c). v2 `enact_huldu_from_c_v2` is pending and correctly uses (c).
   - Vellak's job has NO reference, although his note says "based on (b)".
6. **The sheet's fish and catch columns were built from a stale census.** The census is at 8b1860f2e, which is
   before 693ba6346 (fish repointed to their own art, 10-07). So for Duul, Ikkal, Tarrik, Ullo, Vobbal and Ozhu,
   "A/B" showed donor Meat_Small while the game actually shows the C render (pixel-identical). These pass because
   the effective pick is C, but he never saw the in-game picture labelled as such.

## Rows

| row | his decision / note | what exists | verdict |
|---|---|---|---|
| ColossusToad | B; "Redo more alien, rename Colossia, regenerate description, based on the current (b) but extended." | B bytes at `WeepingStones/Textures/Things/Pawn/Animal/RM_Colossia/`; new def RM_Colossia replaces ColossusToad on the RM_WeepingStones roster; new description; `wsrow_colossia_v1` pending with B as reference | PASS — scope: a whole new creature def (stats, body) was invented; he asked for a rename and a redraw |
| Plant_Ambrosia | redo; "...Drop the art currently here." | job done (awaiting pick), reference = A, the art he dropped; A still live in UtinniPatches; no description change | FAIL |
| Plant_Reeds | B; "Two more variants, more realistic." | B at `RM_Reeds/RM_Reeds_A.png`; 2 variant jobs done; `RM_Reeds_OwnArt.xml` repoints Odyssey `Plant_Reeds` | PASS — scope: a global repoint that changes reeds in every biome, from a biome-scoped sheet |
| RM_Bladderquill | B, + variants A and B | only A live | FAIL |
| RM_Burrak | B; "Rename to Burra Burra" | label "burra burra" ok; pick B not live, still Warg/Warg (the Warg he ✕'d); description invents an etymology | FAIL (art) |
| RM_Dewblade | B; two more variants | 2 jobs done; pick B not installed (A live) | FAIL |
| RM_Dewgourd | B; two more variants | same as Dewblade | FAIL |
| RM_Dewshrooms | B, + variants B, C, E; improve description | B/C/E in the Seadew folder; D purged; description rewritten | PASS |
| RM_Dripfringe | B; two more variants | pick B not installed; job a done, job b FAILED | FAIL |
| RM_Duul | C; improve description | C live (pixel-identical); description rewritten | PASS |
| RM_Gorrask | C | pick not live; still Tortoise | FAIL |
| RM_Huldu | redo; based on (c)... regenerate and expand description | v2 pending with (c); description unchanged | FAIL (description) |
| RM_HulduCatch | redo; dead one, blocking until source settled | rendered before Huldu was settled; no reference | FAIL |
| RM_Ikkal | A, by-name pick C; "call it a Softstone" | C live; label "softstone"; description rewritten | PASS (stale-sheet caveat) |
| RM_Ivvol | C | pick not live; still Tortoise | FAIL |
| RM_IvvolCatch | redo; dead one | rendered with no source reference | FAIL |
| RM_Karrek | C; "Rename the Iaala" | label "iaala" everywhere; pick not live, still Cobra | FAIL (art) |
| RM_KarrekCatch | redo; dead one | rendered/active, no source reference | FAIL |
| RM_Kirruk | redo; ...Rename to "Dewglider" | job done; label still "kirruk" | FAIL |
| RM_Loomu | redo; beef up description; remove the turtle art | job references the tortoise; description unchanged | FAIL |
| RM_LoomuCatch | redo; dead one | rendered before Loomu was settled | FAIL |
| RM_Mirrik | hold + "cut this" | off the inline RM_WeepingStones roster and absent from the patch; def kept | PASS |
| RM_Murrin | redo completely | job done, cobra reference | PASS (concern: reference) |
| RM_MurrinCatch | redo; dead one | failed, re-pending, own old catch as reference | FAIL |
| RM_Ozhu | redo; dead one | job done, no reference; "these" is unclear for an item row | PASS (concern) |
| RM_Rockfinger | B; two more variants; 50% larger | visualSizeRange 1.5~3.2 → 2.25~4.8 ok; jobs a done / b pending; pick B not installed | FAIL (art) |
| RM_Salvecomb | B; two more variants | 2 jobs pending; pick B not installed | FAIL |
| RM_Shadefern | B, + variants A and B; two more variants | 2 jobs pending; B not installed | FAIL |
| RM_Sillik | B | pick not live; still Squirrel | FAIL |
| RM_Skarrin | redo; enhance description | job done (cobra reference); description unchanged | FAIL |
| RM_SkarrinCatch | redo; dead one | rendered before Skarrin was settled | FAIL |
| RM_Ssurr | redo; expand description; fix crest-fan | job done; description unchanged | FAIL |
| RM_Steamfrond | A, + variant B; "Creates a unique Star Wars cuisine spice. Improve the description." | description ok; variant B not shipped; scope: coined "korrim", new def RM_Korrim, harvest changed from RM_RawSalt, murrin broth recipe changed | FAIL (variant) + scope |
| RM_Tarrik | A, by-name pick C | C live | PASS (stale-sheet caveat) |
| RM_Tirbak | A, by-name pick B; description note | description matches his note; packAnimal true; pick B not live, still Muffalo (which he ✕'d) | FAIL (art) |
| RM_Ullo | A, by-name pick C | C live | PASS (stale-sheet caveat) |
| RM_Vellak | redo; based on (b)...; description after art | job has no (b) reference; the description follow-up is untracked | FAIL |
| RM_Verdimoss | A, + variant B; two more variants; description | description ok; jobs pending; variant B not shipped | FAIL (variant) |
| RM_Vhakk | redo; drop all art; new description | job with no reference ok; description unchanged | FAIL |
| RM_Vizhik | redo; rename Fan Eel; drop all art | label "vizhik"; cobra reference; description unchanged | FAIL |
| RM_VizhikCatch | redo; dead one | rendered/pending before Vizhik was settled | FAIL |
| RM_Vobbal | A, by-name pick C | C live | PASS (stale-sheet caveat) |
| RM_Weepmat | A, + variant B; two more variants; description | description ok; jobs pending; variant B not shipped | FAIL (variant) |
| RSW_Boma | B | B byte-identical; 8 purges gone from src | PASS |
| RSW_Dactillion | B; "Old Flyer art must be removed (remove F)" | B installed; 12 Flying frames and flyingAnimation fields removed; no dangling refs | PASS — the game copy keeps the frames, because the deploy plan only removes them with `--prune`, so the progress file's claim is wrong |
| RSW_Fanback | B, swim F, + variants B and C | B and F live; variant C not shipped | FAIL (variant) |
| RSW_Ollopom | B, swim E; beauty bonus | B live at `RimStarWars/SWBestiary/Ollopom/`; PawnBeauty 1 (the agent asked him whether it should have a gameplay effect) | PASS |

## Purges

0 of the 45 ✕'d pictures remain in src, checked by bytes and by pixels. But for every creature whose ✕ hit
donor art (Burrak, Gorrask, Ivvol, Huldu, Karrek, Sillik, Tirbak, Vellak, Ssurr), the def still binds the
vanilla texPath, so the game still draws that animal.

## Deploy (dry-run plans, not applied)

- **SWBestiary:** drift (Boma, Dactillion, Fanback, Ollopom art and defs).
- **UtinniPatches:** drift (`RUT_WeepingStonesFish_Items.xml`, plus unrelated faction and HolyFlame files).
- **Composed Biomes** (WeepingStones, TheRot): drift (RM_Colossia, the Reeds patch, Korrim, flora), and the
  plan writes DLLs. The game was running, so all three were skipped, as expected.
