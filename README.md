# TLAPITZA © 2026 Andrés Amaury Pérez Chávez. Todos los derechos reservados.
TLAPITZA: Suite Total de Simulación y Endurecimiento de Infraestructura Crítica Protecció Electromagnética, Biomecánica Y Sísmica de Alta Seguridad 

📜 Licencia y Propiedad Intelectual (Modelo Dual) 

Este proyecto opera bajo un esquema de Licencia Dual (Source-Available) propiedad de Andrés Amaury Pérez Chávez

@FreakFTR369 
https://github.com/FreakFTR369

Consulta el archivo [`LICENSE`](./LICENSE) para los términos legales íntegros.

🎓 Uso Académico, Personal y de Investigación (Gratuito): 100% libre de costo. Queda prohibido comercializar o cobrar a terceros bajo esta modalidad.

🤝 Colaboraciones Científicas y Obras Derivadas: Cualquier réplica, modificación o bifurcación del código o la metodología requiere aprobación previa. Envía tu propuesta a tochininmeztik@proton.me con el asunto: "Solicitud de Colaboración".

💼 Uso Comercial y Consultorías Remuneradas: Para integrar TLAPITZA en servicios de consultoría, auditorías pagadas o despliegues corporativos, es obligatorio adquirir una autorización comercial previa. Escribe a tochininmeztik@proton.me con el asunto: "Solicitud comercial".

© 2026 Andrés Amaury Pérez Chávez. Todos los derechos reservados.

# 🛡️ TLAPITZA v3.7.1
**Suite Total de Simulación y Endurecimiento de Infraestructura Crítica**

Desarrollada por Andrés Amaury Pérez Chávez (`@FreakFTR369`), TLAPITZA es una suite numérica de grado industrial diseñada para el análisis, modelado y endurecimiento físico, acústico, electromagnético, sísmico y biomecánico de infraestructuras críticas.

* **Repositorio Oficial:** [://github.com](https://github.com/FreakFTR369/tlapitza)
* **Suite Web Multiplataforma (PC / Android / iOS):** [TLAPITZA Web v3.7.1](https://sites.google.com/view/tlapitza-web-v3-7-1/suite-multiplataforma-pc-android-ios)

---

## 🚀 Novedades en la Versión 3.7.1

* **Esta actualización consolida el núcleo analítico de TLAPITZA incorporando tres módulos avanzados de ingeniería:

* 🔹 𝗙𝗶𝗹𝘁𝗿𝗼 𝗚𝗲𝗼𝗺𝗲́𝘁𝗿𝗶𝗰𝗼 𝗪𝗮𝘃𝗲𝗴𝘂𝗶𝗱𝗲 𝗕𝗲𝘆𝗼𝗻𝗱 𝗖𝘂𝘁𝗼𝗳𝗳 (𝗪𝗚𝗕𝗖): Modela el blindaje electromagnético en rejillas de ventilación tipo panal de abejas (honeycomb) para chasis de Mu-Metal. Calcula la frecuencia de corte física (𝑓꜀) y la atenuación evanescente exponencial, penalizando las fugas por el arreglo de aperturas en paralelo.

* 🔹 𝗔𝗻𝗮́𝗹𝗶𝘀𝗶𝘀 𝗱𝗲 𝗙𝗮𝘁𝗶𝗴𝗮 𝗠𝗲𝗰𝗮́𝗻𝗶𝗰𝗮 𝘆 𝗩𝗶𝗱𝗮 𝗨́𝘁𝗶𝗹 𝗥𝗲𝗺𝗮𝗻𝗲𝗻𝘁𝗲 (𝗥𝗲𝗴𝗹𝗮 𝗱𝗲 𝗣𝗮𝗹𝗺𝗴𝗿𝗲𝗻-𝗠𝗶𝗻𝗲𝗿): Evalúa el daño acumulado (𝐷ₜₒₜₐₗ) en soportes elásticos (silentblocks) sometidos a espectros de vibración continua mediante curvas 𝑆–𝑁. Estima el porcentaje de vida útil restante y los ciclos disponibles antes de la falla estructural.

* 🔹 𝗩𝗶𝘀𝘂𝗮𝗹𝗶𝘇𝗮𝗰𝗶𝗼́𝗻 𝗣𝗮𝗿𝗮𝗺𝗲́𝘁𝗿𝗶𝗰𝗮 𝗧𝗿𝗶𝗱𝗶𝗺𝗲𝗻𝘀𝗶𝗼𝗻𝗮𝗹 (𝟯𝗗): Mapea mediante Axes3D la superficie de respuesta de atenuación geométrica WGBC en función del diámetro de celda (𝑑) y la profundidad del conducto (𝐿).

* 🔹 𝗥𝗲𝘀𝗶𝗹𝗶𝗲𝗻𝗰𝗶𝗮 𝗱𝗲 𝗘𝘅𝗽𝗼𝗿𝘁𝗮𝗰𝗶𝗼́𝗻 (𝗣𝗗𝗙 / 𝗛𝗧𝗠𝗟): Compila reportes ejecutivos en PDF nativo mediante WeasyPrint con respaldo automático a HTML autónomo en caso de ausencia de librerías gráficas del sistema. Filtro Geométrico *Waveguide Beyond Cutoff* (WGBC):** Modela el blindaje electromagnético en rejillas de ventilación tipo panal de abejas para chasis de Mu-Metal.

---

## 📋 Requisitos e Instalación

### 1. Dependencias de Python
Clona el repositorio e instala los paquetes base requeridos:

```bash
git clone https://://github.com.git
cd tlapitza
pip install numpy matplotlib pandas
```

*(Nota: Para compilación directa a PDF con `weasyprint`, instala `weasyprint` y, en Windows, el entorno [GTK3 Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases). En Linux/Debian instala `libpango1.0-dev` y `libcairo2-dev`).*

---

## ▶️ Ejecución

Ejecuta el script principal desde tu terminal o entorno virtual:

```bash
python tlapitza_suite_industrial_v_3_7_1.py
```

### 📦 Entregables Generados
Encontrarás los resultados dentro del directorio `./generated/`:
* `reporte_infraestructura_completo_v3.7.1.html` — Informe corporativo interactivo autocontenido.
* `bitacora_tlapitza_v3.7.1.csv` — Registro metrológico con espectros RKU y efectividad de blindaje.

---

## ⚙️ Arquitectura y Plataformas

* **Núcleo Nativo (Rust + Kotlin):** Paralelismo automático para barridos de frecuencia y espectros de choque, con un peso inferior a 800 KB e integración vía `uniffi` para Jetpack Compose. (PRÓXIMAMENTE)
* **Aplicación Web Multiplataforma:** Ejecución 100% autónoma en navegador a 60 FPS con gráficos 3D interactivos. 

---

## 📚 Documentación Bilingüe y Citación

* **Documentación:** Disponibles en `docs/es/` (Español) y `docs/en/` (English).
* **Citación:** Puedes emplear el botón "Cite this repository" en GitHub o la referencia BibTeX disponible en el repositorio oficial.
* **Licencia Dual (*Source-Available*):** Gratuita para uso académico, personal y de investigación; requiere autorización o licencia comercial para consultorías y despliegues corporativos (contacto: `tochininmeztik@proton.me`).

© 2026 **Andrés Amaury Pérez Chávez** ([@FreakFTR369](https://github.com)). Todos los derechos reservados.

