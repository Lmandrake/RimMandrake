# ROT_STILL_ALIVE_SWALLOW_1 — Still Alive In There: the hwelgrue swallows the downed, and muffled knocking says who is inside and how long they have

Caused by `ROT_SCORING_SITTING_1` (turn 1, new-marks redo). Free tier, `mandrake.rm.therot`. Design:
`design/Jawa/worldbuilding/biomes/rot_new_marks_redo_2026-10-02.md` O1, review
`design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §8. Ruling: **sound = Still Alive In
There** (decision taken by question card 2026-10-02 10:50 PDT): *swallowed pawns knock from inside the gut*.
Mark 7 (soundscape): the sound does work.

## spec

**Measured in RimSage 2026-10-02 (decompiled 1.6, Anomaly):** `CompDevourer` (`ThingComp, IThingHolder`) holds
**one** thing in a `ThingOwner`; `StartDigesting` despawns the target into it and starts
`JobDefOf.DevourerDigest` (`JobDriver_DevourerDigest`: a `Toils_General.Wait` for the digestion ticks, the
devourer standing still); digestion time is `CompProperties_Devourer.bodySizeDigestTimeCurve` **in seconds**
(0.2 → 10 s, 1 → 60 s, 3.5 → 90 s); it releases the pawn on `Notify_Downed` or `Notify_Killed` (abort, acid
damage from `timeDamageCurve`) or on completion (`completeDigestionDamage` 125 acid); `CompInspectStringExtra`
prints `digestingInspector` with the pawn and seconds left; it calls `AnimationDefOf.DevourerDigesting` and
resets `AbilityDefOf.ConsumeLeap_Devourer` on a failed start. ⇒ **Reuse its shape, not the class as-is:** the
animation and the leap-ability calls are devourer-specific and its private methods cannot be overridden, so
write `RM_CompGutSwallow` modelled on it (same `ThingOwner`, same release-on-downed/killed, same scribing), with
the differences below. 🔴 Do not attach `CompDevourer` to the hwelgrue directly.

1. **Targets: only the already downed.** The hwelgrue's graze branch (`ROT_HWELGRUE_GIANT_BUILD_1`) takes a
   downed pawn (any faction, humanlike or animal) lying in the open within reach before any item. One at a
   time; a second downed pawn waits.
2. **Digestion is slow enough to rescue:** default **one in-game day for a body size 1** (60,000 ticks), scaled
   by body size, a Mod Settings curve. The swallowed pawn takes small acid damage on a schedule (the vanilla
   `timeDamageCurve` shape, stretched) and dies at the end if not freed; corpse and gear go into the digest
   owner (so the metal comes back as a casting).
3. **Cut them out.** Released alive (stunned, Sheen-coated: add `RM_SheenCoating`) when the hwelgrue is downed
   or killed (vanilla devourer behaviour), **or** when it takes a cumulative **150** damage (setting) to its
   torso/body parts since swallowing: a giant is hard to down, so a hard focused attack on the belly opens it.
   The release pawn takes the acid damage the time inside earned.
4. **The sound (the mark).** While anything alive is inside: a sustained positional `SoundDef
   RM_GutKnocking` on the hwelgrue: muffled knocking and a voice through the hide, **louder and faster early,
   fainter and slower as time runs out** (volume and rate driven by remaining fraction; three sub-sounds:
   strong, weak, failing). An animal inside makes scrabbling instead of a voice. Silence when the inside is
   dead.
5. **Who and how long:** the inspect string names the pawn and the time left in hours (*"Something is still
   alive in there: Mara, about 9 hours."*); a letter when a colonist or colony animal is swallowed (*"Mara was
   swallowed by the hwelgrue."*), a message when the knocking stops.
6. **Strangers:** if no downed pawn exists when a hwelgrue is generated on a map, a chance (setting, default
   0.15) that it already holds one: a trader's pack animal still wearing its packs, or a wounded wanderer
   (vanilla pawn kinds), with a few hours left.
7. **Mod Settings** (Giant section): on/off; digestion curve; belly-cut threshold; stranger chance; loudness.

Depends on: `ROT_HWELGRUE_GIANT_BUILD_1`. Art: none (sound only). Sounds: authored or sourced audio for the
three knocking stages and scrabbling (no artpipe; list the source files in the item close).

## criteria

Deterministic, in `THE_ROT_FIRST_SCRIPT_1`'s `validation.py`, through debug `[Tool]`s:
- `SoundDef/RM_GutKnocking` resolves; `RM_Hwelgrue` carries `RM_CompGutSwallow` and **not** `CompDevourer`.
- Downed colonist 5 cells from a hwelgrue, nothing else edible: within 5,000 ticks the colonist is not spawned
  and the comp's held pawn is that colonist; an undowned colonist beside it is never taken.
- Inspect string while held contains the pawn's name and a number of hours; it is null when empty.
- Rescue: dealing 150 damage to the hwelgrue after a swallow respawns the colonist alive on the map within 2
  ticks of the threshold; killing it does the same.
- Timeout: advancing the full digestion time leaves the colonist dead and their gear in the digest owner.
- Sustainer: while a living pawn is held, the hwelgrue has an active `RM_GutKnocking` sustainer whose volume
  at 80% time left is higher than at 20% (read from the sustainer state); none while empty or after death.
- Toggle off: a downed colonist beside the hwelgrue is never swallowed over 30,000 ticks.
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">head -1 /home/mandrake/rm/bench/infrastructure/state/items/ROT_STILL_ALIVE_SWALLOW_1.md