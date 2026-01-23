import platform

# Determine the appropriate command
if platform.system() == 'Windows':
    python_cmd = 'python'
    upgrade_pip = False  # Skip pip upgrade on Windows
else:
    python_cmd = 'python3'
    upgrade_pip = True  # Upgrade pip on non-Windows systems

try:
    import pip
    pip_cmd = 'pip'
except ImportError:
    # If pip is not available, assume it will be installed via get-pip.py
    pip_cmd = python_cmd + ' -m pip'

if upgrade_pip:
    import subprocess
    subprocess.check_call([pip_cmd, 'install', '--upgrade', 'pip'])

# Install requirements
import subprocess
subprocess.check_call([python_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'])
