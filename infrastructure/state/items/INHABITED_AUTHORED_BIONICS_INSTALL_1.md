# INHABITED_AUTHORED_BIONICS_INSTALL_1

Split out of `INHABITED_ROSTER_LIFECYCLE_SWEEP_1` finding 6 (2026-09-02).
`CharacterDef.items` mixes carried goods with bionics and the prose does not
distinguish; `CharacterApplier` split them on `ThingDef.isTechHediff` and
applied the CARRIED half only. This is the skipped half.

Filed thin, with no `## spec` — the sections below are FOUNDRY's own scoping,
per the charter's "specs state outcomes; implement a better route freely and
record what you assumed."

## spec

Install the `isTechHediff` entries of `CharacterDef.items` onto the authored
pawn's body, at the moment `CharacterApplier.ApplyTo` materialises them.

⭐ **The route is vanilla's own, copied rather than invented.**
`PawnTechHediffsGenerator.InstallPart`
(`Source/RimWorld/PawnTechHediffsGenerator.cs:52-72`) is how the engine puts a
bionic into a pawn with no surgeon, no operating table, no bleeding and no
recovery — which is exactly an authored character being materialised off-map
into a roster. It is the closest existing precedent and there was no reason to
write a second one. The chain it uses, and that we use:

| step | what actually does it |
|---|---|
| ThingDef → RecipeDef | `pawn.def.AllRecipes` filtered by `RecipeDef.IsIngredient(partDef)` |
| RecipeDef → BodyPartRecord | `recipe.Worker.GetPartsToApplyOn(pawn, recipe)` |
| install | `recipe.Worker.ApplyOnPawn(pawn, part, billDoer: null, NoIngredients, bill: null)` |

Decisions taken, and why:

1. **`pawn.def.AllRecipes`, not `DefDatabase<RecipeDef>.AllDefs`.** `AllRecipes`
   (`Source/Verse/ThingDef.cs:545-569`) is the ThingDef's own `recipes` plus
   every RecipeDef whose `recipeUsers` names it, so a recipe that cannot be
   performed on this race is never a candidate. `InstallBionicArm`'s
   `recipeUsers` is `<li>Human</li>` — that single line is what makes a droid
   or a modded chassis fall through to the warning instead of getting a
   human arm.
2. **No reverse-index is built and none is needed.** There is no engine-provided
   ThingDef→RecipeDef map; vanilla scans, and the scan here is over one race's
   recipe list (tens of entries), run at most a handful of times per world.
   Building and caching an index would be more code guarding a cost nobody pays.
3. **`addsHediff != null` is ADDED to vanilla's filter.** `IsIngredient`
   (`Source/Verse/RecipeDef.cs:458-468`) is a pure ingredient-filter test and
   would match a recipe that removes or replaces rather than installs;
   `Recipe_InstallArtificialBodyPart.ApplyOnPawn` then dereferences
   `recipe.addsHediff.hediffClass` unconditionally. Vanilla gets away without
   the guard because its candidate set comes from a random roll over parts it
   already knows are installable.
4. **"Already occupied" is the ENGINE's call, not a bespoke test.**
   `Recipe_InstallArtificialBodyPart.GetPartsToApplyOn` and
   `Recipe_InstallImplant.GetPartsToApplyOn` both wrap
   `MedicalRecipesUtility.GetFixedPartsToApplyOn` in a validator that already
   rejects a part carrying this hediff, a part whose parent is missing, and a
   part under an existing directly-added part. So the answer to "skip or
   replace" is **skip, and let the engine decide what counts as occupied** — a
   character authored with two bionic arms gets both shoulders because the
   validator is re-run per entry; a third gets a warning.
5. **Missing part → log and skip, naming the CHARACTER.** `GetPartsToApplyOn`
   returning empty and `AllRecipes` matching nothing are different failures and
   get different messages; the cast file is what an author has to go and fix, so
   the character's defName and label lead the line. This is the entire reason
   the work was deferred once — in vanilla both cases are a silent no-op, and a
   silent no-op here is indistinguishable from working.
6. **Fallback to `CompProperties_UseEffectInstallImplant`**, as vanilla does, for
   tech hediffs that install through a comp rather than surgery (mechlink,
   psychic amplifier). None of the 294 author one today; it costs six lines and
   removes a whole class of future silent miss.
