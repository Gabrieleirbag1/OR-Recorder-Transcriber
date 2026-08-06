#!/bin/bash

current_dir=$(pwd)

# Parse command line arguments
create_desktop=false
for arg in "$@"
do
    if [ "$arg" == "--desktop" ] || [ "$arg" == "-d" ]; then
        create_desktop=true
    fi
done

# Install python312-venv if not installed
if ! dpkg -l | grep -q python3.12-venv; then
    echo "Installing python3.12-venv..."
    sudo apt-get install -y python3.12-venv
else
    echo "python3.12-venv is already installed."
fi

# Check if binutils is installed (provides objdump)
if ! dpkg -l | grep -q binutils; then
    echo "Installing binutils (required for objdump)..."
    sudo apt-get install -y binutils
else
    echo "binutils is already installed."
fi

# Create the virtual environment
if [ ! -d "$current_dir/venv" ]; then
    python3 -m venv "$current_dir/venv"
fi

# Activate the virtual environment
source "$current_dir/venv/bin/activate"
pip3 install pyinstaller

# Install dependencies
pip3 install -r "$current_dir/requirements.txt"

# Create Build directory only if it does not exist
if [ ! -d "$current_dir/Build" ]; then
    mkdir -p "$current_dir/Build"
fi
cd "$current_dir/Build"

# Create the executable
if [ "$(uname)" = "Darwin" ]; then
    pyinstaller --noconfirm --onefile --windowed --add-data "$current_dir/src/or_recorder_transcriber/assets:assets/" --add-data "$current_dir/src/or_recorder_transcriber/config:config/" --distpath "$current_dir" --name "ORRT" "$current_dir/src/or_recorder_transcriber/main.py"
else
    pyinstaller --noconfirm --onefile --windowed --add-data "$current_dir/src/or_recorder_transcriber/assets:assets/" --add-data "$current_dir/src/or_recorder_transcriber/config:config/" --distpath "$current_dir" --name "ORRT" "$current_dir/src/or_recorder_transcriber/main.py"
fi

# Remove the virtual environment
rm -rf "$current_dir/venv"

# Return to the original directory
cd "$current_dir"

echo "ORRT installation script completed successfully."

# Deactivate the virtual environment
deactivate