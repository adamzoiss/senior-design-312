# Senior Design Project - Team 312


## Sharepoint link:

__Files & Notes:__ [SharePoint](https://fsu-my.sharepoint.com/personal/amw21i_fsu_edu/_layouts/15/Doc.aspx?sourcedoc={c8d6e6cb-04f5-4a5c-a4a4-ac70581ecfba}&action=edit&wd=target%28Class%20Handouts.one%7C43749e4e-c570-4688-8d40-703e8b013bf2%2FSenior%20Design%20Projects%7C01b6a98f-3880-41ca-834b-d67c770890d6%2F%29&wdorigin=NavigationUrl)

---

# Quick Links for Navigation and Useful Information

1. [RPI Setup](#rpi-setup)

2. [Coding Environment](#coding-environment)

3. [Running the Code](#running-the-code)

4. [Creating a daemon](#creating-a-daemon)

5. [Documenting Python Code](#documenting-python-code)
    
    4.1 - [Class/Function Docs](#code-documentation)
    
    4.2 - [Type Hinting](#type-hinting-guide)

6. [Using Git](#using-git)

7. [Team/Contributors Info](#contributors)
___

[PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/#introduction) - Guideline for how to code in Python

[Python Project/Package Template](https://github.com/pypa/sampleproject) - To better understand the structure of the project, a template for python projects/packages can be viewed as a reference.

[Raspberry Pi pinout information](https://pinout.xyz/) - Useful for setting up buttons, switches, RF chip, etc. via the GPIO pins.

[CC1101 Python Package](https://github.com/fphammerle/python-cc1101) - Package for controlling the CC1101 Transceiver chip.

[Git Information](https://git-scm.com/book/en/v2) - Information on how to use git.

---

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

---

* __How to SSH to rpi:__

    - using powershell or terminal (must be on same network)

        ```bash
        ssh [username]@[device name].local
        ```

* Follow steps to allow connection

* To make life simpler going forward, get the VS code extension *Remote Explorer*
    - Then follow steps to make a SSH connection in VS code.

---

5. Update and upgrade the rpi to install git
    ```bash
    sudo apt update
    sudo apt upgrade
    sudo apt install -y git
    mkdir git
    cd git
    git clone https://github.com/adamzoiss/senior-design-312.git
    cd senior-design-312
    cd setup_utils
    chmod +x setup.sh
    ./setup.sh



---

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

---

## __Coding Environment:__
* Update to the latest `pip` (Package installing program)
    ```bash
    pip install --upgrade pip
    ```

* Install needed python packages:
    ```bash
    pip install numpy cryptography lgpio
    ```

* Installing the sound subsystem:

    ```bash
    sudo apt install pulseaudio
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
    ./configure --enable-shared --with-pulseaudio
    ```
    * Ensure that when building, the pulse audio option is enabled otherwise try:

        ```
        make clean
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

    ---

    Very helpful if weird messages showing up when running program:

    [Unknown PCM cards.pcm.XXXX](https://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time)

---

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
    > For windows (run this in powershell):
    ```powershell
    $env:PYTHONPATH = "C:\path\to\your\modules"
    ```


* Running each program individually should work now.

## __Creating a daemon:__
A daemon is a background process that runs continuously and independently of user interaction. It starts at boot (or when needed) and runs in the background, typically without a graphical interface. Daemons are often used for tasks like logging, networking, and running services (like web servers, audio managers, etc.). In the case of this project, a daemon is used to start the interface manager program on boot, and if it crashes, restarts the program.

* Creating a Systemd Service:
    ```bash
    sudo nano /etc/systemd/system/run-py-program.service
    ```
    > This should be pasted and modified to use the correct python path, program directory, and *pi* username

```
[Unit]
Description=My Python Script Daemon
After=network.target sound.target
Wants=pulseaudio.service


[Service]
ExecStart=/home/pi/git/senior-design-312/.env/bin/python /home/pi/git/senior-design-312/src/managers/interface_manager.py
WorkingDirectory=/home/adamzoiss/git/senior-design-312
Environment="PYTHONPATH=/home/pi/git/senior-design-312"
User=pi
Group=pi
Restart=always
RestartSec=5
StandardOutput=append:/home/pi/git/senior-design-312/logs/system.log
StandardError=append:/home/pi/git/senior-design-312/logs/system.err


[Install]
WantedBy=multi-user.target
```

* Allow Systemd to use pulse audio:

    > By default, PulseAudio does not allow system services to access it. Run:

    ```
    sudo nano /etc/pulse/client.conf
    ```
    * At the end of the file, add:
        ```
        autospawn = yes
        ```
    * Then restart pulseaudio
        ```
        pulseaudio -k
        pulseaudio --start
        ```

* Enabling and staring the daemon:

    > To apply the changes made in the *.service* file:
    ```
    sudo systemctl daemon-reload
    ```
    > To enable:
    ```
    sudo systemctl enable run-py-program.service
    ```
    > To start:
    ```
    sudo systemctl start run-py-program.service
    ```
    > View the status:
    ```
    sudo systemctl status run-py-program.service
    ```

    * More useful commands:
        ```
        sudo systemctl disable run-py-program.service
        sudo systemctl stop run-py-program.service
        sudo systemctl restart run-py-program.service
        ```




## __Documenting Python Code:__

### __Code Documentation__

`numpy` style documentation is being used for this project.

__Example of a NumPy-style docstring:__
```python
import numpy as np

def compute_mean(arr):
    """
    Compute the mean of a NumPy array.

    Parameters
    ----------
    arr : numpy.ndarray
        Input array of numerical values.

    Returns
    -------
    float
        The mean (average) of the input array.

    Raises
    ------
    ValueError
        If the input is not a NumPy array.

    Examples
    --------
    >>> import numpy as np
    >>> arr = np.array([1, 2, 3, 4, 5])
    >>> compute_mean(arr)
    3.0
    """
    if not isinstance(arr, np.ndarray):
        raise ValueError("Input must be a NumPy array.")
    return arr.mean()
```
__Breakdown of the NumPy docstring format:__

* Short summary: The first line briefly describes what the function does.
* Parameters: List of arguments, types, and descriptions.
* Returns: Description of the return value and type.
* Raises: Expected exceptions that may be thrown.
* Examples: Demonstrates usage with `doctest`-style examples.

---

__Class with NumPy-style Docstrings__

This class represents a __Simple Linear Regression__ model.
```python
import numpy as np

class SimpleLinearRegression:
    """
    A simple linear regression model using the least squares method.

    Attributes
    ----------
    coef_ : float
        The slope (coefficient) of the regression line.
    intercept_ : float
        The y-intercept of the regression line.

    Methods
    -------
    fit(X, y)
        Fits the model to the data.
    predict(X)
        Predicts values using the trained model.
    """

    def __init__(self):
        """
        Initializes the SimpleLinearRegression model with no trained parameters.
        """
        self.coef_ = None
        self.intercept_ = None

    def fit(self, X, y):
        """
        Fit the linear regression model to the given dataset.

        Parameters
        ----------
        X : numpy.ndarray
            Feature array of shape (n_samples,).
        y : numpy.ndarray
            Target array of shape (n_samples,).

        Raises
        ------
        ValueError
            If `X` and `y` have different lengths.

        Examples
        --------
        >>> import numpy as np
        >>> X = np.array([1, 2, 3, 4, 5])
        >>> y = np.array([2, 4, 6, 8, 10])
        >>> model = SimpleLinearRegression()
        >>> model.fit(X, y)
        """
        if len(X) != len(y):
            raise ValueError("X and y must have the same length.")

        X_mean = np.mean(X)
        y_mean = np.mean(y)

        num = np.sum((X - X_mean) * (y - y_mean))
        den = np.sum((X - X_mean) ** 2)

        self.coef_ = num / den
        self.intercept_ = y_mean - self.coef_ * X_mean

    def predict(self, X):
        """
        Predict the target values for given input data.

        Parameters
        ----------
        X : numpy.ndarray
            Feature array of shape (n_samples,).

        Returns
        -------
        numpy.ndarray
            Predicted values based on the trained model.

        Raises
        ------
        ValueError
            If the model has not been trained yet.

        Examples
        --------
        >>> import numpy as np
        >>> X = np.array([6, 7, 8])
        >>> model = SimpleLinearRegression()
        >>> model.fit(np.array([1, 2, 3, 4, 5]), np.array([2, 4, 6, 8, 10]))
        >>> model.predict(X)
        array([12., 14., 16.])
        """
        if self.coef_ is None or self.intercept_ is None:
            raise ValueError("Model is not trained. Call `fit` first.")

        return self.coef_ * X + self.intercept_
```

__NumPy Docstrings Benefits__
* Structured and readable: Clearly defines parameters, return values, and exceptions.
* Works with auto-documentation tools like Sphinx.
* Encourages best practices: Makes it easier to maintain and understand code.


---

### __Type Hinting Guide:__

1. Function Arguments & Return Types
    ```python
    def add(x: int, y: int) -> int:
        return x + y
    ```
    `x: int` and `y: int` specify that x and y should be integers.

    `-> int` means the function returns an integer.

2. Variable Annotations
    ```python
    name: str = "Alice"
    age: int = 25
    height: float = 5.9
    is_active: bool = True
    ```

3. Lists, Tuples, and Dictionaries

    Use `list`, `tuple`, and `dict` with generic types:
    ```python
    from typing import List, Tuple, Dict

    numbers: List[int] = [1, 2, 3, 4]
    point: Tuple[float, float] = (3.5, 7.2)
    person: Dict[str, int] = {"age": 30, "score": 95}
    ```
* `List[int]`: A list of integers.
* `Tuple[float, float]`: A tuple with two floats.
* `Dict[str, int]`: A dictionary with string keys and integer values.

4. Optional & Union Types

    __Optional Type (Allows `None`)__
    ```python
    from typing import Optional

    def get_user_name(user_id: int) -> Optional[str]:
        return "Alice" if user_id == 1 else None
    ```
    `Optional[str]` is equivalent to `Union[str, None]`.

    __Union (Multiple Types Allowed)__
    ```python
    from typing import Union

    def parse_value(value: Union[int, str]) -> str:
        return str(value)
    ```
    `Union[int, str]` means `value` can be an __int__ or __str__.

5. Custom Classes as Types
    ```python
    class User:
        def __init__(self, name: str):
            self.name = name

    def greet(user: User) -> str:
        return f"Hello, {user.name}!"
    ```
    The function `greet` expects a `User` instance.

6. Callable (Hinting Functions)
    ```python
    from typing import Callable

    def execute(func: Callable[[int, int], int], x: int, y: int) -> int:
        return func(x, y)

    def multiply(a: int, b: int) -> int:
        return a * b

    result = execute(multiply, 3, 4)  # Returns 12
    ```
    `Callable[[int, int], int]` means a function that:
    * Takes two integeres.
    * Returns an integer.

7. Type Aliases (For Readability)
    ```python
    from typing import List

    Coordinates = List[Tuple[float, float]]  # Type alias

    route: Coordinates = [(10.0, 20.0), (30.5, 40.2)]
    ```
    Now, `Coordinates` can be used instead of `List[Tuple[float, float]]`.

8. Type Variables (For Generic Functions & Classes)

    *This is the same concept in C++ as `template <Typename T>`*
    ```python
    from typing import TypeVar, Generic

    T = TypeVar('T')  # Generic Type

    def repeat(value: T, times: int) -> List[T]:
        return [value] * times

    print(repeat("Hello", 3))  # ['Hello', 'Hello', 'Hello']
    ```
    Here:

    * `T` is a Type Variable that allows any type.
    * `repeat` works with any type, maintaining type safety.

9. TypedDict (For Struct-like Dictionaries)
    ```python
    from typing import TypedDict

    class UserDict(TypedDict):
        name: str
        age: int

    user: UserDict = {"name": "Alice", "age": 30}
    ```
    This ensures `user` has only the specified keys and types.

10. `Self` Type Hinting for Methods

    Introduced in Python 3.11, `Self` hints that a method returns an instance of its class.
    ```python
    from typing import Self

    class Animal:
        def set_name(self, name: str) -> Self:
            self.name = name
            return self  # Returns instance for method chaining

    dog = Animal().set_name("Buddy")
    ```

---

__Static Type Checking with `mypy`__

To enforce type checking, install mypy:

```bash
pip install mypy
```
Then run:

```bash
mypy my_script.py
```
This will flag type errors before runtime.

---

## __Using Git:__

* Always make edits in a `branch`, do not work directly on main. To see what branch is active:
    ```bash
    git branch
    ```

* To `checkout` an active branch with name *branchname*:
    ```bash
    git checkout branchname
    ```

* To create a new working branch:
    ```bash
    git checkout -b nameofbranch
    ```

* After making changes on a branch, save (`commit`) the changes by:
    ```bash
    git commit -a -m "brief description of what was done"
    ```
    - This saves the changes locally on your computer, to add (push the changes to github)
        ```bash
        git push origin branchname
        ```
        - Alternatively, If you want Git to automatically set upstream branches when pushing new local branches, you can enable:
            ```bash
            git config --global push.autoSetupRemote true
            ```
            This way, next time you create a new branch and push, Git will automatically set up the remote tracking branch. The command will now look like:
            ```bash
            git push
            ```
    

* Getting the most up to date code:
    - save changes that were done on your branch via a commit or stash
    - check out `main`
        ```bash
        git fetch
        ```
        ```bash
        git pull
        ```
    - the most up to date version of main is now what you see

---

## Contributors:
Danielle Awoniyi : danielle1.awoniyi@famu.edu

Amira McKaige : amm21bc@fsu.edu

Amelia Wondracek : amw21i@fsu.edu

Travis Gabauer : tg21b@fsu.edu

Adam Zoiss : aez18@fsu.edu