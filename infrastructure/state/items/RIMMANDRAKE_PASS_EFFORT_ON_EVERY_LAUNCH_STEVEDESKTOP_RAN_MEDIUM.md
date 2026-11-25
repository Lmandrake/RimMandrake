# RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM

## What the card said

<!-- answered 2026-11-25T19:47:14Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Effort is the setting that tells a model how hard to think on each step: medium, high, xhigh or max. I measured the last three days of runs. On Archmagi: 707 Opus runs at high, 134 Sonnet runs at medium, 44 Fable runs at medium. On SteveDesktop: all 32 Opus runs at medium, because that machine lacked the setting (I fixed that at 11:40 AM PST for new runs). Our launchers pass no effort; each run takes whatever the machine's settings say. (Hard to read? Type STE, Binding or Both for a rewrite.) What effort should a run that builds or fixes start at?
**Picked:** No medium anywhere
**Its description:** Why: simplicity, one floor for everything. Buys: no run is ever under-thinking, and no rule to remember. Costs: searches, counts and bare judge calls also pay for high, where a test or a re-read catches mistakes cheaply anyway.
**Other options:** High for all builders (Recommended) · Keep medium first, raise on failure · Extra-high for all builders

**Question:** A worker is stuck when its fix failed once, or when the new ticket filer refuses its attempt to file the problem instead of fixing it. I tested one thing just now: resuming the same session at a higher effort keeps its prompt cache (a Sonnet session went medium to high to xhigh and re-wrote under 600 tokens each time), so 'try harder' in the same context is nearly free. Changing the model is different: it always re-writes the whole context (measured this morning: a median 566k weighted tokens to Opus, 1.2M to Fable). What should the pipeline do with a stuck worker?
**Picked:** Effort up, then model up (Recommended)
**Its description:** Why: use the nearly free step first. The pipeline resumes the same session one effort level higher. If still stuck, the worker writes its theories and readings to a note and a higher model starts fresh from that note. Only then does it reach me. Costs: new launcher code. Recommended: it matches the measured costs.
**Other options:** Effort up only · Model up first · Keep rescue as a Conductor decision

**Question:** You see the Test Pilot (a Fable run that debugs one stuck item live, by experiment), the Fable Rescue (a Fable run sent in when ordinary runs fail on a mod) and the ordinary Work Bundle worker (an Opus run that builds, tests offline and tests live in one context) as one thing. I agree on what they do. The one real difference left is method: the Test Pilot writes its theories before it experiments and changes one thing per experiment, where a builder codes and retests. How should the role definitions change?
**Picked:** One builder, three settings (Recommended)
**Its description:** Why: one definition to maintain and no hand-off between roles. A single builder file; model, effort and scope are launch settings; the Test Pilot's experiment method becomes what any builder does once stuck. Costs: a rewrite of three role files and their launch paths. Recommended: the roles already differ only in settings.
**Other options:** Shared core, three thin files · Leave the three roles · Fold only the rescue into the Test Pilot

**Question:** Fable is the top model tier, used for the Conductor window, the Test Pilot and rescues. I measured 44 Fable runs in three days at medium effort and one at xhigh. I did not separate Conductor windows from rescue and Test Pilot runs in that count. So the tier we escalate to may be thinking less hard than the Opus tier below it. What effort should a Fable run on stuck work use?
**Picked:** High (Recommended)
**Its description:** Why: match the tier below, so an escalation is never a step down in effort. Buys: a clear ladder where each step is stronger. Costs: more thinking tokens per Fable run, on the most expensive model. Recommended: it leaves xhigh as the next step if a Fable run is itself stuck.
**Other options:** Extra-high · Leave it at medium · Measure first on three rescues
