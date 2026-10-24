# HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS

Owner 2026-10-23 22:15: "There should be constraints on the absolute (location), first derivative (slope/angle), and
second derivative (curvature) of the hoses ... Each pipe segment must join with the others absolutely by location and
slope and curvature. ... Please do this right, this is getting embarassing."

Design + numbers + remaining failures: `design/RimMandrake/flowworks_hose_geometry_g2_2026-10-23.md` (§6 lists them).
Progress / handoff file: `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023.md`.
GPT attack raw reply: `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\gpt\answer.md`.

State at 07c6eeeeb4 (published d659c88130): ruler + hard stations + clothoid-chain fit landed, G2 OFF in game
(`HoseMath.G2On = false`, solver too slow). `--hose-curves`: today 17/58, `--hose-curves g2` 30/58.

Next, in order:
1. Speed: analytic Jacobian (d position / d kappa_i is a closed form along the chain) so a lay solves in ms; then G2On=true
   and the full selftest (incl. hose fuzz 4298 cases) stays under its old time.
2. Mates: MateTail through HoseClothoid.TailOnto, length conserved, partner clearance kept (mateA 4.9 -> 21.3 cells today).
3. Tank ports: lay to the flange with endInward = port axis (EnsureLay + HoseCurveChecks alike).
4. Infeasible fits (short, tankW, uturn stall): re-plan the route wider instead of falling back to the shaped pose.
5. Remove the `{pre-mate: ...}` diagnostic in HoseCurveChecks once mates pass; put --hose-curves in the default run when green.
6. Still owed from the brief: before/after previews (`--hose-curves dump`), second GPT consult with images (owner
   screenshots 20261023221102/221228/221721, br1e_caps, br1f_caps, judge_crops), review_map.py stations + northstar
   hose_curve_proof.py + its selftest, full-read code review + mark-clean, then implemented with the live check owed
   (recapture both owner screenshot scenes plus the three hard stations).
Owner item: relay reel has one connector (design §7).
Finding (unverified, from the first run): the lay's lead-out join refuses ends 3.5-3.8 cells away that a clothoid could reach; check when fixing step 4.
