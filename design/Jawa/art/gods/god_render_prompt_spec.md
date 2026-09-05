# The Nine Gods — render prompt spec

_BENCH + owner, 2026-09-05. One strong, reusable prompt definition for generating
the gods as FIGURES (replacing the old abstract-symbol set entirely — do NOT
reference it). Tenets from `divine_satiation_engine.md` §2-3 +
`nine_voices_cast_bible.md` §2. Per-god MOTIFS are BENCH's proposal; style/palette
is BENCH's proposal — owner may override any cell._

## THE JAWA VISUAL LAW — every god, non-negotiable (owner, 2026-09-05)

The gods are **Jawa gods** who **predate the campaign**. Every render obeys:
- **Always hooded and robed** — the face is shadow within the hood.
- **Furry body**; robe over a rodent-like Jawa pelt.
- **Glowing eyes, NO pupils** — per the owner's reference
  (`references/jawa_canon_hands_eyes_rope.jpg`): two **warm amber-orange** lights
  in total hood-shadow, slightly **uneven/asymmetric**, the ONLY part of the face
  that reads. Eyes may be **reshaped by emotion** (narrowed/widened/slanted) —
  nothing else of the face shows.
- **Strange hands** — per the same reference: **furry, dark, gnarled** hands with
  thick textured fingers (mottled green-grey where lit), gripping/reaching. Base is
  canonical Jawa (furry black five-fingered rodent hands, short fur up the wrist);
  for the gods, exaggerate into **strange, gnarled, too-long or too-many-knuckled**
  furry hands from deep sleeves. Focal motif (esp. Ohm, "lonely for his lost hands").
- **Robe (from the reference):** layered rough rust-brown cloth, a **bandolier
  strap with a buckle** across the chest, hem torn/salvaged.
- 🔑 **Feed `references/jawa_canon_hands_eyes_rope.jpg` to the generator as
  `--edit-image` to lock the eyes/hands/robe across all nine gods.**
- **World:** desert, scavenged tech, sand crawlers, droids all welcome.
  🔴 **NO Utinni spaceships / gravships** — the gods predate them.

## Style & palette (BENCH proposal — owner rule)

- **Style:** painterly, reverent, dark religious-iconography concept art; heavy
  chiaroscuro; the eyes and hands catch the only strong light.
- **Ground palette (shared):** oxidised desert rust, bone/sand, deep indigo-black,
  with a hot **brass/amber** sacred accent — the same shell language as the UI.
- **Per-god accent (its domain's colour), layered over the ground:** Ishko
  near-black; Ohm electric-arc blue; Oomo pale water-silver; Mob'Unloo tarnished
  copper/ledger-green; Rekko warm salvage-bronze; Ta'Baa wind-grey/horizon-gold;
  Zizzik sickly spark-green; Sh'kaar searing white-gold (over-exposed); Ozzik
  faded royal purple + tarnished gold.

## The nine — tenet · persona · motif · accent

| # | God | Domain (canon) | Persona (canon) | Motif (BENCH) | Accent |
|---|---|---|---|---|---|
| 1 | **Ishko the Unmaskable** | hiding, ambush, the prepared dark | patient watcher; speaking costs him | robe dissolving into dark; eyes barely lit, watching from a buried hatch/nook | near-black |
| 2 | **Ohm the All-Current** | the living machine | warm, arrogant; kin to droids; **lonely for lost hands** | reaching with/toward strange hands; dormant droids waking; arcs in the pelt | arc-blue |
| 3 | **Oomo the Unspilled** | water, thirst, rationing | needy, anxious; water finding cracks | a single hoarded droplet cupped in the strange hands; hem damp-dark | water-silver |
| 4 | **Mob'Unloo the Ever-Owed** | debt, trade, exchange | everything is a term sheet | hands weighing scavenged tokens/scales; scratched tallies in the folds | copper/green |
| 5 | **Rekko of the Second Hand** | salvage, repair, the rewoken | memory-keeper; the ONLY comforter; proud | mending a broken droid in his lap; robe patched from salvage; gentlest eyes | salvage-bronze |
| 6 | **Ta'Baa the Unrooted** | leaving, the threshold | breathless, restless; always at the door | mid-stride at a dune edge / sand-crawler ramp; robe wind-caught; looking away | wind-grey/gold |
| 7 | **Zizzik the Spark-Maker** | malfunction, betrayal, misfortune | gleeful trickster, chaotic | eyes slanted in delight; wrong sparks arcing from broken tech | spark-green |
| 8 | **Sh'kaar the All-Searing** | evil light, exposure, destruction | cruel, malevolent; "the eye" | a searing light within the hood over-exposing all; most frightening eyes | white-gold |
| 9 | **Ozzik the Shamed** | ambition, pride, grief (THE TRAP) | grandeur with the wound showing | broken salvaged crown; robe grand but torn; eyes proud AND grieving | purple/gold |

_(The tenth strand — the Cradle's own purpose — has no voice and no figure.)_

## Four output types per god

1. **Bust portrait** — square (1:1). Head-and-shoulders to mid-torso. Eyes + hands
   the focus. The roster/icon image.
2. **Full figure in domain** — portrait (~2:3). The whole robed god within a small
   scene of its domain.
3. **Enthroned scene** — landscape 2560×1440. The god embedded in a rich
   environment; a menu/loading-screen painting.
4. **Shrine hologram manifestation** — the god's PRESENCE for the in-game ship
   shrine: a **glowing, translucent, edge-lit** manifestation on a dark/empty
   ground (compositing-friendly). May be the figure OR a floating abstract form
   (a hooded silhouette of light, a constellation of glowing eyes + hands, a
   spectral emblem). **Generate a few options per god.**

## Prompt skeletons

**Shared prefix (every prompt):**
```
A <TYPE> of <God> the <Epithet>, a Jawa god (predates all spaceships): hooded and
robed, furry rodent-like body, two glowing pupil-less eyes [<emotion>] in hood-shadow,
strange furry black five-fingered hands from deep sleeves. <MOTIF>. Desert / scavenged
tech / sand crawlers / droids as fits; NO spaceships. Painterly dark religious
iconography, chiaroscuro; ground palette rust/bone/indigo + brass accent, this god's
accent <ACCENT>.
```
- **Bust:** `<TYPE>` = "reverent square bust portrait", tight on eyes+hands, 1:1.
- **Full figure:** `<TYPE>` = "full-figure portrait", the god within a small
  domain vignette, 2:3.
- **Enthroned:** `<TYPE>` = "wide cinematic scene", god enthroned/embedded in its
  domain, 16:9 / 2560×1440.
- **Hologram:** `<TYPE>` = "glowing translucent holographic manifestation on a
  black ground, edge-lit, volumetric, compositing-ready" — run 3-4 seeds/variants,
  half as the figure, half as an abstract floating form.

## Generation notes

- Channel: paid Codex (`make_sprite.py`) + rembg where alpha is needed (holograms).
  Reference-image conditioning available via `--edit-image` (feed a real Jawa-hands
  reference once obtained, to lock the hand shape across all nine).
- Do all nine in ONE type first (e.g. all busts) so the SET reads consistent before
  moving to the next type.
