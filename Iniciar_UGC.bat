@echo off
chcp 65001>nul
title Asesor Finanzas UBB - Iniciar (auto-setup)

REM ===== Config =====
set "APP_FILE=app.py"
set "VENV_DIR=venv"
set "REQ_FILE=requirements.txt"
set "PORT_MIN=8501"
set "PORT_MAX=8510"
set "PYTHON_EXE=py -3"                 REM última Python 3 instalada
set "LIB_LOG=libs_instaladas.txt"

REM ===== Verificación =====
if not exist "%APP_FILE%" (
  echo [ERROR] No encuentro %APP_FILE% en esta carpeta.
  pause & exit /b 1
)

REM ===== Crear venv si no existe =====
if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo [SETUP] Creando entorno virtual con la ultima Python 3...
  %PYTHON_EXE% -m venv "%VENV_DIR%" || (
    echo [ERROR] No se pudo crear el entorno virtual.
    pause & exit /b 1
  )
)

REM ===== Activar venv =====
call "%VENV_DIR%\Scripts\activate.bat" || (
  echo [ERROR] No se pudo activar el entorno virtual.
  pause & exit /b 1
)

REM ===== Dependencias =====
python -m pip install --upgrade --quiet pip setuptools wheel
if exist "%REQ_FILE%" (
  echo [DEPS] Instalando dependencias...
  python -m pip install -r "%REQ_FILE%" || (
    echo [ERROR] Fallo instalando dependencias.
    pause & exit /b 1
  )
)

REM ===== Resumen de librerias =====
echo.
echo [INFO] Resumen de librerias instaladas en este entorno:
python -m pip list
for /f %%I in ('python -m pip list ^| find /c /v ""') do set COUNT=%%I
echo.
echo [INFO] Total de librerias instaladas: %COUNT%
echo.

REM ===== Guardar log SIEMPRE (sobrescribe) =====
(
  echo ==========================================================
  echo [Fecha]: %date% %time%
  echo [Python usado]:
  python --version
  echo.
  echo [Librerias instaladas]:
  python -m pip list
  echo.
  echo [Total]: %COUNT% librerias
  echo ==========================================================
) > "%LIB_LOG%"
echo [INFO] Se guardo el listado en %LIB_LOG%

REM ===== Elegir puerto libre =====
set "APP_PORT="
for /l %%P in (%PORT_MIN%,1,%PORT_MAX%) do (
  for /f "tokens=5" %%x in ('netstat -ano ^| findstr "%%P .*LISTENING"') do (set "BUSY=1")
  if not defined BUSY ( set "APP_PORT=%%P" & goto :port_ok )
  set "BUSY="
)
:port_ok
if not defined APP_PORT (
  echo [ERROR] No hay puerto libre entre %PORT_MIN% y %PORT_MAX%.
  pause & exit /b 1
)
echo [PORT] Usare puerto %APP_PORT%

REM ===== Config Streamlit =====
if not exist ".streamlit" mkdir ".streamlit"
> ".streamlit\config.toml" (
  echo [server]
  echo headless = false
  echo port = %APP_PORT%
  echo address = "127.0.0.1"
  echo enableCORS = false
  echo enableXsrfProtection = false
  echo
  echo [browser]
  echo serverAddress = "localhost"
  echo gatherUsageStats = false
)

REM ===== Lanzar =====
start "" "http://localhost:%APP_PORT%"
python -m streamlit run "%APP_FILE%" --server.port %APP_PORT% --server.address 127.0.0.1

echo.
echo [FIN] La aplicacion se ha cerrado.
pause
