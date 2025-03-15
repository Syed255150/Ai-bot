import subprocess
import os

# Define the path to the Python executable and the scheduler script
python_executable = r"C:\Users\pc\AppData\Local\Programs\Python\Python311\python.exe"
scheduler_script = r"K:\Projects\FB ads\scheduler.py"

# Task name
task_name = "FBAdsScheduler"

# Command to create the task
command = [
    "schtasks",
    "/Create",
    "/TN", task_name,
    "/TR", f'"{python_executable} {scheduler_script}"',
    "/SC", "MINUTE",  # Schedule to run every minute
    "/F",  # Force create task
    "/RL", "HIGHEST",  # Run with highest privileges
    "/IT"  # Run only when the user is logged on
]

try:
    # Run the command
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    print(f"Task '{task_name}' created successfully.")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Failed to create task '{task_name}'.")
    print(e.stderr)
