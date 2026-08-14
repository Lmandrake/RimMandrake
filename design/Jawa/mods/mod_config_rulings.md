# mod_config_rulings.md — accept/reject rulings and configuration guidance

_Hand-authored. **This is the reasoning half of the mod inventory.** It was
carved out of `observed/2026-08-13/live_mod_inventory.md` on 2026-08-13, when
that file was put under a generator (`src/RimMandrake/Utils/mod_inventory.py`)
and could no longer carry hand-written prose — a file stamped "do not
hand-edit" must not contain judgement calls._

**Identity questions — does a mod exist, its packageId / Workshop ID /
supported versions — are answered by `observed/2026-08-13/live_mod_inventory.md`,
which is generated and authoritative. This file holds only the "why".**

Sections below are verbatim as of the 2026-08-10 third pass, and carry that
date's judgement; the mod counts they were written against have since moved
(562 → 580). Nothing here has been re-verified against the current stack.

---

## 1. Newly ACCEPTED this pass

| Mod | WS | Role | Notes |
|---|---|---|---|
| **Effigys – Terror Spikes** | 3647930333 | ✅ **ACCEPTED — Hutt territory decor.** Wooden effigy crowned with five human heads; fear aura. | Requires **Ideology**. packageId is literally `YourName.Effigys.Mod` — an unedited template. Cosmetically harmless but a sign of a hobby build; treat as art, not mechanics. Serves `desert_world_design.md` §3F (turf markers on Hutt ground) alongside `GibbetCage`/`Skullspike`. |
| **Torment Master** | 3746663772 | ✅ **ACCEPTED — Hutt flavour + fodder for tile maps / settlements.** | Requires **Biotech**. 6 buildings: Brazen Bull, Oil-Pour Cage, Water Prison, Laser Flayer (yields a wearable skin suit that disguises the wearer as the donor), Live Target Range, Auto-Vending Machine (sells organs; factions send buyers → **goodwill**). Plus a Cranial Pin (surgical prisoner-compliance implant) and trinkets. Author states: compatible with HAR, Facial Animation, Toddlers, Prison Labor; **safe to add mid-save**; to remove cleanly, deconstruct everything and reverse the pin surgeries first. |
| **Dynamic AI Sculptures** | 3753149685 | ✅ ACCEPTED — see §2. | `codex.dynamicaisculptures`, Artas48. Hard deps: Harmony + Powerful AI Integration. |
| **Powerful AI Integration** | 3744421283 | ⚠️ ACCEPTED **as a dependency only** — see §2. | `codex.dynamicrolesstoryteller`, Artas48. Note the packageId: this mod's real identity is a **dynamic-roles storyteller**, not an art library. |

## 2. ⚠️ Powerful AI Integration — read before configuring

Dynamic AI Sculptures is a genuinely good fit: craftable sculptures in 1×1 / 2×2 / 3×3 / 4×4 whose
artwork is AI-generated, imported, or pulled from a public community library, with **textures applied
live in-game** — no restart, no save reload. There is a reveal-cloth animation when the art lands, and
approved community results can be downloaded so it works before you configure any image provider.
For a scrapper clan that venerates salvaged objects, procedurally-unique sculptures are close to ideal.

**But its dependency is not a graphics library.** `Powerful AI Integration`'s own description (Russian)
translates to: *"adds a shared AI layer for the story and life of the colony: an **event director**,
**dynamic roles**, player prayers, live pawn dialogue, conversation memory, relationships and
storylines. It accounts for characters, factions, canon, colony state and real game events, works with
local models, bridges and OpenAI-compatible APIs, and falls back to safe local rules when needed."*
Its packageId is `codex.dynamicrolesstoryteller`.

**That is a fourth LLM director**, on top of RimTalk (30 mods), RimAI Core, and our own external
RimBridge/Imperial-Heat GM layer. Its warning is also explicit: *"do not remove the mod from a started
save without a backup."*

**Ruling: install it, use the sculpture path, leave the director OFF.**
- Turn off / do not configure: the event director, dynamic roles, prayers, pawn dialogue, memory.
- Reason: an LLM firing events competes directly with the **Imperial Heat gauge**, the sanctioned
  pacing mechanism — same objection that parked `RimTalk Expand: AI Storyteller`.
- Its pawn-dialogue layer is a **fifth** owner of speech bubbles. Leave it off.
- It can share the Ollama endpoint (`http://localhost:11434/v1`) for image/text calls once that is up.
- Because it is save-embedded, decide *before* the campaign save, not after.

## 3. Standing conflicts / open items

| Item | State |
|---|---|
| **Speech-bubble owners** | SpeakUp + RimTalk + Interaction Bubbles all active — and Powerful AI adds a fourth if its dialogue layer is enabled. Scope to one. |
| **Big and Small ×6 + Large Pawns** | Deliberate scaling experiment. |
| **AUR trio** | Correct — Hit Point *requires* All Deconstructible. |
| **Lightsabers** | Resolved — only The Force – Lightsaber (KotOR hard-dep). |
| **RimTalk Expand: AI Storyteller** | Recommend OFF (competes with Imperial Heat). |
| **RimTalk – Expand Actions** | Disable `recruit` and `surrender`. |
| **RimAI Core** | Voice-only; actuator tools off. |

