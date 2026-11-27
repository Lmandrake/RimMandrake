FlowWorks SelfTest RiverSwitchFlipChecks.Src() flattens all whitespace to single spaces; a line-based source check (count lines, look N lines back) must read the raw file via File.ReadAllText(SrcPath(rel)), or it silently sees one long line.

Met again 2026-11-27 (FlowWorks blind cycle 5): a per-line // comment strip on Src() text cut the file at its first //, and the new case failed on the real build (30dbdfc2b9); fixed by SrcPath + File.ReadAllText (5d68be6e66).
