# LEANINGSCRUB_SWEETLINE_VISITORS_1 -- choices (FOUNDRY, 2026-10-03)  OWNER VETO OPEN

Item cites no spec of its own; decided from the item's three questions plus
`design/Jawa/worldbuilding/biomes/leaningscrub_sweetline_guardian_activation_2026-10-02.md` (traders and
travellers on the tree-roads are safe; the tree "paying its visitors" is not harm) and the name register
(road-folk register).

Existing before this work: `RM_CompSweetlineStation` (name, history panel, wool timer), setting
`sweetlineStationsEnabled`, `RM_SweetlineWool`. No visitor or token code, no token def. Artpipe: only
`rut_sweetlinewool_v*`; nothing for a sweetline token (the 224 "token" hits are unrelated word matches).

1. WHO: generic `RM_` road-folk, unnamed ("a road-party", "a pilgrim"). No Jawa/campaign dressing, so no
   Utinni patch layer (Q11a: free tier carries it; campaign layer may dress it later).
2. MAPGEN OR LIVE: LIVE, abstract. No mapgen scatter (the planet/maps are repainted once; a placed camp
   would be wrong content). No walking visitor pawns/lord jobs (the guardian spec says travellers are
   untouched; spawning real pawns is a larger, riskier build). The comp rolls a visit every ~8 days
   (0.5x-1.5x) on a mature tree on a player-home map. 40% a travellers' camp (history entry plus cold ash
   beside the trunk), 60% pilgrims (history entry plus a token). Visits land in the tree's History panel.
3. TOKEN: `RM_SweetlineToken`, small trade item, stack 20, MarketValue 3, no art yet (placeholder like
   `RM_RawVenom`). Cap of 3 tokens within 5 cells of the trunk; past that the pilgrim only leaves a history entry.
4. SETTINGS: own toggle `sweetlineVisitorsEnabled` plus `sweetlineVisitIntervalDays` (default 8). Also needs
   `sweetlineStationsEnabled` (the History/inspect surface).
5. ART OWED: `Things/Item/Resource/RM_SweetlineToken` (not queued: owner veto first on the token idea).
