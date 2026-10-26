#!/usr/bin/env bash
# SteveDesktop WSL bootstrap. Run as root inside Ubuntu; bootstrap.ps1 calls it twice:
#   wsl -d Ubuntu -u root -- bash /mnt/c/SteveDesktop/bootstrap_wsl.sh pass1   (before systemd)
#   wsl -d Ubuntu -u root -- bash /mnt/c/SteveDesktop/bootstrap_wsl.sh pass2   (after wsl --shutdown)
# Later, from Archmagi, an agent can re-run any pass, or just the clone:
#   ssh <win> "wsl -d Ubuntu -u root -- bash /mnt/c/SteveDesktop/bootstrap_wsl.sh clone"
# Idempotent. Log: /var/log/stevedesktop_bootstrap.log. Prints BOOTSTRAP_WSL_DONE at the end.
#
# The runner clone needs GitHub access: this script makes ~mandrake/.ssh/id_ed25519 and prints the
# public key; an agent on Archmagi registers it as a deploy key with Archmagi's own gh login
# (RUNBOOK step A3), so nobody has to type a GitHub password on SteveDesktop.
set -uo pipefail

PASS="${1:-pass1}"
U=mandrake
H=/home/$U
REPO_SSH=git@github.com:Lmandrake/RimMandrake.git
RUNNER=$H/rm/runner
STAGE=/mnt/c/SteveDesktop
LOG=/var/log/stevedesktop_bootstrap.log
export DEBIAN_FRONTEND=noninteractive

[ "$(id -u)" = 0 ] || { echo "must run as root (wsl -u root)"; exit 1; }

FAILS=()
step() {  # step <name> <command...>: run, record, never abort the whole script
    local name=$1; shift
    if "$@"; then echo "OK   $name"; else echo "FAIL $name (exit $?)"; FAILS+=("$name"); fi
}
as_user() { sudo -u "$U" -H bash -lc "$1"; }
systemd_up() { [ "$(ps -p 1 -o comm= 2>/dev/null)" = systemd ]; }

make_user() {
    id "$U" >/dev/null 2>&1 || useradd -m -s /bin/bash -G sudo "$U" || return 1
    echo "$U ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-$U && chmod 440 /etc/sudoers.d/90-$U
    visudo -cf /etc/sudoers.d/90-$U >/dev/null
}

wsl_conf() {
    # systemd on, default user, keep Windows interop (agents call powershell.exe from WSL).
    cat > /etc/wsl.conf <<EOF
[boot]
systemd=true

[user]
default=$U

[interop]
enabled=true
appendWindowsPath=true
EOF
}

apt_basics() {
    apt-get update -q &&
    apt-get install -y -q ca-certificates curl wget git python3 python3-venv python3-pip python3-numpy python3-pil jq tmux \
        unzip zip build-essential rsync htop openssh-client gnupg lsb-release
}

install_gh() {
    command -v gh >/dev/null && return 0
    install -d -m 755 /etc/apt/keyrings &&
    wget -qO /etc/apt/keyrings/githubcli-archive-keyring.gpg https://cli.github.com/packages/githubcli-archive-keyring.gpg &&
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg &&
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list &&
    apt-get update -q && apt-get install -y -q gh
}

install_node() {
    command -v node >/dev/null && node -v | grep -q '^v2[2-9]' && return 0
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y -q nodejs
}

install_claude() {
    # Native installer: lands in ~/.local/bin/claude and updates itself; `claude update` forces it.
    as_user 'test -x ~/.local/bin/claude || curl -fsSL https://claude.ai/install.sh | bash'
    as_user 'grep -q "/.local/bin" ~/.bashrc || echo "export PATH=\$HOME/.local/bin:\$PATH" >> ~/.bashrc'
    as_user '~/.local/bin/claude --version'
}

user_keys() {
    as_user 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && { test -f ~/.ssh/id_ed25519 || ssh-keygen -q -t ed25519 -N "" -C "mandrake@stevedesktop-wsl" -f ~/.ssh/id_ed25519; }' || return 1
    if [ -f "$STAGE/archmagi.pub" ]; then
        local k; k=$(head -n1 "$STAGE/archmagi.pub" | tr -d '\r')
        touch "$H/.ssh/authorized_keys"
        grep -qxF "$k" "$H/.ssh/authorized_keys" || echo "$k" >> "$H/.ssh/authorized_keys"
        chown "$U:$U" "$H/.ssh/authorized_keys"; chmod 600 "$H/.ssh/authorized_keys"
    fi
    as_user 'grep -q "^github.com " ~/.ssh/known_hosts 2>/dev/null || ssh-keyscan -T 10 -t ed25519 github.com >> ~/.ssh/known_hosts 2>/dev/null'
    as_user 'git config --global user.name >/dev/null || git config --global user.name "Lukas Mandrake"'
    as_user 'git config --global user.email >/dev/null || git config --global user.email "lukas.mandrake@gmail.com"'
    echo "WSL_PUBKEY: $(cat $H/.ssh/id_ed25519.pub)"
}

clone_runner() {
    if [ -d "$RUNNER/.git" ]; then echo "runner clone present: $(as_user "git -C $RUNNER log --oneline -1")"; return 0; fi
    if ! as_user 'ssh -o BatchMode=yes -T git@github.com 2>&1 | grep -q "successfully authenticated"'; then
        echo "PENDING clone: GitHub does not accept this key yet. On Archmagi run RUNBOOK step A3 (deploy key), then:"
        echo "  ssh <win> \"wsl -d Ubuntu -u root -- bash /mnt/c/SteveDesktop/bootstrap_wsl.sh clone\""
        return 0   # not a failure: it is a known, queued step
    fi
    as_user "mkdir -p $H/rm && git clone $REPO_SSH $RUNNER"
}

