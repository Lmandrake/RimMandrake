./publish can rebase local commits, so a rimflow close --sha taken from HEAD before publishing records a sha that never reaches origin (2026-10-26: 8f39225abd landed as 0b14299c56). Publish the fix first, then close with the sha publish prints, then commit and publish the ledger line.
home: .claude/skills/using-rimflow
