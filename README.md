# The Benefactor

A small Windows desktop app for working out cut prices per client, with saved
client profiles (VIP / Regular), history, lifetime totals and a progress graph.

## Files

| File | What it is |
|---|---|
| `launder_app.pyw` | The app window (the main program) |
| `launder.py` | Prices, profile saving and the command-line version |
| `make_shortcut.py` | Creates `logo.ico` and a shortcut with the logo icon |
| `build_exe.bat` | Builds `The Benefactor.exe` |
| `TheBenefactor.iss` | Inno Setup script that builds `TheBenefactorSetup.exe` |

## Run it

Needs Python 3 (with tkinter, included in the standard Windows installer).

    python launder_app.pyw

## Build the .exe and installer

1. Run `python make_shortcut.py` once (it creates `logo.ico`).
2. Double-click `build_exe.bat` -> `The Benefactor.exe`.
3. Install [Inno Setup](https://jrsoftware.org/isinfo.php), right-click `TheBenefactor.iss` -> Compile -> `TheBenefactorSetup.exe`.

## Your data

Clients are saved in `%APPDATA%\The Benefactor\profiles.json`, outside the
install folder, so updating or uninstalling never deletes them. Back that file up
before big updates. It is deliberately listed in `.gitignore`.

## Updating

Change the files, bump `APP_VERSION` in `launder_app.pyw` and `AppVersion` in
`TheBenefactor.iss`, then rebuild the .exe and recompile the installer.
Publish `TheBenefactorSetup.exe` as a GitHub Release (not in the repository files).
