/* regprobe_classify.h - the fixed answers and the classifier of regprobe (RIMMANDRAKE_BUILD_STEVE_REGISTER_PROBE_SEES_UPPER_HALF_LOSS).
 * Pure C, no OS calls: regprobe.c (Windows) and the Linux selftest harness both include it, so the selftest exercises the
 * classifier that ships. The patterns are compiled-in constants (sha256 of "regprobe-<reg>-<lane>"), never computed on the
 * machine under test, and the cores' work is an identity, so the pattern IS the known answer.
 *
 * Classes, per register (worst wins for a hold):
 *   upper_half_loss   AVX path: bits 0-127 right, bits 128-255 wrong (detail zero = all upper bits 0; minus_k = the value
 *                     a zeroed upper half has after the add/sub straddled the loss; other)
 *   lower_half_error  AVX path: bits 0-127 wrong (whatever the upper half says)
 *   sse_error         SSE path: the 128-bit register wrong
 *   scalar_error      GPR path: the 64-bit register wrong
 */
#ifndef REGPROBE_CLASSIFY_H
#define REGPROBE_CLASSIFY_H
#include <stdint.h>
#include <string.h>

#define RP_NVEC 16
#define RP_NGPR 14

enum { RP_CLEAN = 0, RP_UPPER = 1, RP_LOWER = 2, RP_SSE = 3, RP_SCALAR = 4 };
static const char *const RP_CLASS[] = {"clean", "upper_half_loss", "lower_half_error", "sse_error", "scalar_error"};
enum { RP_PATH_AVX = 0, RP_PATH_SSE = 1, RP_PATH_GPR = 2 };
static const char *const RP_PATH[] = {"avx", "sse", "gpr"};
static const char *const RP_GPR_NAME[RP_NGPR] = {"rax", "rbx", "rdx", "rsi", "rdi", "rbp", "r8", "r9", "r10", "r11",
                                                 "r12", "r13", "r14", "rcx"};

static const uint64_t RP_PAT[RP_NVEC][4] __attribute__((aligned(32))) = {
    {0x939f9fb0a79086efULL, 0xe2329ac7d5593682ULL, 0x15162f316442b6b5ULL, 0x2cc0482352edd789ULL},
    {0x70113d36e1df1271ULL, 0xcf43bd25951c6675ULL, 0xd4a689243c09f75dULL, 0xf365ebd76c45f617ULL},
    {0x99b6026c44e5f542ULL, 0xf5dddd1dff435caaULL, 0x7dc1d554486bc845ULL, 0x881a1103c4d54d6cULL},
    {0x551ba86c8a3d3846ULL, 0x16a4dd49530d32a5ULL, 0xb3cc5bd21d636a73ULL, 0x79da7e36be15b628ULL},
    {0xb22ca1477add951bULL, 0x5e8ff920cda330cbULL, 0xfa56a34aaa0c9189ULL, 0x0cc00e061d58165cULL},
    {0x57988479f2b6aed9ULL, 0x6d60a76c8059f3b4ULL, 0x68f8880765d445abULL, 0x2d4e542c4f1c480aULL},
    {0xcbe641392c9a596aULL, 0xde37cc6127cc01f6ULL, 0x708c71d55c7df539ULL, 0x25d95f2473ec4524ULL},
    {0x28fc938ba18e2999ULL, 0x9d3205d6d62b7c0eULL, 0x63d79e019dd8b0f7ULL, 0x6826ee8f332d0808ULL},
    {0xd6111446205808f8ULL, 0xcf6b0847d92fca8cULL, 0xa518128eacbb480bULL, 0xd6d40282694835ceULL},
    {0x84169effb4760065ULL, 0xf13130d0ed08d2a8ULL, 0x12351d5439a7dbd4ULL, 0x7ab547427b106420ULL},
    {0xc2135e8286780988ULL, 0x58850120282b7f1eULL, 0xc6ff65646b6b5216ULL, 0xaee8d0c933d776edULL},
    {0xf45a16c5abba3ff5ULL, 0x76f0140e46318bdcULL, 0x11751d92d817cf02ULL, 0xbda67ec73cbe051aULL},
    {0xaeff3da313ff63cfULL, 0x37485b9bc5899686ULL, 0x7c4b3cee569befb1ULL, 0xbb4db7d3fc1dd96bULL},
    {0x642e1ad5e18185b2ULL, 0xe2c05af2b95f98d6ULL, 0xc2d3de0e065fba60ULL, 0xe3a9969260b204d6ULL},
    {0x3a1d6ef712b37b6dULL, 0x1ddbc9f5b30f6324ULL, 0xfddcc066abb0db27ULL, 0x1ad9bd20ee675ab8ULL},
    {0xac432c50f4e5179dULL, 0xadfbee0fcc2bee0eULL, 0x9f2892dc915a4e95ULL, 0x8728c692bdfe72f2ULL},
};
static const uint64_t RP_K[4] __attribute__((aligned(32))) = {
    0xe226510a96679e72ULL, 0x23b5bd0f1ec8b38fULL, 0xae0c8c683f97815eULL, 0xd4c03a3334c292c0ULL};
