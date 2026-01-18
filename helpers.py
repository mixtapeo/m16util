import json
import os
import subprocess
import inotify.adapters

# module-level cache for configuration to avoid re-reading the file on every call
_CFG = None

def get_cfg():
    """Return the parsed JSON configuration. The result is cached in-module so
    subsequent calls return the same object instead of re-reading the file.
    """
    global _CFG
    if _CFG is not None:
        return _CFG

    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            _CFG = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"configuration file not found: {cfg_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"failed to parse JSON config {cfg_path}: {e}") from e

    return _CFG

def reload_cfg():
    """Clear the cached config and reload it from disk."""
    global _CFG
    _CFG = None
    return get_cfg()

def set_val(path: str, cmd: str, value: int) -> None:
    # Construct the command: echo 1 | sudo tee /path/to/file
    command = f"echo {value} | sudo tee {path}"
    try:
        # shell=True is required to handle the pipe "|"
        # stdout=subprocess.DEVNULL hides the output (tee prints the value back)
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL)
        print(f"Set {cmd} to {value}.")
    except subprocess.CalledProcessError:
        print("Error: Failed to write (Wrong password or file not found).")

def handle_req(cmd: str, value: int):
    """Set the numeric value at the given filesystem path.

    This calls set_val() if a inputted command and value are valid (exist in json).
    """
    cfg = get_cfg()
    for entry in cfg:
        if entry.get("name") == cmd:
            vals = entry.get("values", {})
            # validate numeric range
            if "range" in vals:
                rng = vals["range"]
                if not (rng["min"] <= value <= rng["max"]):
                    raise ValueError(f"value {value} out of range [{rng['min']}, {rng['max']}] for {cmd}")
            else:
                allowed = set(v for v in vals.values() if isinstance(v, int))
                if allowed and value not in allowed:
                    raise ValueError(f"value {value} not allowed for {cmd}; allowed: {sorted(allowed)}")
            # set_val is expected to accept a path and a value
            set_val(entry["location"], cmd, value)
            return
    raise KeyError(f"unknown command: {cmd}")

def batteryNotify():
    # 0 from below file is AC plugged, 1 is plugged. Cba to use power state (charging / discharged) for anything
    i = inotify.adapters.Inotify()

    i.add_watch('/sys/class/power_supply/AC0/online')
    
    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event # type: ignore
        with open(path + filename) as f:
            print(f.read().strip())
            break

def macro():
    # functions i want:
    # Low power and low refresh rate on battery
    # High refresh rate on battery, if on a known wifi (ex. home)
    # High perf. on AC (playing game or sm lol)
    # Quiet on AC (coding)
    # Super cool on AC (editing word docs)
    # will control prime-select (gpu selection), display ref. rate, and gpu/cpu kernel file setting