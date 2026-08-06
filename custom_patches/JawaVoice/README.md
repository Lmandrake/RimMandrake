# JawaVoice — SpeakUp Jawaese reskin

Makes Jawa pawns speak Jawaese in SpeakUp interaction bubbles, in the shape:

> **Jit jot zoot goot. (Well, there goes everything...)**

A synthesized Jawaese utterance followed by the original English as a
parenthetical "translation of the situation."

## How it works

This is a **pure-XML, assembly-free** patch mod. For every SpeakUp
`InteractionDef`, it uses `PatchOperationAdd` (wrapped in
`PatchOperationConditional` so a missing target is a silent no-op) to inject a
handful of **high-priority, identity-gated** Jawaese lines into the def's
`<rulesStrings>`.

- **Jawa pawns** match the identity gate → their high-priority line wins → they
  speak Jawaese.
- **Everyone else** — temporary non-Jawa slaves (accepted leak, by design) and
  all non-player factions — fails the gate → falls through to SpeakUp's
  **untouched** vanilla English lines.

Because we only **add**, all of SpeakUp's dynamic conditional logic (weather,
mood, jobs, traits, opinion, etc.) is preserved. The Jawa line simply sits on
top at higher priority for pawns who qualify.

## The identity gate

SpeakUp's grammar exposes **no `xenotype` condition** (verified from its
`ExtraGrammarUtility.cs`), and Jawa-ness in this stack is a *xenotype*
(`OuterRim_Jawa`). So the gate is a dual proxy:

| Who | Condition |
|---|---|
| Colonists (all-Jawa colony) | `INITIATOR_faction==PlayerColony` / `PlayerTribe` |
| Encountered NPC Jawas | `INITIATOR_kind==OuterRim_Jawa` / `OuterRim_JawaTribal` |

**Known, accepted leak:** a temporary non-Jawa slave in the colony also matches
the faction gate and will speak Jawaese until sold. This was accepted as fine.

**Precise upgrade path (optional):** author a custom `TraitDef` (e.g.
`Jawaese-speaker`), force it onto the Jawa xenotype/pawnkinds, and switch the
gate to `INITIATOR_trait==...`. To do this, edit `GATES` in
`Utils/build_jawavoice.py` to the single trait predicate and regenerate.

## The three-tier voice (per `jawa_dialogue_source_audit.md`)

1. **Canon anchor** — where a real Ben Burtt licensed phrase fits the moment, it
   is used verbatim with its licensed meaning: `Utinni! (A find!)`,
   `M'um m'aloo. (Hello.)`, `Ibana. (Yes.)`, `Nyeta. (No.)`, `Taa baa. (Thanks.)`.
2. **Chitter** — untranslated §4 fragments, available for idle flavor (no gloss).
3. **Synthesis** — phonology-matched invented Jawaese for the long tail, glossed
   by the def's own English line. Deterministic (seeded by the English text), so
   regeneration yields identical output and clean diffs.

**Policy guard:** synthesized lines are creative pastiche (exactly what the film
sound designers did). They are permitted in-game but must **never** be written
back into the attested corpus (`jawa_dialogue_source_audit.md` §3/§4).

## Regenerating

```
cd Utils
python3 build_jawavoice.py
```

Reads the SpeakUp 1.6 source snapshot in `Utils/_speakup_src_1p6/` and rewrites
`custom_patches/JawaVoice/Patches/*.xml`. Coverage: **185 defs, ~3,200 gated
lines** across weather, needs, thoughts, jobs, games, social chat, jokes,
prisoners, romance, and animals.

## Files

- `Utils/jawaese.py` — the phonology + canon/chitter/synthesis engine.
- `Utils/build_jawavoice.py` — the emitter (harvests glosses, applies gate, writes XML).
- `Utils/_speakup_src_1p6/` — input snapshot of SpeakUp's 1.6 Defs (do not edit).
- `Patches/JawaVoice_*.xml` — generated output, one file per source Defs file.

## Tuning knobs (in `build_jawavoice.py`)

- `GATES` — the identity predicates (swap to a trait gate here).
- `MAX_GLOSSES` — variety lines per def (default 6).
- `PRIORITY` — must stay above SpeakUp's own (~5); default 9.
- `ANCHORS` — defName → canonical-phrase situation mapping.
