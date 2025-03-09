#!/bin/bash
set -e

export APP=${APP:-mba-scraper}

function log() {
  local date status message
  date=$(date -u +%Y-%m-%dT%H:%M:%S%z)
  status="$1"
  shift
  message=$(echo "$@" | sed s/$/\\n/g)
  printf '{"time":"%s","status":"%s","message":"%s"}\n' "$date" "$status" "$message"
}

if [[ $1 =~ ^(/bin/)?(ba)?sh$ ]]; then
  log INFO "First CMD argument is a shell: $1"
  log INFO "Running: exec ${@@Q}"
  exec "$@"
elif [[ "$*" =~ ([;<>]|\(|\)|\&\&|\|\|) ]]; then
  log INFO "Shell metacharacters detected, passing CMD to bash"
  _quoted="$*"
  log INFO "Running: exec /bin/bash -c ${_quoted@Q}"
  unset _quoted
  exec /bin/bash -c "$*"
fi

log INFO "Running command: /usr/local/bin/dumb-init ${@@Q}"
exec /usr/local/bin/dumb-init "$@"
