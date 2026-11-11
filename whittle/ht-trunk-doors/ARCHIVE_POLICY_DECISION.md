# O08 safe archive route — parent technical decision

Keep the unchanged required O08 archive check and remove --no-archive. The original task prohibits copying credentials; my earlier suggestion to archive the original full log privately did not satisfy that instruction.

Before each offline preflight, under the fresh own SteveDesktop lease and independently proven actual game DOWN:

1. Read the current Player.log in memory. Record its original SHA256, byte size and mtime, and a bounded diagnostic summary (first exception and every Config error, with sensitive lines redacted). Never print or save the original full log.
2. Sanitize the old log in place: replace entire lines matching case-insensitive token, authorization, bearer, api-key/api_key, password, secret or credential indicators with a fixed redaction line. Use the actual bridge discovery pattern as an additional check. Record only original/sanitized hashes, original line count, redaction count and the sanitization script hash. Preserve all other diagnostic lines. Recheck that no sensitive-pattern line survives except the fixed redaction marker.
3. Run unmodified preflight with normal archiving enabled. O08 now archives the actual sanitized current log and must PASS; the other required rows must also PASS (only the established other-host O02 is N/A). The sanitized archive stays at the tool's normal private archive destination, outside committed evidence.
4. Launch once through Steam and require a fresh process and fresh log generation. Bridge discovery may read the new live log for authentication in memory; do not sanitize it while the game is running or retain credential-bearing startup content. Bounded evidence/error selectors must redact sensitive lines.

This preserves old diagnostic content safely and the normal O08 gate. No framework changes, row waivers or fabricated archive receipts are authorized. If any precondition or sanitization check fails, stop before launch and retain the failure with cleanup.
