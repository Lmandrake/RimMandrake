## 1. READS AS

Both images inspected. Image 1 is an offline scale/composition test; it provides no evidence of the actual game's water rendering.

| Object | Honest read at 32-64 px/cell | Confidence |
|---|---|---|
| Weir | A tapered timber-and-net fishing structure, possibly a fish fence or collapsed walkway. The broad end looks barricaded. It does not clearly read as a low dam. | High |
| Bank stake | A lantern on a wooden bollard. The yellow lamp is its strongest identifying feature. Three separated examples read as bank lighting, with no visible flood barrier. | High |
| Silt trap | A short timber fence, palisade, or retaining panel. Sediment capture is not visible. | High |
| Ferry post | A rope winch or mooring bollard. The spool helps, although its side projection dominates the silhouette. A ferry connection requires context. | Med |
| Ferry rope | Clearly rope in the enlarged sheet. At game zoom, probably a pale connecting line; the braid will mostly disappear. Actual thickness depends on its draw size. | Med |
| Sluice box | A wooden trough with transverse bars, but also potentially a ladder or chute. The broad wet intake helps identify its function. | Med |
| Panning spot | A pan or basket on gravel between stones. The activity is plausible; the tiny gold flecks are unlikely to identify it at ordinary zoom. | Med |

## 2. WHAT A REAL ONE LOOKS LIKE

The hydraulic descriptions below are high confidence. The proposed minimum art cues are medium confidence until tested at game zoom.

