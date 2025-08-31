# ==========================================
# installer.iss - Script Inno Setup per installer Windows
# ==========================================

"""
Script per creare un installer Windows professionale

Salva questo contenuto in un file chiamato "installer.iss" e compilalo con Inno Setup
"""

INNO_SETUP_SCRIPT = '''
[Setup]
AppName=Game Watch Bot
AppVersion=1.0.0
AppPublisher=Game Watch Team
AppPublisherURL=https://github.com/sporcannalisa-png/game-watch-bot
AppSupportURL=https://github.com/sporcannalisa-png/game-watch-bot/issues
AppUpdatesURL=https://github.com/sporcannalisa-png/game-watch-bot/releases
DefaultDirName={autopf}\\Game Watch Bot
DefaultGroupName=Game Watch Bot
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=GameWatchBot-Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\\Italian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\\GameWatchBot\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\Game Watch Bot"; Filename: "{app}\\GameWatchBot.exe"
Name: "{group}\\{cm:UninstallProgram,Game Watch Bot}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\Game Watch Bot"; Filename: "{app}\\GameWatchBot.exe"; Tasks: desktopicon
Name: "{userappdata}\\Microsoft\\Internet Explorer\\Quick Launch\\Game Watch Bot"; Filename: "{app}\\GameWatchBot.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\\GameWatchBot.exe"; Description: "{cm:LaunchProgram,Game Watch Bot}"; Flags: nowait postinstall skipifsilent
'''

def create_installer_script():
    """Crea il script per l'installer"""
    with open("installer.iss", "w", encoding="utf-8") as f:
        f.write(INNO_SETUP_SCRIPT)
    
    print("📦 Creato script installer.iss")
    print("💡 Compila con Inno Setup per creare l'installer Windows")