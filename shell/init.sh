#!/usr/bin/env bash

toolbox_shell_source="${BASH_SOURCE[0]:-${(%):-%x}}"
toolbox_shell_dir="$(cd "$(dirname "$toolbox_shell_source")" && pwd)"
PROJECT_ROOT="$(cd "${toolbox_shell_dir}/.." && pwd)"
export PROJECT_ROOT

toolbox_theme="minimal"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --theme)
      shift
      toolbox_theme="${1:-minimal}"
      ;;
  esac
  shift
done

. "${toolbox_shell_dir}/paths.sh"
. "${toolbox_shell_dir}/colours.sh"

toolbox_register_paths
toolbox_prompt_set_theme "$toolbox_theme"
