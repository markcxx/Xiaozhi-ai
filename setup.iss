; 脚本由 Inno Setup 脚本向导生成。
; 有关创建 Inno Setup 脚本文件的详细信息，请参阅帮助文档！

#define MyAppName "XiaoZhi AI"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "markcxx"
#define MyAppURL "https://github.com/markcxx/Xiaozhi-ai"
#define MyAppExeName "Xiaozhi-ai.exe"
#define MyAppIcon "D:/Users/markchen.DESKTOP-SNGEVAJ/AppData/Local/Temp/icon.ico"

[Setup]
; 注意：AppId 的值唯一标识此应用程序。不要在其他应用程序的安装程序中使用相同的 AppId 值。
; (若要生成新的 GUID，请在 IDE 中单击 "工具|生成 GUID"。)
AppId={{E180F878-89C4-4DB2-95E2-69A748677A30}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
; "ArchitecturesAllowed=x64compatible" 指定安装程序无法运行
; 除 Arm 上的 x64 和 Windows 11 之外的任何平台上。
ArchitecturesAllowed=x64compatible
; "ArchitecturesInstallIn64BitMode=x64compatible" 要求
; 安装可以在 x64 或 Arm 上的 Windows 11 上以"64 位模式"完成，
; 这意味着它应该使用本机 64 位 Program Files 目录和
; 注册表的 64 位视图。
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=D:\Code\xiaozhiAI\LICENSE.txt
; 取消注释以下行以在非管理安装模式下运行 (仅为当前用户安装)。
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=D:\Code\xiaozhiAI\installer
OutputBaseFilename=XiaozhiAI-v1.0.1-Windows-x86_64-Setup
SetupIconFile={#MyAppIcon}
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\PIL\*"; DestDir: "{app}\PIL"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\PyQt5\*"; DestDir: "{app}\PyQt5"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\_sounddevice_data\*"; DestDir: "{app}\_sounddevice_data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\aiohttp\*"; DestDir: "{app}\aiohttp"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\certifi\*"; DestDir: "{app}\certifi"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\charset_normalizer\*"; DestDir: "{app}\charset_normalizer"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\cryptography\*"; DestDir: "{app}\cryptography"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\ctypes\*"; DestDir: "{app}\ctypes"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\frozenlist\*"; DestDir: "{app}\frozenlist"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\libs\*"; DestDir: "{app}\libs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\multidict\*"; DestDir: "{app}\multidict"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\numpy\*"; DestDir: "{app}\numpy"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\numpy.libs\*"; DestDir: "{app}\numpy.libs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\propcache\*"; DestDir: "{app}\propcache"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\psutil\*"; DestDir: "{app}\psutil"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\scipy\*"; DestDir: "{app}\scipy"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\scipy.libs\*"; DestDir: "{app}\scipy.libs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\soxr\*"; DestDir: "{app}\soxr"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\websockets\*"; DestDir: "{app}\websockets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\yarl\*"; DestDir: "{app}\yarl"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\zstandard\*"; DestDir: "{app}\zstandard"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\*.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Code\xiaozhiAI\build\Xiaozhi-ai.dist\*.pyd"; DestDir: "{app}"; Flags: ignoreversion
; 注意：不要在任何共享系统文件上使用 "Flags: ignoreversion" 

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: {#MyAppIcon};
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: {#MyAppIcon}; Tasks: desktopicon;

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent