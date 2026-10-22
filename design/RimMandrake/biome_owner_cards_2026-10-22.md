# Owner question cards: retirement, leaning-scrub art, shell part, dead patches (2026-10-22)

Prepared by a FOUNDRY helper, read-only, 2026-10-22 4:45 PM PDT. 14 cards, ordered by how much each answer unblocks.
Every card is written to be sent as a question card as is: plain labels, every term defined, costs and buys on each
option, one recommendation. Stamp the real time (`date`) on its own line above each card when asking.
Sources are cited in the card text so each fact can be re-checked. Rulings obeyed: stop evictions (no roster edits),
no worldgen or painting work (a biome on zero tiles is expected), every DLC assumed.

Order, with what each unblocks:

| # | card | unblocks |
|---|---|---|
| 1 | The shell body part that overrides vanilla | a live gameplay bug on 31 bodies; one yes ends it |
| 2 | Deleting the dead patches | the code-review loop (107 XML files left dirty) |
| 3 | Juvenile pictures crossed out on the Leaning Scrub sheet | 3 of the 5 stuck sheet conflicts (Igitz, Mudhorn x2) |
| 4 | Rust Cathedral roaches mod | one mod off the load list, near-zero risk |
| 5 | Shokkweave Economy mod | one mod off the load list, one campaign feature decision |
| 6 | Kybuck new pictures | closes the last redo on the Leaning Scrub sheet |
| 7 | Wrecked Machines mod | one mod off the list, a gameplay feature decision |
| 8 | Greentide Raid Ant mod | one mod off the list; a hidden raid faction decision |
| 9 | Vanilla Factions Tribals mod | the largest piece: ideoligion rework, but expensive |
| 10 | Moss beetle south picture | last sheet conflict but one |
| 11 | Nysyllin old picture | last sheet conflict |
| 12 | Durrok and mullgoth sizes | restores a 2026-09-19 ruling that is currently not applied |
| 13 | Three Inhabited cast files disagree with their source | stops a generator from overwriting by accident |
| 14 | Shyrack's fourth flying frame | one flyer animation bug |

---

## Card 1. The shell body part that quietly overrides vanilla's (also: what to rename it)

