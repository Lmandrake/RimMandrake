# SUMP_SOLVENT_WAKE_BUILD_1 — pour solvent in the pit: the tar beast wakes at once, manhunter

Caused by `SUMP_BEDAZZLE_SITTING_1` (turn 2). Free tier, the Sump in Baroque Biomes (wherever
`SUMP_FREE_TIER_MOVE_BUILD_1` lands the bulge and the solvents); the god half rides
`mandrake.rm.ninefold`. Design: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §9.

Owner, typed: *"Oh! Throwing solvent into the pit should INSTANTLY wake the beast in Manhunter"*. By
question card 2026-10-02 06:08 PDT: a deliberate **player weapon**, a scorched-earth last resort, not
a rite and not a passive hazard. By card 06:18 PDT: it **serves both the sun god and Zizzik at once**
(a rare shared offering).

## spec

1. **The act.** A float-menu order on a tar bulge (`RUT_BeastBulge`, or its free-tier name after the
   move): "Pour solvent into the tar". A pawn carries the solvent (weak or strong tar solvent, the
   seepwax solvents; a minimum quantity is a Mod Settings number) to the bulge's edge and pours it.
   No ritual, no learning step: anyone who has solvent can do it. A confirmation dialog states the
   consequence plainly ("The tar beast will wake now and hunt everyone on this map.").
2. **The effect.** The bulge wakes **instantly** through its existing wake call (no day of warning:
   the pour is the warning) and the emerged tar beast (`SUMP_TAR_BEAST_BUILD_1`) enters
   `ManhunterPermanent`: it hunts every pawn on the map, colonists included, instead of crawling to the
   densest building cluster. Its trail still lays tar; buildings in its path still go. It sinks back to
   a bulge on the beast item's own timer and building count, or when no target remains.
   ⚠ Ban 2 of the sheet (the beast is never a fightable spawn) bends here by his words: manhunter means
   it attacks. Its health and armour stay as the beast item sets them; killing it is not the design.
3. **Both gods.** On the pour, `GameComponent_Ninefold.ApplyDelta` for `God.Shkaar` and for
   `God.Zizzik`, each sized by the solvent poured (read the sign convention before wiring; sizes are
   Mod Settings numbers), reason "the tar woken by solvent". No hediff, no stat; the Narrator voices
   it.
4. **Readable signs.** The pour (a black-gold splash mote and a hiss); the bulge heaving; a letter
   naming who poured and that the beast is awake and hunting; the beast's manhunter state shown on its
   inspect pane like any manhunter animal. Nothing vanishes.
5. **Mod Settings.** On/off; minimum solvent; whether a strong solvent is required; the two god delta
   sizes; manhunter on/off (off = the beast wakes into its normal station-eater behaviour).
6. One kind of heat: nothing here touches temperature; "sun god" is Sh'kaar the god.

Depends on: `SUMP_TAR_BEAST_BUILD_1` (the beast body and its sink-back), `SUMP_FREE_TIER_MOVE_BUILD_1`
(free-tier defNames of the bulge and the solvents).

## criteria

Deterministic state reads through debug `[Tool]`s, recorded in the Sump's functional script
(`THE_SUMP_FIRST_SCRIPT_1`'s script):
- With a bulge and solvent on a quicktest map, issue the pour job: within the job's end tick the bulge
  is gone, one tar beast pawn is spawned, and its `MentalStateDef` reads `ManhunterPermanent`; the
  solvent stack is consumed by the configured amount.
- Ninefold reads one Sh'kaar delta and one Zizzik delta tagged "the tar woken by solvent".
- No pour option is offered without solvent or with less than the minimum (reason line shown).
- Manhunter toggle off: the same pour spawns the beast in its normal state.
