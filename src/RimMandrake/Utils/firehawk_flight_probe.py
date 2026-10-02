"""Throwaway probe for FIREHAWK_FLIGHT_BEHAVIOR_1 live verification. Not committed."""
import sys
import time

sys.path.insert(0, ".")
from rimbridge_client import RimBridge

TOKEN = "e05739d8573f4c078bc9fc4994eca90b"

rb = RimBridge(token=TOKEN)
rb.connect()
print("connected, welcome:", rb.welcome)

r = rb.call("jawa/start_debug_game_ready", {})
print("start_debug_game_ready:", r)
