# SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1 — "Spawned 2/2" delivered one of something else

Measured live 2026-08-27, 582 mods.
Evidence: `infrastructure/state/evidence/bridge_session_2026-08-27_BUILD.md`.

```
jawa/spawn_pawn {kindDef:"Jawa_Hutt_Specialist", faction:"Jawa_HuttCartel", count:2}
  -> success: true, "Spawned 2/2 Jawa_Hutt_Specialist in faction Jawa_HuttCartel."

jawa/list_pawns -> Jawa_Hutt_Specialist x1   +   Colonist x1  (xenotype baseliner)
```

The tool counted two spawns and named the kind it was asked for. One of the two is a **vanilla
`Colonist`**. The other three Hutt kinds delivered 2/2 correctly in the same call sequence.

⭐ **And the substituted pawn is the only bare one of the eight.** The seven real Hutt pawns
all carried a weapon and apparel; the `Colonist` carried nothing.

## 🔑 Why this may matter far beyond one tool
`facts/roll_arm_harvest_2026-08-24.md` records **21 of 285** pawns rolling bare across 16 of
49 roster kinds, and attributes 13 to violence-disabling backstories while leaving **8
combat-capable bare pawns unexplained**. If those 8 are substituted vanilla kinds rather than
our kinds failing to arm, the remaining bare-hands mystery is not an arming defect at all.

⚠️ **UNTESTED — this is a hypothesis with one supporting observation.** It is cheap to settle:
spawn N of a roster kind and compare the requested `kindDef` against the `kindDef` read back,
which no previous harvest did. **Do that before anyone tunes another `weaponMoney`.**
🔑 It would also explain the *"baseliners generate in five factions"* gap already filed to
DECIDE in `five-design-gaps-found-auditing-the-seven-authored-factions-3c81ea` — a baseliner
is what a substituted vanilla kind looks like.

## criteria
- [ ] The kind read back matches the kind requested, or the tool reports the substitution.
- [ ] The bare-hands cohort in `roll_arm_harvest` is re-scored with requested-vs-actual kind
      recorded per pawn.

---

## ✅ MEASURED 2026-08-27, 150 spawns — the hypothesis above is CONFIRMED as a cause, and it is not the only one

**Run A — 16 kinds × 5.** 80 spawned: 76 ours, **4 substituted**, and **4 of the 4
substituted pawns were bare**. Substitution appeared only on `Jawa_Empire_Heavy`,
`Jawa_Empire_Specialist`, `Jawa_Hutt_Grunt`, `Jawa_Hutt_Leader`, one pawn each, with
`Spawned 5/5 <requested kind>` reported every time.

**Run B — 7 kinds × 10.** 70 spawned, 0 substituted, 5 bare, and **all 5 carry a
violence-disabling backstory. Zero unexplained.**

🔑 **Together these close the bare-hands question: two causes, no third.** A pacifist
backstory, or a substituted vanilla kind. ⛔ **There is no `weaponMoney` defect** — the
corrected `weapon_affordability.py` reports `always arms 49 · sometimes 0 · never 0 ·
unmeasured 0`, and the live evidence now agrees with it rather than contradicting it.

⭐ **This retires the "8 combat-capable bare pawns" of `roll_arm_harvest_2026-08-24.md`.**
That harvest recorded the **requested** kind, so a substituted vanilla `Colonist` was counted
as one of our kinds arriving bare with no pacifist excuse. Rates agree: 5 in 70 = **7.1%**
against 21 in 285 = **7.4%**.

⚠️ **Substitution rate here is 4 of 80 = 5%, and the sample is small.** What is NOT measured:
why those four kinds and not the others, whether the rate differs at raid generation rather
than direct spawn, and whether the substitution is `spawn_pawn`'s or the engine's
`PawnGenerator` falling back. **The last of those is the one worth knowing** — if it is the
engine, it affects raids too and no bridge fix touches it.

