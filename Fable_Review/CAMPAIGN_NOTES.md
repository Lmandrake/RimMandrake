# The campaign, judged as a game — and a V2_DREAMS triage

## §1 The Utinni campaign is genuinely good design

Said plainly, because the process review above is critical and this part earns the
opposite: the campaign concept is stronger than most published RimWorld scenario mods.

- **The anti-exponential principle is the real insight.** RimWorld's endgame problem
  is that colony power compounds until the storyteller can't threaten it. Making the
  ship+factory the *only* scalable progression tree — no psycasts, no gene ladder, no
  mechanitor ladder — keeps the Oregon-Trail loop (land, strip, improve, flee) alive
  for a whole campaign. This is a principled cut most designers wouldn't have the
  nerve to make, and it is the thing to protect most fiercely against v2 feature
  creep.
- **Water as master scarcity on a tidally-locked world** is mechanically expressible
  in RimWorld's systems (biome commonality, terrain, rivers) and thematically load-
  bearing rather than decorative. The hand-painted Ash'karr — substellar furnace,
  terminator sea, dayside rivers, nightside poison forest — reads as a place, not a
  parameter sweep, which is exactly what "one map, not a generator" buys.
- **The frozen single world is the right call** and its cost is honest: whatever
  faction/ideoligion isn't there at the stamp is absent forever. That makes step 9
  (factions) and the "worldgen-locked" v2 items the highest-stakes decisions left.
- **The scavenger-faith ideoligion ("The Salvation") plus twelve factions each with
  their own faith** gives the fixed world its replay texture — since the map can't
  vary, the social landscape has to, and it does.

**Two design risks worth one bench conversation each, before v1:**

1. **The pursuit loop needs a mechanism, not just lore.** "Leave before the Empire
   arrives" is the campaign's heartbeat; if no escalating incident/timer actually
   enforces it, players will turtle and the anti-exponential design loses its
   pressure partner. If a mechanism exists, ignore this; if it's still flavor, it's
   the most important unbuilt system in the game (raid-scaling by time-on-tile is
   probably enough — RimSage can confirm what `StorytellerComp`s are patchable).
2. **One permanent enemy risks monotony across a long campaign.** The Hutts/Junkers/
   tribes mitigate socially; make sure at least one *military* texture besides the
   Empire survives faction selection (the "They!" ants would do exactly this — see
   §2).

## §2 V2_DREAMS triage — endorsements and vetoes

The design agent's viability reads were sound; where it matters I've sharpened them:

**Do in v1 (worldgen-locked — the frozen world makes "later" mean "never"):**
- **"They!" giant-ant desert faction** — its own note says the faction must exist at
  worldgen or be lost forever. Decide it now, even if the content ships shallow; a
  dormant faction on the map is recoverable, an absent one is not. Same check applies
  to any of the eleven FactionDef ideoligion blocks that add *factions* (blocks on
  existing factions are save-safe).

**Strong, cheap, do early in v2:** Sarlacc pit (Anomaly PitGate rebrand — defs
verified), domestic Star Wars animals as mutators (donors active), Jawa rag-nest/egg
reskins, the eleven ideoligion blocks (pattern proven).

**Plausible, keep:** everything-detonates energy model; mountain-only violent rain
(mechanism identified); Cantina Kitchen; restraining bolts; mid-game gravship layout
import; mapgen *scorer* (needs an owner ruling — scoring the one map is fine, and the
ruling should say so in one line to stop it being re-litigated).

**Veto recommended:**
- **GREAT_NAMESPACE_RENAME** — kill it, don't park it. Its own entry documents that a
  `MayRequire` packageId rename silently drops 166 patch elements, and the window
  closes when the savegame freezes — which is v1. Cosmetic gain, catastrophic silent
  failure mode, deadline already effectively passed. Mark it dead per the worldgen
  precedent ("V2 is not a parking space").
- **Nine LLM ship-voices** — gated on an unbuilt in-game LLM stack; park as a
  research line, not a content item.
- **Full 69-species race regeneration** — its own note admits it fixes no defect.
  The bestiary-made-real work already captures the value at a fraction of the scope.

**A note on V2_DREAMS itself:** it's an append-only log (24.5k words, 64 commits)
mixing dreams with deferred bugfixes. At v1 ship, one curation pass should split it:
deferred *defects* go to the queue or die; *dreams* stay, one heading each. Don't do
it before then — it's exactly the kind of tidying that burns tokens now for value
later.

## §3 The retroactive lore pass

Deferring lore sync until the game is v1-final is correct — the game is the source of
truth and the docs admit it. Two things will make that pass cheap when it comes:
- the supersession-banner discipline already in place (28% of docs carry markers —
  the drift is *mapped*, which is most of the work);
- `canon.yml` as the number authority — the lore pass becomes "make prose agree with
  canon and the shipped defs," a mechanical sweep Sonnet can draft and you approve.
Keep the existing memory (`worldmap-docs-pass-owed`): do it *with* you, once, not as
a solo sweep.
