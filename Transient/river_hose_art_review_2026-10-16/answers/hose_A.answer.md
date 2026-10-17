1. **READS AS**

**The owner is identifying a real scale and connection problem.** The equipment has recognizable parts, but those parts do not consistently describe one working fluid system.

- **Adjacent composites, images 1-2:** the pump reads as a small portable electric centrifugal pump: motor, rounded casing, short hose and outlet elbow. Beside the reel, it becomes an accessory. The reel's large valve housing can compete with it for the role of "pump."
- **Live pump crop, image 3:** the pump reads as a small motorized fitting attached to a much larger plumbing assembly. The lightning symbol obscures its already small casing. The brass coupling and broad tan hose section dominate.
- **Live tank crop, image 4:** the rigid pipe approaches the tank and disappears near its lower-left support. That suggests a possible connection, but does not show a definite penetration into the vessel. It can read as pipe passing behind the tank.
- **Live reel crop, image 5:** the reel reads as a dark rectangular housing or rack. The orange hose loops are visible, but their departure from a drum or guide is unclear. The central block suppresses the reel's identifying structure; its cause cannot be determined from this crop.

Using your dimensions:

| Feature | Width at 64 px/cell | Consequence |
|---|---:|---|
| Flexible hose | About 30 px | About twice the rigid pipe width |
| Hose coupling | About 70 px | Wider than the pump's entire 1-cell allocation |
| Rigid pipe band | About 15 px | Relatively restrained |
| Reel draw envelope | About 179 px | 1.4 times the tank's 128 px envelope |

Those are visual envelope comparisons, not bore measurements. Nevertheless, a coupling wider than the pump cell makes the pump look undersized immediately.

The composites establish relative scale, not live placement or rendering behavior. Their apparent contacts cannot establish an actual connection.

2. **HOW ADJACENT EQUIPMENT SHOULD VISIBLY CONNECT**

**Choose the flow arrangement first, then make the ports express it.** For a dispensing system using the pictured order:

`REEL <- pump discharge | PUMP <- pump suction <- TANK`

The tank supplies the pump; the pump supplies the reel. If the tank is instead being filled, its connection belongs on the pump's discharge side.

**A buildable arrangement for reel | pump | tank**

| Object | Port position in this arrangement | Visible connection |
|---|---|---|
| Tank, right | West end, low on the vessel, above and clear of the saddle | Reinforced nozzle neck, tank flange, mating flange and short suction spool |
| Pump, middle | East-facing axial suction port on the volute | Spool terminates at a distinct pump flange |
| Pump discharge | Radial outlet from the volute, turned toward the near/south edge | Visible elbow and short delivery run routed west, clear of the motor |
| Reel, left | East-side hub inlet/swivel | Short flexible supply whip with compact union into the stationary swivel |

