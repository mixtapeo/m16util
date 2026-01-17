import argparse
import subprocess
from typing import Optional
from main import set_val, handle_req, get_cfg

def _print_vals_spec(vals: dict) -> None:
    if "range" in vals:
        rng = vals["range"]
        print(f"    values: range [{rng['min']}, {rng['max']}]")
    else:
        allowed = sorted(v for v in vals.values() if isinstance(v, int))
        if allowed:
            print(f"    values: {allowed}")
        else:
            print("    values: <none>")

def cmd_list(args: argparse.Namespace) -> None:
    cfg = get_cfg()
    for entry in cfg:
        print(f"- {entry.get('name')}: {entry.get('description', '<no description>')}")
        print(f"    location: {entry.get('location')}")
        _print_vals_spec(entry.get("values", {}))

def _read_path(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        # fallback to sudo cat (may prompt for password)
        try:
            res = subprocess.run(["sudo", "cat", path], capture_output=True, text=True, check=True)
            return res.stdout.strip()
        except Exception as e:
            return f"<error: {e}>"

def cmd_dumpvals(args: argparse.Namespace) -> None:
    cfg = get_cfg()
    target: Optional[str] = args.command
    entries = (entry for entry in cfg if (target is None or entry.get("name") == target))
    found = False
    for entry in entries:
        found = True
        name = entry.get("name")
        loc = entry.get("location")
        cur = _read_path(loc)
        print(f"{name} @ {loc}: {cur}")
    if not found and target is not None:
        print(f"unknown command: {target}")

def cmd_set(args: argparse.Namespace) -> None:
    try:
        handle_req(args.command, args.value)
    except KeyError as e:
        print(e)
    except ValueError as e:
        print(e)

def main() -> None:
    parser = argparse.ArgumentParser(prog="m16util")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List available commands and their specs")
    p_list.set_defaults(func=cmd_list)

    p_set = sub.add_parser("set", help="Set a command to a numeric value")
    p_set.add_argument("command", help="command name as in config.json")
    p_set.add_argument("value", type=int, help="numeric value to set")
    p_set.set_defaults(func=cmd_set)

    p_dump = sub.add_parser("dumpvals", help="Show current values read from filesystem")
    p_dump.add_argument("command", nargs="?", help="(optional) specific command to dump")
    p_dump.set_defaults(func=cmd_dumpvals)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()