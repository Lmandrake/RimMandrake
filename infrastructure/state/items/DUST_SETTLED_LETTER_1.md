
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row SS-3 there is the spec:

| SS-3 | If a group announced by "dust on the horizon" never actually arrives (its incident fails or times out), send a short "the dust settled — they turned back" letter, and keep the plume up until real arrival instead of a fixed tick. Players currently get a promise that silently evaporates. | nothing | S | low | Stillsand | `RM_HorizonWarning.cs:160-161` queues with a 1 h retry window, plume expires at `fireTick` (`:253`); nothing reports a failed fire. HORIZON_WARNING_DROP_RAIDS_1 is the drop-raid bug only. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
