Env vars set in WSL do not reach dotnet.exe (or any Windows exe) unless listed in WSLENV (e.g. WSLENV=VAR/u). A build switch passed by env silently does nothing otherwise. (GSS allfix 2026-11-09)
