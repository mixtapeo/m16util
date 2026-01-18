can set cpu and gpu settings by editing /sys/ files and monitoring battery state changes to perform macros (e.g., high-perf on cpu when unplugged)

notes
https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-devices-system-cpu
https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-platform-asus-wmi

cpu_atom - e cores
cpu_core - p cores

/sys/devices/platform/asus-nb-wmi 

can detect if plugged in, and will trigger a configured setting.
uses inotify (linux notify) to avoid polling files with info for updates