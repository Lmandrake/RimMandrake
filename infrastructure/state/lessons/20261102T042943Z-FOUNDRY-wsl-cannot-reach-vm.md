From WSL, urllib to the Windows-local VictoriaMetrics at 127.0.0.1:8428 is refused (WSL NAT); Windows curl.exe reaches it. telemetry/store._get now retries a refused localhost GET through curl.exe (HTTP errors are raised as is), so WSL readers (ops_memory, analysis.windows_from_vm) can query VM.
home: telemetry skill
