#!/usr/bin/env bash
# imagination-octo-engine installer — safe to re-run: installs, or updates in place.
#   curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-engine/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-engine/main/install.sh | bash -s -- --clean-legacy
set -u

REPO="djfksjd/imagination-octo-engine"
MARKET="imagination-octo-engine"
PLUGIN="imagination-octo-engine@${MARKET}"
STATE_DIR="${IMAGINATION_OCTO_HOME:-${HOME}/.imagination-octo}"
CLEAN_LEGACY=0
INSTALLED=0
LEGACY_FOUND=0

log()  { printf '\033[1;35m[imagination-octo-engine]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[imagination-octo-engine]\033[0m %s\n' "$*" >&2; }

usage() {
  cat <<'EOF'
Usage: install.sh [--clean-legacy]

  --clean-legacy  Move the standalone pre-rename copy of this skill
                  out of the host skill folders (into ~/.imagination-octo/legacy)
                  and uninstall the plugin's former ids. Nothing is deleted.
EOF
}

for arg in "$@"; do
  case "${arg}" in
    --clean-legacy) CLEAN_LEGACY=1 ;;
    -h|--help) usage; exit 0 ;;
    *) warn "unknown option: ${arg}"; usage >&2; exit 2 ;;
  esac
done

# A standalone clone under the old name answers to a different command with an
# older runtime, so it is reported on every run.
legacy_dir() {
  local dir="$1" host="$2"
  [ -e "${dir}" ] || return 0
  LEGACY_FOUND=$((LEGACY_FOUND + 1))
  if [ "${CLEAN_LEGACY}" -eq 1 ]; then
    local dest="${STATE_DIR}/legacy/$(date +%Y%m%d-%H%M%S)/${host}"
    mkdir -p "${dest}" && mv "${dir}" "${dest}/" \
      && log "moved legacy copy ${dir} -> ${dest}/" \
      || warn "could not move ${dir}"
  else
    warn "legacy copy found: ${dir}"
  fi
}

scan_legacy() {
  local host="$1" host_dir="$2"
  legacy_dir "${host_dir}/skills/imagination-engine" "${host}"
}

claude_version() {
  claude plugin list --json 2>/dev/null | python3 -c '
import json, sys
for plugin in json.load(sys.stdin):
    if plugin.get("id") == sys.argv[1]:
        print(plugin.get("version", "unknown"))
' "${PLUGIN}" 2>/dev/null
}

install_claude() {
  # `add` fails when the marketplace is already configured; `update` then
  # refreshes it, and fails if it is still missing.
  claude plugin marketplace add "${REPO}" >/dev/null 2>&1
  claude plugin marketplace update "${MARKET}" >/dev/null 2>&1 || return 1
  if [ -n "$(claude_version)" ]; then
    claude plugin update "${PLUGIN}" >/dev/null 2>&1 || return 1
  else
    claude plugin install "${PLUGIN}" >/dev/null 2>&1 || return 1
  fi
  if [ "${CLEAN_LEGACY}" -eq 1 ]; then
    claude plugin uninstall "imagination-engine@djfksjd" >/dev/null 2>&1
  fi
  log "✓ Claude Code: ${PLUGIN} v$(claude_version)"
}

install_codex() {
  codex plugin marketplace add "${REPO}" >/dev/null 2>&1
  codex plugin marketplace upgrade "${MARKET}" >/dev/null 2>&1 || return 1
  codex plugin add "${PLUGIN}" >/dev/null 2>&1 || return 1
  if [ "${CLEAN_LEGACY}" -eq 1 ]; then
    codex plugin remove "imagination-engine@djfksjd" >/dev/null 2>&1
  fi
  log "✓ Codex: ${PLUGIN}"
}

try_host() {
  local name="$1" host="$2" host_dir="$3"
  if "install_${host}"; then
    INSTALLED=$((INSTALLED + 1))
  else
    warn "✗ ${name} install failed — see the README for manual steps"
  fi
  scan_legacy "${host}" "${host_dir}"
}

if command -v claude >/dev/null 2>&1; then
  try_host "Claude Code" claude "${CLAUDE_CONFIG_DIR:-${HOME}/.claude}"
else
  warn "claude CLI not found — skipping Claude Code"
fi

if command -v codex >/dev/null 2>&1; then
  try_host "Codex" codex "${CODEX_HOME:-${HOME}/.codex}"
else
  warn "codex CLI not found — skipping Codex"
fi

if [ "${INSTALLED}" -eq 0 ]; then
  warn "Nothing was installed. Install Claude Code or Codex first, or clone manually:"
  warn "  git clone https://github.com/${REPO}.git"
  exit 1
fi

if [ "${LEGACY_FOUND}" -gt 0 ] && [ "${CLEAN_LEGACY}" -eq 0 ]; then
  warn "An older standalone copy under the previous name is still installed."
  warn "Re-run with --clean-legacy to move it aside (nothing is deleted)."
fi

log "Done. Restart the host, then start with: use \$imagination-octo-engine on: <brief>"
