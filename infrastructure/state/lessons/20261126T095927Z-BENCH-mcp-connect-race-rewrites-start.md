An MCP server's connection race rewrites a run's start: the same user server read 'still connecting' in one helper and 'failed' in the next, 90 s apart, and the deferred-tools text in message 1 differed, so 21,621 tokens were written new (share 0.711; 1.000 with --strict-mcp-config --mcp-config <clone>/.mcp.json, measured 2026-11-26).
item: RIMMANDRAKE_SHARE_HELPER_START_ONE_STATUS_LINE_REWRITES_IT
home: design/specs/2026-11-26-shared-helper-start/boundary.md
