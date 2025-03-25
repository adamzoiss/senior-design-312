#!/bin/bash

# Only run this once, if it fails, do not run again.

# This script is used to setup the environment for the project.
# It installs the required packages and sets up the environment variables.

# Function to echo a yellow string
echo_yellow() {
    echo -e "\e[33m$1\e[0m"
}

# Function to echo a green string
echo_green() {
    echo -e "\e[32m$1\e[0m"
}

##############################################################################
# Adding alias to the bashrc file
#!/bin/bash

BASHRC="$HOME/.bashrc"

# Define all lines you want to add to .bashrc
LINES=(
'alias ptree="tree -I '\''env|__pycache__|.env|*egg-info|.vscode|*.bin|*.wav'\''"'
'alias penvca="python3 -m venv .env --system-site-packages && source .env/bin/activate && pip install --upgrade pip"'
'alias penva="source .env/bin/activate"'
'export PYTHONPATH="$HOME/git/senior-design-312"'
)

echo "[+] Appending aliases and exports to .bashrc (if not already present)..."

for LINE in "${LINES[@]}"; do
    if ! grep -Fxq "$LINE" "$BASHRC"; then
        echo "$LINE" >> "$BASHRC"
        echo "  -> Added: $LINE"
    else
        echo "  -> Already present: $LINE"
    fi
done

source "$HOME/.bashrc"
echo_green "[✓] Done. You can run 'source ~/.bashrc' to use the changes now."

##############################################################################
# Update the raspberry pi
echo_yellow "Updating the raspberry pi"
sudo apt update
sudo apt -y upgrade
echo_green Update and upgrade completed.

# Enable I2C on Raspberry Pi
echo_yellow "Enabling I2C on Raspberry Pi..."
sudo apt install -y i2c-tools
sudo raspi-config nonint do_i2c 0
echo_green "I2C has been enabled, i2c-tools installed."

# Enabling SPI
echo_yellow "Enabling SPI on Raspberry Pi..."
sudo raspi-config nonint do_spi 0
echo_green "SPI has been enabled."

##############################################################################
# Installing pulseaudio
echo_yellow "Installing pulseaudio"
sudo apt install -y pulseaudio
echo_green "Pulseaudio installed."
##############################################################################
# Downloading and installing portaudio from source.
echo_yellow "Downloading and installing portaudio from source."
cd "$HOME"
git clone https://github.com/PortAudio/portaudio.git
cd portaudio
./configure --enable-shared --with-pulseaudio
make -j$(nproc)
sudo make install
sudo ldconfig
echo_green "Portaudio installed."
##############################################################################
# Setting up the python environment
echo_yellow "Setting up the python environment"
cd "$HOME/git/senior-design-312"
sudo apt install -y python3.11-dev
penvca
pip install -e .
echo_green "Python environment setup complete."
##############################################################################
# Setting up the voice bonnet drivers
sudo apt install --upgrade -y python3-setuptools
cd "$HOME"
sudo apt-get install -y git wget
git clone https://github.com/HinTak/seeed-voicecard
wget https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/raw/refs/heads/main/install_wm8960.sh
wget https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/raw/refs/heads/main/wm8960-soundcard.service
sudo chmod +x install_wm8960.sh
sudo bash install_wm8960.sh
echo_green "Voice bonnet drivers installed."
##############################################################################
# Sleep for 10 seconds then reboot
echo_yellow "System will reboot in 10 seconds..."
sleep 10
sudo reboot now
##############################################################################
