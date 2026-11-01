/* rm_preload.c -- the libc half of the selftest dependency instrument (known_results.py).

   Python's audit hooks see Python. They do not see git, tar, sh, a C extension, or a compiler: to the old tracer those
   were opaque children. This shim is LD_PRELOADed into every dynamically linked process of a traced test and logs what
   the process asks libc for, so "what did this test depend on" is a measurement for native programs too.

   A process logs to <RM_SELFTEST_TRACE>/<pid>.native:
     @ <exe>                 the process exists (written by the constructor; a child with no such line was NOT observed)
     P                       this process carries the python runtime, whatever its file is called
     R <path>                opened for reading
     W <path>                opened for writing, or the target of a rename/link/symlink
     K <path>                what a new link points at, or what a rename took: the test's own TMPDIR must not launder a
                             shared file
     L <dir>                 directory listed
     S <path>                stat/access probe
     X <prog>                exec attempted by this process
     F <prog>                that exec came back (it failed, so no child will appear)
     N <what>                network: connect() to a non-unix peer, or a name lookup
     U <path>                connect() to a unix socket
     E <name>                getenv of <name>
     C realtime              a python process read the wall clock after its startup (first read only). Native tools
                             are not counted: git stamps everything it does, and that is not a result depending on the
                             date. A `date` command is caught by name in the analyser.

   Lines are written straight through with one write(2) on an O_APPEND fd, deduplicated in process, so a test that
   SIGKILLs a child loses nothing. The file is the record; there is no end marker. Everything here must stay
   async-signal-safe (no malloc, no stdio): exec wrappers run between vfork and exec.

   What this cannot see, and why that is safe: a static or Go binary, a .exe through WSL interop, a raw syscall(). The
   first two write no "@" line, so the analyser counts their "X" against the "@" lines and refuses the record. A raw
   syscall from a dynamically linked program, and glibc's own internal calls (nss, iconv), are the residual hole the
   sampled audit exists for. */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <dirent.h>
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <netdb.h>
#include <spawn.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>

#define TABLE (1u << 16)
static volatile uint64_t seen[TABLE];
static int log_fd = -1;
static char log_path[PATH_MAX];
static int clock_said;
static __thread int clock_muted __attribute__((tls_model("initial-exec")));
static int clock_armed;      /* python: every interpreter reads the clock at startup, so sitecustomize arms this after */

static size_t slen(const char *s) { size_t n = 0; while (s && s[n]) n++; return n; }

static uint64_t fnv(char op, const char *s) {
    uint64_t h = 1469598103934665603ULL ^ (unsigned char)op;
    for (h *= 1099511628211ULL; *s; s++) { h ^= (unsigned char)*s; h *= 1099511628211ULL; }
    return h ? h : 1;
}

/* 1 the first time this (op, text) is seen. A full table only costs duplicates. */
static int first(char op, const char *text) {
    uint64_t h = fnv(op, text);
    for (uint32_t i = 0; i < 64; i++) {
        uint32_t at = (uint32_t)(h + i) & (TABLE - 1);
        uint64_t cur = seen[at];
        if (cur == h) return 0;
        if (cur == 0 && __sync_bool_compare_and_swap(&seen[at], 0, h)) return 1;
    }
    return 1;
}

/* Out of the range programs close by number: closefrom(3) in sh/ssh would otherwise blind us silently */
static void open_log(void) {
    int fd = (int)syscall(SYS_openat, AT_FDCWD, log_path, O_WRONLY | O_CREAT | O_APPEND | O_CLOEXEC, 0644);
    if (fd >= 0) {
        int high = (int)syscall(SYS_fcntl, fd, F_DUPFD_CLOEXEC, 900);
        if (high >= 0) { syscall(SYS_close, fd); fd = high; }
    }
    log_fd = fd;
}

static void put(char op, const char *text) {
    char buf[PATH_MAX + 8];
    size_t n = slen(text);
    if (log_fd < 0 || !text) return;
    if (n > PATH_MAX) n = PATH_MAX;
    buf[0] = op; buf[1] = ' ';
    memcpy(buf + 2, text, n);
    buf[n + 2] = '\n';
    int e = errno;
    if (syscall(SYS_write, log_fd, buf, n + 3) < 0 && errno == EBADF) {
        open_log();                  /* closerange(3, big) in a fork child: an exec it then makes must still be counted */
        if (log_fd >= 0) (void)!syscall(SYS_write, log_fd, buf, n + 3);
    }
    errno = e;
}

static void note(char op, const char *text) { if (log_fd >= 0 && text && first(op, text)) put(op, text); }

