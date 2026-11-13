; Inno Setup 6 script: wraps the onedir build into ONE setup .exe (Start menu entry, uninstaller).
; Built by CI after build.bat:   ISCC.exe /DAppVersion=1.1.0 packaging\windows\installer.iss
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6F1C2B7E-3A54-4D8B-9E21-5B8C0D7A4F13}
AppName=Music Downloader
AppVersion={#AppVersion}
AppPublisher=Music Downloader
DefaultDirName={autopf}\Music Downloader
DefaultGroupName=Music Downloader
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=..\..\assets\icon.ico
UninstallDisplayIcon={app}\music-downloader.exe
LicenseFile=..\..\LICENSE
OutputDir=..\..\dist
OutputBaseFilename=music-downloader-v{#AppVersion}-windows-x64-setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "..\..\dist\music-downloader\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\Music Downloader"; Filename: "{app}\music-downloader.exe"
Name: "{autodesktop}\Music Downloader"; Filename: "{app}\music-downloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\music-downloader.exe"; Description: "Launch Music Downloader"; Flags: nowait postinstall skipifsilent
