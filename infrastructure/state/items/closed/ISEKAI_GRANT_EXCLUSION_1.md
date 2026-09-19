# ISEKAI_GRANT_EXCLUSION_1 — keep the Star-Wars identity traits off the random-roll path

Filed 2026-08-30, caused by `PAWN_FLAVOR_STARWARS_1`. Owner's ruling: our reflavored
identity traits must not be dispensed by blind chance — they arrive via backstory and play,
through the Hero's Awakening Scroll and the Villain's Mask.

🔑 **There is no `Jawa_`-prefixed TraitDef.** "Jawa_ traits" means the Isekai traits we
reflavored: `IsekaiTraits_StarWarsReflavor.xml` renames `Isekai_Protagonist` /
`Isekai_Antagonist` to *Chosen One* / *Dark Side Ascendant*, keeping the upstream defNames
per that item's own ruling.

## Two INDEPENDENT random-roll pathways, not one

**(1) Vanilla pawn generation** reads the TraitDef's own `commonality` for every pawn
generated anywhere. Both ship `commonality=0.01` upstream (workshop `3657580708`), an
explicit "extremely rare natural roll, also earned via scroll/mask" design we are overriding.

✅ **CLOSED** by `src/Jawa/Jawa_Patches/Patches/IsekaiTraits_ExcludeFromRandomRoll.xml` —
`PatchOperationFindMod`-gated `PatchOperationReplace`, `commonality` → 0 on both, mirroring
the `Isekai_Rank_*` "never randomly assigned" convention already in the mod.
`validate_patch.py` against the live 585-mod set: 2/2 matches, 0 errors, 0 warnings.
Explicit grants (`CompUseEffect_IsekaiTrait` → `AddIsekaiTrait` → `Trait.GainTrait`) never
consult commonality and are unaffected.

**(2) Isekai's OWN NPC roller**, `IsekaiTraitHelper.RollRandomTraits`, reads a **hardcoded C#
dictionary** mirroring the same 0.01/0.01 — not the live TraitDef. ⛔ No XML patch can reach
it. Would need a Harmony reflection patch stripping Protagonist/Antagonist from the private
static `RollableTraits` list, and there is no existing `Jawa_` Harmony DLL to host it
cheaply. Exposure is small (0.01 weight among dozens of candidates, itself behind an
80%-chance-of-zero roll) but nonzero over a long campaign. **Flagged for a BENCH call on
whether that residual is worth a new DLL — deliberately not built here.**

## 2026-08-30 (FOUNDRY) — deployment confirmed; the live roll test is not

**The patch is in the running build.** `…/Mods/Jawa_Patches/Patches/IsekaiTraits_ExcludeFromRandomRoll.xml`
was written **10:22** and the running RimWorld process (pid 33580) started **11:23:36** —
loaded, not merely written. `deploy_custom_mods.py --mod Jawa_Patches` reports the mod in
sync across all 162 files.

### 🔴 A near-miss worth keeping: I almost reported this shipped fix as a no-op
`jawa/get_defs` on the live `DefDatabase` returned **`commonality: "(no such field)"`** for
`Isekai_Protagonist`, `Isekai_Antagonist` **and vanilla `Nimble`** — which reads as *TraitDef
has no such field, so the patch targets nothing*. It is wrong. `RimWorld/TraitDef.cs` declares
**`private float commonality = 1f;`** — a real field, set by the XML loader like any other,
and invisible to a `BindingFlags.Public` reflection pass. The tool was reporting *"I cannot
see it"* in the words *"it does not exist"*.

⇒ **`jawa/get_defs` fixed this pass**: when a field is NAMED, it now also searches
`NonPublic | Instance` fields up the type hierarchy, and an unreadable non-public value says
so explicitly instead of falling through to `(no such field)`. An unfiltered dump stays
public-only. Builds clean (`build.py --gm`, zero tool removals). ⚠️ **Built, not deployed** —
the running game holds the companion DLL open; deploy at the next game-down window with
`python.exe src/RimMandrake/bridgetools/build.py --gm --apply`.

### Blocker
The verify clause — N grant-item rolls in a quicktest, confirming the roll path is dead and
explicit grants still work — needs a map, and none could be created. RimWorld is wedged on a
**"Loading world." long event that never completes**: `mapCount 0`, `ticksGame` frozen at
9252, `go_to_main_menu` answers with its own NRE, `Root_Play.UIRootUpdate` throws every frame
on a null `Find.WorldGrid`. Three `start_debug_game_ready` calls and one `load_game` failed;
the first two aborted inside `BetterRomance.SettingsUtilities.ChildAge` during **starting-pawn**
generation, before anything had been spawned. The bridge stayed healthy — dead game, not dead
bridge. Needs an owner restart.

