#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "tools" / "registry.json"
PRESETS_PATH = ROOT / "tools" / "presets.json"
TOOLBOX_PATH = ROOT / "tools" / "toolbox.py"

HELP_TEXT = """HelpBox hakd

[t] tools    - list all tools
[i] info     - show info for one tool
[p] presets  - list preset templates/examples
[d] doctor   - check dependencies and PATH
[u] update   - upgrade all tools (+ self update if clean repo)
[s] search   - scan/search tools in registry
[h] help     - show this help screen
[q] quit     - exit
"""


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def load_registry() -> List[Dict[str, Any]]:
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("registry", [])


def load_presets() -> Dict[str, Any]:
    if not PRESETS_PATH.exists():
        return {}
    with PRESETS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def print_header(title: str) -> None:
    print(title)
    print("-" * len(title))


def list_tools(registry: List[Dict[str, Any]]) -> None:
    print_header("Tools")
    for tool in registry:
        print(f"- {tool['name']}: {tool.get('description', '')}")


def info_tool(registry: List[Dict[str, Any]], name: str) -> None:
    for tool in registry:
        if tool["name"] == name:
            print_header(f"Info: {tool['name']}")
            print(f"Category: {tool.get('category', '')}")
            print(f"Description: {tool.get('description', '')}")
            print(f"Source: {tool.get('source', '')}")
            print(f"Docs: {tool.get('docs', '')}")
            print(f"Install: {tool.get('install', '')}")
            print(f"Update: {tool.get('update', '')}")
            print(f"Verify: {tool.get('verify', '')}")
            return
    print(f"No tool named '{name}' found.")


def list_presets() -> None:
    presets = load_presets()
    print_header("Presets")
    if not presets.get("presets"):
        print("No presets configured yet. Add entries to tools/presets.json.")
        return
    for preset in presets["presets"]:
        print(f"- {preset['name']}: {preset.get('description', '')}")
        for example in preset.get("examples", []):
            print(f"  > {example}")


def run_toolbox(args: List[str]) -> int:
    command = [sys.executable, str(TOOLBOX_PATH)] + args
    return subprocess.call(command)


def doctor() -> None:
    run_toolbox(["doctor"])


def update_all(registry: List[Dict[str, Any]]) -> None:
    for tool in registry:
        print_header(f"Updating {tool['name']}")
        run_toolbox(["--verbose", "--explain", "update", tool["name"]])
    self_update()


def self_update() -> None:
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        print("Self-update skipped (not a git repository).")
        return
    status = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    if status.stdout.strip():
        print("Self-update skipped (working tree not clean).")
        return
    response = input("Repo is clean. Run 'git pull' to self-update? [y/N] ").strip().lower()
    if response != "y":
        print("Self-update cancelled.")
        return
    subprocess.call(["git", "-C", str(ROOT), "pull"])


def search_tools(registry: List[Dict[str, Any]], query: str) -> None:
    query_lower = query.lower()
    matches = [
        tool
        for tool in registry
        if query_lower in tool["name"].lower()
        or query_lower in tool.get("category", "").lower()
        or query_lower in tool.get("description", "").lower()
    ]
    if not matches:
        print(f"No tools match '{query}'.")
        return
    print_header(f"Matches for '{query}'")
    for tool in matches:
        print(f"- {tool['name']}: {tool.get('description', '')}")


def prompt_loop() -> None:
    registry = load_registry()
    while True:
        clear_screen()
        print(HELP_TEXT)
        choice = input("Select an option: ").strip().lower()
        if not choice:
            continue
        if choice == "q":
            return
        if choice == "h":
            continue
        if choice == "t":
            clear_screen()
            list_tools(registry)
            input("\nPress Enter to continue...")
        elif choice == "i":
            name = input("Tool name: ").strip()
            clear_screen()
            info_tool(registry, name)
            input("\nPress Enter to continue...")
        elif choice == "p":
            clear_screen()
            list_presets()
            input("\nPress Enter to continue...")
        elif choice == "d":
            clear_screen()
            doctor()
            input("\nPress Enter to continue...")
        elif choice == "u":
            clear_screen()
            update_all(registry)
            input("\nPress Enter to continue...")
        elif choice == "s":
            query = input("Search query: ").strip()
            clear_screen()
            search_tools(registry, query)
            input("\nPress Enter to continue...")
        else:
            print("Unknown option.")
            input("\nPress Enter to continue...")


def main() -> int:
    try:
        prompt_loop()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
