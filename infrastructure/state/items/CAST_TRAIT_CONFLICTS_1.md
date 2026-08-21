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

## ruling
**DECIDE, 2026-08-21. All 14 resolved off the hook, as the item asked. Audit: 269 trait
lines scanned, 0 conflicting pairs.**

⛔ **Do not "restore" a dropped trait.** Each one below was decided against the character's
own blockquote, and the reasoning is recorded so it is not relitigated.

| character | now | dropped | why the survivor is the character |
|---|---|---|---|
| Schoolmistress Perrin Aleth | `TooSmart, Abrasive` | `Kind` | *"corrected his grammar in front of his own men"* · *"the moral authority of Ashgarrison and is not entirely wrong, which is the unbearable part."* The unbearableness IS the joke |
| Comptroller Ish Ondo Vell | `TooSmart, Jealous` | `Ascetic` | *"has personally buried two other exemption applications."* Textbook jealousy; the framed exemption on the wall is status, not restraint |
| Rrekk the Returned | `Brawler, Masochist` | `ShootingAccuracy(Trigger-happy)` | *"starts fights he has no interest in winning and thanks you afterward"* — brawler and masochist say the whole man |
| Attendant Qu'raa | `GreatMemory, Jealous` | `Ascetic` | *"two rival attendants reassigned to the smelt floor on paperwork she personally filed."* Her paleness is twenty years underground, not doctrine |
| Prith Vane | `Psychopath, TooSmart` | `Kind` | ⭐ *"the people she discontinues thank her on the way out"* is **performed** warmth, and psychopath-plus-performance is the better character. Same idea as Ren Ashek's card |
| Bessa Trull | `Ascetic, Kind` | `Abrasive` | *"the most generous person in this town toward anybody except herself"* — and she answers criticism with *"thank you for your concern"*. Nothing in her brief is abrasive |
| Ren Ashek | `Psychopath, GreatMemory` | `Kind` | *"She feels nothing, and has said so plainly at a gathering, to four hundred people."* She says it herself |
| Ossik the Outrider | `Brawler, NaturalMood(Pessimist)` | `ShootingAccuracy(TriggerHappy)` | a scout who *"greets kin by biting the air beside their shoulder"*. Nothing in the brief is about shooting |
| Atai Vosk | `Jealous, AnnoyingVoice` | `Ascetic` | *"cannot bear anyone else running her errands and will elbow a child out of the way to do it"* |
| Harra Ghul | `Ascetic, Abrasive, GreatMemory` | `Jealous` → **`Abrasive`** | ⭐ the only SUBSTITUTION, not a drop. *"takes her ration from the common cup at the back of the line"* is `Ascetic`; *"driven off three apprentices in nine years… raised the interest without consulting a soul"* is `Abrasive`, not `Jealous` — she guards an office, not possessions |
| Orr'gash | `Kind, GreatMemory` | `Abrasive` | *"will not go in on a farm with children on it. He has aborted two raids over it, in front of everyone, and said why."* Eleven silent years is not abrasiveness |
| Shaa Nel | `ShootingAccuracy(CarefulShooter), Ascetic` | `Jealous` | *"what recovers nothing is waste, and waste is the sin"* — the asceticism is her doctrine. Wanting a kill is desire, not envy |
| Ess'kan | `Kind, Brawler` | `Abrasive` | *"He cannot put down a person who is standing still; the arm simply does not go."* `Brawler` even backs the arm |
| Nikko the Sap-Namer | `GreatMemory, Kind` | `Abrasive` | *"will walk you round and introduce you personally for as long as you fail to escape"* is comic tenacity, and she is fifteen |

🔑 **Thirteen are drops, not swaps.** Two traits is an ordinary pawn; adding a third to fill
the hole would be inventing characterisation the brief does not have.

✅ **The house-habit note the item asked for is written** — `INHABITED_DESIGN.md` **§5.7b**,
in the format section where an author writing the next `traits:` line will hit it, with all
four forbidden pairs and why `Ascetic`+`Jealous` and `Kind`+`Psychopath` are the two our
voice reaches for.

⇒ BUILD regenerates `src/Jawa/Inhabited/Defs/CastRosters/` from the prose with
`cast_to_xml.py`; the XML is derived and must not be hand-edited.