7. **Ordering: bionics BEFORE weapon and apparel.**
   `Recipe_InstallArtificialBodyPart.ApplyOnPawn` runs
   `pawn.health.RestorePart(part)` on the natural part first, so a part the pawn
   was generated without comes back — and `ApparelUtility.HasPartsToWear` reads
   the body as it stands when it runs.
8. **Random among valid parts, matching vanilla.** Which shoulder wears the arm
   is not authored, and the pawn being overwritten was itself rolled;
   determinism is not a property this path has anywhere else.
9. **`try`/`catch` around the one `ApplyOnPawn` call.** A throw inside a recipe
   worker would abort `WorldObject_Inhabited.InstantiateCast` and take a
   settlement's whole population with it. One person missing an arm is
   survivable; a place with nobody in it is not.

## verify

- `Inhabited.csproj` builds Release clean, 0 warnings 0 errors.
- Offline: every authored `isTechHediff` entry across the 294 resolves to a real
  recipe reachable from the Human ThingDef, and to a body part that exists on
  the Human BodyDef. Enumerated below rather than asserted.
- ⛔ **OWED, and not done here: the live spawn-and-inspect.** Spawn each of the
  seven characters through the `Spawn authored character` debug action on a
  quicktest map and read the Health tab: the named bionic present, on a
  plausible part, with no red error and no `[RimMandrake.Inhabited] ... was NOT
  installed` warning in `Player.log`. Not deployed and not run — this repo had
  other live work potentially in flight.

## criteria

Every authored bionic either goes in, or produces a log line that names the
character, the def, and which of the two ways it failed. No silent skips. The
resolution chain is read out of real 1.6 source before it is written, not
guessed — and where the offline evidence genuinely runs out, that is said in
this file rather than papered over.

## 2026-09-02 — built (FOUNDRY)

`src/RimMandrake/Inhabited/Source/CharacterApplier.cs` gains
`ApplyInstalledItems` + `InstallPart`, called from `ApplyTo` between
`ApplySkills` and `ApplyWeapon`. `ApplyCarriedItems` is unchanged and still
skips `isTechHediff`; the two halves now cover the field between them.
`CharacterDef.items`' doc comment and `CharacterApplier`'s class header both
stated the install half was unbuilt and now state what IS.

**Source read before writing, all of it 1.6 (`1.6.4871 rev591`):**

| what | where |
|---|---|
| the whole precedent | `Source/RimWorld/PawnTechHediffsGenerator.cs:52-72` (`InstallPart`) |
| ThingDef's recipe set | `Source/Verse/ThingDef.cs:545-569` (`AllRecipes`) |
| ingredient test | `Source/Verse/RecipeDef.cs:458-468` (`IsIngredient`) |
| `targetsBodyPart` defaults **true** | `Source/Verse/RecipeDef.cs:105` |
| the two part fields | `Source/Verse/RecipeDef.cs:80` (`appliedOnFixedBodyPartGroups`), `:82` (`addsHediff`); `appliedOnFixedBodyParts` read via `GetFixedPartsToApplyOn` |
| part enumeration | `Source/RimWorld/MedicalRecipesUtility.cs:76-110` (`GetFixedPartsToApplyOn`) |
| occupancy validator (prosthetics) | `Source/RimWorld/Recipe_InstallArtificialBodyPart.cs:9-26` |
| occupancy validator (implants) | `Source/RimWorld/Recipe_InstallImplant.cs:9-18` |
| the off-map install branch | `Source/RimWorld/Recipe_InstallArtificialBodyPart.cs:28-71` — with `billDoer == null` **and** `pawn.Map == null` it takes `pawn.health.RestorePart(part)` then `AddHediff`; nothing is spawned on any floor, no surgery roll, no tale, no ideoligion event |
| default `GetPartsToApplyOn` | `Source/Verse/RecipeWorker.cs:21-24` — returns EMPTY, so a non-surgery worker yields no parts and we warn rather than misfire |
| comp fallback | `Source/RimWorld/CompProperties_UseEffectInstallImplant.cs:5-27` |

⚠️ Two engine details that read as traps and are handled: `ApplyOnPawn`'s
`flag2` (`IsViolationOnPawn`) is computed unconditionally but only *consumed*
inside `if (billDoer != null)`, so the null-surgeon path cannot report a
violation; and `RecipeWorker.GetPartsToApplyOn`'s base returns an empty
sequence rather than throwing, which is why an empty result must be treated as
"this recipe cannot go anywhere on this body" and not as an error.

