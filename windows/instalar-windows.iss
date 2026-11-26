; Instalador visual de THC Contabilidad para Windows.
; Las preferencias se escriben en %APPDATA%\THC Contabilidad\config.json.
; La base de datos NO se toca: se crea sola en esa misma carpeta al abrir.

#define MyAppName "THC Contabilidad"
#define MyAppVersion "1.2.1"
#define MyAppPublisher "ThcDev"
#define MyAppExeName "thc-contabilidad.exe"
#define MyAppDiagName "thc-contabilidad-diag.exe"

[Setup]
AppId={{B7E3C7F4-9A2D-4E68-9F1B-6C0D5E8A7B31}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=THC-Contabilidad-{#MyAppVersion}-Windows
SetupIconFile=..\thc-contabilidad.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
ShowLanguageDialog=no
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"
Name: "resetpref"; Description: "Restablecer preferencias iniciales (reemplaza la configuración actual)"; GroupDescription: "Preferencias:"; Flags: unchecked

[Files]
Source: "..\dist\thc-contabilidad\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\thc-contabilidad\{#MyAppDiagName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\thc-contabilidad\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "{#MyAppExeName},{#MyAppDiagName}"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\thc-contabilidad.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\thc-contabilidad.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar THC Contabilidad ahora"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent

[Code]
var
  PaginaPreferencias: TWizardPage;
  CbIdioma: TComboBox;
  CbTema: TComboBox;
  CbTamano: TComboBox;
  CbMoneda: TComboBox;
  CbFormato: TComboBox;
  ChkConfirmar: TCheckBox;

procedure CrearCombo(Parent: TWinControl; Top: Integer; const Titulo: string; var Combo: TComboBox);
var
  Etiqueta: TLabel;
begin
  Etiqueta := TLabel.Create(Parent);
  Etiqueta.Parent := Parent;
  Etiqueta.Caption := Titulo;
  Etiqueta.Left := 20;
  Etiqueta.Top := Top + 3;
  Etiqueta.Width := 170;

  Combo := TComboBox.Create(Parent);
  Combo.Parent := Parent;
  Combo.Left := 200;
  Combo.Top := Top;
  Combo.Width := 320;
  Combo.Style := csDropDownList;
end;

procedure InitializeWizard;
var
  Nota: TLabel;
begin
  PaginaPreferencias := CreateCustomPage(
    wpReady,
    'Preferencias iniciales',
    'THC Contabilidad es gratuito y no pide licencia. Elige cómo quieres verlo; podrás cambiarlo después en Ajustes.'
  );

  CrearCombo(PaginaPreferencias.Surface, 10, 'Idioma de la aplicación:', CbIdioma);
  CbIdioma.Items.Add('Español');
  CbIdioma.Items.Add('English');
  CbIdioma.Items.Add('Deutsch');
  CbIdioma.Items.Add('Русский');
  CbIdioma.Items.Add('中文');
  CbIdioma.Items.Add('日本語');
  CbIdioma.Items.Add('Français');
  CbIdioma.Items.Add('Português');
  CbIdioma.Items.Add('Italiano');
  CbIdioma.Items.Add('한국어');
  CbIdioma.ItemIndex := 0;

  CrearCombo(PaginaPreferencias.Surface, 50, 'Tema:', CbTema);
  CbTema.Items.Add('Oscuro azul pastel');
  CbTema.Items.Add('Claro');
  CbTema.Items.Add('Según el sistema');
  CbTema.ItemIndex := 0;

  CrearCombo(PaginaPreferencias.Surface, 90, 'Tamaño del texto:', CbTamano);
  CbTamano.Items.Add('Pequeño');
  CbTamano.Items.Add('Normal');
  CbTamano.Items.Add('Grande');
  CbTamano.ItemIndex := 1;

  CrearCombo(PaginaPreferencias.Surface, 130, 'Moneda:', CbMoneda);
  CbMoneda.Items.Add('COP - Peso colombiano');
  CbMoneda.Items.Add('USD - Dólar estadounidense');
  CbMoneda.Items.Add('EUR - Euro');
  CbMoneda.Items.Add('GBP - Libra esterlina');
  CbMoneda.Items.Add('MXN - Peso mexicano');
  CbMoneda.Items.Add('ARS - Peso argentino');
  CbMoneda.Items.Add('BRL - Real brasileño');
  CbMoneda.Items.Add('CLP - Peso chileno');
  CbMoneda.Items.Add('PEN - Sol peruano');
  CbMoneda.Items.Add('JPY - Yen japonés');
  CbMoneda.ItemIndex := 0;

  CrearCombo(PaginaPreferencias.Surface, 170, 'Formato de importes:', CbFormato);
  CbFormato.Items.Add('Símbolo (US$ 1.000)');
  CbFormato.Items.Add('Código (USD 1.000)');
  CbFormato.Items.Add('Solo número (1.000)');
  CbFormato.ItemIndex := 0;

  ChkConfirmar := TCheckBox.Create(PaginaPreferencias.Surface);
  ChkConfirmar.Parent := PaginaPreferencias.Surface;
  ChkConfirmar.Caption := 'Pedir confirmación antes de eliminar';
  ChkConfirmar.Left := 20;
  ChkConfirmar.Top := 214;
  ChkConfirmar.Width := 500;
  ChkConfirmar.Checked := True;

  Nota := TLabel.Create(PaginaPreferencias.Surface);
  Nota.Parent := PaginaPreferencias.Surface;
  Nota.Left := 20;
  Nota.Top := 250;
  Nota.Width := 500;
  Nota.Caption := 'Estos valores solo cambian la presentación. No convierten ni alteran los importes guardados.';
end;

function CodigoIdioma(Indice: Integer): string;
begin
  case Indice of
    1: Result := 'en';
    2: Result := 'de';
    3: Result := 'ru';
    4: Result := 'zh';
    5: Result := 'ja';
    6: Result := 'fr';
    7: Result := 'pt';
    8: Result := 'it';
    9: Result := 'ko';
  else
    Result := 'es';
  end;
end;

function CodigoTema(Indice: Integer): string;
begin
  case Indice of
    1: Result := 'claro';
    2: Result := 'sistema';
  else
    Result := 'oscuro';
  end;
end;

function CodigoTamano(Indice: Integer): string;
begin
  case Indice of
    0: Result := 'pequeno';
    2: Result := 'grande';
  else
    Result := 'normal';
  end;
end;

function CodigoMoneda(Indice: Integer): string;
begin
  case Indice of
    1: Result := 'USD';
    2: Result := 'EUR';
    3: Result := 'GBP';
    4: Result := 'MXN';
    5: Result := 'ARS';
    6: Result := 'BRL';
    7: Result := 'CLP';
    8: Result := 'PEN';
    9: Result := 'JPY';
  else
    Result := 'COP';
  end;
end;

function CodigoFormato(Indice: Integer): string;
begin
  case Indice of
    1: Result := 'codigo';
    2: Result := 'plano';
  else
    Result := 'simbolo';
  end;
end;

function TextoBooleano(Valor: Boolean): string;
begin
  if Valor then
    Result := 'true'
  else
    Result := 'false';
end;

function JsonPreferencias: string;
begin
  Result := '{' + #13#10 +
    '  "idioma": "' + CodigoIdioma(CbIdioma.ItemIndex) + '",' + #13#10 +
    '  "tema": "' + CodigoTema(CbTema.ItemIndex) + '",' + #13#10 +
    '  "tamano_texto": "' + CodigoTamano(CbTamano.ItemIndex) + '",' + #13#10 +
    '  "moneda": "' + CodigoMoneda(CbMoneda.ItemIndex) + '",' + #13#10 +
    '  "formato_moneda": "' + CodigoFormato(CbFormato.ItemIndex) + '",' + #13#10 +
    '  "confirmar_eliminar": ' + TextoBooleano(ChkConfirmar.Checked) + #13#10 +
    '}';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Directorio, Archivo: string;
begin
  if CurStep <> ssPostInstall then
    Exit;

  Directorio := ExpandConstant('{userappdata}\THC Contabilidad');
  if not ForceDirectories(Directorio) then
    RaiseException('No se pudo crear la carpeta de datos: ' + Directorio);

  Archivo := AddBackslash(Directorio) + 'config.json';
  if FileExists(Archivo) and (not WizardIsTaskSelected('resetpref')) then
    Exit;

  if not SaveStringToFile(Archivo, JsonPreferencias, False) then
    RaiseException('No se pudo guardar la configuración en: ' + Archivo);
end;
