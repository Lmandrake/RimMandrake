**The machines read individually, but the plumbing does not.** My first impression is “large hose dispenser, small loose pump, storage tank.” Placement suggests a relationship; the open mouths and disconnected hose ends contradict it.

All dimensions below are **native pixels at 64 px/cell**. Current measurements are approximate, taken from the 2× composites and divided by two. The live crops establish appearance and relative proportions; their zoom is not established.

**1. What players believe happens**

In the offline lineup, players will probably infer **reel → pump → tank** from reading order. The hardware does not confirm that interpretation:

- The reel’s large valve housing looks capable of pumping by itself. The actual pump looks like an accessory.
- The reel’s hose points toward the viewer, while the pump’s mouths point elsewhere.
- The tank has no obvious receiving socket facing the pump.
- Modern’s red paint groups the machines, but does not clarify their connections or direction.

For a dispensing system, my preferred interpretation would actually be:

```text
REEL  ←  PUMP  ←  TANK
  |
  └── deployed hose → user/tool
```

If gameplay instead fills the tank from the reel, reverse those arrows. **Adjacency should communicate connection; the pump should communicate direction.** Put a persistent, high-contrast arrow about **10 × 6 px** on the pump’s clear upper surface. During operation, optional moving ticks can reinforce it.

The live pipe entering the tank communicates continuity better than the offline arrangement. However, the thin orange loops, frayed-looking end, and nearby lightning symbol make the deployed hose easy to read as electrical cable. The dark rectangular reel also loses the drum silhouette that would explain where those loops originate.

**2. The three biggest proportion problems**

| Problem | Current read | Recommended target |
|---|---|---|
| **Reel overwhelms an equally sized tank** | Reel including projections ≈ **168 × 140 px**; tank ≈ **120 × 94 px**. Both occupy 2×2 cells, but the reel is about **1.4× wider**. | Reel including fixed projections **112–124 × 112–124 px**. Reduce its oversized valve housing as well as the drum. Keep the tank near its current size. |
| **Pump has weak visual authority; proposal overcorrects** | Current pump ≈ **58 × 46 px**, but much of that is projecting hose and mouths. Proposed assembly is roughly **135 px wide**, over **two cells** for a 1×1 machine. | Recognizable motor/volute/base silhouette around **48–54 × 38–44 px**, with fixed sockets reaching at most **64 px overall**. Increase useful body mass, rather than scaling everything. |
| **Hose, pipe and couplings suggest different systems** | Reel tail roughly **10–14 px** thick; its coupling including ears roughly **24–28 px** across. Live orange hose is much thinner than the rigid pipe and brass connector. | Shared service bore represented by **6 px hose**, **8 px rigid-pipe outside diameter**, **12 px hose union**, and **14 px flange**. A hose-end assembly should be about **10 px long**, not a second machine. |

A larger trunk pipe can exist, but show a deliberate reducer into the **6 px branch**. A thin hose apparently entering a huge brass collar makes the collar look like a nozzle or separate apparatus.

**3. A small connection kit**

Use the same geometry and silhouettes in both looks. Industrial gets dark steel, restrained rust and brass; Modern gets clean metal with red collars. Keep the mating band bright enough to survive against dirt.

Sizes below are **length along flow × width across flow**, except square pieces.

| Piece | Native size | Placement and purpose |
|---|---:|---|
| **Port stub** | **8 × 8 px** | Fixed machine socket facing the compatible edge. Root overlaps the body by **2–3 px**. |
| **Flange collar** | **3 × 14 px** | At a rigid port’s mating face. One strong rim and a few bolt marks suffice. |
| **Straight spool** | **4 × 8 px** repeat | Extends between exposed stubs. Repeat or stretch the plain middle; preserve the ends. |
| **Hose union** | **8 × 12 px** | At a detachable hose connection. Use a distinct central seam. |
| **Hose end / ferrule** | **10 × 12 px** | Terminates the **6 px hose**; overlaps it by **3 px**. Meets the union directly. |
| **Blanking cap** | **3 × 10 px** | Closes an unused socket. Connected state replaces it. |
| **Elbow** | **14 × 14 px** | Optional quarter-turn using the same **8 px pipe**. For a designed route, not a rescue for arbitrary misalignment. |
| **Saddle** | **10 × 10 px** | Optional support beneath a longer exposed run. Never required to prove connection. |

