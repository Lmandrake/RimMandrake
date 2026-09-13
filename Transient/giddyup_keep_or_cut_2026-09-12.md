# Giddy-Up: keep, trim, or cut — analysis for the owner's ruling

GIDDYUP_KEEP_OR_CUT_1 · BENCH Fable agent, 2026-09-12 · every machine claim is
from disk on this machine; every web claim is dated.

## The short answer

**Recommend: KEEP, with one settings decision (card below).** The mod you are
running is not the mod that earned the old reputation. It is the third-
generation rewrite, actively maintained into RimWorld 1.6 (a 1.6-specific
crash was fixed in its v2.2.5 line this year), it ships its full C# source,
and the code we inspected is defensive where the old one was brittle. Both
2026-09-12 "Giddy-Up" crashes in our log were OUR OWN BiomeCast data defects
— Giddy-Up was the smoke alarm, not the fire, and its error handler is the
reason those defects logged politely at load instead of breaking wild-animal
spawning mid-game. On a desert scavenger world where Jawas ride banthas, the
content fit is about as good as a mod fit gets.

## 1. What we actually run (disk)

- `MemeGoddess.GiddyUp` = **Giddy-Up 2 - Continued v2.2.5**, workshop
  3674332861. Authors chain on the About.xml: Roolo → Owlchemist → dav9670 →
  Meme Goddess. It declares itself INCOMPATIBLE with every old Roolo-era
  module (giddyupcore, rideandroll, caravan, battlemounts) — the historic
  breakers are a different, superseded codebase this mod refuses to coexist
  with.
- `MemeGoddess.RunAndGun` = RunAndGun - Continued (workshop 3562365100), same
  maintainer, separate decision (§6).
- Lineage (web, 2026-09-12): Owlchemist's Giddy-Up 2 was a ground-up
  code-refresh of Roolo's original — "Hugslib removed, peer reviewed for
  performance, all-in-one modular design" (github.com/MemeGoddess/GiddyUp2
  README); dav9670 then MemeGoddess continued it. The Continued line folded
  in the community "mounts stay mounted after save load" patch and fixed a
  1.6 map-open crash (v2.2.3 changelog) and temporarily disabled its no-mount
  zones against the new 1.6 pathfinder — evidence of a maintainer actually
  tracking 1.6 internals rather than recompiling and hoping.

## 2. Code quality, judged from its own shipped source (disk)

The workshop folder ships complete C# (`Source/`). What we read:

- `MountUtility.BuildAnimalBiomeCache()` wraps each biome's walk in
  try/catch, logs the offender and SKIPS — a malformed def costs one log
  line, not the load. That is precisely the failure we watched it survive.
- Settings are cached as shortHash HashSets rebuilt at startup — the 10x
  performance claim is plausible from the shapes (no per-tick def lookups).
- Harmony surface (counted from source): ~30 patch sites. The sensitive ones:
  `Pawn_JobTracker` (4), `PawnRenderer`/`PawnRenderNodeWorker`/
  `Pawn_DrawTracker` (rendering offsets), `IncidentWorker_Raid`/`_Ambush`/
  `_VisitorGroup` (NPC mounts), caravan enter/transfer utilities. This is a
  real footprint — jobs + rendering + incidents — but modular: disabling a
  module in settings short-circuits its patches' logic.
- GitHub issues: **0 open** (2026-09-12; issue creation looks restricted, so
  read that as "support runs through Steam comments", not "bug-free").
  Steam comments this month are load-order questions and feature requests,
  not crash reports.

## 3. Our own record with it (disk, honest attribution)

- The 2026-09-12 `ArgumentNullException`/duplicate-key errors at
  `BuildAnimalBiomeCache` were OUR BiomeCast_Ashkarr.xml defects (a
  Megafauna-gated PawnKindDef cast into a biome; donor/cast overlaps). Any
  core system touching those biomes' animal caches would have hit the same
  nulls — Giddy-Up merely asks FIRST, at load, where we can see it. Both
  fixes are deployed awaiting the next cold load (GIDDYUP_NULLKEY_CRASH_1,
  GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1).
- Beyond that: the current 594-mod session's Player.log carries exactly one
  Giddy-Up line (that canary) and zero errors originating in its own code.

## 4. What the campaign gets (disk)

