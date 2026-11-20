/* regprobe.c - SteveDesktop's register probe (RIMMANDRAKE_BUILD_STEVE_REGISTER_PROBE_SEES_UPPER_HALF_LOSS), a native Windows
 * program that runs beside the fault watch as the scheduled task "SteveDiag Register Probe" (SYSTEM, at startup).
 *
 * Why: every wrong floating-point result the watch logged is the right answer with the upper 128 bits of a 256-bit YMM
 * register lost (infrastructure/state/facts/stevedesktop_cpu_fault_2026-11-19/REPORT.md, appendix C). The old
 * `stevecheck hold` compared two registers that would both lose their upper halves, so it could not see that.
 *
 * What: every CycleS seconds, in a fresh random order of the logical CPUs, pinned to each one, the cores in
 * regprobe_asm.S hold fixed patterns in all 16 YMM registers (steady, then with a higher-priority thread on the same CPU
 * that wakes every ~1 ms and leaves its own AVX state dirty, so the hold is cut by real context switches), in all 16 XMM
 * registers with legacy SSE (the 128-bit control) and in 14 general registers (the scalar control). Every stored register
 * is compared, all 256 bits, with the compiled-in pattern (regprobe_classify.h) and classed: upper_half_loss,
 * lower_half_error, sse_error, scalar_error. Each start runs a CONTROL first: injected VZEROUPPER, injected low-bit flips
 * on each path, and clean holds must each be classed as planted, or the cycles below are unproven.
 *
 * Log (C:\SteveDesktop\diag\logs\regprobe.log, read by testq/regprobe_log.py through fault_monitor.py):
 *   <ts>Z RPSTART boot=<ts>Z logical_cpus=N cycle=300s chunk_ms=20 avx_ms=150+150 sse_ms=50 gpr_ms=50 build=normal pid=P version=1
 *   <ts>Z RPCONTROL cpu=C upper_seen=1 lower_seen=1 sse_seen=1 scalar_seen=1 clean_seen=1 ok=1
 *   <ts>Z RPFAULT cpu=C path=avx class=upper_half_loss reg=ymm3 detail=zero churn=1 hold_ms=20.1 preempts=19
 *         expected=<q0>:<q1>:<q2>:<q3> observed=<q0>:<q1>:<q2>:<q3> running=[name,name:2,...]
 *         (running= is the process list once per bad hold, on its first wrong register; the others say running=as_above)
 *   <ts>Z RPCYCLE uptime_h=X result=clean|fault|partial|unmeasured cpus_measured=M/N holds=H bad_holds=B avx_ms=..
 *         sse_ms=.. gpr_ms=.. preempts=P bad=[cpu:class+class,...] unmeasured=[cpu:why,...] order=[...] secs=S
 * result: fault = at least one wrong register; clean = every CPU looked at on every path and nothing wrong; partial =
 * nothing wrong but some CPU or path could not be looked at; unmeasured = nothing could be looked at.
 *
 *   regprobe.exe [--once] [--log <path>] [--cycle-s 300] [--chunk-ms 20] [--avx-ms 150] [--sse-ms 50] [--gpr-ms 50]
 * --once: control + one cycle, the RPCYCLE line also on stdout, exit 0 clean / 1 fault / 2 could not look (control
 * failed, nothing measured, no AVX2) / 3 log not writable. The loop mode runs one instance only (a named mutex).
 * Build: regprobe.py build (MinGW-w64 from Archmagi); -DRP_FORCE_INJECT=1 is the RED build: every real AVX hold gets a
 * VZEROUPPER, and RPSTART says build=inject_vzeroupper so its faults are never counted as real.
 *
 * LIMITS (each beside its danger):
 * - load: per CPU per cycle avx 150+150 ms, sse 50 ms, gpr 50 ms in 20 ms holds, 18 CPUs = ~7 s of one thread every
 *   300 s (~0.13% of the machine). Danger: the game lane on the same machine is the main experiment (the 48-72 h count);
 *   the brief orders "one short cycle every few minutes". A 20 ms hold spans at least one 15.6 ms clock tick.
 * - FAULT lines: the full values of the first bad hold of each CPU, path and churn mode in a cycle; later bad holds
 *   are counted in bad_holds. Danger: a held fault (the 2026-11-07 boot had 774 bad cycles) would otherwise write 16
 *   lines for every hold, ~4000 lines a cycle.
 */