- **River weir:** A low barrier across the flowing channel, with water passing over a recognizable crest. For ordinary free overflow, show a smoother upstream pool, a narrow spill edge, and broken white water immediately downstream. A submerged weir can have little visible drop, so permanent waterfall foam is not universally correct. **Minimum cues:** continuous cross-channel crest, bank connections, and different water treatment on its two sides. [USGS weir hydraulics](https://pubs.usgs.gov/publication/ofr20221011/full)

- **Stake-line levee:** Stakes can retain an earth bank or support a continuous floodwall. Separated poles, even connected by rope, do not contain water. **Minimum cues:** an uninterrupted earth ridge or filled timber wall between posts, a visible crest, and connected corners/endpoints. Lamps can remain secondary markers. [FEMA levee description](https://emilms.fema.gov/is_0274/groups/30.html)

- **Silt trap:** Sediment settles where flow slows sufficiently. Your river-margin version needs a baffle that creates a sheltered pocket against the bank; an isolated fence on dry ground does not explain the function. **Minimum cues:** wet baffle, quiet pocket, and a shallow sediment deposit inside that pocket. Keep the deposit away from the visibly scoured tip. This applies the settling principle to your particular design. [EPA sediment traps](https://www.epa.gov/system/files/documents/2021-11/bmp-sediment-traps.pdf)

- **Ferry rope and posts:** For your proposed rope ferry, show anchored posts on opposite banks and an uninterrupted working line between them, with a raft or landing establishing its purpose. **Minimum cues:** stout post tops, rope leaving the spool tangentially, continuous connection, and aligned landings. A spool alone establishes a winch, not a ferry.

- **Sluice box:** An open trough carrying water downhill over transverse riffles, which retain heavy material. **Minimum cues:** two rails, a visible wet bed, several broad riffles, an upstream feed, and an open downstream discharge. Your existing design already contains most of this vocabulary. [NPS sluice description](https://www.nps.gov/articles/kantishna-gold.htm)

- **Ford stones:** A ford is a shallow crossing with firm footing; exposed stepping stones are one possible treatment. **Minimum cues:** a bank-to-bank crossing alignment, broad stone tops, water visible between stones, and approaches meeting both banks. Avoid a continuous raised crest that would make it read as another dam. [USFS ford guidance](https://www.fs.usda.gov/t-d/pubs/pdfpubs/pdf07232806/pdf07232806dpi300.pdf)

## 3. WHAT IS WRONG WITH OUR WEIR, AND THE FIVE FIXES

**The main problem is structural identity.** The tall posts, hanging mesh, taper, braces, and end palisade describe an upright fishing fence more strongly than a low overflow barrier. There is no obvious continuous crest. **[High]**

**The perspective is too elevated and directional for simple rotation.** Large upright faces and sloping braces establish a particular camera view. Rotating the bitmap 90 degrees rotates those elevation cues sideways instead of showing the structure from another heading. The supplied rotation makes it resemble a timber object laid across the water surface. **[High]**

**Its axis crosses the river, but its reach does not span the channel in this composite.** It connects to the right bank and terminates in open water, leaving a substantial passage toward the left bank. That can support a bank fishing wing or local sheltered pocket; it does not visually explain a channel-wide impoundment. **[High for the visible gap; med for the resulting hydraulic effect without depths and elevations.]**

**There is no visible water interaction.** The composite shows neither a spill edge nor upstream/downstream differentiation, wet contact, or tip wake. That is a finding about this composite only. **[High]**

All dimensions below are **final screen pixels at 64 px/cell**, before the supplied 3x enlargement. Halve them at 32 px/cell. These are starting specifications, not measured optima.

1. **Replace the hanging-fence silhouette with a low barrier. [Med recommendation]**  
   **Layer: sprite.** Within the roughly 141 px long draw envelope, draw a 124-136 px continuous timber/stone crest. Give it a 20-28 px body depth along the flow direction. Use three or four 6-8 px post caps, a 3-4 px crest highlight, and a 2-3 px downstream face shadow. Reduce tall mesh panels and projecting braces. Keep the main body within the one-cell depth budget.

2. **Make the water establish the function. [Med recommendation]**  
   **Layer: terrain overlay.** For an illustrative downward-flow orientation, place quiet water above the horizontal crest and turbulence below it. Mask or reduce current streaks over the affected upstream cells; fade the treatment near the gameplay area's boundary. Eight cells is your gameplay extent, not something this sprite establishes hydraulically.  
   **Layer: separate animated water mote.** Add a broken 2-4 px spill highlight immediately downstream of the crest, followed by an irregular 8-16 px foam apron. Move small foam patches 4-8 px downstream before fading. Clip everything to water. For flooded/submerged states, weaken the distinct spill line.

3. **Author directional views and solve the open end. [High diagnosis; med specification]**  
   **Layer: sprite.** Draw four headings from the same fixed camera convention. Post tops remain tops; short visible upright faces continue to project toward screen bottom. Rotate the plan layout, then redraw elevation and lighting cues.  
   **Layer: connected sprite segments.** If channel-wide calming is intended, let repeated sections connect to the opposite bank. A fixed two-cell object cannot span arbitrary river widths. If the object must remain a single bank projection, retain the open end and show a local sheltered pocket plus flow bending around its tip.

4. **Give the bank-end store a separate silhouette. [Med recommendation]**  
   **Layer: sprite.** At the shore attachment, replace part of the dense palisade with an approximately 18 x 22 px lidded basket or screened box. Use a dark opening at least 6 x 8 px and a broad lid rim. Connect a short slatted guide to that opening. Uprights projecting above the crest can explain drift interception while water passes through or over the lower barrier.

5. **Draw the breach where the water can pass through it. [Med recommendation]**  
   **Layer: damaged sprite variant.** Remove a 20-28 px section of crest and fill; leave one broken stump and displaced timbers at its edges.  
   **Layer: separate animated water mote.** Send a narrow, fast foam plume through that opening. Remove the intact spill treatment across the gap. A coherent intact-versus-breached silhouette will communicate flood failure better than extra surface scratches.

For source work, convert these screen dimensions using the actual texture-to-draw-size ratio. Raw texture dimensions alone do not establish visible feature size because transparent margins matter.

## 4. STAKE AND SILT TRAP: TOP TWO FIXES EACH

**Bank stake**

1. **Build the barrier between lamps. [High need; med dimensions]**  
   **Layer: connected sprite.** Add a continuous 16-24 px wide earth ridge or filled timber crib between neighboring stakes, including corner pieces. Give the crest a 3-4 px light strip and its lower face a broad shadow. Connectors must reach adjacent cell edges; rope or rails alone will still read as fencing.

2. **Reduce the lamp's dominance and flatten the perspective. [Med]**  
   **Layer: sprite.** Retain a compact 4-6 px yellow lamp window, but shorten the long exposed post face and emphasize its top cap. Put the lamp on the levee crest.  
   **Layer: terrain overlay.** Add a narrow damp strip along the water-facing toe to establish the bank relationship.

**Silt trap**

1. **Show the baffle entering margin water. [High need; med dimensions]**  
   **Layer: sprite.** Redraw the roughly 77 px draw envelope around a 60-70 px long low panel with an 8-12 px visible face and three 5-7 px post caps. Keep its bankward end embedded in shore.  
   **Layer: terrain overlay.** Occlude the panel's lower edge with water and add a 2-3 px dark wet band.

2. **Draw the sheltered settling pocket. [High principle; med placement/specification]**  
   **Layer: terrain overlay.** Place a roughly 24 x 40 px muted brown sediment tongue in the sheltered bank-side pocket, aligned to the actual current. Fade it into the bed and suppress strong streaks inside it.  
   **Layer: separate animated water mote.** Add a small ripple around the exposed tip. The quiet pocket should be visibly distinct from that moving water.

## 5. CONFIDENCE AND LIMITS

- **High:** Visible silhouettes, excessive upright faces, the sideways perspective cues after rotation, the composite's open channel gap, and its absent water interaction.
- **High:** Continuous containment is necessary for a levee; a settling pocket explains sediment capture; overflow direction distinguishes a weir's two sides.
- **Med:** Object recognition at ordinary zoom, the ranked art choices, and every proposed pixel dimension. These need a 64 px/cell and 32 px/cell preview against actual RimWorld terrain.
- **Low/unknown:** Actual in-game rotation handling, draw offsets, alpha margins, placement rules, water masking, animation, collision, flood behavior, and whether connected sections already exist.
- **Not inferable:** Flow direction from the static streaks, water depth, crest elevation, discharge, or whether this geometry could produce an eight-cell backwater.
- **Not shown:** Ford-stone art. The ferry, silt trap, sluice, and panning spot also lack scene-scale placement examples; their game-zoom assessments are predictions from the raw sheet.