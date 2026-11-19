# RIMMANDRAKE_DESIGN_REVIEW_TREADMILL_FIX_COUNT_WAS_FLAT

## What the card said

<!-- answered 2026-11-19T07:22:45Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** The problem: nobody wrote down what the pipeline's control code must do and must not do. So each review found about 15 new complaints, and only 0 to 2 were real. Before a helper writes new pipeline code, what do we do first?
**Picked:** Write a one-page list (Recommended)
**Its description:** The page lists what the code accepts, which failures it does not handle, and what it promises. Each promise gets a test. A reviewer can only report a broken promise. I recommend it because builder and reviewer then use the same list. Cost: about 16-20M weighted tokens once [guess]. New code that kills runs goes live in half a day, not one hour.
**Other options:** No list; filter complaints · No list; test by running it · No list; tools block bad code

## What the card said

<!-- answered 2026-11-19T07:21:35Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Your standing rule says only a whole-file review with zero significant findings makes code clean. Each repair therefore earned another whole review, and repair code drew claims at 5 to 8 times the rate of older code. When is a piece of pipeline code 'clean'?
**Picked:** Promises tested + two looks (Recommended)
**Its description:** Why: gives review a stopping point. Recommended because it ends the loop and keeps the first full inspection, where every dangerous finding came from. Buys: later edits stay clean while promise tests pass. Costs: needs the boundary page; a real case left off the page is not looked for.
**Other options:** Only serious findings block · Keep today's rule

**Owed by this card** (the close names where each was done or filed): needs the boundary page

## What the card said

<!-- answered 2026-11-19T07:22:45Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Tonight's reviews left 18 complaints open. A helper says none is dangerous. Eight are small improvements. Ten are about the control code, and nobody has checked if they are true. Earlier tonight you said 'Fix all 24', then you stopped the reviews. What do we do with these 18?
**Picked:** Fix only real problems (Recommended)
**Its description:** We write the one-page list for the control code first. A complaint that breaks a promise on the list gets fixed. The others go on a 'later' list. I recommend it because each complaint is checked against something written. Cost: about 8-12M weighted tokens [guess]. Most of the 18 are not fixed now.
**Other options:** Fix all 18, no more reviews · Fix none now
