## the ask (owner, verbatim, 2026-09-17)

"Now you have been regenerating barbslinger as a dome bodied two tailed
scorpion rather than just another grass munching cow. Let's get back to
that. I hated the versions you showed before. Please make a yellowish large
scorpion like creature with two independent tails and a bulbous domed body.
The tail should have an unusually large javelin like needle on each tail.
Generate that art now and make a note that this animal when generated needs
the ability to shoot two venomous missile weapons in battle every few rounds
then close for pincer assault."

This SUPERSEDES the earlier "Keep both" card for Barbslinger (that ruling
answered the top-down question on the OLD grazer art; the redesign replaces
the creature's whole visual identity).

## art — FILED 2026-09-19, do not reuse the earlier renders

Filed 3 fresh artpipe jobs, prompts built from the owner's words above,
south/east/north: `barbslinger_redesign_v1_{south,east,north}`
(`infrastructure/artpipe/pending/`), 512x512 canvas (room for two extended
tails without clipping), transparent background, dest
`Textures/Things/Pawn/Animal/Pyrelands/Barbslinger/Barbslinger_<facing>.png`
(RUT_Barbslinger's existing texPath, `RUT_PyrelandsPortedFauna.xml`).

⛔ **`infrastructure/artpipe/_artsrc/barbslinger_scorpion_v1_{east,north,south}/`
is NOT this redesign's art.** Those three PNGs are dated 2026-09-17 09:59-10:00,
~7 hours BEFORE the owner's correction above landed at 16:47, have no
matching job/manifest in `pending/`/`done/`/`failed/` (i.e. never ran through
the normal queue), and the south-facing one shows no visible tails at all —
consistent with being exactly the "earlier scorpion-concept renders" the
owner says he HATED. Left in place as history, not deleted (not mine to judge
whether they're worth anything), but the owner's own instruction is explicit:
"do not reuse them or their prompts." Do not wire them.

`pyrelands_barbslinger_v1` through `v4` (also in `_artsrc`/`done/`) are the
OLD "grass-munching cow" grazer design the redesign is explicitly replacing —
also not this creature's answer.

**Candidates go to the owner's eye before wiring** (his own instruction on
this item) — once the daemon finishes these three, this needs a look before
`RUT_Barbslinger`'s texPath or drawSize changes.

## mechanics — OWED, researched not built

"Shoot two venomous missile weapons in battle every few rounds, then close
for pincer assault." `RUT_PyrelandsPortedFauna.xml`'s own header already
records that Barbslinger's donor ability (Alpha Animals' `AA_BarbedQuills`,
a ranged quill volley via VEF `CompProperties_InitialAbility`) was DROPPED
during the port, on purpose, to keep this file free of donor-mod comps/classes
— so this is a genuine rebuild, not a revert.

**The vanilla-only mechanism exists and needs no donor framework.** MEASURED
via RimSage against the decompiled engine: `CompProperties_TurretGun` +
a turret-gun `ThingDef` (`<verbs><li><verbClass>Verb_Shoot</verbClass>...`)
is exactly how vanilla gives a PAWN a native ranged attack without a held
weapon item — precedent `Mech_Warqueen`/`Mech_Diabolus`
(`Defs/Biotech/ThingDefs_Races/Races_Mechanoids_SuperHeavy.xml`), each
carrying `Gun_ChargeBlasterTurret` this way. No VEF, no AA, no GeneticRim.

⚠️ **Not a drop-in copy.** `CompProperties_TurretGun` renders a visible
turret-gun sprite via `PawnRenderNode_TurretGun` — fine for a mechanoid
bolting on a gun, wrong for an organic scorpion whose tails ARE the delivery
mechanism and are already part of the body art. Whoever builds this needs
either (a) a turret-gun ThingDef with no visible graphic (verbs-only, comp
handles firing) so the tails in the art do the visual work, or (b) two
separate `CompProperties_TurretGun` instances (one per tail) if the final
art has the tails positioned distinctly enough to warrant two firing points
— decide once the reviewed art is in hand, since tail geometry drives this
choice.

Second half — "then close for pincer assault" — is a targeting-range/AI
question (fire at range, then melee once adjacent), not free from a single
comp; likely needs `verbProperties.minRange`/`range` tuned so the ranged
verb refuses point-blank and the pincer melee tool (already on the def,
presumably `Scratch`/`Bite` re-themed as a pincer capacity) takes over —
confirm against `JobGiver_AIFightEnemy`'s actual range-preference behavior
before assuming this needs no C#.

Venom: this port already carries `RUT_FlamefangBite`-style venom capacities
elsewhere in this file (see Flamefang) as the established pattern for "this
mod's own toxin, not AA's" — the missile weapon's damage/venom should reuse
that idiom rather than inventing a third one.

## needs: owner

2026-09-20: all 3 renders landed (`barbslinger_redesign_v1_{south,east,north}`,
`infrastructure/artpipe/_artsrc/.../*.png`, `facts: PASS` on all three, no
obvious defects on look — two independent tails each with a large needle tip,
bulbous domed body, consistent yellow-gold, no missing limbs). Built a 3-facing
review page: https://claude.ai/artifact/TqEA4oxv57teqaLAczUZ8n. Not wired into
`RUT_Barbslinger`'s texPath yet and the turret-gun mechanics are not built —
both wait on his verdict per this item's own instruction ("candidates go to
the owner's eye before wiring"; tail geometry decides the turret-gun shape).

Def/mechanics work correctly waits on reviewed art (tail geometry decides
the turret-gun shape), not on the owner. Reclaim once
`barbslinger_redesign_v1_*` lands in `infrastructure/artpipe/done/` and has
been shown to the owner.
