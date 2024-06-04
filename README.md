## install

``poetry install``

## start

``poetry run start``

## build

``poetry run build``

## clean __pycache__

``poetry run clean``


## dependencies

🌎 global

- chrome

🐧 On Linux/BSD - ▶️ KDE (any display server)
Native support. No additional dependencies are needed.
It seems that all dependencies are listed below are already installed by default in all KDE distributions

The only minimum requirement is ``dbus, ``klipper`` (which is now built-in into KDE), and an ``dbus-python``

🐧 On Linux/BSD - X11
Install ``xsel`` or ``xclip`` package
Example: ``sudo zypper install xsel`` OR ``sudo zypper install xclip``

🐧 On Linux/BSD - Wayland
Install wl-clipboard package
Example: ``sudo zypper install wl-clipboard``