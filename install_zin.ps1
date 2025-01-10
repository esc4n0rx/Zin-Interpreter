# Zin Installer Script

function Check-Python {
    $python = Get-Command "python" -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "Python não está instalado. Por favor, instale em: https://www.python.org/downloads/"
        Start-Process "https://www.python.org/downloads/" -Wait
        exit
    } else {
        Write-Host "Python já está instalado."
    }
}


function Check-Git {
    $git = Get-Command "git" -ErrorAction SilentlyContinue
    if (-not $git) {
        Write-Host "Git não está instalado. Por favor, instale em: https://git-scm.com/downloads"
        Start-Process "https://git-scm.com/downloads" -Wait
        exit
    } else {
        Write-Host "Git já está instalado."
    }
}


Check-Python
Check-Git


$installDir = "C:\bin\Zin"
if (-Not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
    Write-Host "Criando diretório de instalação em $installDir"
}

Write-Host "Clonando o repositório do Zin Interpreter..."
git clone https://github.com/esc4n0rx/Zin-Interpreter $installDir


$path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
if ($path -notmatch [regex]::Escape($installDir)) {
    [System.Environment]::SetEnvironmentVariable("Path", "$path;$installDir", "Machine")
    Write-Host "Adicionado $installDir ao PATH do sistema."
}


$batFilePath = Join-Path $installDir "zin.bat"
Set-Content -Path $batFilePath -Value @"
@echo off
set ZIN_DIR=$installDir
if "%1"=="-run" (
    python "%ZIN_DIR%\interpretador.py" %2
) else if "%1"=="-version" (
    echo Zin Interpreter v1.0
) else if "%1"=="-create" (
    echo INICIO PROGAMA %2. > %2
    echo IMPLEMENTACAO PROGAMA %2. >> %2
    echo PRINCIPAL. >> %2
    echo FIM PRINCIPAL. >> %2
    echo EXECUCAO PROGAMA %2. >> %2
    echo EXECUTAR PRINCIPAL. >> %2
    echo FIM PROGAMA %2. >> %2
    echo Arquivo %2 criado com sucesso.
) else (
    echo Comando não reconhecido.
    echo Use: zin -run [arquivo.zin], zin -version ou zin -create [arquivo.zin]
)
"@

Write-Host "Comandos Zin configurados. Use o comando 'zin' para executar."

Write-Host "Instalação concluída. Abra um novo terminal para usar o Zin."