**The authored data, measured not assumed.** 27 of the 294 carry `items`; 10
entries across 7 characters are `isTechHediff`:

| character | cast | authored |
|---|---|---|
| `Inhabited_Blackstar_KessaRynWode` | BLACKSTAR | BionicArm, BionicEye |
| `Inhabited_Droids_Nem` | DROIDS | BionicArm |
| `Inhabited_Geonosian_GizzekVor` | GEONOSIAN | BionicLeg, BionicArm |
| `Inhabited_Geonosian_CommunicantZzir` | GEONOSIAN | BionicJaw |
| `Inhabited_Helix_CuratorAdjunctVekkSilla` | HELIX | BionicArm |
| `Inhabited_Jawa_NokkoUbb` | JAWA | BionicArm, BionicEye |
| `Inhabited_Tusken_IkriNass` | TUSKEN | BionicArm |

Four distinct ThingDefs, and each one's chain, end to end:

| ThingDef | recipe | worker | `appliedOnFixedBodyParts` | on the Human body |
|---|---|---|---|---|
| `BionicArm` | `InstallBionicArm` | `Recipe_InstallArtificialBodyPart` | `Shoulder` | 2 |
| `BionicEye` | `InstallBionicEye` | `Recipe_InstallArtificialBodyPart` | `Eye` | 2 |
| `BionicJaw` | `InstallBionicJaw` | `Recipe_InstallArtificialBodyPart` | `Jaw` | 1 |
| `BionicLeg` | `InstallBionicLeg` | `Recipe_InstallArtificialBodyPart` | `Leg` | 2 |

All four recipes carry `recipeUsers: [Human, CreepJoiner]`, `addsHediff` equal
to the part's HediffDef, and `targetsBodyPart` inherited true, per
`Defs/Core/HediffDefs/BodyParts/Hediffs_BodyParts_Bionic.xml`. The Human part
counts are from `Data/Core/Defs/Bodies/Bodies_Humanlike.xml`. `isTechHediff` is
set once, on the shared parent, at
`Defs/Core/HediffDefs/BodyParts/Hediffs_BodyParts_Base.xml:17`.

Against the LIVE 593-mod set (`defs.sqlite`, `mods=593/8cec2b98fcfbfb4a`,
captured `2026-09-02T19:36:08Z`) all four ThingDefs, all four RecipeDefs and
the `Human` BodyDef are MEASURED present — so nothing in the stack, Cherry
Picker included, has cut the chain out from under this.

⚠️ **What the offline evidence cannot settle, stated rather than assumed:**

1. **`isTechHediff` in the live set is UNMEASURED.** The def dump does not carry
   the flag (`measure flag isTechHediff` → `UNMEASURED — the 'is' block never
   carried isTechHediff in this capture`). Core sets it on `BodyPartBionicBase`;
   whether any of the 593 mods patches it off is not knowable from here. If one
   did, the entry would silently go to the *inventory* instead — carried, not
   installed — which is the pre-existing behaviour, not a regression.
2. **`recipeUsers`, `ingredients` and `appliedOnFixedBodyParts` are NOT in the
   dump either** (a RecipeDef record carries 8 shallow fields). Those three came
   from Core XML, so a mod that retargets `InstallBionicArm` would not show up
   here. This is what the live check is for.
3. **The pawn's actual race is not settled by this item.** `CharacterDef.race`
   is prose and `pawnKind` is null on all 294, so today every authored character
   is generated from the caller's fallback kind and comes out a Human — which is
   why the Human chain above is the one that matters. When DECIDE answers
   `pawnKind`, a non-Human kind will start taking the "no recipe on
   `<ThingDef>`" warning branch, by design; `Inhabited_Droids_Nem` and the two
   Geonosians are the entries most likely to hit it.
4. **`developmentalStageFilter: Child, Adult` is not consulted**, exactly as
   vanilla's `InstallPart` does not consult it. No authored character is an
   infant, so this is inert today and noted only so nobody reads its absence as
   an oversight.

**Compile-verified only.** `Inhabited.csproj` Release: 0 warnings, 0 errors.
⛔ NOT deployed, NOT loaded, NOT seen running. The `## verify` section's live
spawn-and-inspect is owed.
