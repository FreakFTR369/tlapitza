#!/bin/bash
# ==============================================================================
# SCRIPT DE INSTALACIÓN Y EJECUCIÓN: SUITE DE SIMULACIÓN V3.5
# Compatible con Linux (Debian/Ubuntu/WSL) y macOS
# ==============================================================================

echo "[*] Actualizando e instalando librerías del sistema para Weasyprint (Cairo/Pango)..."

if [ -f /etc/debian_version ]; then
    # Ubuntu / Debian / WSL
    sudo apt-get update -y
    sudo apt-get install -y python3-pip python3-dev build-essential \
        libweasyprint-dev libpango1.0-dev libcairo2-dev libgdk-pixbuf2.0-dev libffi-dev shared-mime-info
elif [ "$(uname)" == "Darwin" ]; then
    # macOS (Homebrew)
    brew install python cairo pango gdk-pixbuf libffi
fi

echo "[*] Creando entorno virtual de Python (venv)..."
python3 -m venv venv
source venv/bin/activate

echo "[*] Instalando dependencias de Python..."
pip install --upgrade pip
pip install numpy matplotlib pandas weasyprint

echo "[*] Ejecutando la Suite de Simulación V3.5..."
python codigo_Escudo_ELF_ULF_estructuras_v3_5.py

echo "[+] Proceso finalizado exitosamente. Revisa la carpeta ./generated"