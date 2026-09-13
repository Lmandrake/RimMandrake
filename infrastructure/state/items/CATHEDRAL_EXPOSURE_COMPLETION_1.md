
<!-- Split from the 2026-09-12 build decomposition; standing constraints: arc spec section 'The law' (knowledge gate, bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen) bind this item. -->


## spec
Arc §6.1 as amended by A3+A6 (owner verbatim in §6.1: the Cathedral fights
and slowly falls, the planet becomes a warzone again, the Hutts can get the
players offworld "for the right price... Something ancient and wondrous is
gone forever, and the ship mourns."). Builds the completion, not just the
pressure (pressure + dark flip are item 1's):
- **Exposure-completes event chain** — GM-driven: threshold on item 1's
  pressure fires full Imperial discovery; the slow fall is *witnessed, not
  narrated* — staged events on/around Cathedral ground (§GM "losing battle"
  register), bans 2/3/6 holding throughout: no Sentinel-raid story against
  the player, no mercy/drill text even in death.
- **Warzone posture flip** — planet-level posture change via the GM layer +
  existing pursuit/raid pacing surfaces; no worldgen, no map regeneration.
- **Priced Hutt extraction window** — a real, losable campaign ENDING: offer
  rides Hutt Interest (kyber §4's fixer lane); price scales with Interest/
  standing; registration as a ruled campaign ending belongs to
  `CAMPAIGN_STORY_SITTING_1` — this item builds the mechanism and hands the
  ending shape to that pass.
- **Gravship mourning register** — the ship feels the loss, kin to A1's
  receiver lore (item 7's propagation): text register on ship-adjacent
  surfaces, §P discipline, Oracle-optional.
- Knowledge gate: opens for nobody but the player even in full discovery —
  the Empire finds a thing, never the truth the player was told.

## verify
Shadow-mode first: chain fires only past the ruled pressure threshold;
demotion/dark precedes it (no skip from VOUCHED straight to fall); every
authored consequence stays inside the faction-13 hysteresis (arc §8 seed 4 —
no raid/manhunt authored anywhere in the chain); all fall/mourning text
passes item 3's linter; extraction offer priced and refusable; ending
reachable with the Oracle absent; post-fall world state carries no §GM truth
in any player-visible string.

## criteria
Full chain runs on a quicktest campaign in accelerated shadow mode; ending
handoff filed to CAMPAIGN_STORY_SITTING_1; mourning register shipped.

**Depends on:** item 1 (pressure + dark), item 3 (linter), kyber Hutt
Interest lane (M4), item 7 soft (reveal-state interaction: a revealed-then-
exposed Cathedral must still fall correctly; buildable before 7 with the
flag stubbed), `CAMPAIGN_STORY_SITTING_1` for ending ratification (mechanism
builds now, ending ships gated on that sitting). **Waited on by:** nothing.
**Seat/needs:** FOUNDRY; GM Python + event authoring + bridge; game-up for
the witnessed-fall staging. Posture-flip/ending plumbing may need C# — if so,
row-3, model per `infrastructure/agents/Agent_Policy.md` ladder.
