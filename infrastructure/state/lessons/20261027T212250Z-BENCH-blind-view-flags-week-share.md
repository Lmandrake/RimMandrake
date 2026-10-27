blind_view.sensitive_word treats ordinary words like week, wk, share and pct as cost-shaped, so a quality page for the token-blind Auditor fails the blind check unless it uses neutral labels (v3_vs_v2 BLIND_LABELS, 'period' for 'week'). Test the blind page by asserting redact(page) == page rather than only a word scan.
home: src/RimMandrake/rimflow/roles/auditor.md