#include <windows.h>
#include <tlhelp32.h>
#include <mmsystem.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "regprobe_classify.h"

#ifndef RP_FORCE_INJECT
#define RP_FORCE_INJECT 0
#endif
#define RP_VERSION 1

void rp_hold_avx(const void *pat, const void *k, void *out, uint64_t iters, uint64_t inject);
void rp_hold_sse(const void *pat, const void *k, void *out, uint64_t iters, uint64_t inject);
void rp_hold_gpr(const void *pat, const void *k, void *out, uint64_t iters, uint64_t inject);
void rp_dirty(void);

static char g_log[MAX_PATH] = "C:\\SteveDesktop\\diag\\logs\\regprobe.log";
static int g_log_ok = 1;

static void stamp(char *buf, size_t n)
{
    SYSTEMTIME t;
    GetSystemTime(&t);
    _snprintf(buf, n, "%04d-%02d-%02d %02d:%02d:%02dZ", t.wYear, t.wMonth, t.wDay, t.wHour, t.wMinute, t.wSecond);
    buf[n - 1] = 0;
}

static void logline(const char *s)
{
    char ts[32];
    FILE *f;
    stamp(ts, sizeof ts);
    f = fopen(g_log, "ab");
    if (!f) { g_log_ok = 0; return; }
    fprintf(f, "%s %s\r\n", ts, s);
    fclose(f);
}

static double now_ms(void)
{
    static LARGE_INTEGER fr;
    LARGE_INTEGER c;
    if (!fr.QuadPart) QueryPerformanceFrequency(&fr);
    QueryPerformanceCounter(&c);
    return (double)c.QuadPart * 1000.0 / (double)fr.QuadPart;
}

static uint64_t g_rng;
static uint64_t rnd(void)
{
    g_rng ^= g_rng << 13; g_rng ^= g_rng >> 7; g_rng ^= g_rng << 17;
    return g_rng;
}

/* ---- the churn thread: same CPU, higher priority, wakes every ~1 ms and dirties its own AVX state */
static volatile LONG g_churn_on, g_churn_quit, g_wakes;
static HANDLE g_churn;
static DWORD WINAPI churn_main(LPVOID p)
{
    (void)p;
    while (!g_churn_quit) {
        if (!g_churn_on) { Sleep(5); continue; }
        Sleep(1);
        rp_dirty();
        InterlockedIncrement(&g_wakes);
    }
    return 0;
}

/* ---- what else was running: process names, sorted, a count after a repeated name */
static int cmpstr(const void *a, const void *b) { return _stricmp(*(char *const *)a, *(char *const *)b); }
static void running(char *buf, size_t n)
{
    HANDLE h = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    PROCESSENTRY32 pe;
    char *names[4096];
    int k = 0, i;
    size_t used = 0;
    buf[0] = 0;
    if (h == INVALID_HANDLE_VALUE) { _snprintf(buf, n, "UNMEASURED(snapshot_failed)"); return; }
    pe.dwSize = sizeof pe;
    if (Process32First(h, &pe)) {
        do {
            char *s = pe.szExeFile, *dot;
            if (k >= 4096) break;
            names[k] = _strdup(s);
            if ((dot = strrchr(names[k], '.')) && !_stricmp(dot, ".exe")) *dot = 0;
            for (dot = names[k]; *dot; dot++)     /* the log's [a,b] list: no bracket, comma or space inside a name */
                if (*dot == '[' || *dot == ']' || *dot == ',' || *dot == ' ' || *dot == '=') *dot = '_';
            k++;
        } while (Process32Next(h, &pe));
    }
    CloseHandle(h);
    qsort(names, k, sizeof names[0], cmpstr);
    for (i = 0; i < k;) {
        int j = i;
        while (j < k && !_stricmp(names[j], names[i])) j++;
        if (used + strlen(names[i]) + 16 < n)
            used += j - i > 1 ? _snprintf(buf + used, n - used, "%s%s:%d", used ? "," : "", names[i], j - i)
                              : _snprintf(buf + used, n - used, "%s%s", used ? "," : "", names[i]);
        i = j;
    }
    for (i = 0; i < k; i++) free(names[i]);
}

