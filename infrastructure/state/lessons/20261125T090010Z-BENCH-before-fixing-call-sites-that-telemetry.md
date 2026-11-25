Before fixing call sites that a telemetry study blames, re-read the telemetry after the study date: the FlowWorks paused-clock order waits (visit 9, 2026-11-23: 32 calls / 614 s by clock_still_waits.py) were already gone in visit 10 (0 of 192 long order calls) because the C# wait now ends after one poll on a paused clock (JawaBenchWaitCore.End, 7aa1752ee4). The study's own 40 / 757 s was not reproduced: its join was not kept as code, so a study number without its reader cannot be re-measured.
item: RIMMANDRAKE_STOP_FLOWWORKS_ORDERS_WAITING_OUT_A_PAUSED_CLOCK
home: NONE
