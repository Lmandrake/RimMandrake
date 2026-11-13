## spec
Re-prove Explosive Knockback's closed-container rule live, under the owner's 2026-11-12 ruling (OWNER:1794529787425697771): "Anything that draws its contents is open ... a shelf should be ruled as open, period. So the scene is staged misleadingly."

The earlier live pass (note on RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED, Station 5, 10/10) staged a ShelfSmall tagged closed by the proof build's CloseStorage. That staging is now invalid; CloseStorage is gone (RM_KnockbackProof.cs has a read-only IsClosed instead).

Run on the minimal list plus LWM's Deep Storage (lwm.deepstorage), with a PROOF build (winbuild.py ExplosiveKnockback -- -p:RmProofs=true; never commit that DLL):
1. `src/RimMandrake/ExplosiveKnockback/proof/storeroom_pit_proof.py --storage` (default --container-def LWM_WeaponsLocker; row NAME_CONTAINER_CLOSED needs IsClosed to read CLOSED with no tag).
2. Scenes sc_closed_containers, sc_storeroom_bomb_pit, sc_settings_sweep, sc_open_storage as now written in design/concepts/ExplosiveKnockback/scenes.json (Shelf, ShelfSmall and Hopper are open; LWM_WeaponsLocker, LWM_Safe 500 kg, SealedCrate, AncientSecurityCrate closed). The RM_KnockbackProof container_thrown and Matrix rows already use LWM_WeaponsLocker; closed_containers' own staging must be checked against the new scene text.

## Watch out
- Wrong material: saves EK_SITTING_STATION5_CONTAINER_SURVIVES_20261112 (ShelfSmall tagged closed) and EK_SITTING_STATION1_STORAGE_20261112 (a Hopper staged as the closed container) stage the old misleading rule. Delete or restage both, and fix every inbound reference (grep the repo and the conductor scratch). The game was live in the owner's sitting when this was filed, so nothing was touched.
- Deploy first (RIMMANDRAKE_DEPLOY_KNOCKBACK_DRAWING_STORAGE_OPEN): the game copy still holds Patches/RM_Knockback_ClosedContainers.xml, which tags the Cold Storage lockers and crock closed.
