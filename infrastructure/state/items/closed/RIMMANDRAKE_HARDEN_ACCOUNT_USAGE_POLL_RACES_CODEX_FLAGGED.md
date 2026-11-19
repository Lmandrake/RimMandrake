## spec
Three Codex review claims on src/RimMandrake/Utils/account_usage.py (2026-11-18, D:\ClaudeWork\scratch\fable_meter\codex_review.txt),
each confirmed by reading poll() and probe_local() and then by a red test on 8716c3bcdd:
(a) config() turned an unreadable or invalid account_usage.json into {}, so poll() read "no remotes" with remote_ok
true and could warm a login a remote holds live (a non-object config crashed poll outright);
(b) the live login was read once before the remote probes and never again under Lock(), so a switch landing in
between could vault-probe the now-live login;
(c) the live probe ran auth status and /usage with nothing between them, so a switch could file one login's quota
under the other's name (the remote probe the same).
Codex's full-file review of the fix added: explicit null remotes, an unreadable live login under the lock, a login live
on a remote whose probe failed still vault-probed, token expiry checked before the lock wait, and a RimPulse reading's
measured_at lost when carried. Two switches inside one /usage call (A to B and back) stay open, documented in
_same_login: `claude-account use` waits only 5 s for the machine lock, so holding it across a live /usage would
refuse real switches.

## verify
python3 src/RimMandrake/Utils/selftest_account_usage_poll_races.py   # exit 0, "all passed"
Watched failing on 8716c3bcdd: 14 cases FAIL plus an AttributeError crash on a non-object config.

## criteria
- An unreadable or malformed config, a switch landing mid-poll, and a remote-live login never warm or vault-probe the wrong login, and every refusal is named in the record's why.
