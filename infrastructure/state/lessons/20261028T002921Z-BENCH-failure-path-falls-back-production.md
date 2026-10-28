A failure path that falls back to default (production) paths when argument parsing itself failed will write into production from a selftest: delegated_digest --pre-launch --bogus wrote Transient/delegated_digest_<date>.FAILED.md from a test run. Recover the caller's paths with parse_known_args before falling back (delegated_digest._partial).
home: NONE
