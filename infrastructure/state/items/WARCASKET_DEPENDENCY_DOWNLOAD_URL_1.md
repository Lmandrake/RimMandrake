# WARCASKET_DEPENDENCY_DOWNLOAD_URL_1 - Warcasket dependency download URL

Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).

## spec
Warcasket About.xml (src/RimStarWars or src/RimMandrake Warcasket; find with measure/glob About.xml) declares a modDependencies entry for mandrake.rm.biomes with no downloadUrl / steamWorkshopUrl; the game logs "Warcasket dependency (mandrake.rm.biomes) needs to have <downloadUrl> and/or <steamWorkshopUrl> specified", failing defs_and_load/no_warcasket_log_errors. Check how other mods in the repo satisfy this for mandrake.rm.* dependencies and copy that.

## verify
Deploy (compose biomes where relevant) and read Player.log after a load, or grep the log from the last run.

## criteria
A1: Warcasket About.xml dependency carries the repo's standard downloadUrl/steamWorkshopUrl.
A2: Player.log shows no "needs to have <downloadUrl>" line for Warcasket; no_warcasket_log_errors PASSes.

NEXT: claim this item and start with criterion A1.
