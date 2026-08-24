## spec
🔴 **DECIDE ruled 2026-08-22 (`UNARMED_RAIDERS_ACCEPTABLE_RATE_1`): a pacifist pawn is
acceptable from ten of the twelve factions and unacceptable from two.** The full ruling,
with the per-faction table and the reasoning, is in
`design/Jawa/worldbuilding/pawnkind_roster.md` — *"Who may arrive unable to fight"*.

**Galactic Empire and Blackstar Company must never field a combat pawn whose backstory
disables `Violent`.** Eight kinds:

    Jawa_Empire_Grunt      Heavy  Leader  Specialist
    Jawa_Blackstar_Grunt   Heavy  Leader  Specialist

Measured 2026-08-21: **5 of 20 Empire rolls** drew a violence-disabling backstory
(`observed/2026-08-21/armed_sweep_48/rolls.json`).

⛔ **Do not apply this to the other ten factions.** DECIDE ruled their pacifist rolls are
wanted texture; narrowing them is a regression, not a bonus.

🔑 **HOW is yours.** Backstory category constraint, a curated filter, whatever the engine
actually supports. DECIDE has no opinion on the mechanism.

## verify
Spawn 20 of each of the eight kinds and read `childhood`/`adulthood` back: **zero** may
disable `Violent`. Then re-run the 240-roll sweep and confirm the other ten families'
pacifist incidence is **unchanged** — a drop there means the fix over-applied.

## criteria
Empire and Blackstar combat kinds: 0 violence-disabling backstories in 20 rolls each.
Other ten families: pacifist incidence within noise of the 2026-08-21 baseline (13/180).

## watch out
⚠️ Violence-disabling **traits** were never measured — the dump reports 0 `TraitDef`s with
`Violent` in `degreeDatas`, which is a dump blind spot rather than a proven zero. If a
trait route exists, backstory filtering alone will not close this.

## 🔴 MEASURED LIVE 2026-08-24 — this item names the wrong two factions
285 pawns rolled; backstories resolved through `jawa/get_defs`:

| cohort | distinct backstories | disable `Violent` |
|---|---|---|
| bare (21 pawns) | 32 | **10** |
| armed (264 pawns) | 256 | **0** |

**Zero overlap — a violence-disabling backstory is SUFFICIENT to produce a bare pawn.** Not one of
264 armed pawns carried one.

🔑 **It is roster-wide, not an Empire/Blackstar problem.** The 13 pacifist rolls landed on
**Droid ×3, Wildsteam ×2, Geonosian ×2, TradeMoot ×2, Homestead, Hutt, Gamorrean, Empire ×1** —
Blackstar rolled **none**. Widen the fix to every authored combat kind or it will keep reappearing
under a different faction's name.

⚠️ **It is not NECESSARY, so a backstory filter alone will not close the bare-pawn problem:** the
other **8 of 21** bare pawns can do violence and rolled bare anyway. That is the `weaponMoney` roll —
a separate defect with a separate fix. Evidence: `facts/roll_arm_harvest_2026-08-24.md` §2.
