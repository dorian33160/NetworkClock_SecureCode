from datetime import datetime
import ctypes
import ctypes.util
import prctl
import sys

prctl.cap_effective.limit(prctl.CAP_SYS_TIME)
prctl.cap_permitted.limit(prctl.CAP_SYS_TIME)

libcso6 = ctypes.CDLL('libc.so.6')
PR_SET_MM = 0x6
PR_SET_MM_EXE_FILE = 10 


libcso6.prctl(PR_SET_MM, PR_SET_MM_EXE_FILE, 1, 0, 0)

CLOCK_REALTIME = 0
class timespec(ctypes.Structure):
    _fields_ = [
        ('tv_sec', ctypes.c_long),
        ('tv_nsec', ctypes.c_long)
    ]

# Loading the system c library
libc = ctypes.CDLL(ctypes.util.find_library('c'))

# Definition of system API functions for time management
clock_gettime = libc.clock_gettime
clock_settime = libc.clock_settime

# Calling the system API functions to change the time
def set_system_time(new_time):
    # Conversion of the time into timespec format required by the system API
    ts = timespec()
    ts.tv_sec = int(new_time.timestamp())
    ts.tv_nsec = 0

    # Calling clock_settime to change the system time
    clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python hour_change.py <date> <time>")
        sys.exit(1)

    date_str = sys.argv[1]
    time_str = sys.argv[2]

    try:
        date_components = [int(comp) for comp in date_str.split('-')]
        time_components = [int(comp) for comp in time_str.split(':')]

        new_datetime = datetime(*date_components, *time_components)
    except ValueError:
        sys.exit(1)

    set_system_time(new_datetime)