# Pyneko

Manga downloader for Linux, Windows, and MacOS based on [hakuneko](https://github.com/manga-download/hakuneko). This project incorporates code from the SmartStitch program for its image slicing capabilities, enabling efficient and seamless manga downloads.

<a href="https://github.com/Lyem/pyneko/releases">
    <img src="https://img.shields.io/github/downloads/Lyem/pyneko/total" />
</a>

## Support

[![](https://dcbadge.limes.pink/api/server/EYm6svnw5b)](https://discord.gg/EYm6svnw5b)

## Installation

```bash
poetry install
```

## Start

```bash
poetry run start
```

## Build

```bash
poetry run build
```

## Clean `__pycache__`

```bash
poetry run clean
```

## Create a New Provider

```bash
poetry run new
```

## Dependencies

🌎 **Global**

- Chrome

🐧 **On Linux/BSD**

- **KDE (any display server)**  
  Native support. No additional dependencies are needed.  
  All dependencies listed below are typically installed by default in KDE distributions. The minimum requirements are `dbus`, `klipper` (now built-in in KDE), and `dbus-python`.

- **X11**  
  Install the `xsel` or `xclip` package.  
  Example: 
  ```bash
  sudo zypper install xsel
  ```
  OR
  ```bash
  sudo zypper install xclip
  ```

- **Wayland**  
  Install the `wl-clipboard` package.  
  Example: 
  ```bash
  sudo zypper install wl-clipboard
  ```

## Credits

This project uses code from the [SmartStitch](https://github.com/MechTechnology/SmartStitch) for image slicing.

## Sponsors ❤️

Check out our awesome sponsors!

<a href="https://github.com/Benjigx"><img src="https://github.com/Benjigx.png" width="80px" alt="Benjigx" /></a>&nbsp;&nbsp;

---

Agora você pode copiar e colar esse texto! Se precisar de mais alguma alteração, é só avisar.