# MIASMA_FLOTSAM_YARD_1 work note (2026-10-03)
- Started. Plan: flotsam table + map-gen/post-surge scatter on root-line cells, Mod Settings toggle + amount slider.
## Choices
- Component RM_MapComponent_FlotsamYard (auto-instantiated, no genstep/patch): seeds 24 stacks on first tick of a Miasma map, restocks 14 when shared axis LastRecedeCompletedTick (reflection) advances; cells within 2 of RM_Thessamor/Brelloch/Thrannock; vanilla goods Steel/WoodLog/Cloth/ComponentIndustrial; cap 70 stacks x amount. Settings flotsamEnabled + flotsamAmount (0.25-3). No art needed (vanilla items); artpipe search not applicable beyond confirming no flotsam art. Live criterion UNMEASURED.
