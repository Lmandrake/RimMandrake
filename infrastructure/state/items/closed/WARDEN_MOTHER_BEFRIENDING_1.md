# WARDEN_MOTHER_BEFRIENDING_1 — the giant who cannot reach her own young

**the Miasma**

🔑 **The design IS `design/Jawa/worldbuilding/biomes/miasma_fauna_roster_2026-09-23.md` §6 — read
it, do not re-derive it from here.** Sheet: `the_miasma.md` §4 (amended by this ruling, in place).

⚠️ **Provenance note.** This is the owner's ruling, given by him in conversation on 2026-09-23 and
quoted in §6 of the roster. It is **not** stamped with the owner-authorization flag on the ledger:
the forgery guard refused the quote (his sentence contains an apostrophe and parenthesised text,
and the transcript check did not match it), so per that guard's own prescribed exit the item is
filed under BENCH's seat with the attribution recorded here in prose instead. ⛔ Do not re-quote it
into that flag to "fix" this — the guard erring toward refusal is the safe direction.

## why this exists

The owner asked for the Miasma to be brought up to its siblings' standard. The gap identified: the
Fever Wood has the Sekkulaath, the Greentide has trunks you mine through, the Slime has its
reactor — **the Miasma had weather and a mood.** Its best ideas (the Working, fever-forging, the
pilgrimage) were all atmosphere with no object attached. Of five proposals he chose this one, *"only,
all the way"*, and then specified it well past what was pitched.

🔴 **And the creature it is about does not exist.** `RUT_WardenMother` appears only as an **XML
example inside a C# comment** in `RM_CompTerritorialAnchor.cs`. Two documents asserted it shipped;
both are corrected. ⇒ Also note the `RUT_` prefix in that comment is **wrong**: she is invented,
not canon, so under Q11a and `SEA_BEASTS_TIER_RULING_1` she is **`RM_WardenMother`** and belongs in
the franchise-free mod.

## spec

🔑 **The whole mechanism is the waterline.** She goes anywhere the water goes and nowhere else. A
receding surge strands one of her young in a pool the water has left; she can hear it and see it and
will never cross the few metres of dry ground between. A colony can. **That is the friendship.**

1. **`RM_WardenMother` ThingDef + PawnKindDef** — enormous, aquatic, lethal within reach. Nothing
   exists in any form today.
2. 🔴 **A water-only movement constraint.** The one genuinely new mechanism. ⛔ Nothing in this repo
   does it: `RM_JobGiver_ReturnToWater` gets a stranded animal *back* to water,
   `RM_LurkingWaterExtension` marks pool terrain, `RM_ScattererValidator_BrineShallowWater`
   validates placement. None forbids *leaving* water.
3. **The crèche is the anchor, in the shallows.** ✅ `RM_CompTerritorialAnchor.SetAnchor()` takes
   any `Thing`, and `RM_ScattererValidator_BrineShallowWater` already validates shallow-water
   placement. Her `anchorRadius` is her reach.
4. **The young's call** — a locatable, persistent audible cue a player learns to recognise.
5. **Spawn linkage:** when she spawns, **sometimes** stranded young spawn with her. 🔑 This is
   load-bearing, not flavour — without it the whole relationship waits on an irregular storm-driven
   surge that hard ban 4 forbids making predictable, and a colony could play a full game and never
   be offered it.
6. **A tolerance state** — per-colony, Scribed through save/load, and **visible**: she must
   observably stop treating you as prey.
7. **Tolerance is a predicate on an existing target test, not a new AI.** ✅
   `RM_JobGiver_AnchorDefense` already fights *anything hostile-or-harvesting inside the radius*;
   being tolerated means being removed from that set. Nothing more.

## verify

- A quicktest on a **scratch** world tiled to the Miasma: she must lumber along the channels, and
  must **never** be found standing on dry ground.
- Strand a young behind a dried margin: she must approach, stop at the waterline, and stay.
- Free it; confirm tolerance is granted, is visible, and **survives a save/load**.
- Then harvest something inside her reach and confirm she attacks anyway.
- Zero new Config errors in `Player.log` — 🔴 grep the log, `validate_patch.py` cannot see them.

## criteria

The Miasma has a centrepiece a player remembers: a giant who is never tamed, whose protection is
bought by where you choose to build, and whose friendship is earned by doing the one thing she
physically cannot.

## Watch out

- 🔴 **THE TRAP, and `RM_AnchorGuard.xml`'s own comment already names it:** assigning that DutyDef
  requires the pawn's ThinkTreeDef to actually consult `mindState.duty` — **vanilla's plain Animal
  tree does NOT; only insect-shaped trees do.** ⇒ A warden mother on a plain Animal tree will
  **silently ignore the duty**, wander off, defend nothing, and read as correctly configured. That
  comment explicitly hands this decision to the roster pass, i.e. to this item.
- ⚠️ **`RM_EnvironmentalHazards.csproj` sets `EnableDefaultCompileItems false` and lists every
  file.** The new water-constraint `.cs` needs a `<Compile Include>` line or it compiles into
  nothing, with no error. Always a two-file change.
- 🔴 **Three things are UNMEASURABLE on the Mac** — ⛔ do not reason them out from a doc: whether a
  pawn's pathing can be constrained to a terrain set at all; whether a `bodySize` that large paths
  through shallow water without breaking; whether the duty seam behaves on a non-insect tree.
- 🔴 **She is never tamed.** ⛔ No commanding, feeding on demand, moving, bonding, hauling, healing,
  riding, or safe crowding. Tolerance is *only* removal from her target set.
- ⛔ **No second giant.** The eviction of `AA_OvergrownColossus` is reasoned as *"the giant lane
  here is owned by warden mothers… a random giant dilutes them"*, and that holds harder now.