/* Join dirfd + path into an absolute path, with no allocation. Empty result on failure: the path is logged raw. */
static void absolute(int dirfd, const char *path, char *out, size_t cap) {
    size_t at = 0;
    out[0] = 0;
    if (!path) return;
    if (path[0] != '/') {
        ssize_t n;
        if (dirfd == AT_FDCWD) {
            n = syscall(SYS_getcwd, out, cap - 1);
            n = n > 0 ? n - 1 : 0;
        } else {
            char link[40];
            memcpy(link, "/proc/self/fd/", 14);
            int v = dirfd, d = 0; char tmp[12];
            do { tmp[d++] = (char)('0' + v % 10); v /= 10; } while (v);
            size_t i = 14;
            while (d) link[i++] = tmp[--d];
            link[i] = 0;
            n = syscall(SYS_readlink, link, out, cap - 1);
            if (n < 0) n = 0;
        }
        at = (size_t)n;
        if (at + 1 < cap) out[at++] = '/';
    }
    size_t k = slen(path);
    if (at + k + 1 > cap) k = cap - at - 1;
    memcpy(out + at, path, k);
    out[at + k] = 0;
}

static void note_path(char op, int dirfd, const char *path) {
    char full[PATH_MAX + 2];
    if (log_fd < 0 || !path) return;
    if (op == 'S' && !strcmp(path, "/rm-selftest/clock-armed")) { clock_armed = 1; clock_muted = 0; return; }
    if (op == 'S' && !strcmp(path, "/rm-selftest/clock-muted")) { clock_muted = 1; return; }
    absolute(dirfd, path, full, sizeof full);
    note(op, full[0] ? full : path);
}

/* What a link at (dirfd, at) points at: relative to the link's folder, not the cwd. */
static void note_target(int dirfd, const char *target, const char *at) {
    char full[PATH_MAX + 2];
    if (log_fd < 0 || !target || !at) return;
    if (target[0] == '/') { note('K', target); return; }
    absolute(dirfd, at, full, sizeof full);
    size_t n = slen(full), k = slen(target);
    while (n && full[n - 1] != '/') n--;
    if (n + k + 1 > sizeof full) return;
    memcpy(full + n, target, k + 1);
    note('K', full);
}

static void note_flags(int dirfd, const char *path, int flags) {
    int acc = flags & O_ACCMODE;
    if (acc == O_WRONLY || acc == O_RDWR || (flags & O_CREAT)) note_path('W', dirfd, path);
    if (acc == O_RDONLY || acc == O_RDWR) note_path(flags & O_DIRECTORY ? 'S' : 'R', dirfd, path);
}

__attribute__((constructor)) static void start(void) {
    extern char **environ;
    const char *dir = NULL;
    for (char **e = environ; e && *e; e++)
        if (!strncmp(*e, "RM_SELFTEST_TRACE=", 18)) dir = *e + 18;
    if (!dir || !*dir) return;
    char exe[PATH_MAX];
    char *path = log_path;
    size_t n = slen(dir);
    if (n + 32 > sizeof log_path) return;
    memcpy(path, dir, n);
    long pid = syscall(SYS_getpid);
    char num[24]; int d = 0;
    do { num[d++] = (char)('0' + pid % 10); pid /= 10; } while (pid);
    path[n++] = '/';
    while (d) path[n++] = num[--d];
    memcpy(path + n, ".native", 8);
    open_log();
    if (log_fd < 0) return;
    ssize_t k = syscall(SYS_readlink, "/proc/self/exe", exe, sizeof exe - 1);
    exe[k > 0 ? k : 0] = 0;
    put('@', exe);
    if (dlsym(RTLD_DEFAULT, "Py_Initialize")) put('P', "");
}

#define REAL(name) static __typeof__(&name) real_##name; \
    if (!real_##name) real_##name = (__typeof__(&name))dlsym(RTLD_NEXT, #name)

/* ---- open ------------------------------------------------------------------------------------------------------- */
#define OPEN_MODE() mode_t mode = 0; if (flags & (O_CREAT | O_TMPFILE)) { va_list a; va_start(a, flags); \
    mode = va_arg(a, mode_t); va_end(a); }

int open(const char *p, int flags, ...) { OPEN_MODE(); REAL(open); note_flags(AT_FDCWD, p, flags); return real_open(p, flags, mode); }
int open64(const char *p, int flags, ...) { OPEN_MODE(); REAL(open64); note_flags(AT_FDCWD, p, flags); return real_open64(p, flags, mode); }
int openat(int fd, const char *p, int flags, ...) { OPEN_MODE(); REAL(openat); note_flags(fd, p, flags); return real_openat(fd, p, flags, mode); }
int openat64(int fd, const char *p, int flags, ...) { OPEN_MODE(); REAL(openat64); note_flags(fd, p, flags); return real_openat64(fd, p, flags, mode); }
int creat(const char *p, mode_t m) { REAL(creat); note_path('W', AT_FDCWD, p); return real_creat(p, m); }
int creat64(const char *p, mode_t m) { REAL(creat64); note_path('W', AT_FDCWD, p); return real_creat64(p, m); }

