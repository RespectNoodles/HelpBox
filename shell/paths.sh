#!/usr/bin/env bash

toolbox_add_path_once() {
  local entry="$1"
  if [ -z "$entry" ]; then
    return 0
  fi
  case ":$PATH:" in
    *":$entry:"*) return 0 ;;
  esac
  PATH="${entry}:${PATH}"
}

toolbox_register_paths() {
  if [ -z "${PROJECT_ROOT:-}" ]; then
    return 0
  fi
  toolbox_add_path_once "${PROJECT_ROOT}/bin"
  toolbox_add_path_once "${PROJECT_ROOT}/.tools/bin"
}
