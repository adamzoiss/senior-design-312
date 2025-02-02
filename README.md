# Senior Design Project - Team 312


## Sharepoint link:

__Files & Notes:__ [SharePoint](https://fsu-my.sharepoint.com/personal/amw21i_fsu_edu/_layouts/15/Doc.aspx?sourcedoc={c8d6e6cb-04f5-4a5c-a4a4-ac70581ecfba}&action=edit&wd=target%28Class%20Handouts.one%7C43749e4e-c570-4688-8d40-703e8b013bf2%2FSenior%20Design%20Projects%7C01b6a98f-3880-41ca-834b-d67c770890d6%2F%29&wdorigin=NavigationUrl)

___
# Quick Links for Navigation and Useful Information

1. [RPI Setup](#rpi-setup)

2. [Coding Environment](#coding-environment)

3. [Running the Code](#running-the-program)

4. [Using Git](#using-git)

5. [Team/Contributors Info](#contributors)
___

[PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/#introduction) - Guideline for how to code in Python

[Python Project/Package Template](https://github.com/pypa/sampleproject) - To better understand the structure of the project, a template for python projects/packages can be viewed as a reference.

[Raspberry Pi pinout information](https://pinout.xyz/) - Useful for setting up buttons, switches, RF chip, etc. via the GPIO pins.

[CC1101 Python Package](https://github.com/fphammerle/python-cc1101) - Package for controlling the CC1101 Transceiver chip.

[Git Information](https://git-scm.com/book/en/v2) - Information on how to use git.

___

## __RPI Setup:__

1. Download the [Raspberry PI imager](https://www.raspberrypi.com/software/)

2. Select RPI 5 as device and Raspian 64-bit Desktop as OS

3. Customize settings before flashing
    - Name the device (ex. rpi5-312)
    - Set username (ex. team312)
    - Set password (ex. password)
    - Enable SSH in second tab
    - Finally flash the SD card with the OS

4. Plug SD card in, power on

___

* __How to SSH to rpi:__

    - using powershell or terminal (must be on same network)

        ```bash
        ssh [username]@[device name].local
        ```

* Follow steps to allow connection

* To make life simpler going forward, get the VS code extension *Remote Explorer*
    - Then follow steps to make a SSH connection in VS code.

___
5. Once SSH connection to the rpi is made, open the config menu via:

    ```bash
    sudo raspi-config
    ```

6. Open interface options (3)
    - Enable VNC
    - Enable SPI
    - Enable Serial Port
    - Enable Remote GPIO

7. Get a VNC client (easier for signing in to github to get access to repo)
    -   [RealVNC](https://www.realvnc.com/en/connect/download/viewer/) is a good option
        - at top bar enter:
        ```
        [device name].local
        ```
        - then follow steps to see the desktop

8. open a terminal in the vnc and install github CLI:
    ```bash
    sudo apt install gh
    ```

9. __Accessing the Repo:__
    * First set username and password via:
        ```bash
        git config --global user.name "github username"
        git config --global user.email "github email"
        ```

        - To verify they were set correctly:
            ```bash
            git config --global -l
            ```

    1. Make a github account (Make sure you set your username and email in global config)
    2. install _gh_ for github authentication (VNC is a lot easier to use when setting this up on a rpi)
        ```bash
        gh auth login
        ```
    3. Follow steps and log in
    4. Verify with:
        ```bash
        gh auth status
        ```
    5. Cloning with HTTP should work now

10. Update and upgrade the rpi
    ```bash
    sudo apt update
    ```
    ```bash
    sudo apt upgrade
    ```

    - reboot the rpi
        ```bash
        sudo reboot
        ```

___

## __Coding Environment:__
* Update to the latest pip (Package installing program)
    ```bash
    pip install --upgrade pip
    ```

* Install needed python packages:
    ```bash
    pip install numpy cryptography lgpio
    ```

* Installing package for audio
    ```bash
    cd ~
    ```
    ```
    git clone https://github.com/PortAudio/portaudio.git
    ```
    ```
    cd portaudio
    ```
    ```
    ./configure --without-jack
    ```
    ```
    make -j$(nproc)
    ```
    ```
    sudo make install
    ```
    ```
    sudo ldconfig
    ```
    * Run this command to make sure the package was installed:
    ```
    ldconfig -p | grep portaudio
    ```
    * If installed correctly install the package:
    ```
    pip install pyaudio
    ```

    ___

    Very helpful if weird messages showing up when running program:

    [Unknown PCM cards.pcm.XXXX](https://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time)

___

## __Running the Code:__

* While testing or developing, run:
    ```bash
    pip install -e .
    ```
    - This creates a development package on the local device, this is used for package managemnet (ensure all the files can be accessed throughout the code)

* Make sure to export the path if there are any errors about imports not working via:
    ```bash
    export PYTHONPATH="/path/to/repo"
    ```

* Running each program individually should work now.

## __Using Git:__

* Always make edits in a branch, do not work directly on main. To see what branch is active:
    ```bash
    git branch
    ```

* To checkout an active branch with name *branchname*:
    ```bash
    git checkout branchname
    ```

* To create a new working branch:
    ```bash
    git checkout -b nameofbranch
    ```

* After making changes on a branch, save (commit) the changes by:
    ```bash
    git commit -a -m "brief description of what was done"
    ```
    - This saves the changes locally on your computer, to add (push the changes to github)
        ```bash
        git push origin branchname
        ```

* Getting the most up to date code:
    - save changes that were done on your branch via a commit or stash
    - check out main
        ```bash
        git fetch
        ```
        ```bash
        git pull
        ```
    - the most up to date version of main is now what you see

___

## Contributors:
Danielle Awoniyi : danielle1.awoniyi@famu.edu

Amira McKaige : amm21bc@fsu.edu

Amelia Wondracek : amw21i@fsu.edu

Travis Gabauer : tg21b@fsu.edu

Adam Zoiss : aez18@fsu.edu