⭐ **Once the fixed companion is deployed, half this verify no longer needs a map at all:**
`jawa/get_defs` with `defs=TraitDef/Isekai_Protagonist;TraitDef/Isekai_Antagonist` and
`fields=commonality` reads the live post-patch value straight out of `DefDatabase`, which is
loaded at startup and does not depend on a game being loaded. Only the explicit-grant half
still needs a pawn.

## criteria
- [x] Mechanism read, not guessed — both roll pathways identified, and which one XML can reach.
- [x] Vanilla random-roll path closed by a validated, FindMod-gated patch, deployed and
      loaded in the running build.
- [x] Residual NPC-roller risk named and escalated to BENCH rather than silently fixed.
- [x] Live confirmation: commonality reads 0 from the running DefDatabase (with a control
      proving the reader is not blind), an explicit grant still applies the trait, and 120
      freshly generated pawns rolled neither. See the section below.

## ✅ LIVE CONFIRMATION 2026-08-30 (FOUNDRY) — all three checks pass. CLOSED.

Fresh 585-mod quicktest. The fixed `jawa/get_defs` (NonPublic field search) is deployed.

### 1. `commonality` reads a real 0 — and the control proves it is a MEASURED zero
```
jawa/get_defs {defs: "TraitDef/Isekai_Protagonist;TraitDef/Isekai_Antagonist;
                      TraitDef/Nimble;TraitDef/Isekai_Rank_S", fields: "commonality"}

  Isekai_Protagonist   commonality 0.0     (upstream 0.01 -> patched)
  Isekai_Antagonist    commonality 0.0     (upstream 0.01 -> patched)
  Nimble        (Core) commonality 1.0     <- CONTROL
  Isekai_Rank_S        commonality 0.0     (the mod's own never-rolled convention)
```
🔑 **`Nimble` reading `1.0` is what makes the two zeroes worth anything.** `commonality` is
`private float` on `TraitDef`; the previous pass's tool could not see it and said
*"(no such field)"* on all three alike, which was indistinguishable from the patch having
missed. A reader that returns 1.0 for a def nobody patched and 0.0 for the two that were
patched is reading the field, not failing on it. ⇒ the shipped XML fix is confirmed applied,
and the earlier near-miss is fully retired.

### 2. The explicit grant still works on a commonality-0 trait
```
jawa/pawn_traits {action: "list"}  -> traitCount 4  [Undergrounder, Straight, Isekai_Rank_C, Isekai_Title_Archer]
jawa/pawn_traits {action: "add", trait: "Isekai_Protagonist"} -> added 1, refused []
jawa/pawn_traits {action: "list"}  -> traitCount 5, Isekai_Protagonist present
```
This exercises `TraitSet.GainTrait`, the same terminal call
`CompUseEffect_IsekaiTrait.DoEffect` → `IsekaiTraitHelper.AddIsekaiTrait` makes (read from
the mod's own `Source/IsekaiLeveling/Items/CompUseEffect_IsekaiTrait.cs`). ⇒ `commonality 0`
removes the trait from the random roll **without** disabling the scroll/mask route, which is
exactly the owner's ruling.

### 3. 120 freshly generated pawns rolled neither
```
120 pawns via jawa/spawn_pawn (Colonist, 4 batches of 30)
  Isekai_Protagonist  0
  Isekai_Antagonist   0
  traits that DID roll: Bisexual 58, Isekai_Rank_F 39, Isekai_Rank_E 30,
                        Straight 28, Isekai_Rank_D 26, PsychicSensitivity 18
```
The right-hand column is the control: trait assignment is plainly running on these pawns.

### ⚠️ What this sample does NOT prove — pathway (2) is untouched and still open
🔑 **The `Isekai_Rank_*` rows are live evidence for this item's pathway (2), which until now
was source-only.** `Isekai_Rank_S`/`_F`/`_E`/`_D` all read `commonality 0.0` in check 1, and
**39 + 30 + 26 of them appeared on these 120 pawns anyway** — so Isekai's own C# roller
demonstrably assigns traits the TraitDef says are never rolled. (`jawa/drain_log` shows its
narration during map gen: *"[Isekai Forge] Enhancing Alpha, Techie (rank D)…"*.)

⇒ 0/120 on Protagonist/Antagonist confirms **pathway (1) is closed** and is *consistent with*
pathway (2) being rare, but at a hardcoded 0.01 weight behind an 80%-chance-of-zero roll a
120-pawn sample would expect roughly zero hits either way. **It is not evidence that
pathway (2) is closed, and pathway (2) is not closed** — it remains flagged for BENCH exactly
as this item already recorded, now with a live demonstration that the mechanism is real
rather than a source reading.
