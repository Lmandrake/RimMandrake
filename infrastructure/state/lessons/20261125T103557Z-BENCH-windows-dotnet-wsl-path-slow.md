A Windows dotnet.exe that builds and runs a harness from a \\wsl$ path is slow: selftest_deviation_record's harness ran past its 30 s hang guard from .git on ext4, and took 8 s from D:. On SteveDesktop the SDK is C:\Program Files\dotnet (not ~/.dotnet); put the harness under the agent storage root.
item: RIMMANDRAKE_BUILD_DEVIATION_RECORD_SETTINGS_FIELD_JOINS_FIRST