/* ---- one hold: run a core on the pinned CPU, classify, return the class (-1: could not look: migrated) */
typedef void (*core_fn)(const void *, const void *, void *, uint64_t, uint64_t);
static const core_fn CORE[3] = {rp_hold_avx, rp_hold_sse, rp_hold_gpr};
static uint64_t g_iters[3];

typedef struct {
    int cls, nbad, churn;
    double ms;
    LONG preempts;
    uint64_t out[RP_NVEC * 4];
} hold_t;

static int hold(int cpu, int path, int churn, uint64_t iters, uint64_t inject, hold_t *h)
{
    const void *pat = path == RP_PATH_GPR ? (const void *)RP_GPAT : (const void *)RP_PAT;
    LONG w0;
    double t0;
    DWORD c0, c1;
    memcpy(h->out, RP_PAT, sizeof h->out);
    h->churn = churn;
    g_churn_on = churn;
    if (churn) Sleep(2);    /* let the churn thread reach its timed sleep */
    c0 = GetCurrentProcessorNumber();
    w0 = g_wakes;
    t0 = now_ms();
    CORE[path](pat, RP_K, h->out, iters, inject);
    h->ms = now_ms() - t0;
    h->preempts = g_wakes - w0;
    c1 = GetCurrentProcessorNumber();
    g_churn_on = 0;
    if ((int)c0 != cpu || (int)c1 != cpu)
        return -1;
    h->cls = rp_classify_hold(path, h->out, &h->nbad);
    return h->cls;
}

static void hex4(char *b, size_t n, const uint64_t *q, int lanes)
{
    if (lanes == 4)
        _snprintf(b, n, "%016llx:%016llx:%016llx:%016llx", (unsigned long long)q[0], (unsigned long long)q[1],
                  (unsigned long long)q[2], (unsigned long long)q[3]);
    else if (lanes == 2)
        _snprintf(b, n, "%016llx:%016llx", (unsigned long long)q[0], (unsigned long long)q[1]);
    else
        _snprintf(b, n, "%016llx", (unsigned long long)q[0]);
    b[n - 1] = 0;
}

/* the full values of every wrong register of one bad hold */
static void log_fault(int cpu, int path, const hold_t *h)
{
    static char snap[16384];
    char line[20000], e[80], o[80];
    const char *run = snap;
    int r;
    running(snap, sizeof snap);
    if (path == RP_PATH_GPR) {
        for (r = 0; r < RP_NGPR; r++) {
            if (rp_classify_gpr(h->out, r) == RP_CLEAN) continue;
            hex4(e, sizeof e, &RP_GPAT[r], 1);
            hex4(o, sizeof o, &h->out[r], 1);
            _snprintf(line, sizeof line, "RPFAULT cpu=%d path=gpr class=%s reg=%s detail=- churn=%d hold_ms=%.1f preempts=%ld "
                      "expected=%s observed=%s running=[%s]", cpu, RP_CLASS[RP_SCALAR], RP_GPR_NAME[r], h->churn, h->ms,
                      (long)h->preempts, e, o, run);
            line[sizeof line - 1] = 0;
            logline(line);
            run = "as_above";
        }
        return;
    }
    for (r = 0; r < RP_NVEC; r++) {
        const char *d;
        int c = rp_classify_vec(path, h->out + 4 * r, r, &d);
        int lanes = path == RP_PATH_SSE ? 2 : 4;
        if (c == RP_CLEAN) continue;
        hex4(e, sizeof e, RP_PAT[r], lanes);
        hex4(o, sizeof o, h->out + 4 * r, lanes);
        _snprintf(line, sizeof line, "RPFAULT cpu=%d path=%s class=%s reg=%s%d detail=%s churn=%d hold_ms=%.1f preempts=%ld "
                  "expected=%s observed=%s running=[%s]", cpu, RP_PATH[path], RP_CLASS[c], path == RP_PATH_SSE ? "xmm" : "ymm",
                  r, *d ? d : "-", h->churn, h->ms, (long)h->preempts, e, o, run);
        line[sizeof line - 1] = 0;
        logline(line);
        run = "as_above";       /* one snapshot per hold: the first wrong register's line carries it */
    }
}

static int pin(HANDLE th, int cpu)
{
    return SetThreadAffinityMask(th, (DWORD_PTR)1 << cpu) != 0;
}

/* iterations for one CHUNK_MS hold of each path on CPU 0: the fastest of 5 timings, so a busy moment at start (a boot)
 * does not shorten every hold; under load later a hold takes longer, which only adds interrupts to it */
static void calibrate(double chunk_ms)
{
    int p, t;
    for (p = 0; p < 3; p++) {
        hold_t h;
        double ms = 1e30, t0;
        uint64_t it = 200000;
        for (t = 0; t < 5; t++) {
            t0 = now_ms();
            CORE[p](p == RP_PATH_GPR ? (const void *)RP_GPAT : (const void *)RP_PAT, RP_K, h.out, it, 0);
            t0 = now_ms() - t0;
            if (t0 < ms) ms = t0;
        }
        if (ms < 0.01) ms = 0.01;
        g_iters[p] = (uint64_t)(it * chunk_ms / ms);
        if (g_iters[p] < 1000) g_iters[p] = 1000;
    }
}

/* -> 1 when every planted fault is classed as planted and the clean holds are clean */
static int control(int cpu)
{
    hold_t h;
    char line[256];
    int up, lo, sse, sc, cl, ok, i;
    const char *d;
    HANDLE me = GetCurrentThread();
    if (!pin(me, cpu) || !pin(g_churn, cpu)) {
        _snprintf(line, sizeof line, "RPCONTROL cpu=%d upper_seen=0 lower_seen=0 sse_seen=0 scalar_seen=0 clean_seen=0 ok=0 why=affinity_failed", cpu);
        logline(line);
        return 0;
    }
    Sleep(0);
    up = hold(cpu, RP_PATH_AVX, 0, g_iters[0] / 10, 1, &h) == RP_UPPER && h.nbad == RP_NVEC;
    for (i = 0; up && i < RP_NVEC; i++)
        up = rp_classify_vec(RP_PATH_AVX, h.out + 4 * i, i, &d) == RP_UPPER && !strcmp(d, "zero");
    lo = hold(cpu, RP_PATH_AVX, 0, g_iters[0] / 10, 2, &h) == RP_LOWER && h.nbad == 1;
    sse = hold(cpu, RP_PATH_SSE, 0, g_iters[1] / 10, 2, &h) == RP_SSE && h.nbad == 1;
    sc = hold(cpu, RP_PATH_GPR, 0, g_iters[2] / 10, 4, &h) == RP_SCALAR && h.nbad == 1;
    cl = hold(cpu, RP_PATH_AVX, 0, g_iters[0] / 10, 0, &h) == RP_CLEAN;
    cl = cl && hold(cpu, RP_PATH_AVX, 1, g_iters[0] / 10, 0, &h) == RP_CLEAN;
    cl = cl && hold(cpu, RP_PATH_SSE, 0, g_iters[1] / 10, 0, &h) == RP_CLEAN;
    cl = cl && hold(cpu, RP_PATH_GPR, 0, g_iters[2] / 10, 0, &h) == RP_CLEAN;
    ok = up && lo && sse && sc && cl;
    _snprintf(line, sizeof line, "RPCONTROL cpu=%d upper_seen=%d lower_seen=%d sse_seen=%d scalar_seen=%d clean_seen=%d ok=%d",
              cpu, up, lo, sse, sc, cl, ok);
    logline(line);
    return ok;
}

typedef struct { double avx_ms, sse_ms, gpr_ms, chunk_ms; } budget_t;

/* one cycle -> 0 clean, 1 fault, 2 partial, 3 unmeasured; writes the RPCYCLE line (and copies it to out) */
static int cycle(int n, const budget_t *b, char *out, size_t outn)
{
    static char bad[4096], unm[4096], ord[1024];
    int order[64], i, k0, measured_cpus = 0, any_bad = 0, any_unm = 0, holds = 0, bad_holds = 0;
    double ms[3] = {0, 0, 0}, t0 = now_ms();
    LONG pre = 0;
    size_t bu = 0, uu = 0, ou = 0;
    HANDLE me = GetCurrentThread();
    char line[12000];
    bad[0] = unm[0] = ord[0] = 0;
    for (i = 0; i < n; i++) order[i] = i;
    for (i = n - 1; i > 0; i--) { int j = (int)(rnd() % (uint64_t)(i + 1)), t = order[i]; order[i] = order[j]; order[j] = t; }
    for (i = 0; i < n; i++) ou += _snprintf(ord + ou, sizeof ord - ou, "%s%d", i ? "," : "", order[i]);
    timeBeginPeriod(1);
    for (i = 0; i < n; i++) {
        int cpu = order[i], p, seen_paths = 0, logged[4] = {0, 0, 0, 0}, c2;
        unsigned cpu_bad = 0;
        if (!pin(me, cpu) || !pin(g_churn, cpu)) {
            uu += _snprintf(unm + uu, sizeof unm - uu, "%s%d:affinity_failed", uu ? "," : "", cpu);
            any_unm = 1;
            continue;
        }
        Sleep(0);
        /* the paths: avx steady, avx with churn, sse, gpr */
        for (p = 0; p < 4; p++) {
            int path = p < 2 ? RP_PATH_AVX : p - 1, churn = p == 1, k, nk, good = 0;
            double want = p < 2 ? b->avx_ms : (path == RP_PATH_SSE ? b->sse_ms : b->gpr_ms);
            uint64_t inject = (path == RP_PATH_AVX && RP_FORCE_INJECT) ? 1 : 0;
            nk = (int)(want / b->chunk_ms + 0.5);
            if (nk < 1) nk = 1;
            for (k = 0; k < nk; k++) {
                hold_t h;
                int c = hold(cpu, path, churn, g_iters[path], inject, &h);
                if (c < 0) continue;
                good++;
                holds++;
                ms[path] += h.ms;
                pre += h.preempts;
                if (c != RP_CLEAN) {
                    bad_holds++;
                    cpu_bad |= 1u << c;
                    if (!logged[p]) { log_fault(cpu, path, &h); logged[p] = 1; }
                }
            }
            if (good) seen_paths++;
            else {
                uu += _snprintf(unm + uu, sizeof unm - uu, "%s%d:%s%s_migrated", uu ? "," : "", cpu, RP_PATH[path], churn ? "_churn" : "");
                any_unm = 1;
            }
        }
        if (seen_paths) measured_cpus++;
        if (cpu_bad) {     /* every class this CPU showed, joined by + */
            bu += _snprintf(bad + bu, sizeof bad - bu, "%s%d:", bu ? "," : "", cpu);
            for (c2 = 1, k0 = 0; c2 <= RP_SCALAR; c2++)
                if (cpu_bad & (1u << c2)) bu += _snprintf(bad + bu, sizeof bad - bu, "%s%s", k0++ ? "+" : "", RP_CLASS[c2]);
            any_bad = 1;
        }
    }
    timeEndPeriod(1);
    {
        const char *res = any_bad ? "fault" : (!measured_cpus ? "unmeasured" : (any_unm ? "partial" : "clean"));
        _snprintf(line, sizeof line, "RPCYCLE uptime_h=%.2f result=%s cpus_measured=%d/%d holds=%d bad_holds=%d avx_ms=%.0f "
                  "sse_ms=%.0f gpr_ms=%.0f preempts=%ld bad=[%s] unmeasured=[%s] order=[%s] secs=%.1f",
                  GetTickCount64() / 3600000.0, res, measured_cpus, n, holds, bad_holds, ms[0], ms[1], ms[2], (long)pre, bad, unm,
                  ord, (now_ms() - t0) / 1000.0);
        line[sizeof line - 1] = 0;
        logline(line);
        if (out) { _snprintf(out, outn, "%s", line); out[outn - 1] = 0; }
        return any_bad ? 1 : (!measured_cpus ? 3 : (any_unm ? 2 : 0));
    }
}

