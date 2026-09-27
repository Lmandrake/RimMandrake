# The Twilight Sea — underwater flora design pass (2026-09-27)

**Item:** `TWILIGHTSEA_FLORA_PASS_1` · DESIGN pass (Fable subagent, 2026-09-27). Sibling of
`the_scald_underwater_flora_pass_2026-09-27.md` in shape; nothing in content is shared with
any other sea's roster, by commission.

## Commission

Owner, by question card 2026-09-26 (recorded on `SCALD_UNDERWATER_FLORA_1`'s ruled block):
**every sea floor gets its own strange-flora design pass** — the Scald's verbatim brief was
*"strange little underwater 'plants' like strings and filaments of bacterial colonies,
sponges, soft corals, all with alien twists; it should not be barren"* — and the Twilight's
is commissioned in the Twilight's OWN register: **the light economy**. Here light is
currency, tenancy and danger (`the_twilight_deep_light_economy_pass_2026-09-27.md`), so the
native strange flora are the ones that **make, hold, steal or spend light**.

This roster is deliberately NOT the content drop's fourteen seaweed analogs
(`the_twilight_deep_content_2026-09-26.md` §3 — oruvell, ghallowyn, sennefan and the rest,
still proposed, not built). Those are the sea's canopy and crops. This pass is the small
strange stratum beneath them: the bacterial strings, the sponges, the soft corals — the
Scald commission's categories, run through the Twilight's physics.

## Sources read

- `design/Jawa/worldbuilding/biomes/the_twilight_deep.md` — the frozen sheet (waveglass
  amendment 2026-09-26; the six hard bans; "darkness between, busy and alive").
- `the_twilight_deep_content_2026-09-26.md` — the content drop: the fourteen seaweeds, the
  clinging layer, the colour grammar (gold = home and harvest, blue-white = moving, green =
  growing), the channel mechanism, the bioluminescence rules (§6).
- `the_twilight_deep_light_economy_pass_2026-09-27.md` — the well-ledger (wells live 5–9
  days), warning stages, the constellation cap, the sun-sphere arc, leases and charts, and
  the 🔴 glow-grid-only engine trap (§1.4).
- `the_twilight_deep_danger_pass_2026-09-27.md` — the lightweb: the suulk grazes the
  brightest player-owned glower; the vaulisk counterfeits a gold lamp, one per map, tell
  always readable (no breathing pulse, no piip, dead ring); lid-dark; the sink.
- `the_scald_underwater_flora_pass_2026-09-27.md` — the sibling pass, for shape, and its
  ruled precedent: a twist borrowed from another biome's register is *silly* and gets cut.
- `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TwilightSea.xml` — live def, re-measured
  this pass (see below: the brief's "wildPlants empty, plantDensity unset" is now stale).
- `Defs/ThingDefs_Plants/RM_TwilightSeaFlora.xml` and `RM_TwilightLightPlants.xml` — the
  three plants that already ship (salt blade, hoolimbre, noothelm) and the shared engine
  facts their headers record.
- `Defs/MapGeneration/RM_TwilightChannels.xml` + `Source/RM_GenStep_TwilightChannels.cs` —
  the channel genstep paints **`RM_ChannelBed`** and **`RM_BankSilt`** (via
  `GetNamedSilentFail` + `PaintIfPresent`, so it tolerates the terrain defs not existing
  yet — they do not, as of this reading; the names are nonetheless established).
- `Defs/ThingDefs_Buildings/RM_TwilightSkylight.xml` (`RM_Skylight`, glowRadius **6.0**,
  gold `(255,214,130)`) · `RM_TwilightLightEconomyItems.xml` (`RM_LampBladder` glow 2.5,
  `RM_NoothelmBulb`, `RM_TetherChain`, `RM_SkylightRight`, `RM_WellChart`) ·
  `RM_VauliskLure.xml` + `RM_TwilightScatterVauliskLure.xml` (the liar and its scatter) ·
  `RM_SuulkArrival.xml` (the grazer's incident).

All ten proposed defNames collision-checked against `src/` and `design/` (recursive grep,
2026-09-27): **tithemoss, gloamurn, murkspindle, weircomb, tollhorn, hushcoral, gleamfloss,
glimmerhusk, farwick, almslight — every one FREE.**

## Current state of the biome — re-measured, and the brief's premise is stale

The commission described `RM_TwilightSea` as "wildPlants EMPTY and plantDensity unset."
**No longer true** — `TERMINAL_SEAS_FLOOR_DRESSING_1` and `TWILIGHT_LIGHT_ECONOMY_1` landed
between the briefing and this pass (shared tree; numbers decay). Live def as read
2026-09-27: `plantDensity` **0.2**, and three `wildPlants` rows —
`RM_SaltBladeTwilight 0.03` · `RM_HoolimbrePlant 0.15` · `RM_NoothelmPlant 0.05`. The
mat-roof plant is retired (the ceiling is an event + item, `RM_VeilPane`), the vanilla
`Plants` genstep is registered, and the three engine facts are already paid: floor plants
need `completelyIgnoreFertility` (the floor is fertility-0 `RM_SeaFloorGround`), density
and the genstep both had to be added, and were.

So this pass **owes an upgrade, not a rescue**: a floor with two lamp-plants and one sparse
blade is lit but still nearly barren — exactly the state the Scald commission ruled
against. The three incumbents stay, unchanged; everything below is added around them.

## Where flora can live

Four grounds, already distinct in the built and ruled systems:

1. **Shaft cells** — under a standing `RM_Skylight` (glow 6.0 gold). The bright, contested,
   *temporary* ground: everything here dies or changes when the well closes (5–9 days).
2. **The dark between** — open `RM_SeaFloorGround` outside any glow. The loohn's, suulk's
   and vaulisk's country; the standing threat surface.
3. **Channel banks** — `RM_BankSilt`, the current-fed silt strip between the stake-line and
   the bed. The richest ground; refreshed by the undersurge.
4. **Bottom-house adjacency** — the Compact's lamp-lit yards, stakes and buoy-rings: ground
   that is lit *permanently*, by tenants rather than by the sky. Flora here are planted
   practice, not wilderness (Route B dressing near the Inhabited houses).

The channel **bed** (`RM_ChannelBed`) stays bare by design — it is the current's, and ban 3
says entering it means sinking with it. No plant below grows on the bed.

## The roster

Ten new flora. The organizing law, matching the Scald pass's discipline (there: each
plant's survival trick in boiling water is its twist, no two repeat): **each plant here is
one VERB of the light economy, and no two verbs repeat.** Named up front so distinctness is
checkable: *tax* (tithemoss), *bank* (gloamurn), *refuse* (murkspindle), *mint* (weircomb),
*record* (tollhorn), *answer* (hushcoral), *inhabit* (gleamfloss), *eat* (glimmerhusk),
*carry* (farwick), *give* (almslight). The incumbents already own their verbs — hoolimbre
and noothelm *sell* light (the harvest lamps), the salt blade abstains — so nothing below
is a harvestable lamp; that register is taken.

Every glow entry states what it does to the **suulk/vaulisk lightweb** and to **well
tenancy**, per the commission. All names invented, franchise-free `RM_` tier (Q11a), all
ten grepped FREE. Coverage of the commissioned categories: bacterial strings/filaments ×4
(tithemoss, murkspindle, weircomb, gleamfloss), sponges ×2 (gloamurn, glimmerhusk), soft
corals ×2 (tollhorn, hushcoral), plus one runner (farwick) and one turf (almslight).

### 1. RM_Tithemoss — bacterial felt on living lamps · *tax*

A grey-green felt of filament colonies that grows nowhere but on the bodies of living
lights — a wild hoolimbre rope, a noothelm bulb, an aluun-hung stem — drinking a tithe of
the glow straight out of the symbionts and wearing a faint rim of the stolen colour. A
tithed lamp is a dimmer lamp; a heavily tithed one is a lamp in name only. The Compact
weed their stakes every morning the way surface people sweep a doorstep, and a stake gone
furry is the chart-readable sign of an abandoned claim. Everything in this sea pays for
light one way or another; tithemoss is the tax collector, and it has never once been
thanked.

- **Twist:** a parasite in a currency economy is a tax — it steals light without ever
  making any.
- **Lightweb:** a tithed lamp reads one radius step dimmer, so the suulk — which beelines
  for the *brightest* player-owned glower — passes it over: the poor colonist's suulk
  insurance, paid for in light. And tithemoss **will not take on the vaulisk's lure**
  (the false gold is a predator's organ, sealed; there is nothing alive in it to drink
  from) — a fourth tell, slower than the piip-check: a "hoolimbre" that has stood a week
  bare of moss is not a hoolimbre.
- **Tenancy:** the Compact's weeding is visible daily work (the same register as buoy
  re-placement); moss-furred stakes mark lapsed claims on any chart.
- **Art:** a mangy fringe on the host's silhouette, grey-green, rim-lit in the host's own
  colour; drawSize small, drawn as an attachment overlay. No glow of its own beyond the rim.
- **Harvest:** none — a weeding job (cut, no yield). growDays 3; placement by host
  adjacency (Route B), never freestanding.

### 2. RM_Gloamurn — the afterglow sponge · *bank*

A translucent urn-sponge that drinks the gold all the days a well stands over it and gives
none of it back — dark, swollen, miserly — until the well closes. Then, alone on ground
the sky has abandoned, the urns light: a soft steady gold, radius small, spending the
hoard down over most of a week. A closed well's kelp graveyard glitters with them. The
Deepwater call that ground *the afterglow*, and they walk it without lamps.

- **Twist:** a light bank — it stores the well's rent and spends it after the landlord
  leaves. The one gold in the biome that gets *brighter* when the sky goes out (lid-dark
  included: a lid-dark night in urn country is the biome's best look).
- **Lightweb:** when a well closes, the charged urns are suddenly the brightest things on
  that ground — so the suulk's next graze goes THERE, not to the colony's lamps: the sea's
  own decoy field, and the reason a wild suulk survives between player visits at all.
  Honest breathing glow (it carries the pulse), so it also shrinks the vaulisk's dark —
  the liar does not sit in the afterglow.
- **Tenancy:** the week after a well dies, its ground still has value — see the owner
  question on **afterglow rights** (a closing well's cheap second lease, the one paper the
  well-keeper sells *after* refusing to sell the waning well itself).
- **Art:** a squat urn, translucent grey-green when charging, honey-gold and inner-lit
  when spending; drawSize ~0.9; glow radius 2.5 gold, breathing, **only while discharging**.
- **Harvest:** a charged urn squeezes to **1× `RM_LampBladder`** (the existing item — the
  same symbiont colony, wild-banked); harvesting ends the urn. growDays 10, commonality
  0.5, open floor (Route A) — cells near well sites charge; the rest stay dark and lean.
- **Engine honesty:** the charge/discharge is one tiny comp (glower enabled when local
  ambient glow falls below a threshold — or driven by the well-ledger where present).
  Glow-grid only, per the §1.4 trap; no sky condition anywhere near it.

### 3. RM_Murkspindle — the dark-adapted filter strings · *refuse*

Upright spindles of jet-black filament, matte as soot, strung in loose stands across the
dark between the beams — the commission's *dark-adapted filter strings*, and the one plant
in the sea that wants nothing from the light. It combs the still water for the fine
detritus that settles only where nothing swims, and light ruins it: the filter-life is
photophobic, and a well opening overhead kills a stand in days. Where murkspindle grows,
nothing has been bright for a long time — which is exactly what a diver needs to know
about that ground.

- **Twist:** the refusal — in an economy where everything trades in light, one organism
  shorted the currency and lives on the dark itself.
- **Lightweb:** no glow. A spindle stand is a legible map of the standing threat surface:
  murkspindle country IS loohn and vaulisk country, and the liar prefers to hang its false
  gold against spindle-black, where it is most beautiful (siting input for
  `RM_TwilightScatterVauliskLure`: weight lure placement toward spindle stands — one more
  way the tell is taught: gold standing in the spindles gets checked first).
- **Tenancy:** the anti-chart — spindles mark ground the well-ledger has not visited in a
  long time, i.e. ground where a well is *due*; the Compact's pilots read spindle-kill
  (a browning stand) as the cheapest forecast of an opening.
- **Art:** thin black verticals in loose sheaves, matte, faint blue-white beads where the
  thurrim-register filter-life feeds; drawSize 0.8. Drawn as an absence: the one silhouette
  with no lustre.
- **Harvest:** none — dressing and danger-map. growDays 6, commonality 0.6 (Route A, the
  dark floor's staple).
- **Engine honesty:** vanilla has `growMinGlow` and no growMax — "dies in light" needs a
  one-line comp (wilt above a glow threshold) or stays placement-plus-prose. Owner
  question below; the comp is tiny and shared with nothing.

### 4. RM_Weircomb — the current combs · *mint*

Rows of upright combs rooted in the bank silt, teeth of stiff bacterial filament held
against the invisible river — and along each tooth, blue-white light in proportion to the
current that feeds it. A slack day is a dim bank; a running day is a lit weir; and in the
hours before an undersurge the whole bank blazes, because the combs feel the flood coming
before anything with eyes does. It is the only light in the sea that owes the sky nothing:
weircomb mints its glow from motion, and the river has never once stopped paying.

- **Twist:** light minted from current, not from the sun — the sky-independent glow, and
  the river's own gauge drawn in light.
- **Lightweb:** blue-white is *moving* in the colour grammar, and the vaulisk speaks only
  gold — combs cannot be counterfeited, so bank-light is the one light a diver never has
  to check. Too dim and too fixed ever to be the suulk's brightest target.
- **Tenancy:** none — bank wealth is the ruled counterweight to well tenancy, and the
  combs mark it: where the weirs glow brightest, the silt is richest. Their pre-surge
  blaze joins the sennefan snap and the vanishing murrol as the undersurge's tells (danger
  pass D6), and it is the one tell readable from across the map.
- **Art:** a comb silhouette, copper-dark teeth lit blue-white along the edges, rows
  aligned to the flow; drawSize 1.0; glow radius 1.5 blue-white, brightness stepped by
  current (an effecter/graphic stage, not a mechanic the player must track).
- **Harvest:** none for the player; it is grazing ground — its strained catch feeds the
  bank's grazers (built cast: the weloon and lunoowa work the comb rows; the content
  drop's nuudal, when built, grazes here). growDays 6; **wildTerrainTags on `RM_BankSilt`**
  (Route A via terrain tag — the tag rides the terrain def when it is authored),
  commonality 0.7 on banks.

### 5. RM_Tollhorn — the ledger coral · *record*

A soft horn-coral, blunt and unbeautiful, that grows where wells recur — and keeps books.
Every week of standing gold above it lays a gold-veined growth band; every dark season
lays a blank one. A cut tollhorn core is a core sample of the sky: decades of the
well-ledger's weather, banded like tree rings, readable by anyone the well-keeper has
taught. Her charts are calibrated against tollhorn cores — her thirty years, written in
coral — and she buys cores dearly, and has never once sold one.

- **Twist:** it neither makes nor spends light — it *records* it. The sea's own ledger,
  and the only witness of the sky's history that predates the Compact.
- **Lightweb:** no glow; deliberately inert to the suulk and the vaulisk both. Every
  roster needs one instrument that the web cannot touch, or the web has no baseline.
- **Tenancy:** the estate secret. Thick-banded tollhorn ground is ground where wells
  RECUR — the one fact about the drift that is knowledge rather than forecast, which is
  exactly why the well-keeper hoards cores: a player who learns to read tollhorn is
  reading the Compact's real ledger over their shoulder.
- **Art:** a cluster of blunt horns, dusty rose-grey, band-lines faintly gold on the
  weathered flanks; drawSize 1.2; no glow.
- **Harvest:** slow, high-work — **1× tollhorn core**, a high-value trade good (Beauty on
  the item; the Compact pay best). Whether a carried core also steadies a `RM_WellChart`'s
  forecast is an owner question below. growDays 20 (an old thing, like the Scald's
  thurlsponge), Route B: seeded by the dressing genstep on well-recurrence ground (the
  skylight-site clusters the generator already knows).

### 6. RM_Hushcoral — the answering coral · *answer*

A soft coral of small gold polyps that do not make their own case: they *answer*. Within a
few cells of any honest living light, the colony entrains — its faint glow breathing in
time with the lamp it hears — and beside a light with no pulse it goes silent and dark. A
ring of hushed coral around a gold lamp is the oldest alarm in the sea. The Compact plant
hushcoral around every claim-buoy, and their children learn the proverb in its long form:
*a lamp with no piip around it is not a lamp; a lamp the coral will not answer is a trap.*

- **Twist:** light as speech — it neither mints nor spends, it *replies*, and its silence
  is the reply that matters.
- **Lightweb:** the vaulisk's tell, made into a plant and readable at a glance from range:
  the liar's glow is steady (it lacks the breathing comp by design — absence of code as
  the monster's tell), so hushcoral beside it never entrains. Radius 1 and never the
  brightest thing anywhere — deliberately below the suulk's notice, because a tell the
  grazer could eat is not a tell.
- **Tenancy:** buoy-rings are Compact practice (Route B dressing at their claims and
  yards); a player can transplant a ring around their own constellation — the cheap,
  living vaulisk alarm that costs no chain and no research.
- **Art:** low cushions of small polyps, dusty gold over grey-green, drawn mid-pulse;
  drawSize 0.7; glow radius 1 gold, entrained pulse (a sibling of `RM_Comp_WarblingGlow`,
  reading the nearest honest glower's phase — small C#, same verified `ForceRegister` API).
- **Harvest:** none; Beauty positive. growDays 12, commonality 0.3 (Route A) plus the
  Route B rings at Compact sites.

### 7. RM_Gleamfloss — the colony in the column · *inhabit*

The golden shafts are not empty light: they are inhabited. Gleamfloss is a bacterial floss
so fine it has no purchase on the floor at all — it lives suspended IN a skylight's
column, a slow drifting haze of gold-lit filament that is half the reason the shafts read
as *literal golden shafts* from the floor. The pallu eat it, which is why the pallu stack
in the wells, which is why the well-keeper counts pallu to price a lease: the whole
pricing chain stands on this floss. When a well closes, the floss starves and settles —
a gold dust-fall the Deepwater call **gilt** — and for a few days the dead well's floor
is worth sweeping.

- **Twist:** it lives in a place made of light — no floor, no root, no body to point at;
  the only flora whose habitat is the currency itself.
- **Lightweb:** the suulk cannot graze it (diffuse, unownable); the vaulisk cannot fake
  it — **a gold glow with no shimmer standing over it is a lie**, a tell readable from
  farther away than the piip-check. Floss density is why the shafts are where the shoals
  are: niim hunt the pallu that eat the floss; the columns' whole food chain starts here.
- **Tenancy:** floss thickness IS the sky-read at floor level — young wells thin, mid-life
  wells dense, waning wells shedding gilt early. The free forecast the light-economy pass
  promised (§1.2's sky-read) gets its floor-level instrument.
- **Art:** the column form is art on the `RM_Skylight` thing (a drifting haze layer in the
  shaft render, when the shaft-of-light art lands — the content drop's one flagged
  art-engineering question, unchanged by this pass); the floor form is a low gold shimmer
  plant on shaft cells, drawSize 0.5, no glower of its own (the skylight's 6.0 covers it).
- **Harvest:** the settled **gilt** — a few days' window after a closure, sweepable for a
  small yield of gold pigment: the third ink beside vaal-green and lamp-black, the gold
  the Compact's charts are veined with. New tiny item (`RM_Gilt`), owner question below.
  growDays 2 (it must bloom inside a well's 5–9 day life); Route B: shaft cells only,
  seeded and killed by the well-ledger.

### 8. RM_Glimmerhusk — the sponge that eats light · *eat*

A barrel sponge of the dark between, big as a barrel and twice as patient, that strains
the water for the sea's smallest lights — drifting piip-scale glow-plankton — and cannot
digest the glow as fast as the flesh. Its body is speckled with the still-lit remains of
everything it has eaten: a constellation inside a husk, gold and blue-white and green all
at once, each point fading over days. It is the only thing in the sea that shines in all
three colours, and every one of them is quoted.

- **Twist:** light predation at the food chain's bottom — its glow is entirely
  second-hand, a husk full of other things' last light.
- **Lightweb:** the suulk's wild pasture. A fat glimmerhusk out-glows a small lamp, and
  the grazer will take it first — husk fields are where wild suulk feed between visits to
  the colony, and a husk stand near the map edge is a free decoy the Compact's own
  lit-stake practice imitates. The vaulisk *prefers* husk country: scattered mixed points
  make one steady false gold hard to pick out (second siting input for the lure scatter,
  beside the murkspindle stands). The one honest breaker of the colour grammar — its
  lights are all three colours because none of them is its own.
- **Tenancy:** none; the dark between is nobody's lease.
- **Art:** a squat charcoal barrel flecked with dozens of tiny mixed-colour points, a few
  visibly brighter (fresh); drawSize 1.1; glow radius 1.5, mixed/dappled, breathing
  unevenly (it is many small lights, not one).
- **Harvest:** none — it is fodder and camouflage, the web's infrastructure. growDays 15,
  commonality 0.35 (Route A, dark floor).

### 9. RM_Farwick — the light-pipe runner · *carry*

A creeping runner of glassy thread that roots at a shaft's rim and grows *away* from it,
cell by cell into the dark, piping the well's gold down its own fibre to a single small
lit bud at the far end — light delivered where the sky never reached. The Compact watch
farwick buds the way surface people watch signal fires: every bud on the floor dies the
same hour its home well closes, so the buds are the fastest messengers the drift has. A
lone gold bud burning in country whose well is a week dead is not a farwick, and every
Deepwater child knows what it is instead.

- **Twist:** light as plumbing — the one plant that moves light without moving, spending a
  well's rent on ground the well never touched.
- **Lightweb:** buds (radius 1.5 gold, breathing — the pulse travels the fibre) sit below
  the suulk's targeting, but a suulk *follows* a farwick line inward toward the brighter
  source: the runners are the grazer's roads, and a colony between a shaft and its lamps
  should know it. Bud-death is common knowledge, so a "bud" still glowing after its well's
  death is the liar's second-favourite costume — and the tell is already taught.
- **Tenancy:** micro-tenancy without paper — a bud lights one workbench, one snare-line,
  one doorstep, lease-free. The well-keeper does not sell farwick light and will not
  discuss it; the runners give away in ones what she leases in wholes.
- **Art:** a hair-thin glassy line drawn across the floor cells it crosses, near-invisible
  except where a shaft catches it, ending in one small gold bead; drawSize of the bud 0.5;
  glow radius 1.5 gold at the bud only, alive only while the home well stands.
- **Harvest:** the bud, picked, is **1× `RM_NoothelmBulb`** (the existing item — the same
  organ grown at the end of a wire; one-day light, poor meal) and picking kills the
  runner. growDays 15 (a long line is a season's work); Route B: seeded at shaft rims by
  the dressing genstep, drawn outward along a straight run of 4–8 cells.

### 10. RM_Almslight — the giving turf · *give*

A low cushion-turf that cannot keep what it is given: everything it drinks by the standing
light it leaks straight back, all hours, as a floor-hugging carpet glow too dim to work by
and too kind to waste. It grows only within the spill of standing light — a well's skirt,
a lamp-row's verge — and its soft-lit edge maps the true reach of every light in the sea
more honestly than any radius number. The Compact seed it along their paths, and their
children are raised on the whole economy's gentlest rule: *walk on the alms.*

- **Twist:** the economy's refusal from the other side — where murkspindle shorted the
  currency, almslight holds none of it: it spends everything on arrival, the one organism
  in the sea with no account.
- **Lightweb:** alms-lit ground is never fully dark, so it shrinks the loohn's hunting
  dark and the vaulisk avoids it (the drag into the dark needs dark to drag into) —
  alms verges are the safe roads, which is why the Compact plant them as streets. Radius-1
  diffuse carpet: nothing for the suulk to graze.
- **Tenancy:** its edge is the honest survey line — where the alms stop, the lease's real
  value stops, whatever the paper says. (The well-keeper prices by pallu; smart players
  price by alms.)
- **Art:** a felted turf, grey-green with a soft under-lit warmth, brightest at the centre
  of its patch; drawSize 1.0 carpet; glow radius 1, a warm neutral (it gives back whatever
  colour it was given — near a well, faint gold; by a lamp-row, the lamp's cast).
- **Harvest:** none; it is grazing ground (Nutrition — the built detritivores work it, the
  content drop's nuudal grazes it when built) and pathing texture. growDays 4,
  commonality 0.8 with `growMinGlow` ~0.15 (Route A — the low glow gate does the
  "only within the spill" placement for free, on the glow grid, exactly as ruled).

## plantDensity and route split

### The density

**Proposed `plantDensity`: 0.2 → 0.35.** Calibration across the four seas and vanilla:
desert 0.05, arid shrubland ~0.17, temperate forest 0.6; the Propane Lake proposes 0.18,
the Grey 0.22, the Scald 0.30. The Twilight is the sheet's *"abundance as the rule"* sea —
crowded, for once, by ruling — so it takes the top of the ladder: unmistakably the richest
floor of the four, still short of a land forest, because open dark between stands is
load-bearing here (the dark between is the standing threat surface, and murkspindle
country must read as country). The shipped 0.2 was set for a three-plant floor; ten more
rows under 0.2 would dilute everyone including the incumbents. Single knob; the roster
works unchanged from 0.25 (sparser) to 0.5 (lush). One deliberate reserve: the fourteen
canopy seaweeds (content doc §3) will share this budget when they land — the number gets
one revisit at that sitting, and it revises upward, never down: the canopy adds, the
understorey stays.

### Route split

**Route A — `wildPlants` (density-driven).** Six new rows beside the three incumbents
(unchanged: `RM_SaltBladeTwilight 0.03` · `RM_HoolimbrePlant 0.15` · `RM_NoothelmPlant
0.05`), in the shorthand `<DefName>commonality</DefName>` form (⚠️ never `<li>` — the
custom loader silently discards a wrapped row):

```
RM_Almslight 0.8 · RM_Weircomb 0.7 (terrain-gated) · RM_Murkspindle 0.6 ·
RM_Gloamurn 0.5 · RM_Glimmerhusk 0.35 · RM_Hushcoral 0.3
```

Every def carries `completelyIgnoreFertility` (the floor is fertility-0
`RM_SeaFloorGround` — the paid engine fact). Two use the glow gate deliberately:
almslight's `growMinGlow` ~0.15 does its "only within the spill" placement for free, on
the glow grid, exactly as ruled; everything else gates at 0 and lets its comp or its
route do the light logic. Weircomb alone is terrain-gated — `wildTerrainTags
RM_BankSilt`, high weight within the banks, absent everywhere else (the Grey brinecomb's
shipped pattern). ⚠️ `RM_BankSilt` does not exist yet as a TerrainDef — the channel
genstep `PaintIfPresent`-tolerates its absence — so the comb's row is a dead letter until
the bank terrain is authored. That is sequencing, not a defect; the tag name is already
established by the genstep and the row ships with it.

**Route B — the dressing genstep (adjacency and ledger placement, which `wildPlants`
cannot express).** Four species plus one ring:

- **RM_Tithemoss** — attachment overlay on living-lamp hosts (wild hoolimbre ropes,
  noothelm bulbs, aluun-hung stems), never freestanding — and never on a vaulisk lure,
  which is the fourth tell working.
- **RM_Tollhorn** — seeded on well-recurrence ground (the skylight-site clusters the
  generator already knows).
- **RM_Gleamfloss** — shaft cells only, seeded and killed by the well-ledger (growDays 2
  inside the 5–9 day life); the sweepable gilt window follows each closure.
- **RM_Farwick** — seeded at shaft rims, drawn outward along a straight 4–8 cell run.
- **RM_Hushcoral rings** — placed at Compact claims and yards, in addition to its
  Route A row.

**Route C — runtime comps, all tiny, all named in the entries, all glow-grid only per
the §1.4 trap:** gloamurn's charge/discharge glower, hushcoral's entrained pulse (a
sibling of `RM_Comp_WarblingGlow`, same verified `ForceRegister` API), and murkspindle's
wilt-above-glow (owner question below; placement-plus-prose is the fallback). Nothing
here touches the sky, and nothing adds a second clock — every ledger-driven placement is
a call into `RM_MapComponent_WellLedger`.

**What changes in `RM_TwilightSea.xml`, summarized:** one field (`plantDensity` 0.2 →
0.35, pending the density question) and six `wildPlants` rows beside the kept three.
New defs live beside the shipped `RM_TwilightSeaFlora.xml`; Route B placements extend
the dressing genstep the skylight generator already runs.

## Ecology — wiring flora into the built cast

The danger pass built the lightweb's animals; this roster builds the web's terrain, so
every wire below runs to something already shipped or already ruled:

- **The suulk's table, ranked.** The grazer beelines for the brightest player-owned
  glower — and the roster builds the sea around that appetite. **Glimmerhusk** fields
  are its wild pasture (a fat husk out-glows a small lamp); a closed well's charged
  **gloamurn** ground is its decoy field — suddenly the brightest thing on abandoned
  ground, and the reason a wild suulk survives between player visits at all;
  **farwick** lines are its roads inward toward the brighter source; and a
  **tithemoss**-dimmed lamp drops below its notice — insurance paid in light. The
  constellation-pressure knob (light pass §2.2) reads only player-owned glowers, so
  none of this changes the incident math; it gives the wild suulk somewhere true to be.
- **The vaulisk's tell-stack, now taught by the floor itself.** To the three built
  tells (no breathing pulse, no piip, dead ring) the flora add four, all passive:
  tithemoss will not take on a lure, **hushcoral** beside it goes silent and dark, no
  **gleamfloss** shimmer stands over a false gold, and a farwick bud alive after its
  well's death is not a bud. Two siting inputs for `RM_TwilightScatterVauliskLure`:
  weight toward **murkspindle** stands (gold against spindle-black, where the liar is
  most beautiful) and glimmerhusk country (scattered mixed points hide one steady
  gold). The plant layer makes the liar's life harder AND his stage better — both
  correct.
- **Niim and noolim, split by light (ruled), get their food chain.** Gleamfloss is why
  the pallu stack in the shafts; pallu are why the niim — the lit shoal — hunt there;
  pallu counts are how the well-keeper prices a lease. The whole pricing chain bottoms
  out on floss. The noolim, the dark shoal, works glimmerhusk and murkspindle country;
  and the loohn's hunting dark shrinks wherever **almslight** runs — alms verges as
  safe roads is the Compact's own street plan, made of turf.
- **The banks graze.** Weircomb's strained catch feeds the weloon and lunoowa in the
  comb rows; almslight is grazing ground for the built detritivores, and the content
  drop's nuudal works both when it ships. The pre-surge comb-blaze joins the danger
  pass's undersurge tells, readable from across the map.
- **Well tenancy gets its instruments, one per stage of a well's life.** Opening due:
  murkspindle browning. Standing: gleamfloss thickness as the free floor-level
  sky-read. Waning: floss shedding gilt early. Closed: gloamurn's afterglow (value
  after death — owner question), farwick bud-death as the fastest messenger, and the
  gilt window worth sweeping. Recurrence: **tollhorn** cores, the Compact's real
  ledger. And always: the almslight edge as the honest survey line under any lease's
  paper. All of it rides `RM_MapComponent_WellLedger`'s one clock — no plant here has
  a timer of its own (§1.1's law, held).
- **The Compact's practice stays visible daily work:** weeding tithed stakes, walking
  hushcoral buoy-rings out to claims, seeding alms streets, buying tollhorn cores
  dearly and never selling one. Tenancy as labour, never menus.
- **The web keeps its baseline.** Tollhorn neither makes, spends, answers nor steals
  light — deliberately inert to suulk and vaulisk both, the one instrument the web
  cannot touch.
- **Audit.** Nothing adds a predator; nothing grows on the channel bed (ban 3 — the
  bed stays the current's); nothing touches or tends the waveglass (ban 2 — the roof
  is the gardener's alone); no new plant is a harvestable lamp (the incumbents' taken
  register — wild light pays out only in existing items); and no skylight becomes
  permanent because a plant loved it (ban 5 — gloamurn, gleamfloss and farwick are
  all built on wells dying).

## Ruled

Nothing in this pass has been carded yet. This section records the cuts the pass made
on itself under standing rulings — the Scald precedent (*"No, this is silly. No cold."*
— a twist borrowed from another biome's register dies) applied before asking:

1. **A prism plant — CUT.** The first draft's *carry* verb was a crystal refractor
   angling shaft-gold into the dark. Mineral flora is the Grey's entire register (the
   content doc's own boundary: the Twilight *drinks* the light, the Grey *precipitates*
   the sea). Farwick carries light down a glassy organic fibre instead — organ, not
   mineral — and that is as close as this sea comes to glass.
2. **A lying plant — CUT.** A flower that counterfeits a lamp to gather grazers.
   Counterfeiting is the vaulisk's, one per map by ruling; a plant that lies cheapens
   the monster and multiplies the tell-checking chore. This roster's plants are the
   liar's opponents (hushcoral, tithemoss, gleamfloss, farwick), never his colleagues.
3. **A light-eating hazard plant — CUT.** A snare that douses a passing pawn's carried
   light. The engine has no negative light, so a "darkness radius" is a fiction the
   glow-grid-only law (§1.4) cannot pay — and the dark's teeth belong to the danger
   pass's cast besides. Glimmerhusk keeps the light-predation idea at plankton scale,
   where it is fodder and camouflage rather than a hazard.
4. **A fourth harvestable lamp — CUT, repeatedly.** Drafts kept inventing new
   portable-light yields. The roster's opening law holds: hoolimbre and noothelm own
   *sell*, and that register is taken. Where wild light pays out, it pays in EXISTING
   items — gloamurn squeezes to `RM_LampBladder`, farwick's bud picks as
   `RM_NoothelmBulb` — wild routes to the same goods, no new lamp SKU.
5. **A wild sun-sphere ancestor — CUT.** A free-growing ollumin patch on the floor.
   Stage 3's whole cost is the arc — techprints, research, a seed that is the sea's;
   a wild sun-strength plant collapses independence into foraging.
6. **A roof-tending plant — CUT.** Moss that patches waveglass tears or props a
   skylight from below. Ban 2: the roof and the gardener are one system, nothing else
   tends it — and nothing of ours reaches the lid at all (the held-open skylight is
   already ruled OUT; the lid is a sky).
7. **A walking plant — CUT.** A lamp-plant that migrates to follow the wells. The
   chase is the PLAYER'S verb — the light economy's whole first act — and a plant that
   chases for free deletes the arc; the moving-light slot is the waelune's besides.

## Questions for the owner

1. **plantDensity 0.2 → 0.35 — accept, or name a different number?** The single knob;
   the roster works unchanged from 0.25 (sparser) to 0.5 (lush). The fourteen canopy
   seaweeds (content doc §3) will share this budget when they land, and that sitting
   may revise it upward.
2. **Murkspindle's dies-in-light: ship the one-line wilt-above-glow comp, or
   placement-plus-prose only?** Vanilla has `growMinGlow` and no maximum. The comp is
   tiny and shared with nothing; the prose-only fallback keeps the plant but loses the
   spindle-kill forecast (a browning stand as the cheapest read of a well due to open).
3. **Afterglow rights (gloamurn): when a well closes, does the well-keeper sell a
   cheap second lease on the charged-urn ground** — the one paper she sells *after*
   refusing to sell the waning well itself — **or is the afterglow free ground?**
   Either fits her: the lease prices the week after a death; free ground makes it the
   poor diver's window.
4. **Tollhorn cores: trade good only, or does a carried core also steady an
   `RM_WellChart`** (slower aging, less forecast noise)? Steadying makes the coral a
   real instrument and slightly undercuts her chart monopoly — which may be exactly
   the point, or exactly wrong.
5. **RM_Gilt: a new tiny pigment item** — the third ink beside vaal-green and
   lamp-black, the gold the Compact's charts are veined with — **or fold the settled
   floss into an existing yield?** The new item is one def and pays the chart fiction;
   folding is cheaper and loses it.
6. **Does tithemoss colonize the player's own clipped lamps, or only wild and Compact
   stakes?** Colonizing gives the player the dimming-as-suulk-insurance trade and a
   weeding chore — which brushes the no-feed-chores refusal (light pass §2.2-4);
   weeding is optional where feeding was not, but it is still a chore. Wild-and-Compact
   only is the safe default and what the numbers above assume.
