# RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD

## spec

Step 1 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.

## Watch out

The carrier must survive a save taken mid-flight as ONE thing (never a duplicate, never lost). The per-tick overflow cap goes away, so frame cost is owed by RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF. A thrown good never enters a hidden or open pit by a careless path (leaf no_careless_fall); pits are entered by force only.

## 2026-11-12 built at 92e65812cbc8 (live proof and owner's look owed)
Steps in: 1 arc carrier RM_ThingFlyer_Knockback (merge, no-free-cell fallback, save/load via IThingHolder), 2 blast damage / wall impact / shelf+container / pit rules kept, 3 spin, 4 rebound chain (keep 70%, max 6 bounces), 5 toggle + sliders ("Flying goods" group), 6 perf: one flyer per stack, no new cap (risk on RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF).
Proof code is fenced behind RM_PROOFS (csproj RmProofs=true); the committed/deployed DLL is release (selftest_explosiveknockback_proofgate R1/P1/G1). Proof scripts exit 3 "PROOF BUILD REQUIRED" on release.
Live proof owed: build proof flavor (winbuild.py ExplosiveKnockback -- -p:RmProofs=true), deploy, validation.py chain flying_goods (goods_fly_midair/lands/wall/rebound/off) and proof/goods_flight_saveload.py, then rebuild release.
Not in this build: the 1.6x goods distance and removing the old per-tick overflow cap. Corpse draw while unspawned needs a live look.
