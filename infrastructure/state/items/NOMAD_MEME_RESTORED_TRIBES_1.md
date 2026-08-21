## spec
🔴 **OWNER, 2026-08-21: "But I like VME_Nomad!"** That reverses his 2026-08-20 drop. His
preference is the ruling; what follows is only about executing it where it is safe.

⭐ **On an NPC faction it costs nothing, and that is measured, not assumed.** The whole case
against `VME_Nomad` was its forced precept `VME_PermanentBases_Despised` and its escalation
to −50 mood at 60 days in place. That precept carries:

```
/mnt/c/.../workshop/content/294100/2636329500/1.6/Defs/PreceptDefs/Precepts_PermanentBases.xml:19
    <enabledForNPCFactions>false</enabledForNPCFactions>
```

⇒ **it never fires for an NPC faction.** `Jawa_IndigenousTribes` is NPC-generated, so on this
FactionDef `VME_Nomad` reduces to what the owner actually likes about it: the *Nomadism*
symbol pack, the name and description generation, `VME_Travel_Desired`, `VME_Ranching_Nomadic`
(TameAnimalChance ×1.25, TrainAnimalChance ×1.25) and auto-granted `RoughLiving_Welcomed`.
**Zero mood risk. Restore it.**

**Do:** in `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml`, restore
`<li MayRequire="vanillaexpanded.vmemese">VME_Nomad</li>` to `forcedMemes`, beside the four
that are there. ⛔ **Replace the 2026-08-20 removal comment at ~line 109 rather than leaving
it** — a comment that argues against the line directly beneath it is how the next reader gets
this wrong again. Replace it with the reversal and the `enabledForNPCFactions` reason.
⚠️ Also correct the header comment at ~line 29 ("carried here ONLY because the owner's
approved file carries it… measured as hazardous"): the hazard is player-side only.

⚠️ **Meme budget.** `APPROVED.md` records the def at **impact 7 over 4 memes** after the drop.
`VME_Nomad` is impact **3**, so this returns it to **10 over 5**. Confirm that is legal before
committing — `validate_ideoligion.py` is the instrument and it must pass.
⚠️ `llunak.moreprecepts` is active and its `NomadPatch.xml` relabels the meme **"wanderlust"**.
Expect that string, not "Nomadism", anywhere it is read back.

⛔ **Do NOT touch `The Salvation.rid` in this item.** The player side is a different risk and
is held under `DEPLOY_SALVATION_RID_1` pending a measurement.

## verify
- `python3 skills/rimworld-ideoligion/scripts/validate_ideoligion.py --xml` → 1/1 VALID, and
  it reports **5 memes**. ⚠️ Pass `--mods-config` if a minimal list is live, or every modded
  meme reads INVALID.
- `grep -c 'VME_Nomad' src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml` counts the live
  `<li>`, not just comments — read the hits, do not trust the count.
- `deploy_custom_mods.py --mod Jawa_Patches` plan is clean, then `--apply`. Writing the repo
  file is not deploying it.

## criteria
CHECK, next load: a `Jawa_IndigenousTribes` settlement's ideoligion lists five memes including
*wanderlust*/*Nomadism*, and **no** pawn there carries a `VME_PermanentBases_Despised` thought.
