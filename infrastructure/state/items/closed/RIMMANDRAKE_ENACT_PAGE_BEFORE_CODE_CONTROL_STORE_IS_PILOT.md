# RIMMANDRAKE_ENACT_PAGE_BEFORE_CODE_CONTROL_STORE_IS_PILOT

## What the card said

<!-- answered 2026-11-19T07:22:45Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** The problem: nobody wrote down what the pipeline's control code must do and must not do. So each review found about 15 new complaints, and only 0 to 2 were real. Before a helper writes new pipeline code, what do we do first?
**Picked:** Write a one-page list (Recommended)
**Its description:** The page lists what the code accepts, which failures it does not handle, and what it promises. Each promise gets a test. A reviewer can only report a broken promise. I recommend it because builder and reviewer then use the same list. Cost: about 16-20M weighted tokens once [guess]. New code that kills runs goes live in half a day, not one hour.
**Other options:** No list; filter complaints · No list; test by running it · No list; tools block bad code
