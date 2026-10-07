# FOUNDRY acceptance sweep 2026-10-07 (owner AFK)
- 00:55 start. Live list = FULL (612 active mods, parsed ModsConfig via ET), not minimal; presence reads are a superset check.
- 01:05 get_defs/get_def FAIL live: TypeLoadException LaidPiece (GSS asm loaded != JawaBench build ref). L1 via get_defs UNMEASURED on this load. Remedy: kill, rebuild JawaBench --gm vs deployed GSS (00:06), relaunch same 612 list.
- 00:57 launched via steam (612 list)
- 01:19 ROOT CAUSE: JawaBench TerrainTools (get_def/get_defs) throws TypeLoadException(LaidPiece) unless mandrake.rm.gimmesomeslack is loaded; owner list lacks GSS. Added GSS to live ModsConfig (backup Transient/ModsConfig_before_foundry_acc_20261007.xml), relaunched.
