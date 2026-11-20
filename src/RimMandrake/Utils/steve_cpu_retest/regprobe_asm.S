# regprobe_asm.S - the register-hold cores of regprobe (RIMMANDRAKE_BUILD_STEVE_REGISTER_PROBE_SEES_UPPER_HALF_LOSS).
# Microsoft x64 calling convention (Windows; the Linux selftest declares them __attribute__((ms_abi))). GNU as, Intel syntax.
# Each core loads fixed patterns into every register of its kind, runs ITERS iterations of "add K, subtract K" on each
# register (an identity, so the right answer is the pattern itself), then stores every register for the C side to compare
# with the compiled-in pattern. Interrupts, DPCs and context switches land while the values are live; a save/restore
# that drops state shows as a wrong stored value. The add/sub keeps each register live; it does not cross 128-bit lanes,
# so an upper-half loss stays in the upper half and is classed as one.
#   arg1 rcx  pattern (avx/sse: 16 x 32 bytes; gpr: 14 x 8 bytes)
#   arg2 rdx  K (32 bytes; must be 16-byte aligned for the legacy SSE memory operands)
#   arg3 r8   out (same layout as pattern)
#   arg4 r9   iterations (>= 2)
#   arg5 [rsp+40] inject: bit 0 VZEROUPPER at the midpoint (avx), bit 1 flip bit 0 of register 5 (avx, sse),
#                 bit 2 flip bit 0 of rbx (gpr). 0 = the real probe.
.intel_syntax noprefix
.data
.balign 32
rp_flip32: .quad 1, 0, 0, 0
.text

# void rp_hold_avx(pat, k, out, iters, inject)
.globl rp_hold_avx
rp_hold_avx:
    push rbp
    mov rbp, rsp
    sub rsp, 160
    vmovdqu [rsp+0], xmm6
    vmovdqu [rsp+16], xmm7
    vmovdqu [rsp+32], xmm8
    vmovdqu [rsp+48], xmm9
    vmovdqu [rsp+64], xmm10
    vmovdqu [rsp+80], xmm11
    vmovdqu [rsp+96], xmm12
    vmovdqu [rsp+112], xmm13
    vmovdqu [rsp+128], xmm14
    vmovdqu [rsp+144], xmm15
    mov r10, [rbp+48]
    mov r11, r9
    shr r11, 1
    .irp i, 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    vmovdqu ymm\i, [rcx+\i*32]
    .endr
1:
    .irp i, 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    vpaddq ymm\i, ymm\i, [rdx]
    vpsubq ymm\i, ymm\i, [rdx]
    .endr
    cmp r9, r11
    jne 3f
    test r10, 1
    jz 2f
    vzeroupper
2:
    test r10, 2
    jz 3f
    vpxor ymm5, ymm5, [rip+rp_flip32]
3:
    dec r9
    jnz 1b
    .irp i, 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    vmovdqu [r8+\i*32], ymm\i
    .endr
    vmovdqu xmm6, [rsp+0]
    vmovdqu xmm7, [rsp+16]
    vmovdqu xmm8, [rsp+32]
    vmovdqu xmm9, [rsp+48]
    vmovdqu xmm10, [rsp+64]
    vmovdqu xmm11, [rsp+80]
    vmovdqu xmm12, [rsp+96]
    vmovdqu xmm13, [rsp+112]
    vmovdqu xmm14, [rsp+128]
    vmovdqu xmm15, [rsp+144]
    vzeroupper
    mov rsp, rbp
    pop rbp
    ret

# void rp_hold_sse(pat, k, out, iters, inject): the 128-bit control. Legacy SSE encodings on the low halves only; the
# pattern and out keep the 32-byte stride, the upper 16 bytes of each out slot are left as they were.
.globl rp_hold_sse
rp_hold_sse:
    push rbp
    mov rbp, rsp
    sub rsp, 160
    vzeroupper
    movdqu [rsp+0], xmm6
    movdqu [rsp+16], xmm7
    movdqu [rsp+32], xmm8
    movdqu [rsp+48], xmm9
    movdqu [rsp+64], xmm10
    movdqu [rsp+80], xmm11
    movdqu [rsp+96], xmm12
    movdqu [rsp+112], xmm13
    movdqu [rsp+128], xmm14
    movdqu [rsp+144], xmm15
    mov r10, [rbp+48]
    mov r11, r9
    shr r11, 1
    .irp i, 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    movdqu xmm\i, [rcx+\i*32]
    .endr
