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
