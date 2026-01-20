#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "tools" / "registry.json"
CONFIG_PATH = ROOT / ".config" / "toolbox.json"
SHELL_INIT_PATH = ROOT / "shell" / "init.sh"

COLOR_CODES = {
    "reset": "\033[0m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
}


@dataclass
class Context:
    verbose: bool
    dry_run: bool
    explain: bool
    color: bool
    prefix: Path


@dataclass
class Tool:
    name: str
    category: str
    description: str
    install: str
    update: str
    verify: str
    docs: str
    requires_root: bool
    source: str


class ToolboxError(Exception):
    pass


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def load_registry() -> List[Tool]:
    payload = load_json(REGISTRY_PATH)
    registry = payload.get("registry", [])
    tools: List[Tool] = []
    for entry in registry:
        tools.append(
            Tool(
                name=entry["name"],
                category=entry.get("category", "uncategorized"),
                description=entry.get("description", ""),
                install=entry.get("install", ""),
                update=entry.get("update", ""),
                verify=entry.get("verify", ""),
                docs=entry.get("docs", ""),
                requires_root=bool(entry.get("requires_root", False)),
                source=entry.get("source", ""),
            )
        )
    return tools


def load_config() -> Dict[str, Any]:
    return load_json(CONFIG_PATH)


def colorize(text: str, color: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{COLOR_CODES.get(color, '')}{text}{COLOR_CODES['reset']}"


def log_info(ctx: Context, message: str) -> None:
    print(colorize(message, "cyan", ctx.color))


def log_warn(ctx: Context, message: str) -> None:
    print(colorize(message, "yellow", ctx.color))


def log_error(ctx: Context, message: str) -> None:
    print(colorize(message, "red", ctx.color), file=sys.stderr)


def explain(ctx: Context, message: str) -> None:
    if ctx.explain:
        print(colorize(f"[explain] {message}", "magenta", ctx.color))


def ensure_prefix(ctx: Context) -> None:
    for subdir in ("bin", "tmp"):
        (ctx.prefix / subdir).mkdir(parents=True, exist_ok=True)


def build_env(ctx: Context) -> Dict[str, str]:
    env = os.environ.copy()
    prefix_bin = str(ctx.prefix / "bin")
    env["PATH"] = os.pathsep.join([prefix_bin, env.get("PATH", "")])
    return env


def format_command(command: str, ctx: Context) -> str:
    return command.format(prefix=str(ctx.prefix))


def run_command(command: str, ctx: Context, reason: Optional[str] = None) -> int:
    if reason:
        explain(ctx, reason)
    formatted = format_command(command, ctx)
    if ctx.verbose or ctx.dry_run:
        log_info(ctx, f"$ {formatted}")
    if ctx.dry_run:
        return 0
    try:
        return subprocess.call(formatted, shell=True, env=build_env(ctx))
    except OSError as exc:
        raise ToolboxError(f"Failed to run command: {formatted}") from exc


def find_tool(tools: Iterable[Tool], name: str) -> Tool:
    for tool in tools:
        if tool.name == name:
            return tool
    raise ToolboxError(f"Unknown tool: {name}")


def is_installed(tool: Tool) -> bool:
    return shutil.which(tool.name) is not None


def list_tools(tools: List[Tool], ctx: Context) -> None:
    for tool in tools:
        status = "installed" if is_installed(tool) else "missing"
        status_color = "green" if status == "installed" else "red"
        print(
            f"{colorize(tool.name, 'bold', ctx.color)}\t"
            f"{tool.category}\t"
            f"{colorize(status, status_color, ctx.color)}\t"
            f"{tool.description}"
        )


def search_tools(tools: List[Tool], query: str, ctx: Context) -> None:
    query_lower = query.lower()
    matches = [
        tool
        for tool in tools
        if query_lower in tool.name.lower()
        or query_lower in tool.category.lower()
        or query_lower in tool.description.lower()
    ]
    if not matches:
        log_warn(ctx, f"No tools match '{query}'.")
        return
    list_tools(matches, ctx)


def info_tool(tool: Tool, ctx: Context) -> None:
    installed = is_installed(tool)
    print(colorize(tool.name, "bold", ctx.color))
    print(f"  Category: {tool.category}")
    print(f"  Description: {tool.description}")
    print(f"  Source: {tool.source}")
    print(f"  Requires root: {tool.requires_root}")
    print(f"  Docs: {tool.docs}")
    print(f"  Installed: {installed}")
    print(f"  Install: {format_command(tool.install, ctx)}")
    print(f"  Update: {format_command(tool.update, ctx)}")
    print(f"  Verify: {format_command(tool.verify, ctx)}")


def install_tool(tool: Tool, ctx: Context) -> int:
    ensure_prefix(ctx)
    if tool.requires_root and os.geteuid() != 0:
        log_warn(ctx, f"{tool.name} may require root privileges for install.")
    reason = f"Installing {tool.name} using {tool.source}."
    return run_command(tool.install, ctx, reason)


def update_tool(tool: Tool, ctx: Context) -> int:
    ensure_prefix(ctx)
    if tool.requires_root and os.geteuid() != 0:
        log_warn(ctx, f"{tool.name} may require root privileges for update.")
    reason = f"Updating {tool.name} using {tool.source}."
    return run_command(tool.update, ctx, reason)


def verify_tool(tool: Tool, ctx: Context) -> int:
    if not is_installed(tool):
        log_warn(ctx, f"{tool.name} is not installed (missing from PATH).")
    reason = f"Verifying {tool.name} using registry verify command."
    return run_command(tool.verify, ctx, reason)


def doctor(ctx: Context) -> None:
    checks = {
        "apt-get": shutil.which("apt-get"),
        "pip": shutil.which("pip"),
        "go": shutil.which("go"),
        "cargo": shutil.which("cargo"),
        "git": shutil.which("git"),
        "curl": shutil.which("curl"),
        "fzf": shutil.which("fzf"),
    }
    for name, path in checks.items():
        status = "ok" if path else "missing"
        color = "green" if path else "red"
        print(f"{colorize(name, 'bold', ctx.color)}\t{colorize(status, color, ctx.color)}")
    print()
    print(f"Config: {CONFIG_PATH}")
    print(f"Registry: {REGISTRY_PATH}")
    print(f"Prefix: {ctx.prefix}")
    print()
    path_doctor(ctx)

def normalize_path_entry(entry: str) -> str:
    return os.path.expandvars(os.path.expanduser(entry))


def path_doctor(ctx: Context) -> None:
    raw_entries = [entry for entry in os.environ.get("PATH", "").split(os.pathsep) if entry]
    seen: Dict[str, int] = {}
    duplicates: List[str] = []
    missing: List[str] = []

    for entry in raw_entries:
        normalized = normalize_path_entry(entry)
        count = seen.get(normalized, 0) + 1
        seen[normalized] = count
        if count == 2:
            duplicates.append(normalized)
        if not os.path.isdir(normalized):
            missing.append(normalized)

    print(colorize("PATH diagnostics", "bold", ctx.color))
    if duplicates:
        print(colorize("Duplicate PATH entries:", "yellow", ctx.color))
        for entry in duplicates:
            print(f"  - {entry}")
    else:
        print(colorize("No duplicate PATH entries found.", "green", ctx.color))

    missing_unique = list(dict.fromkeys(missing))
    if missing_unique:
        log_warn(ctx, "PATH segments that do not exist:")
        for entry in missing_unique:
            print(f"  - {entry}")
    else:
        print(colorize("All PATH segments exist.", "green", ctx.color))


def detect_shell_rc() -> Path:
    shell = os.environ.get("SHELL", "")
    rc_name = ".zshrc" if "zsh" in shell else ".bashrc"
    return Path.home() / rc_name


def backup_file(path: Path) -> Optional[Path]:
    if not path.exists():
        return None
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = path.with_name(f"{path.name}.bak-{timestamp}")
    shutil.copy2(path, backup_path)
    return backup_path


def setup_shell(ctx: Context, theme: str) -> None:
    rc_path = detect_shell_rc()
    source_line = f'source "{SHELL_INIT_PATH}" --theme {theme}'
    content = ""
    if rc_path.exists():
        content = rc_path.read_text(encoding="utf-8")
        if source_line in content:
            log_info(ctx, f"Shell setup already present in {rc_path}.")
            return
    updated_lines: List[str] = []
    replaced = False
    for line in content.splitlines():
        if "shell/init.sh" in line:
            updated_lines.append(source_line)
            replaced = True
        else:
            updated_lines.append(line)
    if not replaced:
        if content and not content.endswith("\n"):
            updated_lines.append("")
        updated_lines.append(source_line)
    if updated_lines:
        updated_lines.append("")
    backup_path = backup_file(rc_path)
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    rc_path.write_text("\n".join(updated_lines), encoding="utf-8")
    if backup_path:
        log_info(ctx, f"Backed up {rc_path} to {backup_path}.")
    log_info(ctx, f"Updated shell configuration at {rc_path}.")


def export_registry(output: Optional[Path]) -> None:
    payload = load_json(REGISTRY_PATH)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def import_registry(input_path: Path) -> None:
    payload = load_json(input_path)
    if "registry" not in payload:
        raise ToolboxError("Import file missing registry key.")
    save_json(REGISTRY_PATH, payload)


def run_tui(tools: List[Tool], ctx: Context) -> None:
    if not shutil.which("fzf"):
        raise ToolboxError("fzf is required for the TUI mode.")
    entries = [f"{tool.name}\t{tool.category}\t{tool.description}" for tool in tools]
    proc = subprocess.run(
        "fzf --ansi",
        input="\n".join(entries),
        text=True,
        shell=True,
        capture_output=True,
    )
    selection = proc.stdout.strip()
    if not selection:
        return
    name = selection.split("\t", 1)[0]
    info_tool(find_tool(tools, name), ctx)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Portable tool registry manager")
    parser.add_argument("--verbose", action="store_true", help="Show commands before execution")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running them")
    parser.add_argument("--explain", action="store_true", help="Explain each step")
    parser.add_argument("--no-color", action="store_true", help="Disable color output")
    parser.add_argument("--prefix", type=str, help="Install prefix for portable PATH")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List tools")

    search_parser = subparsers.add_parser("search", help="Search tools")
    search_parser.add_argument("query")

    info_parser = subparsers.add_parser("info", help="Show tool info")
    info_parser.add_argument("tool")

    install_parser = subparsers.add_parser("install", help="Install a tool")
    install_parser.add_argument("tool")

    update_parser = subparsers.add_parser("update", help="Update a tool")
    update_parser.add_argument("tool")

    verify_parser = subparsers.add_parser("verify", help="Verify a tool")
    verify_parser.add_argument("tool")

    subparsers.add_parser("doctor", help="Check system dependencies")

    setup_parser = subparsers.add_parser("setup", help="Install shell integration")
    setup_parser.add_argument(
        "--theme",
        choices=["minimal", "vivid", "high-contrast"],
        default="minimal",
        help="Prompt theme profile",
    )

    export_parser = subparsers.add_parser("export", help="Export registry to JSON")
    export_parser.add_argument("--output", type=str, help="Output file")

    import_parser = subparsers.add_parser("import", help="Import registry from JSON")
    import_parser.add_argument("input", type=str, help="Input registry file")

    subparsers.add_parser("tui", help="Interactive selector using fzf")

    return parser.parse_args()


def build_context(args: argparse.Namespace) -> Context:
    config = load_config()
    raw_prefix = Path(args.prefix or config.get("prefix", "./.tools"))
    prefix = raw_prefix if raw_prefix.is_absolute() else (ROOT / raw_prefix)
    prefix = prefix.resolve()
    color = config.get("color", True) and not args.no_color
    return Context(
        verbose=args.verbose,
        dry_run=args.dry_run,
        explain=args.explain,
        color=color,
        prefix=prefix,
    )


def main() -> int:
    args = parse_args()
    ctx = build_context(args)
    tools = load_registry()

    try:
        if args.command == "list":
            list_tools(tools, ctx)
        elif args.command == "search":
            search_tools(tools, args.query, ctx)
        elif args.command == "info":
            info_tool(find_tool(tools, args.tool), ctx)
        elif args.command == "install":
            return install_tool(find_tool(tools, args.tool), ctx)
        elif args.command == "update":
            return update_tool(find_tool(tools, args.tool), ctx)
        elif args.command == "verify":
            return verify_tool(find_tool(tools, args.tool), ctx)
        elif args.command == "doctor":
            doctor(ctx)
        elif args.command == "setup":
            setup_shell(ctx, args.theme)
        elif args.command == "export":
            export_registry(Path(args.output) if args.output else None)
        elif args.command == "import":
            import_registry(Path(args.input))
        elif args.command == "tui":
            run_tui(tools, ctx)
        else:
            raise ToolboxError(f"Unknown command: {args.command}")
    except ToolboxError as exc:
        log_error(ctx, str(exc))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
