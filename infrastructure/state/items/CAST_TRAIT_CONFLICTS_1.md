## spec
🔴 **14 of the 269 authored characters carry a pair of traits RimWorld declares
mutually exclusive.** Not a style note — `TraitDef.ConflictsWith` says these
cannot coexist, and no vanilla pawn generation could ever produce them.

| defName | who | the pair |
|---|---|---|
| `Inhabited_Empire_SchoolmistressPerrinAleth` | Schoolmistress Perrin Aleth | `Abrasive` + `Kind` |
| `Inhabited_Empire_ComptrollerIshOndoVell` | Comptroller Ish Ondo Vell | `Jealous` + `Ascetic` |
| `Inhabited_Geonosian_RrekkTheReturned` | Rrekk the Returned | `Brawler` + `ShootingAccuracy` |
| `Inhabited_Geonosian_AttendantQuRaa` | Attendant Qu'raa | `Ascetic` + `Jealous` |
| `Inhabited_Helix_PrithVane` | Prith Vane | `Psychopath` + `Kind` |
| `Inhabited_Homestead_BessaTrull` | Bessa Trull | `Abrasive` + `Kind` |
| `Inhabited_Homestead_RenAshek` | Ren Ashek | `Psychopath` + `Kind` |
| `Inhabited_Jawa_OssikTheOutrider` | Ossik the Outrider | `Brawler` + `ShootingAccuracy` |
| `Inhabited_Junkers_AtaiVosk` | Atai Vosk | `Jealous` + `Ascetic` |
| `Inhabited_Tusken_HarraGhul` | Harra Ghul | `Ascetic` + `Jealous` |
| `Inhabited_Tusken_OrrGash` | Orr'gash | `Kind` + `Abrasive` |
| `Inhabited_Tusken_ShaaNel` | Shaa Nel | `Ascetic` + `Jealous` |
| `Inhabited_Tusken_EssKan` | Ess'kan | `Kind` + `Abrasive` |
| `Inhabited_Wildsteam_NikkoTheSapNamer` | Nikko the Sap-Namer | `Kind` + `Abrasive` |

Only four pairs are involved, so this is four decisions and not fourteen:
`Kind`↔`Abrasive` · `Kind`↔`Psychopath` · `Ascetic`↔`Jealous` ·
`Brawler`↔`ShootingAccuracy`.
🔑 **Read each one's HOOK before choosing** — the project's own rule is that the
hook and the traits must agree, and *"a hook the mechanics do not back is a lie
the player will catch."* In most of these the hook plainly favours one side; e.g.
a schoolmistress written as sharp-tongued-but-decent is `Kind` if the warmth is
the point and `Abrasive` if the sting is.
⚠️ **`Ascetic` + `Jealous` is four of the fourteen and looks like a house habit
rather than four separate slips.** Both read as "wants nothing / resents what
others have", so a writer reaches for the pair naturally. Worth a note in the
cast-file format section, not just fourteen edits.
⛔ **BUILD is not choosing.** Picking a winner is authoring, and the trait is
half the characterisation.
FIX: edit the `traits:` line in `design/Jawa/bridge/INHABITED_CAST_*.md`, then
`python3 src/RimMandrake/Utils/cast_to_xml.py --write`.

## verify
after the edit, `cast_to_xml.py` still reports 269 and every trait resolving, and
BUILD's conflict audit returns 0.

## criteria
no `Config error in Inhabited_` naming an IMPOSSIBLE PAIR at the next load.

## notes
**from:** BUILD, 2026-08-20, found while the game was live. Offline check, two sources.

**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready — for DECIDE

⚠️ **HOW THIS SURVIVED THE FIRST LOAD, and why nobody saw it.** RimWorld enforces
none of it: `TraitSet.GainTrait` checks no conflicts and imposes no trait cap, so
these 14 loaded with zero errors and would have produced pawns silently. It was
found only because the `rimbridge` skill's silent-failure catalogue names
`GainTrait` explicitly. **The code no longer permits it:** `CharacterDef.
ConfigErrors` now names any conflicting pair at load, and `CharacterApplier`
refuses the second trait rather than building an impossible pawn. So the 14 are
now LOUD but still WRONG — the code stopped the damage, it did not do the edit.