This keeps the pictured motor-left, volute-right arrangement mechanically understandable. An end-suction centrifugal pump takes fluid through its axial suction port and discharges radially; two decorative fittings at opposite motor ends would not express that arrangement. [Grundfos end-suction pump description](https://www.grundfos.com/uk/about-us/media/latest-news/Grundfos-have-the-last-word-in-end-suction-pumps)

Keep the tank suction connection low and reasonably direct. A flooded suction arrangement is plausible when the liquid level is above the pump inlet; the artwork alone cannot establish that condition. [KSB suction and priming reference](https://www.ksb.com/en-global/centrifugal-pump-lexicon/s)

**Use fittings according to their job.**

- **Tank to rigid pipe or pump:** nozzle neck plus a flange pair and short spool. Put the nozzle on the vessel shell, visibly separate from the support frame.
- **Rigid pipe to hose:** a branch tee or terminal elbow, then an adapter and quick-coupler. The hose terminates inside that coupler.
- **Pump to reel inlet:** short flexible whip, compact union and hub swivel. A real reel uses a swivel to feed the rotating assembly; Hannay also specifies a flexible connector between inlet piping and the swivel. [Hannay industrial reel reference](https://www.hannay.com/assets/downloads/literature/Industrial_Hose_Reels.pdf?v=1765518261)
- **Tank directly beside reel:** show a tank outlet feeding the reel swivel only if that is a supported connection. Pressure or elevation must provide the driving force; the reel does not create pressure.

**Separate the reel's inlet from its payout.** Supply enters at the axle/hub swivel. Working hose leaves tangentially from the wound hose surface, through a guide or level-wind if fitted. For this sprite, use the near/lower drum tangent, with a short visible lead through the guide before it curves onto the ground. A parked coupling can hang just beyond the front edge of the stand, clear of the foot. Once deployed, replace that parked tail with the continuous rendered hose.

**The minimum readable joint is:** aligned centerlines, an uninterrupted neck, an enlarged collar, one dark seam and a small contact shadow. Individual threads are unnecessary.

For grid placement, define explicit port anchors. On a 2-cell edge, choose a particular cell lane, such as the lower row, rather than allowing joins to drift toward whichever painted edge is closest. Rotate the port layout with the object.

Adjacency should produce a join when compatible ports face each other. A hose crossing a pipe should remain a crossing unless a branch fitting exists there.

3. **WHAT READS WRONG NOW, RANKED, WITH BUILDABLE FIXES**

All dimensions below are proposed final artwork dimensions at **64 px/cell**, including outlines where applicable.

| Rank | Fix | Buildable direction | Carrier |
|---|---|---|---|
| 1 | Missing physical endpoints | Add permanent nozzle roots and conditional fittings. Use 14-16 px rigid necks, 22-26 px flange diameters and a 2 px dark mating seam. Bridge the actual distance between anchors. | Object sprite + join overlay |
| 2 | Hose and coupling overpower the equipment | Start with 10-12 px ordinary delivery hose and a 16-20 px coupling body, with small latch ears. Keep a separate 14-18 px reinforced suction-hose variant if needed. | Hose renderer + endpoint fitting |
| 3 | Pump lacks visual mass and identity | Prefer the 2x1 skid. Target roughly 108-116 x 46-54 px of machinery/base, with a 40-46 px motor and a 28-34 px volute. Preserve a visible motor-to-casing transition. | Object sprite |
| 4 | Live reel loses its drum and payout | Restore two clear cheeks, a visible wound-hose band, stand and guide. Match the exposed tail's thickness to the rendered hose. Inspect the central rectangle separately before repainting around it. | Object sprite + hose renderer |
| 5 | Painted equipment envelopes compete with occupied cells | Bring the reel's principal structure toward 120-136 px across its 128 px footprint; reserve larger overhang for limited details. Anchor connections to the footprint and port definitions. | Object sprite + placement/render configuration |

**Implement rank 1 before polishing machinery.** A small pump with unmistakable joins will communicate a system better than a larger pump whose pipes merely overlap it.

Additional implementation rules:

- **Object sprites carry permanent structure:** nozzle roots, reinforcement pads, hub swivel, pump casing ports.
- **Join overlays carry connection state:** mating collar, spool, union, adapter and local shadow. Leave an unused port visibly capped or otherwise clearly terminated.
- **The hose renderer owns the deployed path:** start at the guide or fitting anchor, preserve a short exit tangent, and end underneath the coupling lip. Avoid drawing a second baked hose beneath it.
- **At a connected hose/pipe intersection, show a branch.** The pipe continues through the tee; the hose ends at the branch socket. Simply placing brass over the crossing repeats the current ambiguity.

For both Industrial and Modern variants, preserve identical anchors and fitting silhouettes. Red paint improves separation in image 2, but cannot substitute for a joint. Industrial needs a particularly clear bright collar edge and dark seam against the rust.

4. **CRITIQUE OF THE PROPOSED PUMP, IMAGE 6 BOTTOM**

**The 2x1 skid is a strong direction. The current mockup needs a clearer discharge and a more elevated viewpoint.**

What works:

- Motor, coupling region, casing and base now form one substantial machine.
- Its width being comparable to a 2-cell-wide tank is reasonable. Pump capacity cannot be inferred from tank sprite size.
- The spool toward the tank establishes an intentional connection.
- A genuine 2x1 footprint gives the equipment room to read without relying on excessive overdraw.

What I would change:

- **Declare the footprint as 2x1.** Keep the main skid within approximately 112-120 x 48-56 px of its 128 x 64 px allocation. Let controlled fittings reach the join anchors.
- **Raise the viewing angle.** It currently reads strongly as a side elevation: prominent vertical casing, feet and front rail. Show more motor top, casing top and skid deck; shorten the visible front face. Match the tank's existing oblique overhead view rather than forcing strict orthographic plan view.
- **Expose the second fluid port.** The tank-side spool is readable, but the discharge route is not comparably clear. Add a distinct radial outlet and elbow. The top bolted cover currently reads as a casing cover, not an outlet.
- **Resolve flow direction.** If the right-hand nozzle is axial into the pictured volute, the tank is feeding the pump. For a literal "pump to tank" filling arrangement, connect the tank to the radial discharge and supply the axial inlet from elsewhere.
- **Reduce the stack of striped collars.** Use one recognizable flange pair at a joint. The repeated oversized striped pieces compete with the casing and can resemble mechanical shaft hardware.
- **Keep the tank nozzle above the saddle.** The spool should visibly enter the vessel through a neck and reinforcement pad, rather than terminate at the supporting rail.
- **Simplify for reduction.** Keep several broad motor ribs, two or three readable fastener marks per flange, and a strong casing outline. Fine ribbing and rust scratches are secondary.

If gameplay requires the pump to remain 1x1, redraw it as a compact close-coupled unit with a roughly 52-58 px main silhouette and thinner connections. Shrinking this entire skid into one cell would restore the original readability problem.

5. **CONFIDENCE AND LIMITS**

| Claim | Confidence |
|---|---|
| The stated hose/coupling dimensions overpower the current pump | High; follows directly from the supplied dimensions |
| Live contacts lack decisive joint cues | High for these crops; the tank connection is suggestive but ambiguous |
| The current pump depicts a small electric centrifugal pump | High for the composites; medium in the obscured live crop |
| The proposed tank-facing axial port would represent suction on an end-suction pump | High, conditional on that pump interpretation |
| The proposed skid improves identity and relative visual weight | High |
| The proposed viewpoint needs more visible top surfaces | Medium-high; an art judgment against the supplied tank |
| The live reel's central rectangle indicates a rendering defect | Undetermined; it could be artwork, an overlay or another rendering condition |
| The proposed pixel sizes will survive actual game zoom | Medium until tested in-game |

I could not judge actual connection logic, port coordinates, rotation handling, draw layers, texture filtering or the cause of the reel rectangle. The crops also do not establish flow direction, liquid level, pump duty or hose rating.

The decisive next check is one actual-scale in-game placement of **tank -> pump -> reel**, plus one connected hose/pipe branch and one unconnected crossing. At ordinary play zoom, each should explain its connection through silhouette and fitting placement before texture detail is inspected.