Mount eligibility is `baseBodySize > 1.2` by default (ResourceBank.cs), per-
animal overridable in settings. From our census (frozen-dump sizes; names
now carry the RSW_ port prefixes): **Dewback 3.0 · Bantha 4.0 · Ronto 6.0 ·
Fambaa 6.0 · Mudhorn 4.0 · Dalgo 2.5 · Eopie 1.4 — all mount-eligible out of
the box.** That is the Star Wars tableau: Jawas on banthas and dewbacks
crossing a fixed 21,872-tile desert world, and pre-industrial raiders
arriving mounted (33% chance by default) — Tusken-raid energy with zero
authoring cost.
- Ride & Roll: colonists auto-mount for long hauls on the huge yard maps.
- Caravans: riding in caravans is on by default; the caravan SPEED bonus is
  a separate toggle (`giveCaravanSpeed`) currently at its default **false**.
- Mechanoids module: enemy mechanitors ride mechs (40% default) — on a droid
  world this is flavor-coherent, and the owner's one non-default setting is
  already here (some mechs deselected in `mechSelector`).
- Owner's config on disk (`Mod_3674332861_Mod_GiddyUp.xml`): everything else
  at code defaults — all four modules enabled.

## 5. The costs, stated plainly

- ~30 Harmony sites across jobs/render/incidents/caravans in a 594-mod stack
  that already patches rendering (facial animation, large pawns, melee
  animation) and AI (CAI-5000). No pairwise incident is on record in OUR
  logs, and none surfaced in this month's Steam comments (2026-09-12 read),
  but the class of risk is real: every mounted-pawn render is an offset
  computed inside someone else's render pipeline.
- Known current soft spots (maintainer's own notes, dated 2026): no-mount
  zones disabled pending the 1.6 pathfinder; odd draw offsets on exotic
  body shapes (reported against dinosaur mods — our oversized fauna like
  Fambaa/Ronto could need per-animal draw-rule tweaks in settings, which
  exist for exactly this).
- It is one more mod that must survive every RimWorld point release; the
  Continued line's response time this cycle was good (1.6 crash fixed in a
  point release), but a single-maintainer fork is a single maintainer.

## 6. RunAndGun - Continued (separate call)

Five Harmony sites (Verb/VerbProperties/JobDriver/Pawn/MentalStateHandler) —
much smaller surface. It exists here mostly as Giddy-Up's combat companion
(shooting while mounted/moving); Battle Mounts is where riding gets its
teeth. Same maintainer, same era. If Giddy-Up stays, keeping RunAndGun is
cheap and completes the fantasy; if Giddy-Up ever goes, RunAndGun loses its
main reason to stay. It also globally lets ENEMIES fire while fleeing/
advancing — a genuine difficulty/AI-texture change some players cut on its
own merits.

## The cards

**CARD 1 — Giddy-Up disposition**
- **(A) Keep all four modules at defaults** (today's state). Trade: full
  flavor (mounted raids, visitors, mechs) for the widest patch surface; you
  keep the ~30 Harmony sites and the render-offset class of glitches on our
  biggest beasts.
- **(B) Keep, trim to player-side riding** — Battle Mounts OFF (or enemy
  mount chances to 0), Mechanoids module OFF, keep Ride & Roll + Caravans.
  Trade: Jawas still ride banthas everywhere, but raids/visitors arrive on
  foot — quieter incident code, fewer NPC edge cases, less spectacle.
- **(C) Keep + also switch ON `giveCaravanSpeed`.** Trade: banthas make
  world-map travel genuinely faster on the huge fixed map — stronger reason
  to keep beasts fed — at the cost of one more system the balance pass must
  own. (Combinable with A or B.)
- **(D) Cut both mods.** Trade: two fewer assemblies, ~35 fewer Harmony
  sites, zero mounted anything on a Star Wars desert world — the tableau
  the setting is practically begging for goes away. Not recommended.

**Recommendation: A or B + C is defensible; my pick is A + C** — the mod has
earned current-era trust, the mechanoid module is flavor-coherent here, and
the caravan speed toggle is the one default that undersells the campaign.

Sources: About.xml + Source/ + Config on this machine (2026-09-12);
https://github.com/MemeGoddess/GiddyUp2 · Steam workshop 3674332861 page and
comments · workshop 3659593396 (the folded-in save patch) — all read
2026-09-12.
