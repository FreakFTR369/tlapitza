# 🛡️ TLAPITZA v3.7.1
**Total Simulation and Hardening Suite for Critical Infrastructure**

[![Version](https://shields.io)](https://github.com)
[![License](https://shields.io)](https://github.com)
[![Core](https://shields.io)](https://google.com)
[![Español](https://shields.io)](./README.md)

Developed by **Andrés Amaury Pérez Chávez** ([@FreakFTR369](https://github.com)), **TLAPITZA** is an industrial-grade numerical suite for physical, acoustic, electromagnetic, seismic, and biomechanical analysis of critical infrastructure.

* **Official Repository:** [://github.com](https://github.com/tlapitza)
* **Cross-Platform Web Suite:** [TLAPITZA Web v3.7.1](https://google.com)

---

## 🚀 What's New in Version 3.7.1

* **Waveguide Beyond Cutoff (WGBC) Filter:** Models electromagnetic shielding in honeycomb ventilation grilles for Mu-Metal chassis.
* **Mechanical Fatigue Analysis:** Uses the Palmgren-Miner rule to evaluate cumulative fatigue in elastomeric mounts (*silentblocks*).
* **3D Parametric Visualization:** Maps WGBC attenuation across cell diameters and waveguide depths.
* **Self-Contained Reporting:** Generates interactive HTML, PDF, and CSV reports without heavy dependencies.

---

## 📋 Requirements & Installation

Requires **Python 3.8+**. Run the following to install core dependencies:

```bash
git clone https://github.com/tlapitza.git
cd tlapitza
pip install numpy matplotlib pandas
```

---

## ▶️ Execution

Execute the main suite script:

```bash
python tlapitza_suite_industrial_v_3_7_1.py
```

Generated audit files appear in `./generated/` (`reporte_infraestructura_completo_v3.7.1.html` and `bitacora_tlapitza_v3.7.1.csv`).

---

## ⚙️ Architecture & Platforms

* **Native Engine (Rust + Kotlin):** High-speed parallel processing under an 800 KB footprint.
* **Cross-Platform Web App:** 60 FPS browser-based rendering with interactive 3D touch surfaces and live parametric controls.

---

## 📚 Bilingual Documentation & Citation

Documentation is available in `docs/es/` and `docs/en/`. For academic citations, see [`CITATION.cff`](./CITATION.cff) or the repository sidebar.

---

## 📜 Dual License & Intellectual Property

Operated under a Dual License (*Source-Available*) by **Andrés Amaury Pérez Chávez** ([@FreakFTR369](https://github.com)). 
* Free for academic, personal, and non-profit research. 
* Commercial, consulting, or derivative work uses require prior approval via email to **`tochininmeztik@proton.me`**. 

Full legal terms are available in the [`LICENSE`](https://github.com) file.
