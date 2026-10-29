# ACCOUNT_USAGE_MEASURE_DORMANT_GAP

`account_usage.py` reads a DORMANT login (live on no machine; today `steven`) only while its stored access
token is valid for 15 more minutes, so the probe never refreshes and rotates the credential under the account
switcher. `claude-account warm` renews dormant logins once a day (~04:30) and access tokens last ~8 h, so a
dormant account is MEASURED about 8 h a day and an ESTIMATE (carried lower bound) the rest.

Options to close the gap (a decision for the switcher's owner, not made here): run `claude-account warm`
every ~6 h, or let account_usage.py refresh a dormant vault login under the switcher's lock (the same act warm
performs). Evidence: poll at 2026-10-26 12:43 PDT, steven "vault token on archmagi needs a refresh".
