# CONTAGION_GPT_ENRICHMENT_1 — three GPT-suggested enrichments the owner picked

Source: a GPT enrichment consult (codex exec, gpt-5.6-sol xhigh, 2026-09-30) on the Contagion. The
owner picked these three by question card; GPT's seven other ideas were not picked, so they are out.
Builds on `CONTAGION_RULED_CONTENT_1` and `CONTAGION_MECHANICS_BUILD_1`, and must stay inside what the
Contagion sitting ruled.

## spec

1. **Draftprints.** The owner typed this note on the card: *"I like the helix offering to purchase
   strange scans of the beasts here. You assume the risks"*. Sampling an Unfinished before it dissolves
   yields a labelled Draftprint that records its rolled limbs, its extreme stat and its failure. The Helix
   posts contracts for particular combinations ("eyeburst, asymmetric locomotion, excessive clotting")
   and buys the scans. The risk of getting close to an Unfinished is the player's. GPT also suggested
   that Draftprints could steer Wombpod gestation toward a chosen limb without removing that limb's
   danger; that is optional, and the owner did not comment on it. Build: dynamic `ThingComp` data,
   inspect strings, a sample `ThingDef`, Helix contract `QuestNode`s. Small C#. **Model: sonnet.**
2. **The Dive.** When a Burn approaches, UV-shy natives visibly race, crawl or flop toward roofs, red
   water, dense Eyebark or goo pockets. Gawpsacks lower without despawning, and Skinflaps drape over
   branches. Sun-lovers (Scaldhides, Crisplings) go the opposite way. Colonists must decide whether to
   follow the animals. Build: a Burn-response `DefModExtension`, shelter scoring and a `JobDriver`, and a
   Harmony insertion into animal job selection. Large C#. **Model: opus.** Once `SOLAR_HEAT_EXPOSURE_1`
   lands, reuse its shelter-seeking and pathing pieces rather than duplicating them.
3. **Bodyprints**, which enforces the owner's no-vanishing rule. Native corpses pass through visible
   phases: a recognizable carcass, then collapsed skin, then a glossy anatomical print stained into the
   ground. Bloody Mess must physically reach and consume the remains; otherwise the print persists long
   enough for one final sample, which feeds Draftprints. Blisterfloats leaving the map deposit burst
   husks at the ridge. Build: XML corpse and filth defs, plus a small C# dissolution comp. **Model: sonnet.**

Each ships a Mod Settings toggle and tuning.

## criteria

Each of the three is quicktest-proven on a Contagion map, and no native disappears without a
visible remainder.
