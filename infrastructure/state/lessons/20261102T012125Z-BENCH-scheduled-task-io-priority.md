A Windows scheduled task runs at default Priority 7: BelowNormal CPU class and I/O priority Low (read as io=1 with NtQueryInformationProcess, class 33). Long copies crawl at it: wimlib read 15 MB/s from a disk that gave 2,259 MB/s direct. Set the task Priority to 4 at registration, or raise the running tree with NtSetInformationProcess class 33 value 2 and PriorityClass Normal.
home: NONE