- 🔴 **She dies of age, and the young inherit her — ruled 2026-09-23, design in §6a of the
  roster.** Three things this adds to the spec, all owed:
  - **the young are trainable and SELF-TAME** while your record against their crèche is clean —
    barred or reset the moment you harvest, kill or butcher one. ⛔ Not a taming grind: they
    consent, exactly as the mother's tolerance and the Fever Wood guild do.
  - **trainability must be WATER-SCOPED** — Guard, Release, and ⭐ Haul-from-water-only, which
    lands them on `RM_Thrannock`'s flotsam root-lines, an economy the sheet already has. ⛔ Not
    Rescue and not general Haul: both need land, and an animal that fails its own trained job is a
    bug wearing a feature.
  - ⭐ **succession is the payoff, and the successor is still a CHILD.** ⛔ The "raise it into a
    leviathan" version is **CUT** — owner, 2026-09-23: *"the game isn't that long to watch it
    grow."* ⇒ ⛔ Nothing may depend on a maturation arc, there is no "it leaves for the sea", and
    ⛔ the note about meeting the grown adult later is **withdrawn**. What inherits the crèche is a
    tamed juvenile a fraction of her size, which needs **no growth simulation** (the same anchor
    comp on a smaller creature) and is what the sheet already describes — *"the sea's memory dying
    in its lifeboat."* The gift is continuity, not a replacement. ⛔ Still not guaranteed.
- 🔴 **Foreshadowing her age is a REQUIREMENT and subtlety is failure.** Visibly ancient in the art
  brief (⛔ not merely large), an inspect string that says it outright, a measurable slowing as she
  ages, and somebody who tells you — the Deepwater vigil measure the brine yearly and would know
  how long she has. ⛔ **A player surprised by her death means this was built wrong**, however good
  the rest is.
- 🔴 **Do NOT solve the ache.** A tamed young follows you along the water, stops at the waterline,
  and watches you walk inland. ⛔ No land-walking upgrade, no tank, no carrying it about. The
  affection is real and the geography does not care — that inversion of the mother's own tragedy is
  the content, not a defect.
- ⭐ **CANALS are in scope and they change her category — ruled 2026-09-23, design in §6b of the
  roster.** Because she goes where water goes and a canal is water a colonist put there, her reach
  becomes **player-authored**: you can canal her inland and buy her protection with labour instead
  of location. 🔴 **And you can strand HER** — a canal that silts, is cut, or is redrawn by a surge
  leaves the giant who cannot leave water sitting in a dry ditch, needing you, by your own doing.
  ⚠️ Designed against **`mandrake.rm.flowworks`**, which is ours; **no mod named "Earth Flow" is in
  the 2026-09-19 snapshot of 621 active mods**, and the live list is unreachable from the Mac, so
  if a third-party canal mod is intended its behaviour must be measured on the Desktop first.
  🔴 **THE SWIM RULE, ruled 2026-09-23 — and the mechanism is already built.** He ruled a canal must
  let her swim *"as long as it connects to the sea"*, and **connection, not wetness, is the gate** —
  which is exactly the model `RM_MapComponent_StrandingPools` has implemented since 2026-09-14: a
  full 4-way flood-fill of water cells into connected components, largest treated as the main
  network, `IsReconnected()` testing whether a pool rejoins open water, and cell-by-cell decay for
  the ones that do not. ⇒ **Swim-eligibility is that same predicate.** ⛔ Do not write a second
  connectivity system, and note it unifies both halves of the design: *a stranded young is simply a
  young in water that lost its connection.*
  ⚠️ **One real gap his wording exposes:** the built check uses *"reaches the map edge"* as its proxy
  and its own header is honest about it — but on a Miasma map the **fresh** end touches the edge too,
  because rivers do. So a canal to a river mouth would read as connected to the sea and let a
  brine-broken sea elder swim inland up fresh water. ✅ Fix needs no new machinery:
  `RM_GradientAxisExtension` already knows which direction is brine, so the test becomes *"reaches
  the **seaward** edge."* A refinement of an existing method, not a new system.
  🔴 **Gating engine question, UNMEASURABLE on the Mac:** do FlowWorks' canal cells register as
  water-band cells in that flood-fill? If not, canals are invisible to every mechanism here and the
  whole section is fiction.
  ⭐ **And the reversal is sharper than first written:** a cut canal leaves her not in a dry ditch but
  in **a pond** — still swimming, unable to reach the sea, with the existing decay code shrinking it
  around her. **The mother suffers her children's fate, by the player's doing.**
  ⛔ A canal is water, never a bridge. Do not let one carry her onto dry land; the constraint is the
  content.
- 🔴 **Corrected on his word 2026-09-23: there are no nautical ships in this world.** The sheet's
  *"its mother is the reason ships sink"* was a dead metaphor, amended in `the_miasma.md` §4 to
  *"why nobody goes out onto the open water."* ⚠️ `design/Jawa/campaign/CAMPAIGN_ARC_GATHER.md` G34
  still quotes the old phrasing and is stale — ⛔ do not propagate it further.
- ⚠️ **Depends on the stranded**, which per the same sitting are a *condition* on nursery juveniles
  rather than their own species (`MIASMA_FAUNA_FLOOR_ROSTER_1` §3) — and the free tier's nursery
  depends on `SEA_BEASTS_TIER_RULING_1` landing. Sequence after both.
- 🧊 **This ruling AMENDED the frozen sheet in two places, edited in place** (`the_miasma.md` §4):
  *"stationary"* → lumbering within the water, and *"Placed set-pieces, never random spawns"* → she
  spawns, sometimes with young. Her **crèche** remains a placed, mapped, named site. ⛔ Nothing else
  in §4 moved.
