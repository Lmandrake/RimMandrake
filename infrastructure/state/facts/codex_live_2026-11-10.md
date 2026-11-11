# Codex live-game run, owner order 2026-11-10

## Dependency preflight repair

The October 10 dependency baseline recorded Harmony `353daafec180bb8e`.
The installed Workshop item 2009463077 now declares mod version 3.0.1.0,
with LoadFolders.xml selecting root and `1.6` for this game. `Current` no
longer exists. The selected `0Harmony.dll` hashes `8ac54fdf0fab2571`;
its companion `HarmonyMod.dll` hashes `408c2cd72b45da8c`. Every other
baseline assembly and RimBridgeServer 2.3.0 remains unchanged.

Preflight now resolves the real load folders for both dependency mods,
hashes all selected assemblies, rejects conflicting duplicate assembly names,
and requires Harmony, RimBridgeServer and Assembly-CSharp by name.
The supported `--accept-deps` establishes this investigated installed update
as the new environment. This is NOT comparability with October and is NOT
live compatibility evidence; the ensuing clean launch/proof must supply that.
Regression controls: selected-version hash, matching baseline, changed selected
Harmony FAIL, and missing Harmony UNMEASURED. Required wrapper PASS 1/1.

## Deployment rescue

GSS was first rescued with `deploy_custom_mods.py --pull GimmeSomeSlack`.
Its old deployed DLL SHA256 is
`28ee963764beaa5fdff0b3285d5e3e8546fd23e828df851809395313cc78d1db`.
The DLL, stamp and older review manifest were preserved under
`D:\ClaudeWork\rimmandrake\backups\codex-live-20261110\GimmeSomeSlack`.
These unproven older artifacts were not adopted into the source tree.
The complete deploy plan finished with `Drift found`, covering 41 drifted mods;
261 files from 40 existing divergent mod copies were rescued through --pull
before applying origin/main (TileFeatures was entirely new). Rescue hashes and
paths are in whittle/evidence/codex-live/codex-live-all-rescues.json.

The installed JawaBench companion embeds source hash
`48258bf21f617ff5b51bfe3951b4b3f20132ba6353887b5a81a34e60e03ad6ea`,
identical to this clone's source hash. Only the ignored local comparison artifact
was recovered from the deployed copy; no companion replacement was needed.

## Driver identity repair

The driver lock recognized only a Claude ancestor; Codex tool shells could
therefore record a dead process, or fail release across shells. It now recognizes
the nearest Codex or Claude process, preserving explicit RM_DRIVER_PID priority
and the parent fallback. Separate-shell regression controls for both runners,
override and fallback, plus existing exclusivity/CLI cases: wrapper PASS 1/1.
