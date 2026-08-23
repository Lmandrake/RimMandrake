
## spec
DECIDE ruled 2026-08-23 (`JAWA_FARMING_BAN_OR_PENALTY_1`): **the Jawa may not SOW. They keep
harvesting, plant cutting and tree chopping.** A −8 aptitude says *"bad at this"*; the design
needs *"does not do this"*.

⛔ **NOT a `PlantWork` work-tag ban**, and not a second gene mirroring
`RimMandrake_Jawa_MiningDisabled`. `Growing` and `PlantCutting` both carry the `PlantWork` tag,
so a tag-level ban removes harvest, cut and chop as well — which the play test explicitly wants
kept.

✅ **The narrow mechanism, read from source, not assumed:**

| fact | source |
|---|---|
| `WorkGiver.ShouldSkip(Pawn pawn, bool forced = false)` is `virtual` and takes the pawn | `RimWorld/WorkGiver.cs:10-13` |
| `WorkGiver_GrowerSow` is its own class | `RimWorld/WorkGiver_GrowerSow.cs:7` |
| it derives from `WorkGiver_Grower`, so ⭐ **one hook covers BOTH the growing zone and the hydroponics basin** | same file |
| the job it hands out is `JobDefOf.Sow` | `WorkGiver_GrowerSow.cs:209` |

⇒ A Harmony postfix on `WorkGiver_GrowerSow.ShouldSkip` returning `true` when the pawn's
xenotype is the Jawa one. ⚠️ **Key it on the PAWN, never on the colony** — a non-Jawa colonist
must still be able to farm. That is deliberate: it makes recruiting an outsider valuable.

⚠️ **A Jawa can still CREATE a growing zone; nobody will sow it.** Accepted trade, on the
ruling — the alternative is the blunt tag ban. The designator is a separate, narrower question.

## verify
On a live pawn, both halves, against a Baseliner control:
1. A Jawa colonist **will not sow** a growing zone or a hydroponics basin; a Baseliner will.
2. The same Jawa **still harvests, still cuts plants, still chops trees.**
🔴 **Both halves or it is not done** — the failure mode of this item is a fix that also kills
harvesting, which is exactly what the rejected mechanism would have done.
⚠️ `Plants disabled` must still read **False** on the Jawa. If it reads True, a work TAG was
disabled and the wrong instrument was used.

## criteria
- [ ] Jawa cannot sow — zone and hydroponics both.
- [ ] Jawa can still harvest, cut and chop, demonstrated on a live pawn.
- [ ] A non-Jawa colonist in the same colony CAN sow.

## Watch out
⚠️ **The game must be DOWN to deploy an assembly** — the OS locks a loaded DLL. See
`rimbridge-companion`.
⚠️ **A Harmony patch mod must sit after `brrainz.harmony` in `ModsConfig.xml`** or the postfix
never binds, and a postfix that never binds looks exactly like a Jawa who can farm.
⭐ **The world was built to afford this.** `BIOME_FLORA_ROSTERS_1` seeded healroot, tinctoria,
cotton, psychoid, smokeleaf, devilstrand, haygrass and the Star Wars food crops as WILD flora,
so medicine, cloth, dye and food are all gatherable. ⛔ If someone later strips the wild
player-crops out of the biome rosters, this ban becomes cruel — the two are one design.
