# Class prompt — fauna: WALKERS (land animals, including pack animals and wall-clingers)

Read `00_preamble.md` first. A walker needs **south, east, north** body facings (west mirrors east).

Look for, in this order:
1. **Facings** — the owner's most frequent complaint class (19 creature rows of one sitting, 2026-09-15:
   *"North is HUGE compared to east, and South isn't south"*, *"Norht isn't north, south isn't very south
   either"*, *"south isn't south, north isn't north"*):
   - south = face toward camera (`F_SOUTH_NOT_FRONT`); north = rear, no face or eyes (`F_NORTH_FACE`); no
     overhead view on any facing (`F_TOPDOWN`); east a true side profile.
   - same size and proportions on every facing (`F_SIZE_JUMP`) — owner 2026-10-22 (Kell dragon): *"it needs the
     treatment that makes the different facings the same size."*
   - same animal on every facing: horns, tails, limbs and any display structure present and turned correctly in each view
     (`F_INCONSISTENT`) — owner 2026-10-17 (Granite slug): *"your different facings went crazy with putting your
     hallucinated mouth on its front and back."*
   - a missing facing (`F_MISSING`).
2. **Alien and specific** (`STYLE_EARTHLY`, `DESC_MISS`): invented creatures must not read as a recoloured Earth
   animal (owner 2026-10-11, *"terran hippo"*; 2026-10-21, *"absurd standing pronghorn"*). The description's
   signature feature (whatever the description names as defining) must be visible and legible.
3. **Canon** (Star Wars, `CANON_MISS`): every `Must show` line yes/no; anatomy errors the owner caught before:
   *"Those two hooked limbs are its front grabbing limbs, not its rear limbs"* (Shyrack, 2026-10-17); *"the front
   legs are supposed to be much bigger than the back legs"* (Zakkeg, 2026-10-17). Engine limits on the card are
   never a reason.
4. **Scale** (`SCALE_WRONG`): body size beside the human against the description ("bear-sized", "camel-tall",
   "hound-sized") and canon (owner 2026-10-17: *"It should be 10 cells wide. SEE CANON."*).
5. **Style** (`STYLE_CARTOON`, `STYLE_OFF`): painterly, realistic, not cute.
6. **Provenance**: a vanilla or other-mod animal standing in for ours is `DONOR`/`PLACEHOLDER` → delete it,
   never the pick.
7. **Alpha/footprint/legibility** (`ALPHA_HALO`, `FOOTPRINT`, `LEGIB_32`, `RES_LOW`).
8. **Duplicates** (`DUPLICATE`): two facings or two candidates that are the same file.

Pack animals: a pack animal may show harness/packs only if the description says so; otherwise a plain body.
Wall-clingers: still drawn standing on the ground in all three facings.
