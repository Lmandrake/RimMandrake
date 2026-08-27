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
