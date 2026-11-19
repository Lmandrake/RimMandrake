# RIMMANDRAKE_DESIGN_HOLDER_PIPELINE_FUSION_CHECKLIST_NOT_HANDOFF

## What the card said

<!-- answered 2026-11-16T05:43:36Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Sun Nov 15, 9:38 PM PST. All three options share one append-only ledger per mod (every other per-mod file becomes a printed view), blind judges, and one question register. A 'holder' is the one agent that owns a mod; a 'packet' is the short summary (10-20k tokens) the ledger prints for an agent picking the mod up. They differ in what carries context between pipeline stages. Which do we build?
**Picked:** Resumed session per mod (Recommended)
**Its description:** Why: keeps context as the mod progresses, unattended, which is what you asked for. The dispatcher resumes one long session per mod at every stage; built as the packet version first, falls back to it. Cost: a warm session can cling to a refuted theory; may cost more per stage; resume is untested in our detached launcher.
**Other options:** Resumed session, plus you sit in · Fresh runs from the packet only · Long-lived windows, one mod each

**Question:** Two of your rulings conflict. On Nov 13 you said a blind judge that finds problems 'should FIX THEM RIGHT THERE'. Tonight you said their feedback 'should come to that same builder that holds the mod long term'. Outside practice favours one writer of a mod's code. Who fixes what a blind judge finds?
**His words:** Anyone finding anything documents precisely how they would fix it but it goes back to the holder fully informed.
**Other options:** The holder fixes everything (Recommended) · Judge fixes trivial, holder the rest · The judge keeps fixing on the spot

**Question:** The first mod gets the new ledger alone, run beside its old files for a few days before the old files are frozen. Which mod is the pilot?
**His words:** Do all three side by side as a deeper test. When one reveals a needed fix to the system all three benefit.
**Other options:** Gimme Some Slack (Recommended) · FlowWorks · Explosive Knockback

**Question:** How much context may a holder build before it writes a checkpoint and a fresh session of the same holder takes over? Today's windows restart at 200k (our own setting). Artisan ran with a warning at 250k and a firm stop at 350k. The model's window is 1M and compacts itself at about 750k. What ceiling do holders start with?
**His words:** Try 400k first.
**Other options:** 350k, raise on evidence (Recommended) · 600k from the start · No cap until self-compaction
