# Parent dependency review needed before live

No dependency deploy applied. Native source work continues.

TheRot is folded into registered `mandrake.rm.biomes`; the smallest dependency-complete requested baseline plus Biomes is 16 mods (all five DLC, plus LuminousPigment dependency). Standalone TheRot is refused by deploy tool and absent from modset discovery.

Exact raw plans:
- evidence/raw/tier-biomes-plan.stdout.txt (rc0)
- evidence/raw/deploy-biomes-plan.stdout.txt (rc1 drift): only Biomes/Cauldron/Assemblies/RimMandrake.Cauldron.dll + matching .srchash differ.
- evidence/raw/deploy-fw-plan.stdout.txt (rc1 drift): only Assemblies/RimMandrakeFlowWorks.dll + matching .srchash differ.
- evidence/raw/deploy-gss-plan.stdout.txt (inspect actual receipt when completed).

Please review these published deltas before authorizing dependency redeploy; worker will preserve exact installed bytes and hashes before any overwrite. No FlowWorks/GSS/source/item/build edits are requested or made. An exact authorized-delta file can be named DEPENDENCY_APPROVED.json with mod/path/hashes and rationale after backup preparation.

The existing HugeThings plan is in sync (no VERIFIED marker), so direct byte verification remains required. Source/artifact fingerprint gates will still run.

Deployed FlowWorks and Cauldron differing pairs have now been copied without mutation to evidence/raw/dependency-before/; exact installed SHA256 values are in evidence/raw/dependency-before.json. Parent review may inspect the original plans and compare source/published ancestry without touching those backups.

LuminousPigment exact two-file plan/backup: evidence/raw/deploy-luminous-plan.* and evidence/raw/dependency-luminous-before.json. Parent LUMINOUS_DEPENDENCY_AUTHORIZATION.json now grants its published pair. Nothing applied yet; fresh own guard, actual DOWN, remeasured plan/source/backup checks remain required.

Parent review point 9 instructs use of the existing private Player.log archive for O08; --no-archive removed. No full/token-bearing logs enter raw/committed evidence.
