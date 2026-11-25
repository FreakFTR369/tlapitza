# 📋 Guía de Instalación y Configuración de Entorno — TLAPITZA v3.7.1

Esta guía detalla los pasos de configuración del entorno local y ejecución del núcleo numérico en Python de **TLAPITZA v3.7.1** (`tlapitza_suite_industrial_v_3_7_1.py`) en sistemas Windows, Linux y macOS.

---

## 1. Requisitos Previos del Sistema

* **Python:** Versión **3.8 o superior** (se recomienda Python 3.10+).
* **Git:** Necesario para clonar el repositorio oficial.
* **Navegador Web Moderno:** Chrome, Firefox, Edge o Safari (necesario para visualizar el reporte ejecutivo interactivo en HTML y exportar PDFs nativos).

---

## 2. Preparación del Repositorio y Entorno Virtual

Abre tu terminal (Símbolo del sistema / PowerShell en Windows, o Terminal en Linux/macOS) y ejecuta los siguientes pasos:

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com
cd tlapitza
```

### Paso 2: Crear y activar un entorno virtual (Recomendado)
El uso de un entorno virtual aislado evita conflictos de versiones con otros paquetes instalados en el sistema.

* **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

* **En Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(Nota: Si PowerShell bloquea la ejecución de scripts, ejecuta primero `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, o utiliza el Símbolo del sistema con `venv\Scripts\activate.bat`).*

---

## 3. Instalación de Dependencias

Instala las librerías científicas y de procesamiento de datos requeridas mediante `pip`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

De forma alternativa, puedes instalar los paquetes base directamente:
```bash
pip install numpy matplotlib pandas
```

> **Nota sobre Exportación PDF (`WeasyPrint` / GTK3):**  
> A partir de la versión **v3.7.1**, TLAPITZA genera un reporte HTML interactivo autocontenido con función integrada de impresión a PDF desde el navegador (`window.print()`). **No es obligatorio instalar `weasyprint` ni las librerías GTK3** para generar reportes en PDF.

---

## 4. Ejecución de la Suite de Simulación

Una vez instaladas las dependencias y con el entorno virtual activo, ejecuta el script principal:

```bash
python tlapitza_suite_industrial_v_3_7_1.py
```

### Salida esperada en consola
```text
[*] Ejecutando análisis numérico avanzado TLAPITZA V3.7.1...
[+] Bitácora metrológica v3.7.1 exportada a 'generated/bitacora_tlapitza_v3.7.1.csv'.
[+] Reporte interactivo generado en '.../generated/reporte_infraestructura_completo_v3.7.1.html'.
```

---

## 5. Entregables Generados

Al finalizar el cálculo, el script crea automáticamente la carpeta `./generated/` y abre el reporte interactivo en tu navegador predeterminado:

| Archivo | Descripción |
| :--- | :--- |
| `generated/reporte_infraestructura_completo_v3.7.1.html` | Informe ejecutivo de auditoría autocontenido con curvas dinámicas (3×2), superficie paramétrica 3D WGBC, espectro de choque SRS y botones directos para **Guardar / Exportar PDF** y **Descargar CSV**. |
| `generated/bitacora_tlapitza_v3.7.1.csv` | Bitácora metrológica con barridos de frecuencia (`10 Hz – 10 kHz`), factores de pérdida Ross-Kerwin-Ungar (RKU) y efectividad de blindaje Mu-Metal/WGBC (dB). |

---

## 6. Solución de Problemas Frecuentes

* **`ModuleNotFoundError: No module named 'numpy'` (o `matplotlib` / `pandas`):** Verifica que tu entorno virtual (`venv`) esté activado antes de ejecutar `python tlapitza_suite_industrial_v_3_7_1.py`.
* **El reporte no se abre automáticamente en el navegador:** Navega manualmente a la carpeta `./generated/` dentro del directorio del repositorio y haz doble clic sobre `reporte_infraestructura_completo_v3.7.1.html`.
* **Ejecución en servidores sin interfaz gráfica (Headless Linux):** El script captura de forma segura las excepciones al abrir el navegador (`webbrowser.open`), generando igualmente ambos archivos (`.html` y `.csv`) dentro de `./generated/` sin interrumpir la ejecución.
