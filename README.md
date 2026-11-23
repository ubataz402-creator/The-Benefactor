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

## Check for updates

The **Check for updates** button (top right of the window) looks at the newest
[GitHub Release](https://github.com/ubataz402-creator/The-Benefactor/releases) of this repository
and offers to open its download page when it is newer than the installed version.

To publish an update so the button finds it:

1. Bump `APP_VERSION` in `launder_app.pyw` and `AppVersion` in `TheBenefactor.iss`.
2. Rebuild the .exe and compile the installer.
3. On GitHub: Releases -> Draft a new release. Use a tag that is higher than the installed
   version (for example `v1.10`), write what changed, attach `TheBenefactorSetup.exe`, and publish.

Until a release exists, the button says "No newer release has been published yet".

## Updating

Change the files, bump `APP_VERSION` in `launder_app.pyw` and `AppVersion` in
`TheBenefactor.iss`, then rebuild the .exe and recompile the installer.
Publish `TheBenefactorSetup.exe` as a GitHub Release (not in the repository files).
