; Inno Setup script for The Benefactor
; Builds TheBenefactorSetup.exe from "The Benefactor.exe" + logo.ico.
; Clients are stored in %APPDATA%\The Benefactor, outside the install folder,
; so installing, updating or uninstalling never touches your client data.

#define AppName "The Benefactor"
#define AppVersion "1.10"
#define AppExe "The Benefactor.exe"

[Setup]
AppId={{B3E7F1A2-5C84-4D1E-9A36-7F2D8C0B4E91}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\{#AppExe}
OutputDir=.
OutputBaseFilename=TheBenefactorSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Installs just for you without needing admin rights, unless you pick "all users".
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Lets a newer installer replace the app even if it was left running.
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "{#AppExe}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
