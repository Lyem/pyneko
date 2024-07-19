# Pyneko

Manga downloader for Linux, Windows and MacOS based on [hakuneko](https://github.com/manga-download/hakuneko)

## support
[![](https://dcbadge.limes.pink/api/server/EYm6svnw5b)](https://discord.gg/EYm6svnw5b)

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

The only minimum requirement is ``dbus``, ``klipper`` (which is now built-in into KDE), and an ``dbus-python``

🐧 On Linux/BSD - X11
Install ``xsel`` or ``xclip`` package
Example: ``sudo zypper install xsel`` OR ``sudo zypper install xclip``

🐧 On Linux/BSD - Wayland
Install wl-clipboard package
Example: ``sudo zypper install wl-clipboard``

## Sponsors ❤️

Check out our awesome sponsors!

<a href="https://github.com/Benjigx"><img src="https://github.com/Benjigx.png" width="80px" alt="Benjigx" /></a>&nbsp;&nbsp;