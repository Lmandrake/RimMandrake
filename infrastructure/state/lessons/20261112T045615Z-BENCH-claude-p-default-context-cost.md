A bare 'claude -p' in a seat clone loads the full CLAUDE.md layers (~48k tokens) plus a ~134k MCP deferred-tool delta on every call: Claude Whittle setup paid $1.2-1.8 of opus per round (21 turns) just to read a ticket. Script the deterministic part; any model phase that stays runs sonnet with --setting-sources '' --strict-mcp-config --mcp-config '{"mcpServers":{}}' --disable-slash-commands --tools Bash,Read --max-turns/--max-budget-usd (loop.sh claude_slim). MandrakeWorkflows whittle/run.py still pays the full context (not changed here).
item: NONE
home: infrastructure/whittle_claude/loop.sh