## criteria
- [x] The kind read back is compared against the kind requested — done, twice.
- [ ] The substitution is attributed to `jawa/spawn_pawn` or to `PawnGenerator`.
- [ ] The tool reports the substitution instead of counting it as the requested kind.

---

## 🔑 SHARPENED 2026-08-27 — substitution tracks the FACTION, not the kind

A 240-pawn run split cleanly along one line:

    kinds whose defaultFactionDef is a VANILLA faction (Empire, Pirate)   18 of 160   11%
    kinds sitting in factions we authored                                  0 of  80    0%

The guarded set was `Jawa_Empire_*` (`defaultFactionDef: Empire`, vanilla Royalty) and
`Jawa_Blackstar_*` (`defaultFactionDef: Pirate`). The control was `Jawa_Hutt_Grunt`,
`Jawa_Droid_Heavy`, `Jawa_Wildsteam_Grunt`, `Jawa_TradeMoot_Grunt` — all in authored factions,
**zero substitutions**.

⇒ **The next test is one call:** spawn `Jawa_Empire_Grunt` into an AUTHORED faction and see
whether substitution disappears. If it does, this is a faction-side pawn-generation fallback
and not a `jawa/spawn_pawn` defect at all — which also means it would reach raids, where no
bridge fix could touch it.

⚠️ **Confounded, and say so.** The two groups differ in more than faction: the guarded eight
also carry `requiredWorkTags: Violent`, which is a generation constraint that can itself force
a re-roll. **A constraint that cannot be satisfied is at least as good an explanation as the
faction**, and this run cannot separate them. Test the two independently before believing
either.

---

## ✅ CONFOUND RESOLVED 2026-08-27 — it is the FACTION, and `requiredWorkTags` has no effect

A 2×2, 20 pawns per cell, same session:

| | vanilla faction (`Empire`) | authored faction (`Jawa_HuttCartel`) |
|---|---|---|
| **guarded kind** `Jawa_Empire_Grunt` | **3 of 20 substituted (15%)** | **0 of 20 (0%)** |
| **unguarded kind** `Jawa_Hutt_Grunt` | **3 of 20 substituted (15%)** | **0 of 20 (0%)** |

**The rows are identical and the columns are not.** `requiredWorkTags: Violent` changes
nothing; the faction changes everything. Spawning any of our kinds into a VANILLA faction
substitutes ~15% of them for a vanilla kind; into a faction we authored, never.

## 🔴 Why this is a live gameplay defect, not a bridge curiosity
`Jawa_Empire_*` declare `defaultFactionDef: Empire` and `Jawa_Blackstar_*` declare
`defaultFactionDef: Pirate` — **both vanilla**. Every substituted pawn measured this session
was bare-handed. ⇒ Roughly one in seven Empire and Blackstar pawns arrives as a vanilla kind
carrying nothing, and the shipped `requiredWorkTags` guard cannot prevent it.

🔑 **And this is almost certainly the same defect `AUTHORED_KINDS_MUST_FIELD_1` exists to fix.**
That item wires orphaned role kinds into `TribeCivil`, `Pirate` and `Empire` combat groups.
Our authored factions list our kinds in their `pawnGroupMakers`; vanilla `Empire` and `Pirate`
do not. **Untested prediction:** wiring the Empire and Blackstar kinds into those two factions'
combat groups takes the substitution rate to 0, exactly as it already is for every authored
faction. ⚠️ Prediction, not a measurement — the mechanism (a faction-side fallback to
`basicMemberKind` for a kind the faction does not field) has not been read out of the C#.

## criteria
- [x] Kind read back compared against kind requested.
- [x] Attributed: the faction, not the kind and not `requiredWorkTags`.
- [ ] The mechanism confirmed in `PawnGenerator`/faction fallback source, not inferred.
- [ ] Substitution at 0 for Empire and Blackstar kinds in normal play.
