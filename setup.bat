@echo off
call :create_venv
call :create_exec
call :download_models
exit /b

:create_venv
uv sync
exit /b

:create_exec
(
    echo @echo off
    echo start cmd /c ollama serve
    echo uv run src/run.py
) > run.bat 
exit /b

:download_models
start cmd /c ollama serve
start cmd /c ollama pull gemma3:4b
exit /b