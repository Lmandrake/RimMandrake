# Live validation plan

PROVE: RoofWallProbe real RM_TestTitanT2Adult / RM_TestTitanT2Control at measured cleared bounded rectangle, two calls in each actual mode.
EXPECT: default T2 thin roof none and positive wall HP unchanged; legacy T2 roof none and wall HP smaller (positive starting HP); both controls RoofConstructed, HP unchanged, not destroyed. Read each setting before and after every call. Exact race/tier identity is required.
LIES: Missing mode/control, failed hooks, zero initial HP, malformed boolean, wrong roof identity, swapped tiers, settings drift and accepting every intact wall must not pass. Unit cases oppose both expectations. A Position-setter call is L1 only.
CLOSE: strict single R4 aggregate, both mode arms, all required preflight rows PASS except O02 explicitly other-host N/A; actual inherited generation 1394 and fresh process identity. Full runner still requires original five rows. Finally restore scene-begin, compare full rectangle fingerprint, restore exact settings with raw readbacks, stop through rw_game.sh, release SteveDesktop and prove FREE.
