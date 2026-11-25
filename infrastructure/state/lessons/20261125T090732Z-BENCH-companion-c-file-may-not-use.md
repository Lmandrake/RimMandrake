A companion C# file may not use #else or #elif: selftest_tool_metadata.py models only '#if JAWA_GM_TOOLS ... #endif' and fails the file by name. To call a JAWA_GM_TOOLS-only tool body (jawa/lord_set_job) from an always-built tool, look the method up by reflection (GetMethod returns null in a --no-gm build) and say so in the reply.
item: RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER
home: skills/rimbridge-companion
