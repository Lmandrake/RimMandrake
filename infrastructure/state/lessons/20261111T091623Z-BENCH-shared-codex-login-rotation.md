Two machines running Codex on one copied ChatGPT auth.json can strand each other when one refreshes and rotates the refresh token. The Steve HugeThings loop runs ~/codex-steve/ht-loop/auth_sync.py (newest last_refresh wins, copied over ssh, no token printed) before every round; a refresh mid-round on the other machine is still a risk.
home: NONE
