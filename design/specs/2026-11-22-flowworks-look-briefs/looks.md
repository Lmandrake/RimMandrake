# FlowWorks looks: what each of the four looks represents

Item: `RIMMANDRAKE_REDRAW_FLOWWORKS_TANKS_THREE_STYLES_ONLY_SCRAPPER_READS_RIGHT`. Written 2026-11-22 on the owner's
order at the FlowWorks walk: *"Give the briefs for what the four styles normally represent, including that Industrial
also serves "Star Wars standard" and futuristic is more like cyberpunk."*

These briefs drive every FlowWorks look asset (tanks, pipes, sprinklers, pumps, reels, weirs, containers), not only the
tanks. A look is one of Scrapper, Industrial, Modern, Futuristic; the player picks it per building with the shared style
picker (`design/specs/2026-11-20-vanilla-electrical-art-home/design.md`). Each brief is a target for the artist and a
constraint for the art judge (`design/RimMandrake/art_judge_brief.md`). A look's colour range is an option, not a ban
(judge brief B5). Every look is drawn from the one building camera (judge brief C3).

The owner's words that set each look are quoted from the ledger (`python3 src/RimMandrake/rimflow/owner_rulings.py --grep
<word>`), with their dates.

## Scrapper: hand-built from salvage, the reference that reads right

- **Represents:** a Jawa-clan or frontier build. It is made from what was found: mismatched salvaged plates, strapping,
  wire lashings, timber skids. It works, but nobody bought it new.
- **Materials:** riveted steel plates of different ages, patched over each other; copper and brass fittings; scrap
  timber skids; rope or wire lashing; hose clamps.
- **Wear:** heavy and honest. Rust, verdigris, paint from earlier lives (a green panel, a red panel), dents and patches.
  The wear says "salvaged and kept running", never "abandoned".
- **Colour range:** rust orange, oxide brown, faded olive and brick-red panels, bare steel grey, copper.
- **Instruments:** salvaged analog pressure gauge, hand valves with red wheels.
- **The reference:** the shipped Scrapper tanks (`src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank/Scrapper/`).
  Owner 2026-11-22: *"Only the scrapper one looks ok right now."* Do not redraw it for this item.
- **Must NOT look like:** a clean factory product; a single paint colour; a different camera or scale from the other
  three looks.

## Industrial: working heavy industry, and the Star Wars standard

- **Represents:** two things at once. (1) Working heavy industry: a plant, a depot, a mine. The owner called it
  *"brutalist"* (2026-10-23: *"Modern should instead be thought of as "modern consumer / commercial" and industrial is
  "brutalist""*). (2) The **"Star Wars standard"**: the used-future look of the setting's ordinary hardware. That is
  functional, bolted, panelled, maintained by people who need it to work tomorrow (owner 2026-10-04: *"The Jawa should use
  the star-wars grungy industrial look."*; *"an industrial grungy steel Star Wars-style one"*).
- **Materials:** heavy painted steel plate, big bolts and flanges, welded seams, cast fittings, steel skids or a cast
  saddle base. Paint over steel: gunmetal, slate, dull sand-grey or olive drab. Hazard stencils and plates are allowed.
- **Wear:** honest working wear. Scuffed paint on edges, grease and dust at the base, a few rust weeps at bolts and seams.
  The steel is painted and the paint is mostly whole. Owner 2026-11-22: *"The industrial tank is a bit... rusty. Could we
  clean up some of the rust a bit? Otherwise it reads well."* and *"The Industrial one looks ok but is rusty and abandoned
  looking."*
- **Colour range:** dark gunmetal, slate grey, sand-grey, olive drab; yellow-black hazard bands as accents; brass gauge
  faces.
- **Instruments:** an analog dial gauge suits it (owner 2026-11-22: *"The analog dial would look good on the Modern and
  Industrial one though."*). Hand wheels, sight glasses, levers.
- **Must NOT look like:** rusted through; abandoned; a wreck; Scrapper with stripes. Not consumer-glossy, not Modern.

## Modern: what you would really see today, behind a store or on a farm

- **Represents:** present-day real equipment, consumer and commercial (owner 2026-10-23: *"Modern water tanks. Modern hose
  reels. Like you would buy in home depot or find behind a modern store."*; *"modern consumer / commercial"*). For tanks
  the owner picked the real types by card on 2026-10-23: a white leg tank (short), a green poly tank (tall), an IBC tote
  and a white poly tank (cargo).
- **Materials:** UV-aged polyethylene, galvanised steel cages and straps, painted carbon steel, PVC and brass fittings,
  ductile-iron water mains with bolted flanges.
- **Wear:** realistic, normal wear. Smudges, dust, dirt splash at the base, sun-faded paint, water stains, scuffs, a
  label that has faded. Owner 2026-11-22: *"The modern tank reads very cartoonish, needs to be more realistic with some
  smudges and normal wear."* For pipes and the sprinkler, owner 2026-11-22: *"they need to have a little bit of "realism"
  added in terms of some patches of differently colored paint or other non-cartoonishness added. That's what's reading
  futuristic. They look plastic."*
- **Colour range:** off-white and faded poly colours (green, black, tan), galvanised grey, the faded waterworks blue the
  owner chose for the pipe system (2026-10-24), with patches of older or touch-up paint in other colours.
- **Instruments:** an analog dial gauge suits it (owner 2026-11-22, above). Ball valves, brass taps, stick-on level
  labels.
- **Must NOT look like:** cartoonish, plastic or toy-like; a flat clean colour with a glossy highlight; a primary colour
  used as a tier marker (owner 2026-11-06: *"you KNOW that you're not supposed to just use bright red for modern."*); a
  futuristic object.

## Futuristic: cyberpunk, computerized, sleek

- **Represents:** a high-tech future, closer to cyberpunk: a computer-managed tank or line, elegant and sleek (owner
  2026-10-04: *"sleek cybertek-style"*). Owner 2026-11-22: *"The futuristic one just looks like the industrial one with a
  steampunk vibe. It should be more computerized and elegant, sleek with little control access points to slide open access
  ports. No simple analog dials, they should be computerized readouts."*
- **Materials:** seamless composite or ceramic shells, brushed titanium or graphite trim, flush panel lines, glass or
  polymer display windows. Earlier owner taste for this look: *"the same white metal and pale blue "lights""* (2026-10-24,
  weirs). Darker graphite with neon accents is also in range.
- **Wear:** low. Clean, with at most a faint dust film at the base. Sleekness is the point.
- **Colour range:** white or pale grey composite, graphite or matte black, brushed titanium; light accents in cyan, pale
  blue, magenta or amber.
- **Instruments:** computerized readouts only: small lit screens, LED level bars, status lights. Small control access
  points and flush ports whose covers look like they slide open; one may be shown slid open.
- **Must NOT look like:** steampunk; brass, rivets, exposed bolts, hand wheels or analog dials; a recoloured Industrial
  shape with blue lines painted on; bulky exposed plumbing.

## What this changes

- New and redrawn FlowWorks look art is judged against these briefs.
- The 2026-11-22 tank options and the Modern pipe and sprinkler options were drawn to them (review sheet and option
  images: see the item's notes).
