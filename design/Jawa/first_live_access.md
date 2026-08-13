# first_live_access.md — Day-One Runbook (the first real build steps)

_What to actually **do first** now that vacation is over and we're starting to build this for real
(reframed 2026-08-09, replacing the earlier offline-first ordering). The in-game **scenario**
decisions still live in `setup_checklist.md`; this is the tooling / agent-integration runbook._

**The shape of the plan (user, 2026-08-09):** do NOT try to stand up the full campaign at once.
Three deliberately separated phases, each of which produces knowledge that reshapes the next:

> **A. Prove the live-LLM bridge on a *stock vanilla world* first.** Boot RimWorld on a default
> world with **RimBridge**, and get an LLM successfully hooked into the running game — **Ollama
> and/or Claude** (on the user's account). This is its own side project. Its real output isn't
> "a working save" — it's a **kit of agents, skills, and reusable approaches** that will reshape
> everything downstream.
>
> **B. Then load the whole mod stack (ours + the usual favorites) just to see it run.** Confirm the
> game still loads with everything on, make a real save, and **export one giant live inventory** of
> every item, creature, def, faction, etc. — harvested from the *running, everything-loaded* game —
> into a single list we can study together.
>
> **C. Only then decide how to adapt the design.** With the bridge proven and the live catalog in
> hand, we'll finally know enough to translate all this worldbuilding into a genuinely playable game.

**Why this order (the reasoning, so future-us doesn't "optimize" it back):**
- The LLM/bridge spike on a **default world** removes all mod-interaction noise. If something breaks,
  it's the bridge or the model — not a load-order collision. Cheapest possible place to learn the
  hard part.
- The spike is **research, not production**: the point is to discover the agent/skill patterns
  (transport contract, read-then-guarded-write, how the model wants to be prompted) that everything
  else will reuse. Treat throwaway code as expected.
- The **live** inventory (Phase B) is strictly better than an offline `Defs/`-scan for *studying what
  we actually have to work with*: it reflects what truly resolved and loaded together, catching
  silent mod-vs-mod overrides a static scan misses.
- Design-adaptation (Phase C) is **deferred on purpose.** We don't yet know enough to make good
  adaptation calls; A and B are what earn that knowledge.

**Shadow-mode default (carry into every phase):** wherever the divine-satiation / pantheon engine
touches the live game, the default posture is **shadow mode** — the engine *reports what it WOULD
do* (logs the satiation deltas and the events it would fire) without actually firing them, until we
choose to flip live injection on. This is the instrument-autonomy approach: you play a real game
while the system narrates its intentions to a log you can read afterward. (See
`divine_satiation_engine.md` §9 fallback + the playtest-reduction strategy.)

---

## PHASE A — Prove the live-LLM bridge on a stock vanilla world 🟣
_Goal: a running default-world RimWorld with an LLM talking to it through RimBridge. No campaign
mods. Deliverable = reusable infrastructure/agents/skills/patterns, not a save._

**A1. Stand up the local LLM backend (offline-preppable now).** Install Ollama on Windows and
confirm the REST API answers at `http://localhost:11434` (`Ollama is running`); pull a mid-size
instruct model. Full procedure + model-choice guidance in `ollama.md`. In parallel, confirm the
**Claude** path on the user's account (API access / whichever client the bridge will call). We want
to try **both** backends against the same bridge so we learn which is worth the latency/quality
tradeoff. → owns nothing new; consumes `ollama.md`.

**A2. Install RimBridgeServer on a vanilla 1.6 + Odyssey install.** Default world, default scenario,
no campaign mods (RimBridge + its deps only). Confirm the bridge comes up and the game is reachable
on its endpoint. Provenance/architecture notes in `rimbridge.md`. **Verify the READ path first**
(query game state) before any write.

**A3. Get the LLM into the loop — the actual spike.** Wire the model (Ollama first, then Claude, or
vice-versa) to the bridge so it can (i) read live game state and (ii) perform a small, reversible
action through the engine's own calls. **Save-backup before any write.** Success = one clean
round-trip: model reads state → proposes an action → bridge applies it → we see the effect in-game.

**A4. Harvest the reusable kit.** This is the real payoff. As A3 works, capture the patterns as
durable artifacts: the transport/capability contract, the read-then-guarded-write loop, prompt
shapes that worked, and any infrastructure/agents/skills worth keeping. These feed **`design/Jawa/worldbuilding/enrichment_agents.md` §4** and become
the substrate the religious agent cluster (A–H, incl. the divine-satiation engine) is built on.

---

## PHASE B — Full-stack load test + live inventory export 🔵
_Goal: confirm the whole mod list loads, make a real save, and export one giant studyable catalog of
everything live in the game. No design adaptation yet — just "does it run, and what have we got?"_

**B1. Assemble the full load order.** Our campaign mods (`required_mods.md`) **plus the usual
favorites the user enjoys**, RimSort-ordered. JawaVoice + Jawa_Patches load last.

**B2. Boot & red-error pass.** Launch to menu with the full list. Resolve red errors (watch Outland
Genetics — the Jawa def hard-refs its genes; confirm JawaVoice + Jawa_Patches load last). = mirrors
`setup_checklist.md` §0.

**B3. Make a real save.** Embark and save one game as the working fixture — everything loaded, live.

**B4. Export the giant live inventory (the study artifact).** From the running, everything-loaded
game, pull **one consolidated list** of items / things / creatures / terrains / factions / xenotypes
/ pawnkinds / traits / etc., into a single file we can read through **together**. This is the
"what do we actually have to work with" catalog. Two ways to get it, best-effort:
  - **Live via the Phase-A bridge** — query the loaded defs straight from the running game (captures
    exactly what resolved, including mod-vs-mod overrides). Preferred if A3 is solid.
  - **Offline Def index as backstop** — scan every active mod's `Defs/` the way the game does, using
    the **shortHash → defName resolver** (saves store defs as shortHashes, not names; rebuild that
    map by scanning active mods deterministically from defName+defType). Cross-check against
    `concept_defnames.md`. This is the fallback if the live pull isn't ready, and it doubles as
    validation that `OuterRim_Jawa`, the JawaVoice gates, and the `faction_roster_v2` cast actually
    resolve — catching typos before they become silent in-game no-ops.

---

## PHASE C — Decide how to adapt the design into a playable game 🔵
_Deferred on purpose. Only start once A (bridge proven) and B (live catalog in hand) are done._

With the LLM/bridge kit working and the full live inventory to study, we finally have the ground
truth to make the adaptation calls this whole `~/GDrive/Personal/Rimworld/` design corpus has been
building toward: which mechanics survive contact with the real def set, what the agents can actually
reach through the bridge, and how to stage the campaign so it's playable rather than endlessly
tested. **No decisions pre-committed here** — Phase C is where we sit down with the Phase-B export
and choose, together.

---

## Pre-reqs you can build BEFORE launching anything (no game needed)
These accelerate the phases above but don't block Phase A's core spike:
- [ ] **Ollama installed + API answering** (`ollama.md`) — pure offline prep for A1.
- [ ] **shortHash → defName resolver** — needed for the B4 offline backstop; build it now, it's
      deterministic and game-independent.
- [ ] **Enrichment capability contract** (transport-independent read/write schema) — the parent of
      whatever the Phase-A bridge loop implements; sketch it so A4's harvest has a home.
- [ ] **JawaVoice review sheet** + advance scenario spec / faction diffs — offline-authorable,
      consumed in Phase B.

**Open decisions that shape the above:** which LLM backend leads the Phase-A spike (Ollama for
free/local/private vs Claude for quality — plan is to try both); whether the full mod list is on disk
yet (gates Phase B). The eventual primary transport for enrichment (save-edit vs live RimBridge vs both) is
now expected to be **informed by** the Phase-A spike rather than decided before it.
