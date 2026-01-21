#!/usr/bin/env bash

toolbox_prompt_theme="minimal"

toolbox_prompt_apply_bash() {
  local user_colour host_colour time_colour dir_colour reset bold
  reset="\[\e[0m\]"
  bold="\[\e[1m\]"
  case "$toolbox_prompt_theme" in
    minimal)
      user_colour="\[\e[37m\]"
      host_colour="\[\e[36m\]"
      time_colour="\[\e[90m\]"
      dir_colour="\[\e[33m\]"
      ;;
    vivid)
      user_colour="\[\e[32m\]"
      host_colour="\[\e[34m\]"
      time_colour="\[\e[35m\]"
      dir_colour="\[\e[33m\]"
      ;;
    high-contrast)
      user_colour="${bold}\[\e[97m\]"
      host_colour="${bold}\[\e[93m\]"
      time_colour="${bold}\[\e[91m\]"
      dir_colour="${bold}\[\e[96m\]"
      ;;
      dark-contrast)
      user_colour="\[\e[48;5;236m\]\[\e[38;5;82m\]"
      host_colour="\[\e[48;5;236m\]\[\e[38;5;213m\]"
      time_colour="\[\e[48;5;236m\]\[\e[38;5;141m\]"
      dir_colour="\[\e[48;5;236m\]\[\e[38;5;220m\]"
      ;;
    *)
      return 0
      ;;
  esac
  PS1="${user_colour}\\u${reset}@${host_colour}\\h${reset} ${time_colour}\\t${reset} ${dir_colour}\\w${reset} \\$ "
}

toolbox_prompt_apply_zsh() {
  local user_colour host_colour time_colour dir_colour reset bold
  reset="%f%b"
  bold="%B"
  case "$toolbox_prompt_theme" in
    minimal)
      user_colour="%F{white}"
      host_colour="%F{cyan}"
      time_colour="%F{242}"
      dir_colour="%F{yellow}"
      ;;
    vivid)
      user_colour="%F{green}"
      host_colour="%F{blue}"
      time_colour="%F{magenta}"
      dir_colour="%F{yellow}"
      ;;
    high-contrast)
      user_colour="${bold}%F{white}"
      host_colour="${bold}%F{yellow}"
      time_colour="${bold}%F{red}"
      dir_colour="${bold}%F{cyan}"
      ;;
      dark-contrast)
      user_colour="%K{236}%F{82}"
      host_colour="%K{236}%F{213}"
      time_colour="%K{236}%F{141}"
      dir_colour="%K{236}%F{220}"
      ;;
    *)
      return 0
      ;;
  esac
  PROMPT="${user_colour}%n${reset}@${host_colour}%m${reset} ${time_colour}%*${reset} ${dir_colour}%~${reset} %# "
}

toolbox_prompt_apply() {
  if [ -n "${ZSH_VERSION:-}" ]; then
    toolbox_prompt_apply_zsh
  else
    toolbox_prompt_apply_bash
  fi
}

toolbox_prompt_set_theme() {
  case "$1" in
    minimal|vivid|high-contrast|dark-contrast)
      toolbox_prompt_theme="$1"
      ;;
  esac
  toolbox_prompt_apply
}
