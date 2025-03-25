#!/bin/bash

# This script is used to setup the environment for the project.
# It installs the required packages and sets up the environment variables.



##############################################################################
# Adding alias to the bashrc file
LINES=(
    'alias ptree="tree -I '\'env|__pycache__|.env|*egg-info|.vscode|*.bin|*.wav\''"'
    'alias penvca="python3 -m venv .env --system-site-packages && source .env/bin/activate && pip install --upgrade pip"'
    'alias penva="source .env/bin/activate"'
    'export PYTHONPATH="$HOME/git/senior-design-312"'
)

# Target .bashrc file
BASHRC="$HOME/.bashrc"

# Loop through and add each line if it's not already present
for LINE in "${LINES[@]}"; do
  if ! grep -Fxq "$LINE" "$BASHRC"; then
    echo "$LINE" >> "$BASHRC"
    echo "Added: $LINE"
  else
    echo "Already exists: $LINE"
  fi
done

##############################################################################
# Update the raspberry pi
echo "Updating the raspberry pi"

sudo apt-get update
sudo apt-get upgrade
sudo apt install -y git
sudo apt install -y i2c-tools

echo Update completed.