static void note_fopen(const char *p, const char *m) {
    int plus = m && strchr(m, '+') != NULL;
    if (m && m[0] == 'r') note_path('R', AT_FDCWD, p);
    if (m && (m[0] != 'r' || plus)) note_path('W', AT_FDCWD, p);
}
FILE *fopen(const char *p, const char *m) { REAL(fopen); note_fopen(p, m); return real_fopen(p, m); }
FILE *fopen64(const char *p, const char *m) { REAL(fopen64); note_fopen(p, m); return real_fopen64(p, m); }
FILE *freopen(const char *p, const char *m, FILE *f) { REAL(freopen); note_fopen(p, m); return real_freopen(p, m, f); }
FILE *freopen64(const char *p, const char *m, FILE *f) { REAL(freopen64); note_fopen(p, m); return real_freopen64(p, m, f); }

/* ---- stat ------------------------------------------------------------------------------------------------------- */
int stat(const char *p, struct stat *s) { REAL(stat); note_path('S', AT_FDCWD, p); return real_stat(p, s); }
int stat64(const char *p, struct stat64 *s) { REAL(stat64); note_path('S', AT_FDCWD, p); return real_stat64(p, s); }
int lstat(const char *p, struct stat *s) { REAL(lstat); note_path('S', AT_FDCWD, p); return real_lstat(p, s); }
int lstat64(const char *p, struct stat64 *s) { REAL(lstat64); note_path('S', AT_FDCWD, p); return real_lstat64(p, s); }
int fstatat(int d, const char *p, struct stat *s, int f) { REAL(fstatat); if (p && *p) note_path('S', d, p); return real_fstatat(d, p, s, f); }
int fstatat64(int d, const char *p, struct stat64 *s, int f) { REAL(fstatat64); if (p && *p) note_path('S', d, p); return real_fstatat64(d, p, s, f); }
int statx(int d, const char *p, int f, unsigned m, struct statx *s) { REAL(statx); if (p && *p) note_path('S', d, p); return real_statx(d, p, f, m, s); }
int access(const char *p, int m) { REAL(access); note_path('S', AT_FDCWD, p); return real_access(p, m); }
int faccessat(int d, const char *p, int m, int f) { REAL(faccessat); note_path('S', d, p); return real_faccessat(d, p, m, f); }
ssize_t readlink(const char *p, char *b, size_t n) { REAL(readlink); note_path('R', AT_FDCWD, p); return real_readlink(p, b, n); }
ssize_t readlinkat(int d, const char *p, char *b, size_t n) { REAL(readlinkat); note_path('R', d, p); return real_readlinkat(d, p, b, n); }

/* ---- directories ------------------------------------------------------------------------------------------------ */
DIR *opendir(const char *p) { REAL(opendir); note_path('L', AT_FDCWD, p); return real_opendir(p); }
DIR *fdopendir(int fd) {
    REAL(fdopendir);
    if (log_fd >= 0) { char e[1] = ""; note_path('L', fd, e); }
    return real_fdopendir(fd);
}

/* ---- things that land a file under a new name ---------------------------------------------------------------------- */
int rename(const char *a, const char *b) { REAL(rename); note_path('K', AT_FDCWD, a); note_path('W', AT_FDCWD, b); return real_rename(a, b); }
int renameat(int f, const char *a, int t, const char *b) { REAL(renameat); note_path('K', f, a); note_path('W', t, b); return real_renameat(f, a, t, b); }
int renameat2(int f, const char *a, int t, const char *b, unsigned fl) { REAL(renameat2); note_path('K', f, a); note_path('W', t, b); return real_renameat2(f, a, t, b, fl); }
int link(const char *a, const char *b) { REAL(link); note_path('K', AT_FDCWD, a); note_path('W', AT_FDCWD, b); return real_link(a, b); }
int linkat(int f, const char *a, int t, const char *b, int fl) { REAL(linkat); note_path('K', f, a); note_path('W', t, b); return real_linkat(f, a, t, b, fl); }
int symlink(const char *a, const char *b) { REAL(symlink); note_target(AT_FDCWD, a, b); note_path('W', AT_FDCWD, b); return real_symlink(a, b); }
int symlinkat(const char *a, int t, const char *b) { REAL(symlinkat); note_target(t, a, b); note_path('W', t, b); return real_symlinkat(a, t, b); }

