governor.judge on an EMPTY trigger list returns PASS CLEAN, and jawa/vitals events returns only the newest 'limit' triggers (latch caps at 512, check truncated/overflow). A proof that a vitals trigger fired must require a non-empty list and match by subjectId (int) before trusting the verdict.
home: live-debugging-proof-harness
