import os
import subprocess
import sys
import prctl

def drop_privileges():
    # Check if the application is already running with superuser privileges
    if os.getuid() == 0:
        try:
            # Explicitly set the required capabilities (CAP_SYS_TIME) for changing date and time
            prctl.cap_effective.limit(prctl.CAP_SYS_TIME)
            prctl.cap_permitted.limit(prctl.CAP_SYS_TIME)
        except PermissionError as e:
            print("Unable to drop superuser privileges:", e)

def change_datetime(date_command, time_command):
    # Execute the commands using subprocess.Popen without shell
    try:
        subprocess.Popen(date_command, shell=True)
        subprocess.Popen(time_command, shell=True)
    except ValueError as e:
        print(f"An error occurred while changing the date and time: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while changing the date and time: {e}")

# Drop superuser privileges before calling the change_datetime function
drop_privileges()
change_datetime(sys.argv[1], sys.argv[2])