static const uint64_t RP_GPAT[RP_NGPR] = {
    0xd0de456a8fe5bfe6ULL, 0xc994d43b896f4f4fULL, 0xb1cf6f4725549512ULL, 0xdd696a36d9ef9a7cULL, 0xc68e9a4aa993dc17ULL,
    0x397fda823d32e6b8ULL, 0xcf8c0f0bb24b08c0ULL, 0xb0b212ca9cc6d07dULL, 0xcd9be9c795454bf0ULL, 0x45e99cd8906da5d1ULL,
    0xcb0c6569a95e7e23ULL, 0x359288307f8327a8ULL, 0xe566902b76d2f969ULL, 0x61ae3e611c96ea6cULL};

/* One register's verdict. reg: 0-15 (vector) or 0-13 (gpr). detail: for RP_UPPER, "zero", "minus_k" or "other". */
static int rp_classify_vec(int path, const uint64_t obs[4], int reg, const char **detail)
{
    const uint64_t *e = RP_PAT[reg];
    int lo = obs[0] == e[0] && obs[1] == e[1];
    *detail = "";
    if (path == RP_PATH_SSE)
        return lo ? RP_CLEAN : RP_SSE;
    if (!lo)
        return RP_LOWER;
    if (obs[2] == e[2] && obs[3] == e[3])
        return RP_CLEAN;
    if (obs[2] == 0 && obs[3] == 0)
        *detail = "zero";
    else if (obs[2] == (uint64_t)0 - RP_K[2] && obs[3] == (uint64_t)0 - RP_K[3])
        *detail = "minus_k";
    else
        *detail = "other";
    return RP_UPPER;
}

static int rp_classify_gpr(const uint64_t obs[RP_NGPR], int reg)
{
    return obs[reg] == RP_GPAT[reg] ? RP_CLEAN : RP_SCALAR;
}

/* The worst class in one hold's output (out: 16 x 4 qwords for avx/sse, 14 qwords for gpr), and how many registers are wrong. */
static int rp_classify_hold(int path, const uint64_t *out, int *nbad)
{
    int worst = RP_CLEAN, n = 0, r, c;
    const char *d;
    if (path == RP_PATH_GPR) {
        for (r = 0; r < RP_NGPR; r++)
            if ((c = rp_classify_gpr(out, r)) != RP_CLEAN) { n++; worst = c; }
    } else {
        for (r = 0; r < RP_NVEC; r++) {
            c = rp_classify_vec(path, out + 4 * r, r, &d);
            if (c != RP_CLEAN) { n++; if (c == RP_LOWER || worst == RP_CLEAN) worst = c; }
        }
    }
    *nbad = n;
    return worst;
}
#endif
