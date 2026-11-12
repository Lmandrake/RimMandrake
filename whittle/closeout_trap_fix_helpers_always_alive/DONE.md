# Done claim (draft: the close step and the final review are still pending)

## What I'm least sure about
- The guard reads ledger promises through the deadman's own reader (the bench clone plus this clone). Off this machine
  it sees only this clone's ledger.

## What I did not test
- A hook under a renamed event key, or a disabled command that still names the file (`true # x.py`): the guard would
  read either as wired. Both are outside the class (a landing that replaces the file); see BROADEN.md.
