# ROT_UNJOINING_RITE_1 — The Unjoining, for Ta'Baa: a symbiont-joined colonist held through a hard purge until the symbiont dies, just before the clan leaves

Caused by `ROT_SCORING_SITTING_1` (turn 1). Campaign tier, `mandrake.rut.rites` (`src/RimUtinni/Rites/`,
found rite). Design: `design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §6 R2, §8. Register:
`design/Jawa/salvation_rites_2026-10-01.md` B13 (row added) and §(d) for the found-rite machinery.

Ruling: **rite = The Unjoining** (flight god), decision taken by question card 2026-10-02 10:20 PDT: *a
symbiont-joined colonist purged until it dies, before the clan leaves*. **God: Ta'Baa** (*"the Unrooted —
flight, the refusal to root"*, `design/Jawa/divine_satiation_engine.md` ⑥; confirmed). Ta'Baa's found rites:
the Returned (B7, ruled-kept), the Shadow Walk (B7, pitched), the Vindication Walk (B7, pitched), and this:
**four, one under the cap of five.**

## spec

**God: Ta'Baa.** Kind: feeding. Calls `GameComponent_Ninefold.ApplyDelta(TaBaa, <amount>, "The Unjoining")`,
the call shape of `SUMP_SINKING_RITE_BUILD_1`.

1. **Found / learned.** Inscription `RUT_UnjoiningVessel`: on a Wildsteam pilgrim path in the Rot, an empty
   brewing vessel overturned at a grove's edge, a rag stiff with dried Sheen, and footprints that stop shining
   halfway down the path. Placed on `RM_TheRot` maps by a map GenStep with a chance (never worldgen; the
   `RUT_FelledNoonStump` shape). Studying it → the Rites tab's found-rites row → `RUT_ResearchMod_GrantRite`
   adds the precept, per §(d). Performable after on any map.
2. **Target.** A `RitualObligationTargetFilter` over the colony's own humanlike pawns carrying any Rot
   symbiont hediff (`RM_Sym_Quickflesh`, `RM_Sym_Nightwake`, `RM_Sym_Sheenblood`, `RM_Sym_Mycoid`).
3. **The rite.** Participants gather and **hold** the joined colonist (the patient lies at the focus, the others
   stand around) through a long ritual; at the end the patient's symbionts are removed, `RM_SymbiontHusk` drops,
   and `RM_UnjoiningPurge` (from `ROT_UNJOINING_DRAUGHT_1`, the same purge) is applied. The benefit is gone for
   good (Sheen immunity, fast healing, no sleep: whatever the symbiont gave).
4. **Before the clan leaves.** The rite records its tick. On the next gravship launch
   (`src/RimMandrake/Ninefold/Source/Patch_GravshipLaunched.cs`, existing): if within **7 days** (setting) of the
   rite, Ta'Baa's delta is applied (pleased) and the participants' memory is the good one. If no launch
   happens within **15 days** (one season; setting), the participants' memories are replaced by a soured one
   (*"We cut it out of her and stayed anyway."*) and Ta'Baa gets nothing. More participants: a stronger memory
   and a larger delta (scaled by count).
5. **Outcomes: cohesion only.** Shared memories by quality; Ta'Baa's favour told by the Narrator and shown only
   as his Exalted odds (*"better landing sites, travel opportunities, a sense of momentum"*). Never a buff,
   hediff or stat on anyone except the purge itself.
6. **The draught.** The first completed Unjoining finishes `ResearchProjectDef RM_UnjoiningDraught`
   (`ROT_UNJOINING_DRAUGHT_1` part 3): the doctor learned how it was done.
7. **Readable signs:** the patient held at the focus; the purge; the husk; the letter; the soured memory if the
   clan stays.
8. **Mod Settings:** on/off; departure window; sour window; inscription chance.

Collision check (review §6 R2): the launch-rite is a launch; the Returned seals a body aboard; the Shadow and
Vindication Walks are walks; the Left Behind devotion leaves working things. None gives up a benefit rooted in a
colonist's own body.

Depends on: `SALVATION_RITES_UNIFICATION_1` (found-rite machinery), `ROT_UNJOINING_DRAUGHT_1` (purge hediff,
husk, research). Art: `RUT_UnjoiningVessel` in `infrastructure/artpipe/art_lists/rot_turn1_2026-10-02.csv`.

## criteria

Deterministic, in `src/RimUtinni/Rites/validation.py`, through `jawa/get_defs` and debug `[Tool]`s:
- Defs resolve: the rite's `PreceptDef` and `RitualPatternDef`, `ThingDef/RUT_UnjoiningVessel`, the GenStep,
  the good and soured `ThoughtDef`s.
- Target filter: a colonist with `RM_Sym_Mycoid` is a valid target; one without any symbiont is refused with a
  reason; a guest with a symbiont is refused.
- Completing the rite on a target removes every `RM_Sym_*` hediff, adds `RM_UnjoiningPurge`, drops one
  `RM_SymbiontHusk` per symbiont removed, and sets `RM_UnjoiningDraught` research finished.
- Launch within the window: Ninefold logs exactly one delta tagged "The Unjoining" for Ta'Baa, positive.
  No launch for the sour window: no Ta'Baa delta, and every participant holds the soured thought.
- No hediff or stat buff is added to any participant.
- Each Mod Settings toggle off removes exactly its effect.
</content>
</invoke>
