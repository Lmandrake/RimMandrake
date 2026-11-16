You are an independent systems designer. Answer from your own judgment; you are not reviewing anyone's design.

CONTEXT. One human owner directs a fleet of LLM coding agents (Claude Code sessions, each with a hard context
limit of roughly 200k tokens; a session that fills restarts and keeps only what was written to disk) that build
mods for the game RimWorld. Two days ago the work moved to a "Maturation Pipeline": the unit is one versioned mod
(e.g. "Gimme Some Slack" v0.1.0), and it passes stages: 1 Designer (spec + acceptance bars, then locked),
2 preflight, 3 offline build, 4/5 blind offline challenge (a fresh judge that did not build it checks the bars,
fixes what it finds, and hands to another fresh blind judge; cycles counted), 6 in-game acceptance (a live game
driven by a bridge), 7 pre-human check, 8 the owner's live walk. A 60-second dispatcher timer launches a fresh,
detached, capped agent run (USD 15 budget each) for whatever stage a mod needs; each run starts cold from a
ticket/brief and the mod's files. A "steward" (the one orchestrator window the owner talks to) reads evidence at
stage changes. Per-mod state lives today in many places: a stage.json, a journal.md, a log.md, record.json,
exam.json, coverage_verdict.json, a bars file, a test table, run result files, the append-only ticket ledger
(thousands of open items; item notes), reboot handoff files, the orchestrator's log, a dispatcher state.json and
hand-acts log, a generated status page, incident plans. Before this pipeline, two long-lived seats ("Foundry"
and "Bench") each carried a piece of work from build through its own live test.

OBSERVED THIS EVENING. About 22 helper runs ended in 2.5 hours; every mod-facing one ended "offline done, live
unrun"; close to half were the pipeline fixing its own machinery, most filing 1-3 new tickets; a question the
owner had already answered came back from a stale file; a helper was launched twice on a cause already known to
be wrong because it started from ticket prose; the orchestrator relayed ~15 event reports to the owner.

THE OWNER'S WORDS (verbatim): "The pipeline was never intended to replace a total mod ownership. Each step in the
pipeline could even be done with an owning builder that keeps picking up the item as it goes. That way context is
kept as it progresses. I don't think access to the live game would have helped most of these issues. But forcing
everyone to write their progress into a single source of truth would have. That should simply be implemented. We
need a ledger that grows the mod state monotonically and is stored nowhere else. Blind judges are a good idea. We
must not drop that. But their feedback should come to that same builder that holds the mod long term. A fusion.
The pipeline is a checklist for the long term holder to follow, not a handoff between constant context losses."

FIXED POINTS (decided, do not reopen): blind judges stay; one monotonic per-mod source of truth is to be built.

ASK. Design this. Give two or three genuinely different options for how to make it real (what a "long-term
holder" actually is given hard context limits, what the per-mod ledger's schema and single-writer rule are, what
becomes a generated view, how blind-judge feedback reaches the holder while the judge stays blind, which stages
the holder does itself versus which stay independent, how questions to the owner are tracked, smallest first
step). For each: trade-offs, failure modes, cost. Name how established software practice (event sourcing, DRI
ownership, WIP limits, published guidance on long-running agents) bears on it. Then give your pick and why.
Be skeptical of the owner's hypothesis where it deserves it. Under 1500 words.