**What was learned.** One of our Star Wars mods (Utinni patches, the absorbed Cephaloids content) defines a body part
named `Shell` with 2500 hit points that cannot be destroyed and never bleeds. Vanilla RimWorld already has a body part
named `Shell` (30 hit points, a normal part). Two parts with the same name cannot coexist: ours silently replaces the
vanilla one for **every** body that uses it. Checked in the files: 28 bodies of ours use `Shell`, two of them the Cephaloids, 26 others (the Rot beetle and
mantis, Lantern Deeps moth, Acklay, Kinrath, Klorslug, Gelagrub, Lylek, Lava Flea and the rest of the insect-style
Star Wars ports), plus 3 vanilla bodies (the beetle-like animal body in two forms, and Odyssey's larva body). So all
of them now carry an indestructible 2500-hit shell instead of a 30-hit one. Whether that makes any creature
unkillable in play is **not measured**; it certainly changes every fight with them. The only creatures that should use
our tough shell are the two Cephaloid bodies in that same file (Cephaloid and Nautiloid). The saves hold none of them
(0 Cephaloid or Nautiloid in the ship save), so a rename breaks no savegame.
Source: `design/RimMandrake/review_findings_2026-10-22/shell_bodypart_blast_radius.md`; vanilla part at
`Data/Core/Defs/Bodies/BodyParts_Animal.xml`.

**Terms.** *Body part def*: the game's definition of one part of a body (hit points, whether it can be destroyed).
*Rename*: give our tough shell its own name and point only the two Cephaloid bodies at it; vanilla `Shell` returns
untouched for everything else.

1. **Rename ours to a name in our own tier (`RUT_CephaloidShell`) and repoint the two Cephaloid bodies.** Buys: the
   28 bodies and the 3 vanilla ones get their normal shell back; the new name follows the three-tier naming rule.
   Costs: those creatures become easier to kill than they have been (they were effectively armoured by accident); a
   small edit in one file.
2. **Rename to the donor-style name (`JOE_Shell`) the review first suggested.** Buys: same fix, closest to the
   source mod. Costs: a donor prefix breaks your 2026-08-30 naming rule (every new defName is `RM_`, `RSW_` or `RUT_`).
3. **Leave it, and keep the armoured shells deliberately on all insect creatures.** Buys: nothing changes this
   week. Costs: vanilla beetles and larvae stay modified for everyone, and nobody chose that.
4. **Give the insects a tough shell on purpose, with a tuned value, and the Cephaloids their own.** Buys: a
   designed result instead of an accident. Costs: a balance design pass; no one has asked for it.

**Recommended: 1** - it ends an accident in one file with the right prefix, and nothing in a save depends on it.

---

## Card 2. Delete the patches that can no longer do anything?

**What was learned.** Reviewers found patches that target mods or creatures we have already retired, so they match
nothing. These carry no owner-ruled value (the file or the review says what each would have done, and the same value
is already carried elsewhere). Checked just now that they exist; what each is:
- `MechanoidIntrusion_AllowRivers.xml`: has zero operations (header only). The Rust Cathedral biome already allows rivers.
- `OrcClan_GamorreanRename.xml`: renames a faction from a retired mod; the faction is already zeroed.
- `StatNorm_CaravanAdventures_BossStatsNeutral.xml`: 9 operations, all on bosses of a retired mod (Caravan Adventures).
- `TibannaEmbargo_CutMineableRoute.xml`: strips a mine route from a retired mod; with the mod gone, no route exists.
- `Absorbed_Kotorcore_MHC_Patch_IonDamageWorker.xml`: needs a framework we retired; its ion code class is unavailable.
- Three leftover entries in `JawaWorld_BiomeMix.xml` for a retired swamp mod (the rest of the file stays).
Source: `review_findings_2026-10-22/dead_patches.md`. Left out on purpose (they carry ruled value or need a design
call): the grass depth patch, Ancient Arsenal's boss line, the turret relabels (cosmetic), the two Inhabited sets.

**Terms.** *Dead patch*: an edit aimed at a thing that no longer exists, so it changes nothing.

1. **Delete all six now.** Buys: 107 files leave the dirty review list over time; no more stale text for agents to
   misread. Costs: if one of the retired mods ever comes back, its patch would have to be re-written (recoverable
   from git history).
2. **Delete the four that are fully empty or fully dead, and keep the Tibanna and ion ones as written records.**
   Buys: caution on the two with a ruling attached. Costs: two more dead files stay in the dirty list.
3. **Keep everything and mark each file reviewed as is.** Buys: zero deletions. Costs: dead weight stays, and the
   same files get re-opened by the next review.

**Recommended: 1** - you said in 2026-09-09 *"Simply remove offending inaccurate material, don't leave it in and
supersede it."* and these carry no live value.

---

## Card 3. The juvenile pictures you crossed out are the only juvenile pictures in the game

**What was learned.** On the Leaning Scrub open-rows sheet (2026-10-20) you crossed out (marked for deletion) the
current juvenile pictures of the Igitz and the Mudhorn, and picked adult art for each. The new juvenile pictures were
drawn, but you never picked one. The tool refuses to delete a picture that is live in the game, so these three
crossed-out pictures stayed: the Igitz juvenile (east view), the Mudhorn juvenile (east view) and the Mudhorn
juvenile (south view). If we delete them now, those two young animals would have **no juvenile picture** until
someone picks one. Replacement renders that exist: Igitz juvenile has two new tries (one east-only, one east and
south); Mudhorn juvenile has one new try (east and south, no north view). The sheet itself says no human has ruled on
it as a whole. Sources: `Transient/biome_ffar/leaningscrub_open_rows_sheet_2026-10-18.decisions.json`; a dry run of the
art tool (`art.py enact --dry-run`) on 2026-10-22 listed exactly these three as conflicts.

**Terms.** *Juvenile*: the young life stage of an animal, drawn separately from the adult. *Live*: the picture the game
shows right now.

1. **Keep the crossed-out pictures until you pick a juvenile from the new tries, then replace them.** Buys: nothing
   disappears before a replacement exists. Costs: one more look from you (a card per animal showing the new tries).
2. **Delete the old pictures now and fall back to the adult picture scaled down for juveniles.** Buys: sheet closes
   today; matches your cross. Costs: young animals look like small adults; the new renders are never used.
3. **Install the newest render for each automatically (the east and south one for each).** Buys: no look needed.
   Costs: the Mudhorn render has no north view, so that facing falls back; you never saw these tries.
4. **Redraw the juveniles again.** Buys: a fresh attempt. Costs: more art time; the first tries may already be fine.

**Recommended: 1** - the crosses were placed before the new renders existed; a replacement should be chosen, not guessed.

---

## Card 4. Rust Cathedral roaches mod: cut it

**What was learned.** You cut this mod on the retirement sheet and accepted that sheet on 2026-10-21. It is still
active because Wave 4 left it. Checked in the files: the roaches are **already ours in the free tier**: the Rust
Cathedral biome lists `RM_CathedralRoach` (3 mentions) and the Warscar biome lists `RM_ScarRoach`. What the old mod still holds
is a hidden stand-in, `RUT_ScarRoach`, kept "for one release" so saves would still load. One test save
(`ASHKARR_DEV_START..._PARITY_QUIET_R3`) names it once; the three real saves (founders, landed, ship) do not. The campaign
Rust Cathedral biome lists its cathedral roach behind a guard that switches off by itself when the mod is absent.
Other mentions are About text and comments. Source: `design/RimMandrake/wave4_sheet_gap_2026-10-22.md` (its "do the
roaches belong?" question is already answered by the RM copies), plus the files above.

**Terms.** *Stand-in*: a leftover def kept so older saves find a name they expect.

1. **Cut it now: remove it from the modlists, tidy the About text, and retire that one test save's roach.** Buys:
   one less mod to load; nothing visible changes. Costs: that one test save needs its roach removed or re-made.
2. **Keep the stand-in one more release.** Buys: that test save keeps loading. Costs: the mod stays on the list for a
   save we do not ship.
3. **Cut, but first move `RUT_ScarRoach` into the Scarlands mod as an alias.** Buys: every old save loads. Costs:
   new alias work for no shipped save.

**Recommended: 1** - the roaches live in our free mods already, so the shipped game loses nothing.

---

## Card 5. Shokkweave Economy mod: what it still does that the Webwork mod does not

**What was learned.** The wave-4 note said the Webwork biome's files depend on this mod. **That was wrong**: the
Webwork's files only mention it in comments, with no real reference. The mod's own About says the trader and rename
half already moved into the free Webwork mod. What only this mod still does (campaign tier): (a) renames
vanilla hyperweave to "shokkweave", (b) the **silk vein** and **nest raid** objects that scatter on the **older Webwork
copy** (`RUT_Webwork`), which you ruled on 2026-10-22 gets retired at the end paint (the new Webwork is the one painted),
(c) the **Hutt Cartel egg black market** (a rare caravan that sells ollathrix eggs and buys contraband eggs), and
(d) rare-stock for a Wildsteam weaver caravan. No save names any of its defs (0 hits); the ship save lists its package id
once in the mod list only. Source: files under `src/RimUtinni/ShokkweaveEconomy/`, `src/RimMandrake/Webwork/`.

**Terms.** *Campaign tier*: Star Wars layer (`RUT_`). *Free Webwork*: the franchise-free mod `RM_Webwork`, which owns the
nest, eggs and silk there already.

1. **Cut it. Accept losing the Hutt egg black market and the Wildsteam weaver caravan.** Buys: one mod and an old
   biome's scatter code gone. Costs: two small campaign trading features disappear.
2. **Keep it for the egg market and caravan, remove only the old-Webwork scatter.** Buys: the trade flavour stays.
   Costs: the mod stays on the list; a half-trimmed mod to maintain.
3. **Move the egg market and caravan into the Webwork mod's campaign patch, then cut.** Buys: nothing lost, mod
   gone. Costs: a small build.
4. **Keep it entirely until the end paint.** Buys: no work. Costs: the load list stays one mod larger, and the retired
   twin's scatter stays live.

**Recommended: 3** - two cheap trade features are worth porting once the mod is cut; ask for 1 if you don't care about them.

---

## Card 6. Kybuck: use the new pictures, or redo again?

**What was learned.** On the Leaning Scrub sheet you asked for the Kybuck's absurd standing pronghorn images to be
removed and canon regenerated from the dark brown standing animal on a purple background, with the prominent facial
bone plate (your note, 2026-10-20). Three renders were drawn from that (`leaningscrub_kybuck_legends2_v1` east, north,
south) and have been waiting since for you to say if they are right; nothing is installed. The art tool lists them as
"awaiting owner pick". This needs to be looked at in game or on a single image; neither has happened.

**Terms.** *Render*: a freshly drawn candidate picture, not yet in the game.

1. **Install these three.** Buys: the Kybuck has the new look now. Costs: you have not yet judged them.
2. **Show them to you as single images first (full size, true scale, all facings), then decide.** Buys: a real
   judgement. Costs: one more look.
3. **Redo with a firmer note.** Buys: another try. Costs: more time and cost; the note needs wording.

**Recommended: 2** - phone art review needs full size, scale and facings, and these have never been seen.

---

## Card 7. Wrecked Machines mod (the dead factory the crew restores): cut it?

**What was learned.** You cut this mod; it was marked "needs a call". It is the mod that lets wrecked machines in
the Kolyska factory move from wrecked to kludged to restored (alloy forge, automated smelter and others), and it
hard-depends on Vanilla Factions Expanded - Factory. Facts, checked: it is in the ship list, and in the dev, test and
authoring lists, but **not** in the end-paint list. One test save (the parity-quiet one) holds 5 of its research
projects; the ship, landed and founders saves hold none. Three kinds of reference to it remain in our code: research
tab and techprint patches (written as plain edits that do nothing if the research is missing), the Armoury's alloy
forge and smelter patches (about 26 mentions, many guarded), and a list of machine names in one code file. Cutting means
tidying those and losing the restoration progression. Its own README claims it has no defs yet; that is stale.

**Terms.** *Techprint*: a one-time item gating a research project.

1. **Cut it and scrub the Armoury and research patches.** Buys: one mod and its factory dependency gone; the shipped
   saves already lack it. Costs: you lose the wrecked-to-restored progression and the alloy forge gating that rides on
   it; a scrub across 5 files.
2. **Keep it; mark the cut as not enacted.** Buys: the restoration story stays. Costs: another mod and VFE-Factory
   stay in the list.
3. **Keep the mod in ship only, leave out of dev and test lists.** Buys: smaller everyday lists. Costs: the dev game
   no longer exercises a shipped feature.

**Recommended: 2** - the restoration feature is shipped design with real patches built on it; you marked it a call and
nothing forces it out.

---

## Card 8. Greentide Raid Ant mod: keep the giant ant raiders?

**What was learned.** This mod replicates the donor "They!" giant ants as our own: the ant race and its two pawn
kinds, a hidden faction that only raids, carapace leather and a carapace wall. Your sheet note says it is needed only if
the faction exists at the faction pass. Facts: the faction is already in every dev save (3-4 mentions each) and is created
with a start count of zero, so it exists only because a tool added it; the world-remake notes say that works
(`RUT_GreentideAntFaction`, runbook step G15). The Greentide biome itself never mentions the ants. Still owed on the
ants: a coined Star-Wars-style name (the label is still the plain "giant ant"), new art, and two raid sounds. Five
files in our code mention it without a guard (a doctrine About, the megafauna yield patch, the faction list patch, an
armour leather patch and a test manifest).

**Terms.** *Faction pass*: the step in the end remake where factions are created. *Hidden faction*: raids come from
it, but it never appears as a diplomatic party.

1. **Keep it, and finish its owed name, art and sounds.** Buys: Greentide has its signature raid enemy. Costs: three
   unfinished pieces of work.
2. **Cut it, scrub the five references and the saved faction.** Buys: one mod gone; no unfinished ants. Costs: the
   Greentide loses its raiders; test saves need the faction removed.
3. **Move the ants into the free Greentide mod under our own name (no Star Wars).** Buys: the mod count drops
   and the raid enemy stays. Costs: the largest build of the three (race, kinds, faction, and art owed anyway).

**Recommended: 3** - the ants are franchise-free invented creatures, so they belong in the free Greentide mod; but
this is your design call (coin flip between 1 and 3 if you want the lowest effort now).

---

## Card 9. Vanilla Factions Tribals mod: cut it now, or wait for the remake?

**What was learned.** You cut it on the sheet, with the note "demote dev to test". It is the largest of the five
because the **saves name it heavily**: every ideoligion's tech-advancement rituals use Tribals classes (85 obligation
triggers, 17 of each Advance-To ritual), plus a game component, two apparel things and two factions. Counted again:
about 920 lines in each of the dev saves name it (952 in the parity one). Without the mod these saves would not
load cleanly. Our `ResearchRetag` research trio also lists four of its research projects (Bow, Fire, Furniture,
Tribalwear) as prerequisites, unguarded. It is in ship and paint lists, not in dev or authoring. The remake notes
(2026-10) say a mod whose classes the save names cannot leave until the save is remade. Source: the Wave 4 register
line 36 and `world_remake_reinstate_list.md` item 7.

**Terms.** *Ideoligion*: a colony's belief system, here with ritual rules from the mod. *Guarded*: wrapped so the
reference is ignored when the mod is absent.

1. **Keep it until the world is remade, then drop it with the ideoligions re-made.** Buys: saves stay valid, no
   rework now. Costs: the mod stays on the list in the meantime.
2. **Cut it now: re-make every ideoligion without its rituals and guard the research trio.** Buys: mod gone. Costs:
   all ideoligions rebuilt and re-checked, and the ship save would need regenerating.
3. **Cut it for dev and test lists only, keep it in ship and paint.** Buys: smaller everyday lists, as the sheet
   note said. Costs: dev saves would stop loading as they are.

**Recommended: 1** - the saves depend on it in 900+ places; the ideo re-make is the real cost and the remake
already does it.

---

## Card 10. Moss beetle: you picked a picture and also crossed out one of its views

**What was learned.** On the Leaning Scrub sheet you picked render B (the "desert port" moss beetle) for the row. You
also crossed out B's **south** view (the other two views are identical to what the game has). That south view is also
protected because you kept it on the earlier Leaning Scrub sheet (2026-10-08). So the art tool leaves it alone. Either
the cross was a slip, or you want a different south view.

**Terms.** *View*: one facing of the picture (east, north, south).

1. **Install B whole, south included; the cross was a slip.** Buys: matches your row pick and your 2026-10-08 keep.
   Costs: if the south view is wrong you will meet it in game.
2. **Install B's east and north; redraw the south view.** Buys: honours the cross. Costs: a new south view to draw and
   look at.
3. **Choose A (the current game picture) instead.** Buys: no change. Costs: undoes your B pick.

**Recommended: 1** - you kept exactly this picture on 2026-10-08, so the newer cross is the odd one out.

---

## Card 11. Nysyllin: delete the donor's original young-plant picture?

**What was learned.** The Nysyllin wild plant has a young form with six pictures in the game and one original donor
picture. On this sheet you picked young-form picture C and crossed out the donor original. But on the 2026-10-14
donor-art sheet you had kept the donor original for that same form (and picked B); the older keep still protects it, so
the art tool will not delete it. The new pick supersedes the older one for the live art; only the donor file is at issue.

1. **Delete the donor original; the newer sheet wins.** Buys: matches your latest picks. Costs: the donor file is
   gone for good (git history keeps it).
2. **Keep the donor original as an unused archive and install C.** Buys: nothing destroyed. Costs: a stale picture
   stays on disk and keeps tripping the tool.
3. **Go back to B (the 2026-10-14 pick).** Buys: consistency with the older keep. Costs: undoes your newest pick.

**Recommended: 1** - the newer sheet is later and more specific, and you want donor art out.

---

## Card 12. Durrok and mullgoth: restore the sizes you ruled?

**What was learned.** On 2026-09-19 you ruled the Rot's adult sizes by card: durrok 2 -> 6 cells, mullgoth 3.8 -> 5.
The patch that carried that aimed at the old Alpha Animals creatures, which no longer exist, so nothing applies now.
Our copies still draw at 2 and 3.8 (checked: the durrok's adult stage draws at 2, the mullgoth's at 3.8). Since then the
durrok went through the Leaning Scrub review at the small size. You answered 2026-10-22, on whose creatures they are:
*"Like needs to move. Wait until biome reviews. But you are right they should not be like this."* So no move now.
Source: `review_findings_2026-10-22/ruled_values_questions.md`.

**Terms.** *Cell*: one map square. *Draw size*: how wide the picture is drawn; stats do not change.

1. **Restore 6 and 5 now.** Buys: your ruling is honoured; Rot briefs already say six and five. Costs: the
   durrok becomes three times bigger in the Leaning Scrub too, where it was judged at 2.
2. **Wait with the creatures and settle sizes at the biome reviews.** Buys: one decision per creature; matches your
   2026-10-22 answer. Costs: until then the Rot's durrok and mullgoth draw smaller than you ruled.
3. **Keep the small sizes and withdraw the 2026-09-19 ruling.** Buys: no rework. Costs: the Rot loses its big mounds.

**Recommended: 2** - it follows what you said on 2026-10-22; the sizes ride with whichever creature the Rot owns.

---

## Card 13. Three Inhabited cast files disagree with the notes that generate them

**What was learned.** Three cast files of the Inhabited mod (Empire, Wildsteam, Droids) differ from what the
generator would write from their source notes. Empire: race Hussar vs Echani, plus an extra multitool. Wildsteam: three
race lines (Yttakin vs Wookiee, Ortolan and the others). Droids: one hook text and an extra sniper rifle. Running the
generator would overwrite the files; leaving it means the files and notes keep disagreeing. Source: `dead_patches.md`
(run S block).

**Terms.** *Cast file*: the list of who and what populates a settlement type.

1. **The files are right; update the source notes to match.** Buys: nothing in game changes. Costs: the notes need
   editing to match the files.
2. **The notes are right; regenerate the files.** Buys: the written design is what ships. Costs: the settlements
   change (races, items) with no one having looked.
3. **Go line by line with you.** Buys: certainty. Costs: your time.

**Recommended: 1** - these shipped and have been seen; the notes are the part that went stale (a coin flip if you
remember the intent).

---

## Card 14. Shyrack's fourth flying frame has the wrong file name

**What was learned.** The Shyrack flyer is set to a 4-frame flying animation. The game looks for frame files `_1`
to `_4`, but the fourth set of three images is named `_44` (checked: `Shyrack_Flying_1..3` and `Shyrack_Flying_44` in the
Shyrack textures folder), so frame 4 never loads. Flight is verified by state, never by live test.

**Terms.** *Frame*: one picture in the flying flip-book.

1. **Rename the three `_44` files to `_4`.** Buys: the animation becomes the 4 frames intended. Costs: a change to
   art that has not been looked at as a 4-frame animation.
2. **Change the animation to 3 frames.** Buys: the game uses what loads today. Costs: a shorter flap, and the fourth
   frames stay unused on disk.
3. **Redraw the fourth frame.** Buys: a known-good set. Costs: art time.

**Recommended: 1** - it is almost certainly a typo and fixes the whole animation with a rename.
