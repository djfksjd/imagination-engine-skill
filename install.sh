#!/usr/bin/env bash
# imagination-engine one-command installer
#   curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-engine-skill/main/install.sh | bash
#
# Supports two hosts: Claude Code and Codex. Both are attempted when present;
# a failure on one is not fatal for the other.
#
# The runtime skill is Markdown only.
set -u

REPO="djfksjd/imagination-engine-skill"
INSTALLED=0

log()  { printf '\033[1;35m[imagination-engine]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[imagination-engine]\033[0m %s\n' "$*" >&2; }

try_host() { # <name> <command...>
  local name="$1"; shift
  if "$@"; then
    log "✓ ${name} installed"
    INSTALLED=$((INSTALLED + 1))
  else
    warn "✗ ${name} install failed — see the README for manual steps"
  fi
}

if command -v claude >/dev/null 2>&1; then
  try_host "Claude Code" bash -c \
    "claude plugin marketplace add ${REPO} && claude plugin install imagination-engine@djfksjd"
else
  warn "claude CLI not found — skipping Claude Code"
fi

if command -v codex >/dev/null 2>&1; then
  try_host "Codex" bash -c \
    "codex plugin marketplace add ${REPO} && codex plugin add imagination-engine@djfksjd"
else
  warn "codex CLI not found — skipping Codex"
fi

if [ "${INSTALLED}" -eq 0 ]; then
  warn "Nothing was installed. Install the Claude Code or Codex CLI first, or clone manually:"
  warn "  git clone https://github.com/${REPO}.git"
  exit 1
fi

log "Done. During v0.5 evaluation, invoke it explicitly: \"use \$imagination-engine on: <brief>\""