install_tailscale() {
    command -v tailscale >/dev/null || curl -fsSL https://tailscale.com/install.sh | sh || return 1
    systemd_up && systemctl enable --now tailscaled
    return 0
}

tailscale_login() {
    systemd_up || { echo "systemd not running yet; tailscale login waits for pass2"; return 0; }
    if tailscale status >/dev/null 2>&1; then echo "tailscale up: $(tailscale ip -4 | head -1)"; tailscale set --ssh >/dev/null 2>&1; return 0; fi
    # Same flags as Archmagi's break-glass (setup_break_glass.sh). Prints a login URL.
    timeout 25 tailscale up --ssh --hostname stevedesktop-wsl --accept-dns=false --timeout=20s 2>&1 | tee /tmp/ts_up.txt
    grep -o 'https://login.tailscale.com/[^ ]*' /tmp/ts_up.txt | head -1 | sed 's/^/TAILSCALE_WSL_LOGIN_URL: /'
    return 0
}

selfupgrade_units() {
    install -d /opt/stevedesktop /var/lib/runner
    cat > /opt/stevedesktop/selfupgrade.sh <<'EOF'
#!/usr/bin/env bash
# Runner self-upgrade (installed by bootstrap_wsl.sh). Daily: git pull of the runner clone and
# claude update. Weekly (or if the last apt run is over 7 days old): apt upgrade.
# Log: /var/log/runner-selfupgrade.log   Stamp: /var/lib/runner/last_selfupgrade.json
set -uo pipefail
U=mandrake; RUNNER=/home/$U/rm/runner; LOG=/var/log/runner-selfupgrade.log; ST=/var/lib/runner
[ -f "$LOG" ] && [ "$(stat -c %s "$LOG")" -gt 5000000 ] && mv -f "$LOG" "$LOG.old"
exec >>"$LOG" 2>&1
echo "=== $(date -u +%FT%TZ) selfupgrade"
git_rc=skip; apt_rc=skip; claude_rc=skip
# A testq attempt pins the runner to the sha it reported; never move HEAD under it (worker.py pulls itself).
if [ -s /mnt/d/RimTest/testq/current ]; then
    git_rc="busy:$(head -c 80 /mnt/d/RimTest/testq/current | tr -d '\n"')"
elif [ -d "$RUNNER/.git" ]; then
    sudo -u $U -H git -C "$RUNNER" pull --ff-only; git_rc=$?
fi
last_apt=$(cat $ST/last_apt_epoch 2>/dev/null || echo 0)
if [ $(( $(date +%s) - last_apt )) -gt 604800 ]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -q && apt-get -y -q -o Dpkg::Options::=--force-confold upgrade; apt_rc=$?
    [ "$apt_rc" = 0 ] && date +%s > $ST/last_apt_epoch
    apt-get -y -q autoremove >/dev/null; apt-get clean
fi
sudo -u $U -H bash -lc '~/.local/bin/claude update'; claude_rc=$?
df_root=$(df -P / | awk 'NR==2{print $4}')
printf '{"utc":"%s","git_pull":"%s","apt_upgrade":"%s","claude_update":"%s","root_free_kb":%s}\n' \
    "$(date -u +%FT%TZ)" "$git_rc" "$apt_rc" "$claude_rc" "$df_root" > $ST/last_selfupgrade.json
cat $ST/last_selfupgrade.json
EOF
    chmod 755 /opt/stevedesktop/selfupgrade.sh
    cat > /etc/systemd/system/runner-selfupgrade.service <<'EOF'
[Unit]
Description=SteveDesktop runner self-upgrade (git pull, apt weekly, claude update)
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=/opt/stevedesktop/selfupgrade.sh
TimeoutStartSec=1h
EOF
    cat > /etc/systemd/system/runner-selfupgrade.timer <<'EOF'
[Unit]
Description=Daily SteveDesktop runner self-upgrade

[Timer]
OnCalendar=*-*-* 05:30:00
RandomizedDelaySec=15m
Persistent=true

[Install]
WantedBy=timers.target
EOF
    if systemd_up; then systemctl daemon-reload && systemctl enable --now runner-selfupgrade.timer
    else echo "systemd not running yet; timer enabled in pass2"; fi
}

user_linger() {
    # The testq worker detaches each attempt as a transient `systemd-run --user` unit; without linger the
    # user manager (and the attempt with it) dies when the last ssh session closes.
    if systemd_up; then loginctl enable-linger $U && loginctl show-user $U -p Linger
    else echo "systemd not running yet; linger enabled in pass2"; fi
}

journald_cap() {
    install -d /etc/systemd/journald.conf.d
    printf '[Journal]\nSystemMaxUse=200M\n' > /etc/systemd/journald.conf.d/stevedesktop.conf
}

main() {
echo "==== $(date -u +%FT%TZ) bootstrap_wsl.sh $PASS"
step user make_user
step wsl_conf wsl_conf
step journald_cap journald_cap
if [ "$PASS" = clone ]; then
    step clone clone_runner
else
    step apt apt_basics
    step gh install_gh
    step node install_node
    step claude install_claude
    step keys user_keys
    step clone clone_runner
    step tailscale install_tailscale
    step selfupgrade selfupgrade_units
    step linger user_linger
    [ "$PASS" = pass2 ] && step tailscale_login tailscale_login
fi
echo "systemd_pid1=$(systemd_up && echo yes || echo no)"
echo "failed_steps=${FAILS[*]:-none}"
echo BOOTSTRAP_WSL_DONE
}

# A pipeline, not exec > >(tee): wsl.exe must not return before the log line is written.
main 2>&1 | tee -a "$LOG"
