# 📋 Installation & Environment Setup Guide — TLAPITZA v3.7.1

This guide covers the local environment configuration and execution steps for the Python numerical engine of **TLAPITZA v3.7.1** (`tlapitza_suite_industrial_v_3_7_1.py`) on Windows, Linux, and macOS.

---

## 1. System Prerequisites

* **Python:** Version **3.8 or higher** (Python 3.10+ recommended).
* **Git:** Required to clone the official repository.
* **Modern Web Browser:** Chrome, Firefox, Edge, or Safari (required to view the interactive HTML executive report and export native PDFs).

---

## 2. Repository Setup & Virtual Environment

Open your terminal (Command Prompt / PowerShell on Windows, or Terminal on Linux/macOS) and run the following steps:

### Step 1: Clone the Repository
```bash
git clone https://github.com
cd tlapitza
```

### Step 2: Create and Activate a Virtual Environment (Recommended)
Using an isolated virtual environment prevents version conflicts with system-wide Python packages.

* **On Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

* **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(Note: If PowerShell blocks script execution, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first, or use Command Prompt with `venv\Scripts\activate.bat`).*

---

## 3. Installing Dependencies

Install the required scientific and data processing libraries using `pip`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Alternatively, install the core packages directly:
```bash
pip install numpy matplotlib pandas
```

> **Note on PDF Export (`WeasyPrint` / GTK3):**  
> Starting with **v3.7.1**, TLAPITZA generates a self-contained, interactive HTML report with built-in browser print-to-PDF functionality (`window.print()`). **You do not need to install `weasyprint` or GTK3 runtime libraries** to export PDF reports.

---

## 4. Running the Simulation Suite

Once the dependencies are installed and your virtual environment is active, run the main script:

```bash
python tlapitza_suite_industrial_v_3_7_1.py
```

### Expected Console Output
```text
[*] Ejecutando análisis numérico avanzado TLAPITZA V3.7.1...
[+] Bitácora metrológica v3.7.1 exportada a 'generated/bitacora_tlapitza_v3.7.1.csv'.
[+] Reporte interactivo generado en '.../generated/reporte_infraestructura_completo_v3.7.1.html'.
```

---

## 5. Generated Audit Deliverables

Upon completion, the script automatically creates the `./generated/` directory (if not already present) and opens the interactive report in your default browser:

| File | Description |
| :--- | :--- |
| `generated/reporte_infraestructura_completo_v3.7.1.html` | Self-contained engineering audit report featuring 3×2 dynamic response curves, the 3D WGBC parametric surface, SRS shock spectra, and one-click **Save/Export PDF** and **Download CSV** buttons. |
| `generated/bitacora_tlapitza_v3.7.1.csv` | Metrological log containing frequency sweeps (`10 Hz – 10 kHz`), Ross-Kerwin-Ungar (RKU) loss factors, and Mu-Metal/WGBC shielding effectiveness values (dB). |

---

## 6. Troubleshooting

* **`ModuleNotFoundError: No module named 'numpy'` (or `matplotlib` / `pandas`):** Ensure your virtual environment (`venv`) is activated before running `python tlapitza_suite_industrial_v_3_7_1.py`.
* **Report does not open automatically in browser:** Navigate manually to the `./generated/` folder inside your repository directory and double-click `reporte_infraestructura_completo_v3.7.1.html`.
* **Headless Server Execution (Linux without GUI):** The script safely catches browser-launch exceptions (`webbrowser.open`), so it will still generate both the `.html` and `.csv` files in `./generated/` without crashing on headless servers.
