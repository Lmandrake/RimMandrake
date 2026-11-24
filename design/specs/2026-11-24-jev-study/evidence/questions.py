"""Jev study 2026-11-24: every question, written BEFORE the first run. No thresholds are set here."""
MODEL = "jev-latest"
TICKET = {
 "verdict": {"type": "choice",
  "instructions": "A team fixes a ticket only when someone would care about the fix. Read the ticket in `title` and `filed_why`. Which verdict fits?",
  "criteria": {
   "fix_it": "The ticket reports a failure or wrong result that happened, or a significant problem that ordinary use of the game or of the build pipeline reaches.",
   "not_worth_the_touch": "The problem is only predicted, is a narrow case that was never seen, concerns something retired or unused, or the change is only wording, tidying or record-keeping that steers nothing."}},
 "failure_observed": {"type": "noul",
  "instructions": "Does the ticket in `title` and `filed_why` report a failure or a wrong result that was actually observed in a run, a test, a log or the game?",
  "criteria": {"true": "It names something that was seen to fail or to give a wrong result.", "false": "It describes a possible, predicted or hypothetical problem, or a wish, with nothing seen to fail."}},
 "predicted_only": {"type": "noul",
  "instructions": "Is the problem in `title` only a prediction by a reader or reviewer, such as a narrow race or an edge case that was never seen to happen?",
  "criteria": {"true": "It is a predicted or theoretical case; nothing is reported as having happened.", "false": "It reports something that happened, or asks for new work that is not a predicted fault."}},
 "ordinary_reach": {"type": "noul",
  "instructions": "Would ordinary play of the game, or an ordinary run of the build and test pipeline, run into the problem or need described in `title`?",
  "criteria": {"true": "Ordinary use reaches it.", "false": "Only an unusual, rare or retired path reaches it."}},
 "wording_only": {"type": "noul",
  "instructions": "Is the change that `title` asks for only a change to wording, a document, a figure in a document, a name or a record, with no change to how the game or a program behaves?",
  "criteria": {"true": "Only text, names or records change.", "false": "The behaviour of the game or of a program changes."}},
}

FINDING = {
 "verdict": {"type": "choice",
  "instructions": "A reviewer wrote the finding in `finding` about code or a rule document. Is it a significant finding or a minor one?",
  "criteria": {
   "significant": "It is measured, or it gives a concrete case (this input, this wrong result), and it breaks a stated promise or causes a failure in ordinary operation.",
   "minor": "It is a nit, a matter of style or wording, a suspicion that was not measured, or a case that ordinary operation does not reach."}},
 "concrete_case": {"type": "noul",
  "instructions": "Does `finding` give a concrete case: a named input or situation and the wrong result that it produces?",
  "criteria": {"true": "A specific input or situation and its wrong result are named.", "false": "No specific case with a wrong result is named."}},
 "measured": {"type": "noul",
  "instructions": "Does `finding` say that the problem was measured or seen to happen?",
  "criteria": {"true": "It reports a measurement or an observed occurrence.", "false": "It is a suspicion, a prediction or an opinion."}},
}
# play-time sample: a resident's reaction, a closed set of acts (authored), state from the game
REACT = {"type": "choice",
  "instructions": "The `resident` lives and works at the `place`. The `event` just happened. Which one act fits this person best?",
  "criteria": {
   "keep_working": "Carries on with the work as if nothing happened.",
   "watch_warily": "Stops and watches the newcomers from a distance.",
   "greet_and_offer_trade": "Walks over to greet the newcomers and offers to trade.",
   "hide_indoors": "Goes inside and stays out of sight.",
   "fetch_the_guards": "Runs to warn the guards.",
   "flee_the_place": "Leaves the place for good."}}
MOOD = {"type": "score", "instructions": "How does the `resident` feel about the newcomers right now?",
  "criteria": ["Hostile", "Afraid", "Wary", "Neutral", "Friendly"]}
