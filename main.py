import json
import os
import subprocess

@staticmethod
def get_cfg():
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"configuration file not found: {cfg_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"failed to parse JSON config {cfg_path}: {e}") from e

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