int main(int argc, char **argv)
{
    int once = 0, i, n, ok, cpu0;
    double cycle_s = 300;
    budget_t b = {150, 50, 50, 20};
    char line[1024], ts[32], cyc[12000];
    uint64_t up_ms;
    time_t boot;
    struct tm *bt;
    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--once")) once = 1;
        else if (!strcmp(argv[i], "--log") && i + 1 < argc) { strncpy(g_log, argv[++i], MAX_PATH - 1); }
        else if (!strcmp(argv[i], "--cycle-s") && i + 1 < argc) cycle_s = atof(argv[++i]);
        else if (!strcmp(argv[i], "--chunk-ms") && i + 1 < argc) b.chunk_ms = atof(argv[++i]);
        else if (!strcmp(argv[i], "--avx-ms") && i + 1 < argc) b.avx_ms = atof(argv[++i]);
        else if (!strcmp(argv[i], "--sse-ms") && i + 1 < argc) b.sse_ms = atof(argv[++i]);
        else if (!strcmp(argv[i], "--gpr-ms") && i + 1 < argc) b.gpr_ms = atof(argv[++i]);
        else { fprintf(stderr, "usage: regprobe [--once] [--log path] [--cycle-s s] [--chunk-ms ms] [--avx-ms ms] [--sse-ms ms] [--gpr-ms ms]\n"); return 2; }
    }
    if (!once) {
        CreateMutexA(NULL, TRUE, "Global\\SteveDiagRegProbe");
        if (GetLastError() == ERROR_ALREADY_EXISTS) return 0;
    }
    g_rng = (uint64_t)now_ms() * 2654435761ULL ^ GetCurrentProcessId() ^ 0x9e3779b97f4a7c15ULL;
    n = (int)GetActiveProcessorCount(ALL_PROCESSOR_GROUPS);
    if (n > 64) n = 64;     /* one processor group: SteveDesktop has 18 or 20 */
    up_ms = GetTickCount64();
    boot = time(NULL) - (time_t)(up_ms / 1000);
    bt = gmtime(&boot);
    _snprintf(ts, sizeof ts, "%04d-%02d-%02d %02d:%02d:%02dZ", bt->tm_year + 1900, bt->tm_mon + 1, bt->tm_mday, bt->tm_hour,
              bt->tm_min, bt->tm_sec);
    _snprintf(line, sizeof line, "RPSTART boot=%s logical_cpus=%d cycle=%.0fs chunk_ms=%.0f avx_ms=%.0f+%.0f sse_ms=%.0f gpr_ms=%.0f "
              "build=%s mode=%s pid=%lu version=%d", ts, n, cycle_s, b.chunk_ms, b.avx_ms, b.avx_ms, b.sse_ms, b.gpr_ms,
              RP_FORCE_INJECT ? "inject_vzeroupper" : "normal", once ? "once" : "loop", GetCurrentProcessId(), RP_VERSION);
    logline(line);
    if (!g_log_ok) { fprintf(stderr, "regprobe: cannot write %s\n", g_log); return 3; }
    if (!__builtin_cpu_supports("avx2")) {
        logline("RPCONTROL cpu=-1 upper_seen=0 lower_seen=0 sse_seen=0 scalar_seen=0 clean_seen=0 ok=0 why=no_avx2");
        return 2;
    }
    g_churn = CreateThread(NULL, 0, churn_main, NULL, 0, NULL);
    SetThreadPriority(g_churn, THREAD_PRIORITY_HIGHEST);
    pin(GetCurrentThread(), 0);
    Sleep(0);
    calibrate(b.chunk_ms);
    cpu0 = (int)(rnd() % (uint64_t)n);
    ok = control(cpu0);
    if (once) {
        int r = cycle(n, &b, cyc, sizeof cyc);
        printf("%s\n", cyc);
        printf("REGPROBE %s control_ok=%d log=%s\n", r == 1 ? "FAULT" : (r == 0 && ok ? "CLEAN" : "COULD_NOT_LOOK"), ok, g_log);
        g_churn_quit = 1;
        if (r == 1) return 1;
        return ok && r == 0 ? 0 : 2;
    }
    for (;;) {
        double t0 = now_ms(), left;
        cycle(n, &b, NULL, 0);
        left = cycle_s * 1000.0 - (now_ms() - t0);
        if (left > 0) Sleep((DWORD)left);
    }
}
