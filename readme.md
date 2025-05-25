# Portable App Launcher

**Portable App Launcher** is a user-friendly application that allows you to save shortcuts of your frequently used files or scripts and access them conveniently from a single interface.

## Features

- Add and organize shortcuts to files, scripts, and documents
- Assign custom names, descriptions, and icons to each shortcut
- Edit or remove shortcuts as needed
- Launch files and scripts directly from the application
- Simple and intuitive graphical user interface

## Technologies Used

- Python 3
- Tkinter (for the GUI)

## Getting Started

1. **Clone or download this repository.**
2. **Install Python 3** if you haven't already.
3. **Install required dependencies** (Tkinter is included with most Python installations).
4. **Run the application:**
   ```
   python main.py
   ```

## Packaging as an Executable

To create a standalone `.exe` file, use [PyInstaller](https://pyinstaller.org/):

```
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

The executable will be located in the `dist` folder.

## License

This project is open source and available under the [MIT License](LICENSE).