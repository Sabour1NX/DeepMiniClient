[Setup]
AppName=DeepMiniClient AI对话系统
AppVersion=1.0
DefaultDirName={pf}\DeepMiniClient
DefaultGroupName=DeepMiniClient
OutputDir=.\Output
OutputBaseFilename=DeepMiniClient_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\DeepMiniClient.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "*.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\DeepMiniClient"; Filename: "{app}\DeepMiniClient.exe"
Name: "{commondesktop}\DeepMiniClient"; Filename: "{app}\DeepMiniClient.exe"
