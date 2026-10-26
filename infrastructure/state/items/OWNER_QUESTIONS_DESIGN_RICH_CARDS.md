# OWNER_QUESTIONS_DESIGN_RICH_CARDS

The owner's questions for the next card session (2026-10-26, verbatim). Answer them as RICH-CONTEXT
question cards (each card teaches the facts it depends on), together with the single-primary cards
D1-D7 as amended by `design/RimMandrake/orchestration_review_2026-10-26.md` §(e).

> "When we go to the question cards next, I have many questions, so make them rich with context. Like how
> does Bench self-manage its context so I don't have to? How can I track work being done so I'm aware? And
> if there's only one agent per mod, that implies we will always be working on many mods again. We only
> started making real progress closing mods when we focused hard on 1-2 at a time. So I'd like to know what
> we will have in place to bring back that intense focus to really grind on something to finish it, instead
> of make slow progress across many items. Lastly, it seems potentially valuable to use "blocked by" when
> we plan out tickets so that there's some shadow of the plan that can be computed and tracked. I really
> need some kind of "this week's plan" shown graphically and parts being ticked off as we go... REALLY
> ticked off, not just "text generated towards code" as it is today. That's part of what RimPulse should
> really be providing me, not just items to review. We have UtinniControl room and a bunch of other past
> attempts at this same need. DON'T build any UI right now. I want to know how we can get the answers that
> might be visualized on such an interface, not building interfaces."

## What each card must answer (design, not UI)

1. **Bench context self-management** — what Bench does so he never has to manage its context (thin
   orchestration, disk state, compaction, handoff triggers at 60/85%).
2. **Awareness of work in flight** — how he tracks what is being done without logging in (data sources,
   not screens).
3. **Focus vs breadth** — "one worker per mod" (GPT review) must not mean "many mods at once". Design a
   FOCUS mechanism: 1-2 mods ground to done, measured, overriding the allocator's spread. Evidence to cite:
   when mod closures happened historically vs how many mods were in flight.
4. **blocked-by planning** — a dependency field on items so a plan is computable (critical path, what's
   ready, what's blocked); check rimflow for an existing field first.
5. **"This week's plan" with REAL tick-offs** — define "done" as verified (verify levels L0-L4, live
   evidence), not "code generated"; what data answers "how much of this week's plan is truly done".
   Review UtinniControl room and the other past attempts first and say why each fell short.

DON'T build UI. NEXT: draft the cards (rich context, recommendation marked) and ask when he is at the bench.