That is **six core pieces plus two optional pieces per look**, reused across machines. Directional lighting may require orientation variants; adjacency should not require bespoke reel–pump–tank paintings.

Automatic selection should follow these rules:

1. **Declare ports and roles.** The pump has opposed inlet/outlet sockets. The reel has a fixed supply socket and a separate payout guide. The tank has designated service sockets.
2. **Use cell-edge anchors.** At a shared edge, put an anchor at the touching cell’s midpoint: **32 px along that cell edge**. A 2×2 machine therefore has candidate positions **32 or 96 px** along a side. Avoid its overall side midpoint of 64 px, which cannot align with a neighboring 1×1 pump’s center.
3. **Connect only compatible, facing ports across a shared edge.** Proximity or diagonal contact should not produce plumbing. Where several connections are possible, choose deterministically and retain the choice until placement changes.
4. **Replace caps and bridge the actual visible gap.** Use a spool for rigid-to-rigid; a ferrule/union for hose-to-port. Do not stack every fitting on every connection.
5. **Draw each join once.** Give one object ownership of the shared-edge connector. Hide its roots beneath the bodies, while keeping its middle visible.
6. **Preserve the arrow’s meaning under rotation.** Derive direction from the pump’s inlet/outlet roles, never from screen-left versus screen-right.

For this particular dispensing lineup, the **tank’s west socket meets the pump’s east inlet**, and the **pump’s west outlet meets the reel’s east supply socket**.

**The minimum convincing join is two rooted sockets, an uninterrupted bridge, and one readable mating seam.** Leave **8–12 px of bridge exposed** between silhouettes where possible. A flange floating in a gap, or a pipe disappearing behind a tank foot, is insufficient.

**4. How the hose should leave the reel**

It needs two visibly different connections:

- **Fixed supply:** a short pipe into the reel’s axle through a rotary union, on the pump-facing side.
- **Payout:** flexible hose leaving the wound drum **tangentially**, passing through a guide, then reaching the deployed endpoint.

For this view, I would pay out from the **lower/front tangent**. Let the hose remain traceable for **12–18 px** before its first substantial bend, with a centerline bend radius around **12 px**.

**Yes, add a visible outlet guide.** A **16 × 10 px fairlead with a 6–8 px opening** is enough. Align that opening with the first straight hose segment. A detailed traversing level-wind mechanism is optional at this resolution.

The guide should line up with the **hose path**, rather than always pointing at the distant coupling. When deployment changes direction, the hose curves after leaving the guide.

When connected, the current dangling coupling should become the actual endpoint at the receiving port. When idle, park it in a visible cradle. Leaving a decorative loose end on the reel while another hose appears elsewhere implies two hoses.

**5. Five changes ranked by value per effort**

| Rank | Change | Value / effort |
|---:|---|---|
| **1** | Add facing sockets and continuous adjacency bridges, including an explicit tank port. | **Very high / low–medium.** Establishes that a system exists. |
| **2** | Add a clear pump flow arrow and rotate it with the functional ports. | **High / very low.** Resolves direction immediately. |
| **3** | Standardize hose, pipe and fitting gauges; make connected and parked hose ends mutually exclusive. | **Very high / medium.** Fixes continuity across both offline and live views. |
| **4** | Reduce reel scale and valve dominance; restore a readable drum silhouette in live rendering. | **High / medium.** Corrects hierarchy and identifies the orange line’s source. |
| **5** | Rework the pump into a compact motor/volute silhouette with opposed sockets. | **Medium–high / medium.** Makes its role readable without consuming another machine’s space. |

I agree with the proposal’s **recognizable motor, pump housing and continuous connection**. I disagree with its **two-cell width**, repeated hazard-striped collars, and connection disappearing around the tank’s support. Those details consume the space needed to read the join.

Keep its motor/volute idea, compress it to the one-cell envelope, remove most of the striped fittings, and land the bridge on a clearly exposed tank socket. That delivers the proposal’s useful improvement at a scale consistent with the game.