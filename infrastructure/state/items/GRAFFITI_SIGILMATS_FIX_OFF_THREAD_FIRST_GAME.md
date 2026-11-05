## spec
Class MOD (threading), from test pilot gen 19 of GRAFFITI_NORTHSTAR_GREEN_FULL_1.
- Expected: a new game's load logs no red error from Graffiti.
- Observed: the FIRST new game after launch (small 10-mod list, 2026-11-05T09:41:33Z, Player.log lines 137-154) logged 18 errors:
  "Tried to get a resource \"Things/Filth/Art/RM_Graffiti_SigilFrame_{Halo,StencilBox,DripFrame}/..._0\" from a different thread",
  "Tried to get a resource \"UI/Ideoligions/ReligionC\" / \"UI/Ideoligions/Universal/PoliticalE\" from a different thread" and
  "Tried to get a material from a different thread." The two later new games in the same process logged none (cache warm).
- Mechanism (from the code, not yet proven live): `Filth_Mark.Print` calls `RebuildSigilMats()` when `sigilMatsBuilt` is false;
  that sets `sigilMatsBuilt = true` FIRST, then calls `MaterialPool.MatFrom(ext.sigilFrameTexPath)` and `makerIdeo.Icon`. When
  Print runs during map generation, off the main thread, those return null. The flag stays true, so the mark may draw without
  its sigil until it is rebuilt.
- To check: after a fresh launch, the first quicktest holding a tier-A sigil mark; read whether its frame/icon draw (a capture of
  the cell), and fix by deferring the material build to the main thread (e.g. LongEventHandler.ExecuteWhenFinished, or leave
  sigilMatsBuilt false when not UnityData.IsInMainThread).