/* ---- exec: the child's own "@" line proves it was observed; this line is what it gets counted against --------------- */
/* Bare names stay bare: the analyser walks PATH for them. Not note(): every X and F counts, so none may be deduplicated. */
static void put_exec(char op, const char *prog) {
    char full[PATH_MAX + 2];
    if (log_fd < 0 || !prog) return;
    if (prog[0] == '/' || !strchr(prog, '/')) { put(op, prog); return; }
    absolute(AT_FDCWD, prog, full, sizeof full);
    put(op, full[0] ? full : prog);
}
static void exec_try(const char *prog) { put_exec('X', prog); }
static void exec_back(const char *prog) { int e = errno; put_exec('F', prog); errno = e; }

int execve(const char *p, char *const a[], char *const e[]) { REAL(execve); exec_try(p); int r = real_execve(p, a, e); exec_back(p); return r; }
int execv(const char *p, char *const a[]) { REAL(execv); exec_try(p); int r = real_execv(p, a); exec_back(p); return r; }
int execvp(const char *p, char *const a[]) { REAL(execvp); exec_try(p); int r = real_execvp(p, a); exec_back(p); return r; }
int execvpe(const char *p, char *const a[], char *const e[]) { REAL(execvpe); exec_try(p); int r = real_execvpe(p, a, e); exec_back(p); return r; }
int fexecve(int fd, char *const a[], char *const e[]) { REAL(fexecve); exec_try("fexecve"); int r = real_fexecve(fd, a, e); exec_back("fexecve"); return r; }
int posix_spawn(pid_t *pid, const char *p, const posix_spawn_file_actions_t *fa, const posix_spawnattr_t *at,
                char *const a[], char *const e[]) {
    REAL(posix_spawn); exec_try(p); int r = real_posix_spawn(pid, p, fa, at, a, e); if (r) exec_back(p); return r;
}
int posix_spawnp(pid_t *pid, const char *p, const posix_spawn_file_actions_t *fa, const posix_spawnattr_t *at,
                 char *const a[], char *const e[]) {
    REAL(posix_spawnp); exec_try(p); int r = real_posix_spawnp(pid, p, fa, at, a, e); if (r) exec_back(p); return r;
}

/* glibc reaches its spawn through a hidden symbol here, so the shell these start must be counted by hand */
int system(const char *cmd) {
    REAL(system); if (!cmd) return real_system(cmd);
    exec_try("/bin/sh"); int r = real_system(cmd); if (r == -1) exec_back("/bin/sh"); return r;
}
FILE *popen(const char *cmd, const char *m) {
    REAL(popen); exec_try("/bin/sh"); FILE *r = real_popen(cmd, m); if (!r) exec_back("/bin/sh"); return r;
}

int chdir(const char *p) { REAL(chdir); note_path('S', AT_FDCWD, p); return real_chdir(p); }

/* ---- network ----------------------------------------------------------------------------------------------------- */
int connect(int fd, const struct sockaddr *sa, socklen_t len) {
    REAL(connect);
    if (log_fd >= 0 && sa) {
        if (sa->sa_family == AF_UNIX) {
            const struct sockaddr_un *u = (const struct sockaddr_un *)sa;
            note('U', u->sun_path[0] ? u->sun_path : "(abstract)");
        } else {
            note('N', "connect");
        }
    }
    return real_connect(fd, sa, len);
}
int getaddrinfo(const char *h, const char *s, const struct addrinfo *hints, struct addrinfo **res) {
    REAL(getaddrinfo); note('N', "getaddrinfo"); return real_getaddrinfo(h, s, hints, res);
}

/* ---- environment and clock --------------------------------------------------------------------------------------- */
char *getenv(const char *name) { REAL(getenv); note('E', name); return real_getenv(name); }
char *secure_getenv(const char *name) { REAL(secure_getenv); note('E', name); return real_secure_getenv(name); }

static void clock_read(void) {
    if (log_fd >= 0 && clock_armed && !clock_muted && !clock_said) { clock_said = 1; put('C', "realtime"); }
}
int clock_gettime(clockid_t id, struct timespec *t) {
    REAL(clock_gettime);
    if (id == CLOCK_REALTIME || id == CLOCK_REALTIME_COARSE) clock_read();
    return real_clock_gettime(id, t);
}
time_t time(time_t *t) { REAL(time); clock_read(); return real_time(t); }
int gettimeofday(struct timeval *restrict t, void *restrict z) { REAL(gettimeofday); clock_read(); return real_gettimeofday(t, z); }
