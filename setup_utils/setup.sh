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

penvca() {
    python3 -m venv .env --system-site-packages && source .env/bin/activate && pip install --upgrade pip
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
sleep 2
##############################################################################
# Update the raspberry pi
echo_yellow "Updating the raspberry pi"
sudo apt update
sudo apt -y upgrade
echo_green Update and upgrade completed.

# Enable I2C on Raspberry Pi
echo_yellow "Enabling I2C on Raspberry Pi..."
echo "Installing i2c-tools..."
sudo apt install -y i2c-tools
echo "Enabling I2C..."
sudo raspi-config nonint do_i2c 0
echo "Setting I2C baudrate to 1MHz..."
# Desired I2C baud rate
BAUDRATE=1000000
CONFIG_FILE="/boot/firmware/config.txt"
# Backup original config
echo "Creating backup of $CONFIG_FILE..."
sudo cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"
# Check if the baudrate line already exists
if grep -q "i2c_arm_baudrate" "$CONFIG_FILE"; then
    echo "Updating existing i2c_arm_baudrate value..."
    sudo sed -i "s/i2c_arm_baudrate=[0-9]*/i2c_arm_baudrate=${BAUDRATE}/" "$CONFIG_FILE"
else
    # Insert baudrate line directly after dtparam=i2c_arm=on
    echo "Inserting i2c_arm_baudrate line..."
    sudo sed -i "/^dtparam=i2c_arm=on/ a dtparam=i2c_arm_baudrate=${BAUDRATE}" "$CONFIG_FILE"
fi
echo "I2C baudrate set to $BAUDRATE in config.txt."
echo_green "I2C configurations complete."
sleep 2

# Enabling SPI
echo_yellow "Enabling SPI on Raspberry Pi..."
echo "Enabling SPI..."
sudo raspi-config nonint do_spi 0
echo_green "SPI has been enabled."
sleep 2

##############################################################################
# Installing pulseaudio
echo_yellow "Installing pulseaudio"
echo "Installing pulseaudio..."
sudo apt install -y pulseaudio
echo "Installing pulseaudio development libraries..."
sudo apt-get install -y libpulse-dev
echo_green "Pulseaudio installed."
sleep 2
##############################################################################
# Downloading and installing portaudio from source.
echo_yellow "Downloading and installing portaudio from source."
cd "$HOME"
git clone https://github.com/PortAudio/portaudio.git
cd portaudio
./configure --enable-shared --with-pulseaudio
sleep 1
echo "Compiling portaudio..."
make -j$(nproc)
echo "Installing portaudio..."
sudo make install
sudo ldconfig
echo_green "Portaudio installed."
sleep 2
##############################################################################
# Setting up the python environment
echo_yellow "Setting up the python environment"
echo "Creating python environment..."
cd "$HOME/git/senior-design-312"
echo "Installing python3.11-dev..."
sudo apt install -y python3.11-dev
penvca
echo "Installing required python packages..."
pip install -e .
echo_green "Python environment setup complete."
sleep 2
##############################################################################
# Setting up the voice bonnet drivers
echo_yellow "Setting up the voice bonnet drivers"
echo "Installing required packages..."
sudo apt install --upgrade -y python3-setuptools
cd "$HOME"
sudo apt-get install -y git wget
git clone https://github.com/HinTak/seeed-voicecard
wget https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/raw/refs/heads/main/install_wm8960.sh
wget https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/raw/refs/heads/main/wm8960-soundcard.service
echo "Installing voice bonnet drivers..."
sudo chmod +x install_wm8960.sh
sudo bash install_wm8960.sh
echo_green "Voice bonnet drivers installed."
sleep 2
##############################################################################
# Sleep for 10 seconds then reboot
echo_yellow "System will reboot in 10 seconds..."
sleep 10
sudo reboot now
##############################################################################
