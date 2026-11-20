/* regprobe_harness.c - Linux harness for selftest_regprobe.py: runs the shipped register-hold cores (regprobe_asm.S,
 * called with the Microsoft convention they are written for) on this machine's CPU with each injection, and the shipped
 * classifier (regprobe_classify.h) on planted register values. One line per case:
 *   CASE <name> class=<class> nbad=<n> details=<reg:detail,...>
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "regprobe_classify.h"

#define MS __attribute__((ms_abi))
MS void rp_hold_avx(const void *pat, const void *k, void *out, uint64_t iters, uint64_t inject);
MS void rp_hold_sse(const void *pat, const void *k, void *out, uint64_t iters, uint64_t inject);
MS void rp_hold_gpr(const void *pat, const void *k, void *out, uint64_t iters, uint64_t inject);
MS void rp_dirty(void);

static void show(const char *name, int path, const uint64_t *out)
{
    int nbad, r, c = rp_classify_hold(path, out, &nbad), first = 1;
    const char *d;
    printf("CASE %s class=%s nbad=%d details=", name, RP_CLASS[c], nbad);
    if (path != RP_PATH_GPR)
        for (r = 0; r < RP_NVEC; r++)
            if (rp_classify_vec(path, out + 4 * r, r, &d) != RP_CLEAN) { printf("%s%d:%s", first ? "" : ",", r, *d ? d : "-"); first = 0; }
    printf("\n");
}

static void core(const char *name, int path, uint64_t inject)
{
    uint64_t out[RP_NVEC * 4] __attribute__((aligned(32)));
    memcpy(out, RP_PAT, sizeof out);
    rp_dirty();
    if (path == RP_PATH_AVX) rp_hold_avx(RP_PAT, RP_K, out, 100000, inject);
    else if (path == RP_PATH_SSE) rp_hold_sse(RP_PAT, RP_K, out, 100000, inject);
    else rp_hold_gpr(RP_GPAT, RP_K, out, 100000, inject);
    show(name, path, out);
}

static void plant(const char *name, int path, int reg, int lane, uint64_t value, int reg2, int lane2, uint64_t value2)
{
    uint64_t out[RP_NVEC * 4];
    memcpy(out, path == RP_PATH_GPR ? RP_GPAT : &RP_PAT[0][0], path == RP_PATH_GPR ? sizeof RP_GPAT : sizeof out);
    if (reg >= 0) out[path == RP_PATH_GPR ? reg : 4 * reg + lane] = value;
    if (reg2 >= 0) out[path == RP_PATH_GPR ? reg2 : 4 * reg2 + lane2] = value2;
    show(name, path, out);
}

int main(void)
{
    core("core_avx_clean", RP_PATH_AVX, 0);
    core("core_avx_vzeroupper", RP_PATH_AVX, 1);
    core("core_avx_flip_ymm5", RP_PATH_AVX, 2);
    core("core_sse_clean", RP_PATH_SSE, 0);
    core("core_sse_flip_xmm5", RP_PATH_SSE, 2);
    core("core_gpr_clean", RP_PATH_GPR, 0);
    core("core_gpr_flip_rbx", RP_PATH_GPR, 4);
    plant("plant_avx_none", RP_PATH_AVX, -1, 0, 0, -1, 0, 0);
    plant("plant_upper_zero", RP_PATH_AVX, 3, 2, 0, 3, 3, 0);
    plant("plant_upper_minus_k", RP_PATH_AVX, 9, 2, (uint64_t)0 - RP_K[2], 9, 3, (uint64_t)0 - RP_K[3]);
    plant("plant_upper_one_bit", RP_PATH_AVX, 15, 3, RP_PAT[15][3] ^ (1ULL << 63), -1, 0, 0);
    plant("plant_lower_lane1", RP_PATH_AVX, 4, 1, RP_PAT[4][1] ^ 1, -1, 0, 0);
    plant("plant_lower_beats_upper", RP_PATH_AVX, 7, 2, 0, 2, 0, RP_PAT[2][0] ^ 2);
    plant("plant_sse_upper_ignored", RP_PATH_SSE, 6, 2, 0, 6, 3, 0);
    plant("plant_sse_lane1", RP_PATH_SSE, 11, 1, RP_PAT[11][1] ^ 4, -1, 0, 0);
    plant("plant_gpr_rcx", RP_PATH_GPR, 13, 0, RP_GPAT[13] ^ 8, -1, 0, 0);
    return 0;
}
