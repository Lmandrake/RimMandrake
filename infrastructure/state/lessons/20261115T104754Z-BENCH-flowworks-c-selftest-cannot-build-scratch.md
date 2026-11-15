The FlowWorks C# SelfTest cannot build in a scratch clone sparse on src/RimMandrake/FlowWorks: its csproj and harness targets read other mods' source (LuminousPigment/Source/FlowWorksWaterBridge.cs and more), so the build fails as an env failure, not a verdict. Clone with --sparse src/RimMandrake (about 1.6 GB).
item: RIMMANDRAKE_CHALLENGE_FLOWWORKS_BLIND_CYCLE_ONE_FIFTY_SEVEN_BARS
