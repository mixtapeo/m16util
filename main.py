import os

# Change CPU clock configuration (write-only).
# There are three available clock configuration:

#     * 0 -> Super Performance Mode
#     * 1 -> High Performance Mode
#     * 2 -> Power Saving Mode
def set_cpufv(freq):
    with open("/sys/devices/platform/asus-nb-wmi/cpufv") as f:
        try:
            val = int(freq)
        except (TypeError, ValueError):
            raise ValueError("freq must be an integer 0, 1 or 2")
        if val not in (0, 1, 2):
            raise ValueError("freq must be 0, 1 or 2")

        fd = os.open(f.name, os.O_WRONLY)
        try:
            os.write(fd, f"{val}\n".encode())
        finally:
            os.close(fd)
set_cpufv(1)