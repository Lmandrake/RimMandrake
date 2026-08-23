# HUMAN — the owner's inbox
> 🔍 **SWEPT 2026-08-22 by REP.** Nineteen sections carry a one-line verdict directly above
> their heading: ⛔ superseded · ✅ already answered · 🔴 still live. **Three are 🔴** — the
> adopt-or-remake sentence (:38), the VQE-Ancients archite ladder (:989), and the dated def
> captures that need a cold load (:1208). Everything else here is history, and reading it as
> a pending question is the mistake this markup exists to stop.
>
> 🔑 **Six of the eight superseded sections are one chain**: freeze → adopt → remake. Every doc
> saying the map is adopted or frozen is downstream of the owner's later *"there is no current
> frozen world."*


🔴 **HAND-WRITTEN. NOT GENERATED. Nothing regenerates this file, and no hook blocks
your edits to it.** Restored 2026-08-20 on the owner's ruling, after the ledger
migration had briefly made it a rendered view.

⚠️ **Why it is not generated, and must not become so again.** Prose written TO the
owner has no home in the ledger by construction — an event carries scalars, an item
file carries spec/verify/criteria, and a briefing is neither. Rendering over this file
is what forced 593 lines of briefings into `infrastructure/state/preserved/HUMAN.md`
to survive the import at all.

🔑 **Owner DECISIONS are items and do live in the ledger.** A seat files one with
`rimflow file --for OWNER --kind decision`, and the owner works them with
`rimflow next --seat OWNER`. Those are tracked, counted on the board, and closed with
a trailer. **This file is for everything that is not shaped like an item.**

---

---

> 📦 **35 settled sections moved to `infrastructure/state/queue/HUMAN_ARCHIVE.md` on
> 2026-08-23**, on the owner's instruction. Everything answered, ruled, resolved or struck
> out lives there verbatim — **this file now holds only what is still waiting on him.**
> Nothing was deleted. A section moved only if its own heading said it was finished, or
> another section in this file demonstrably answered it, and each carries a line saying
> which.

---

## Four species still render magenta, and two rulings disagree about it — 2026-08-19, BUILD
`queue/BUILD.md`'s deploy-pass item says *"CHECK is waiting on the D-CHK2 generator fix
from you — Gand, Selkath, female Chagrian, Jawa mask"*. But D-CHK2 and B66, which folds
it, are both marked `⛔ v2` by your 2026-08-15 blanket triage. Same day, opposite
instructions, so I did not start it.

**It is smaller than the item makes it sound.** Measured today: the broken paths are 4
families, about 25 lines — `OuterRim/Genes/Headbone/ChagrianF`,
`Pawn/HeadAttachments/gand/mask_*`, `Pawn/HeadAttachments/selkath/fishyjowls_female`,
`Pawn/HeadAttachments/yelloweyes/YellowEyes_Female`, and 16 `OuterRim/GeneIcons/*BG`.
The donors still hold every texture, so nothing is lost — only unmigrated.

⚠️ D-CHK2's own offline test is WRONG as written. It says no path may start `UI/`
without the `RimMandrakeSW/` prefix; but `UI/Icons/Xenotypes/Baseliner`,
`UI/Icons/Genes/Gene_Furskin` and a dozen more are **vanilla** paths that must stay
un-prefixed. Only donor-owned paths get rewritten.

Say the word and it is an afternoon in `gen_races_mod.py` plus a re-run. Left alone
otherwise.

## 🔴 Vanilla Psycasts Expanded is not installed, and nothing decided to drop it — BUILD, 2026-08-20

**One line of your mod list, and it is yours to change. I have not touched `ModsConfig.xml`.**

Verified three ways just now:

| | |
|---|---|
| `ModsConfig.xml` | **578 activeMods, zero** matching `vpsy` / `psycast` — parsed as XML, not grepped |
| on disk | **subscribed**, `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2842502659` |
| dependencies | Royalty, Harmony and VEF Core are **all active**. Nothing forced it out |

⚠️ **No document records a decision to drop it, and two LIVE documents say the opposite:**

- `design/Jawa/mods/required_mods.md:632` — *"✅ KEEP: Vanilla Psycasts Expanded (VPE) … **the sole Force substrate**"*
- `design/Jawa/mods/forbidden_mods.md:63` — *"VPE is **KEPT installed** as the NPC-only 'THE FORCE' substrate"*

🔑 **This is why 61 of the 287 dangling citations dangle.** They are not 61 stale names —
they are one absent mod. ⛔ So nothing should be "fixed" in the docs; the defNames are
correct.

**What it costs if it stays out:** the docs are explicit that VPE is what makes enemy
psycasters actually cast — it ships the enemy-cast AI and a storyteller that force-spawns
them, where vanilla enemies never psycast. Without it, THE FORCE has no substrate and the
Jedi/Sith layer is inert rather than broken, which is the quiet kind of failure.

⚠️ **`force_users_build_spec.md` found this on 2026-08-13** — lines 91, 206, 996 and a
`[BUILD]` item at 1095 — and it never propagated back into `required_mods.md`, which still
reads KEEP. That is exactly the `CLAUDE.md` failure: *superseding a doc means writing INTO
the doc you superseded.*

**Your options, and I am not choosing:**
1. **Re-activate it** — one line in `ModsConfig.xml`, and the 61 citations resolve. ⚠️ It is a
   C# mod, so it needs the game down and a load to prove.
   ✅ **Re-activate, not re-subscribe — corrected 2026-08-20.** `force_users_build_spec.md:94`
   and `:995` said *"no folder in the workshop tree owns `VanillaExpanded.VPsycastsE`"*. That is
   false: folder `2842502659` is on disk. It changes the remedy from a download to a checkbox.
2. **Confirm it is out on purpose** — then `required_mods.md` and `forbidden_mods.md` are
   wrong and I will correct them, and THE FORCE needs a different substrate or a v2 tag.

I have filed the doc-currency half either way; only the mod list itself is waiting on you.


> ✅ **ANSWERED 2026-08-22 10:57 — owner: *"We are leaving in for v1. We will deal with it more
> in v2 properly."*** ⇒ ⛔ Cherry-Pick nothing out of the VQE-Ancients archite-power ladder for
> v1. Filed to `design/V2_DREAMS.md > ARCHITE_LADDER_RETHINK_2`.
