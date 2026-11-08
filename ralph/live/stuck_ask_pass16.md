# Stuck: wall graffiti in RimWorld still reads as dirt to a blind judge, after three different fixes

## What the player should get
A RimWorld mod paints graffiti on walls (tags, throw-ups, stencils, doodles, mockeries with a pawn's head, sigils). At play zoom (64 px per cell, a mark is ~64-190 px wide and ~40 px tall on a wall face) every mark must read as paint a person put there on purpose, never as dirt, grime, mould, soot, rust, blood or debris. Ugly marks (by unskilled hands) must look clumsy, not like stains. Marks must read as punk/urban street marks, not badges or clip-art.

## What happens (blind judge, pass 16, `blind_judge_p16.md` attached; shots attached)
Still "dirt: yes", "register: mixed". Read as dirt: an awful hand's olive-and-soot swirl face (mould), a poor black-and-ochre wolf head (scorch), a W3-weathered magenta throw-up (old grimy stain), a poor pink-and-teal Vandal scrawl in a dim storeroom (mouldy smear), dark overspray/black-blot parts of a warning glyph and a mockery (soot/ash), a pale weathered gear (plaster patch / bird droppings), a pale weathered scribble (chalk dust / dead weed), red tags drawn sideways on walls seen edge-on (rust or blood runs), a green tag edge-on (moss). Read as badges: every raised-fist stencil (clean emoji fist), an ideoligion icon in a sprayed ring (badge), skull/crossbones-like mockeries, a cog-and-hammer stencil (gear logo), a tribute ring with sparkle stars.

## What was tried, and what each showed
1. Pass 14: weathered marks kept a faint stain of their whole shape (flakes alone read as debris). Judge pass 15: W2-W4 read as rust, grime, ash, dry grass.
2. Pass 15: tribute frames redrawn as sprayed crown/roses. Portraits still read as UI icons.
3. Pass 16 (this build): weathering now chalks paler in the paint's own hue instead of greying, eats less, keeps more alpha; no brown "mud" on unskilled hands' paint; Vandal art regenerated in clashing dusty pink/teal/mustard/violet with no green/olive/brown; portraits now 3-tone stencils in the mark's pigment; fist without its ochre disc; halo frame one sprayed loop; throw-up fill magenta (chalk had read as rock chunks); soot pigment only on pale walls; legacy pictures moved off edge-on walls. Result above: rock chunks and UI portraits are gone from the list; faint, thin, dark-edged or pale-weathered marks still read as stains, and clean single-colour silhouettes read as emoji/icons.

## The rendering, briefly
Each mark is a texture drawn in the plane of the wall face (two coats on the face), then the wall's own atlas is drawn back over it at 12-40% so the wall's courses show through. Unskilled hands: wobble, more wall show-through, and a thin offset "second go" under the mark at 28% alpha. Weathering: noise-eaten flakes with a pale stain where paint is gone. Some art is pigmented (pale drawing tinted by one of 8 dull pigments chosen to contrast the wall), some pre-coloured.

## Ask
What, concretely, makes paint at ~40 px tall read as deliberate paint rather than a stain, and what makes a single-colour stencil read as street rather than as an icon? Give me the two or three changes most likely to flip "dirt: yes" for the weak, weathered and unskilled marks, and say which observation would show each one worked.
