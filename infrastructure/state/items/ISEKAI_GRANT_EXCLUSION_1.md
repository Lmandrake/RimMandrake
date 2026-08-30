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
- [ ] Live confirmation: commonality reads 0 from the running DefDatabase, and an explicit
      scroll/mask grant still applies the trait.
