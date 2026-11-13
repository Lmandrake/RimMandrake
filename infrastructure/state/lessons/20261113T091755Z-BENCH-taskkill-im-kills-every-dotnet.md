From WSL, 'taskkill.exe /F /IM dotnet.exe' kills EVERY dotnet.exe on Windows, including other seats' builds and test runs (2026-11-13: it took a second PID that was not the run being stopped). Kill your own run by PID (tasklist /FI, or the Linux /init wrapper's child), never by image name.
item: RIMMANDRAKE_TIME_LOCAL_INERTIAL_IN_CSHARP_FIGURES_STILL_GUESSES
home: infrastructure/state/facts/tool_traps.md