1:
    .irp i, 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    paddq xmm\i, [rdx]
    psubq xmm\i, [rdx]
    .endr
    cmp r9, r11
    jne 3f
    test r10, 2
    jz 3f
    pxor xmm5, [rip+rp_flip32]
3:
    dec r9
    jnz 1b
    .irp i, 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    movdqu [r8+\i*32], xmm\i
    .endr
    movdqu xmm6, [rsp+0]
    movdqu xmm7, [rsp+16]
    movdqu xmm8, [rsp+32]
    movdqu xmm9, [rsp+48]
    movdqu xmm10, [rsp+64]
    movdqu xmm11, [rsp+80]
    movdqu xmm12, [rsp+96]
    movdqu xmm13, [rsp+112]
    movdqu xmm14, [rsp+128]
    movdqu xmm15, [rsp+144]
    mov rsp, rbp
    pop rbp
    ret

# void rp_hold_gpr(pat, k, out, iters, inject): the scalar control. 14 general registers hold patterns:
# rax rbx rdx rsi rdi rbp r8 r9 r10 r11 r12 r13 r14 rcx (out order); r15 counts; K's first qword is read from the stack.
.globl rp_hold_gpr
rp_hold_gpr:
    push rbx
    push rbp
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    mov r10, [rsp+104]
    sub rsp, 32
    mov [rsp+0], r8
    mov rax, [rdx]
    mov [rsp+8], rax
    mov [rsp+16], r10
    mov rax, r9
    shr rax, 1
    mov [rsp+24], rax
    mov r15, r9
    mov rax, [rcx+0]
    mov rbx, [rcx+8]
    mov rdx, [rcx+16]
    mov rsi, [rcx+24]
    mov rdi, [rcx+32]
    mov rbp, [rcx+40]
    mov r8, [rcx+48]
    mov r9, [rcx+56]
    mov r10, [rcx+64]
    mov r11, [rcx+72]
    mov r12, [rcx+80]
    mov r13, [rcx+88]
    mov r14, [rcx+96]
    mov rcx, [rcx+104]
1:
    .irp r, rax,rbx,rdx,rsi,rdi,rbp,r8,r9,r10,r11,r12,r13,r14,rcx
    add \r, [rsp+8]
    sub \r, [rsp+8]
    .endr
    cmp r15, [rsp+24]
    jne 3f
    test qword ptr [rsp+16], 4
    jz 3f
    xor rbx, 1
3:
    dec r15
    jnz 1b
    mov r15, [rsp+0]
    mov [r15+0], rax
    mov [r15+8], rbx
    mov [r15+16], rdx
    mov [r15+24], rsi
    mov [r15+32], rdi
    mov [r15+40], rbp
    mov [r15+48], r8
    mov [r15+56], r9
    mov [r15+64], r10
    mov [r15+72], r11
    mov [r15+80], r12
    mov [r15+88], r13
    mov [r15+96], r14
    mov [r15+104], rcx
    add rsp, 32
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    ret

# void rp_dirty(void): the churn thread's AVX work between its wakes. Fills ymm0-5 with all ones and sets the upper halves
# of ymm6-15 (volatile under the convention) to ones, and returns WITHOUT vzeroupper, so its saved AVX state is never the
# init state: a restore that hands the probe thread this thread's registers, or none, shows.
.globl rp_dirty
rp_dirty:
    .irp i, 0,1,2,3,4,5
    vpcmpeqb ymm\i, ymm\i, ymm\i
    .endr
    .irp i, 6,7,8,9,10,11,12,13,14,15
    vinserti128 ymm\i, ymm\i, xmm0, 1
    .endr
    ret
