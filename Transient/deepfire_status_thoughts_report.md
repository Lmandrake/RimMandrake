# Deepfire: proxy storage fix + status thoughts — 2026-09-30

## 1. DEEPFIRE_PROXY_BLOCKS_STORAGE_1

Status: BUILT, NOT live-proven. Proof (not run):
`python.exe src\RimMandrake\bridgetools\prove_deepfire_proxy_storage.py --start`

- Fix: `RM_DeepfireLightProxy` goes from category **Item** to **Ethereal** (+ `fillPercent 0`,
  item-only `stackLimit` dropped). The altitudeLayer stays **Item**, which is the layer that
  was proven live not to wipe a wall. It is the same shape as the worn proxy.
- Why the wall stays safe (RimSage `GenSpawn.SpawningWipes`): only the category changes. The
  rules that read the category are these: the early returns for
  Attachment/Mote/Filth/Projectile/Plant/PsychicEmitter, the Item-vs-Impassable rule (we are
  Standable), IsEdifice (we have no `building`) and BlocksPlanting (fillPercent 0). None of
  them fires. The altitude rules, which are what wiped the wall, see the same Item layer as
  before.
- Why storage works now (RimSage): `GenSpawn.Spawn`'s move-aside branch only runs for an
  Item-category new thing. `GridsUtility.GetItemCount` counts only Item-category things.
  `StoreUtility.NoStorageBlockersIn` passes a Standable thing with no surface.
- Clustering code is untouched, so 36 coated cells still make 4 proxies.
- Proof actions `T: Proxy: ...` (`Source/DeepfireProxyStorageDebugActions.cs`) plus
  `FloorLightCells()` in the Clusters partial. The proof puts 36 Steel stacks on a stockpile,
  coats under them, and asserts 4 proxies, Ethereal, 0 displaced, GetItemCount 1 on each
  proxy cell. After the stockpile is emptied, every proxy cell must accept a WoodLog. A
  coated Steel wall must survive its own proxy. The log must be clean.
- Build: 0 warnings / 0 errors. XML parses and py_compile is OK.

## 2. DEEPFIRE_STATUS_THOUGHTS_1

(pending)
