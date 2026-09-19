## spec
`Jawa_Empire_Grunt/Heavy/Specialist` carried no training hediffs (`grep -c Training`
on `JawaFactionRoster.xml` was 0, measured 2026-08-28). Apply the stormtrooper
training line via the SAME mechanism `OuterRim_ImpStormtrooper` uses, reading
that def for the field rather than guessing.

## mechanism, read from workshop 2919248699 (Outer Rim - Galactic Empire)
`Defs/PawnKindDefs/PawnKinds_Stormtroopers.xml` — every trooper kind carries:

    <modExtensions>
      <li Class="TabulaRasa.DefModExt_PawnKindExtended">
        <additionalHediffs>
          <li><hediff>OuterRim_StormtrooperTraining</hediff><severityRange>a~b</severityRange></li>
        </additionalHediffs>
        <randomAdditionalHediff>false</randomAdditionalHediff>
      </li>
    </modExtensions>

`TabulaRasa` is that mod's own internal C# namespace — checked: no separate
"Tabula Rasa" mod exists on this modlist. The class lives inside
`OuterRimGalacticEmpire.dll`. Both `neronix17.outerrim.core` and
`neronix17.outerrim.galacticempire` are active in the live `ModsConfig.xml`, so
it resolves (matches the item's own "Watch out": both mods must be active).

severityRange scales by rank in the source (base trooper 0.1~0.48, specialty
troopers 0.2~0.68, officer 0.3~0.45, commander 0.8~1.0). Mapped onto our three
kinds by role analog:
- `Jawa_Empire_Grunt` (stormtrooper) → base trooper: `0.1~0.48`
- `Jawa_Empire_Heavy` (heavy trooper, `ORHeavyWeapon`) → specialty tier: `0.2~0.68`
- `Jawa_Empire_Specialist` (Imperial officer) → `OuterRim_ImperialOfficer`'s own
  range: `0.3~0.45`

Applied in `src/RimMandrake/Utils/gen_pawnkind_roster.py`'s `KIT` table (per the
generator's own header: "EDIT THE KIT HERE, not in the XML" — an XML-only edit
is reverted by the next regeneration), then regenerated.

## verify
    python3 src/RimMandrake/Utils/gen_pawnkind_roster.py
    git diff --stat src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml
    -> 42 insertions, 0 deletions — exactly the three new modExtensions blocks,
       nothing else moved. Re-running the generator a second time reproduces
       the identical file (idempotent).

    python3 skills/rimworld-modding/scripts/validate_patch.py \
      src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml \
      --defs "<Data>" --defs "<Workshop>" --defs "<Mods>"
    -> OK - 0 errors, 0 warning(s) (582 active mods; Class attribute resolution included)

Live confirmation (a pawn of each kind shows the training hediff in its health
tab) needs a quicktest and is left for `EMPIRE_RAID_QUICKTEST_1`, which this may
piggyback per the item's own note — game was DOWN for this session, not
something to force a load for.

## criteria
- [x] Mechanism copied verbatim from `OuterRim_ImpStormtrooper`, field name
      quoted with source path.
- [x] MayRequire/dependency question answered: no wrapping needed, both owning
      mods are unconditionally active (checked, not assumed).
- [x] Neither the OuterRim FactionDef nor `OuterRim_GalacticEmpire` referenced —
      only the training hediff and its modExtension class.
- [ ] Live health-tab confirmation — deferred to `EMPIRE_RAID_QUICKTEST_1` (needs bridge).
