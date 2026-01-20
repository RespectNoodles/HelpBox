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

colour_CODES = {
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
    colour: bool
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


def colourize(text: str, colour: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{colour_CODES.get(colour, '')}{text}{colour_CODES['reset']}"


def log_info(ctx: Context, message: str) -> None:
    print(colourize(message, "cyan", ctx.colour))


def log_warn(ctx: Context, message: str) -> None:
    print(colourize(message, "yellow", ctx.colour))


def log_error(ctx: Context, message: str) -> None:
    print(colourize(message, "red", ctx.colour), file=sys.stderr)


def explain(ctx: Context, message: str) -> None:
    if ctx.explain:
        print(colourize(f"[explain] {message}", "magenta", ctx.colour))


def log_reason(ctx: Context, message: str) -> None:
    print(colourize(f"[reason] {message}", "magenta", ctx.colour))


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


def run_logged_command(command: str, ctx: Context, reason: str) -> int:
    log_reason(ctx, reason)
    formatted = format_command(command, ctx)
    log_info(ctx, f"$ {formatted}")
    if ctx.dry_run:
        return 0
    try:
        return subprocess.call(formatted, shell=True, env=build_env(ctx))
    except OSError as exc:
        raise ToolboxError(f"Failed to run command: {formatted}") from exc


def confirm_action(ctx: Context, prompt: str) -> bool:
    log_warn(ctx, prompt)
    try:
        response = input("Type 'yes' to continue: ").strip().lower()
    except EOFError:
        return False
    return response == "yes"


def detect_wsl() -> bool:
    if os.environ.get("WSLENV") or os.environ.get("WSL_DISTRO_NAME"):
        return True
    try:
        version = Path("/proc/version").read_text(encoding="utf-8").lower()
    except OSError:
        return False
    return "microsoft" in version or "wsl" in version


def pick_available_command(candidates: Iterable[str]) -> Optional[str]:
    for candidate in candidates:
        name = candidate.split()[0]
        if shutil.which(name):
            return candidate
    return None


def net_ping(args: argparse.Namespace, ctx: Context) -> int:
    cmd = f"ping -c {args.count} -s {args.size} -i {args.interval} {args.host}"
    reason = "Send ICMP echo requests to measure reachability and latency."
    return run_logged_command(cmd, ctx, reason)


def net_trace(args: argparse.Namespace, ctx: Context) -> int:
    cmd = pick_available_command(
        [
            f"mtr -rw -c {args.count} {args.host}",
            f"traceroute {args.host}",
            f"tracepath {args.host}",
        ]
    )
    if not cmd:
        log_warn(ctx, "No traceroute tool found (mtr, traceroute, or tracepath).")
        return 1
    reason = "Trace the network path and hop latency to the target."
    return run_logged_command(cmd, ctx, reason)


def net_dns_test(args: argparse.Namespace, ctx: Context) -> int:
    cmd = pick_available_command(
        [
            f"dig {args.host} +short",
            f"nslookup {args.host}",
            f"getent hosts {args.host}",
        ]
    )
    if not cmd:
        log_warn(ctx, "No DNS lookup tool found (dig, nslookup, or getent).")
        return 1
    reason = "Query DNS to validate resolution for the target host."
    return run_logged_command(cmd, ctx, reason)


def net_speed(ctx: Context) -> int:
    cmd = pick_available_command(
        [
            "speedtest --accept-license --accept-gdpr",
            "speedtest-cli",
            "fast",
        ]
    )
    if not cmd:
        log_warn(ctx, "No speed test tool found (speedtest, speedtest-cli, or fast).")
        return 1
    reason = "Run a bandwidth test to estimate download/upload performance."
    return run_logged_command(cmd, ctx, reason)


def net_flush_dns(ctx: Context) -> int:
    tool = pick_available_command(["resolvectl", "systemd-resolve"])
    if not tool:
        log_warn(ctx, "No supported DNS cache tool found (resolvectl/systemd-resolve).")
        return 1
    warning = (
        "WARNING: This will flush system DNS caches via systemd-resolved. "
        "It is safe but can disrupt active DNS queries."
    )
    if not confirm_action(ctx, warning):
        log_warn(ctx, "DNS flush canceled.")
        return 1
    stats_cmd = "resolvectl statistics" if "resolvectl" in tool else "systemd-resolve --statistics"
    flush_cmd = "resolvectl flush-caches" if "resolvectl" in tool else "systemd-resolve --flush-caches"
    run_logged_command(stats_cmd, ctx, "Show current DNS cache statistics before flushing.")
    result = run_logged_command(flush_cmd, ctx, "Flush systemd-resolved DNS caches.")
    run_logged_command(stats_cmd, ctx, "Show DNS cache statistics after flushing.")
    return result


def net_restart_network(ctx: Context) -> int:
    if detect_wsl():
        log_warn(ctx, "WSL detected; skipping network restart for safety.")
        return 1
    warning = (
        "WARNING: This will restart system networking services and may disrupt connectivity."
    )
    if not confirm_action(ctx, warning):
        log_warn(ctx, "Network restart canceled.")
        return 1
    if shutil.which("nmcli"):
        result = run_logged_command("nmcli networking off", ctx, "Disable NetworkManager networking.")
        result = run_logged_command("nmcli networking on", ctx, "Re-enable NetworkManager networking.")
        return result
    if shutil.which("systemctl"):
        return run_logged_command(
            "systemctl restart NetworkManager",
            ctx,
            "Restart the NetworkManager system service.",
        )
    if shutil.which("service"):
        return run_logged_command(
            "service network-manager restart",
            ctx,
            "Restart the network-manager service.",
        )
    log_warn(ctx, "No supported network restart command found.")
    return 1


def net_mtu_test(args: argparse.Namespace, ctx: Context) -> int:
    warning = (
        "This MTU test sends pings with the Don't Fragment flag to estimate "
        "path MTU. It does not change system settings."
    )
    if not confirm_action(ctx, warning):
        log_warn(ctx, "MTU test canceled.")
        return 1
    sizes = [1200, 1400, 1472]
    result = 0
    for size in sizes:
        cmd = f"ping -c {args.count} -M do -s {size} {args.host}"
        reason = f"Probe MTU using payload size {size} bytes."
        result = run_logged_command(cmd, ctx, reason)
        if result != 0:
            break
    return result


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
        status_colour = "green" if status == "installed" else "red"
        print(
            f"{colourize(tool.name, 'bold', ctx.colour)}\t"
            f"{tool.category}\t"
            f"{colourize(status, status_colour, ctx.colour)}\t"
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
    print(colourize(tool.name, "bold", ctx.colour))
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
        colour = "green" if path else "red"
        print(f"{colourize(name, 'bold', ctx.colour)}\t{colourize(status, colour, ctx.colour)}")
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

    print(colourize("PATH diagnostics", "bold", ctx.colour))
    if duplicates:
        print(colourize("Duplicate PATH entries:", "yellow", ctx.colour))
        for entry in duplicates:
            print(f"  - {entry}")
    else:
        print(colourize("No duplicate PATH entries found.", "green", ctx.colour))

    missing_unique = list(dict.fromkeys(missing))
    if missing_unique:
        log_warn(ctx, "PATH segments that do not exist:")
        for entry in missing_unique:
            print(f"  - {entry}")
    else:
        print(colourize("All PATH segments exist.", "green", ctx.colour))


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
    parser.add_argument("--no-colour", action="store_true", help="Disable colour output")
    parser.add_argument("--prefix", type=str, help="Install prefix for portable PATH")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List tools")

    net_parser = subparsers.add_parser("net", help="Network diagnostic utilities")
    net_subparsers = net_parser.add_subparsers(dest="net_command", required=True)

    ping_parser = net_subparsers.add_parser("ping", help="Ping a host")
    ping_parser.add_argument("host", help="Host to ping")
    ping_parser.add_argument("--count", type=int, default=4, help="Number of echo requests")
    ping_parser.add_argument("--size", type=int, default=56, help="Payload size in bytes")
    ping_parser.add_argument("--interval", type=float, default=1.0, help="Interval between packets")

    trace_parser = net_subparsers.add_parser("trace", help="Trace route to a host")
    trace_parser.add_argument("host", help="Host to trace")
    trace_parser.add_argument("--count", type=int, default=5, help="Number of cycles (mtr)")

    dns_parser = net_subparsers.add_parser("dns-test", help="Run DNS lookup for a host")
    dns_parser.add_argument("host", help="Host to resolve")

    net_subparsers.add_parser("speed", help="Run a bandwidth test (if available)")

    net_subparsers.add_parser("flush-dns", help="Flush DNS caches (requires confirmation)")
    net_subparsers.add_parser("restart-network", help="Restart networking services (requires confirmation)")

    mtu_parser = net_subparsers.add_parser("mtu-test", help="Run safe MTU probe tests")
    mtu_parser.add_argument("host", nargs="?", default="1.1.1.1", help="Host to probe")
    mtu_parser.add_argument("--count", type=int, default=1, help="Ping count per size")

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
    colour = config.get("colour", True) and not args.no_colour
    return Context(
        verbose=args.verbose,
        dry_run=args.dry_run,
        explain=args.explain,
        colour=colour,
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
        elif args.command == "net":
            if args.net_command == "ping":
                return net_ping(args, ctx)
            if args.net_command == "trace":
                return net_trace(args, ctx)
            if args.net_command == "dns-test":
                return net_dns_test(args, ctx)
            if args.net_command == "speed":
                return net_speed(ctx)
            if args.net_command == "flush-dns":
                return net_flush_dns(ctx)
            if args.net_command == "restart-network":
                return net_restart_network(ctx)
            if args.net_command == "mtu-test":
                return net_mtu_test(args, ctx)
            raise ToolboxError(f"Unknown net command: {args.net_command}")
        else:
            raise ToolboxError(f"Unknown command: {args.command}")
    except ToolboxError as exc:
        log_error(ctx, str(exc))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
