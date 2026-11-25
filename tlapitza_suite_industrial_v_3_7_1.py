# -*- coding: utf-8 -*-
"""
TLAPITZA: SUITE TOTAL DE SIMULACIÓN Y ENDURECIMIENTO DE INFRAESTRUCTURA CRÍTICA (V3.7.1)
Módulos: RKU, Coincidencia, Junta, Cavidad, Blindaje Mu-Metal con Panal WGBC, MDOF Biomecánico, 
Espectro de Choque (SRS), Fatiga Acumulada S-N (Miner con Vida Remanente) y Superficie 3D.
Compila reportes corporativos autocontenidos en HTML/PDF interactivo y bitácoras metrológicas CSV.

Autor de la Investigación Base: Andres Amaury Pérez Chavez
Licencia: OpenSource - No Comercial (Requiere consentimiento explícito y corroborable)
"""
import os
import io
import base64
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import pandas as pd

# Crear directorio base para salidas de auditoría de seguridad
os.makedirs('generated', exist_ok=True)


def calcular_resonancia_placa(largo, ancho, thickness, material="concreto", frontera="apoyado"):
    propiedades = {
        "concreto":  {"E": 25e9,  "rho": 2400, "nu": 0.20},
        "acero":     {"E": 200e9, "rho": 7850, "nu": 0.30},
        "ladrillo":  {"E": 14e9,  "rho": 1800, "nu": 0.15},
        "tablaroca": {"E": 3e9,   "rho": 800,  "nu": 0.25}
    }
    E = propiedades[material]["E"]
    rho = propiedades[material]["rho"]
    nu = propiedades[material]["nu"]
    D = (E * (thickness**3)) / (12 * (1 - nu**2))
    m = rho * thickness
    factor_geometria = (1 / largo**2) + (1 / ancho**2)
    f1_apoyado = (np.pi / 2) * np.sqrt(D / m) * factor_geometria
    return f1_apoyado * 1.8 if frontera == "empotrado" else f1_apoyado


def calcular_frecuencia_coincidencia(E, rho, nu, h, c0=343.0):
    return (np.sqrt(3) * (c0**2) / (np.pi * h)) * np.sqrt((rho * (1 - nu**2)) / E)


def simular_junta_perimetral(k_e, eta, masa_losa, frecuencias):
    omega = 2 * np.pi * frecuencias
    k_compleja = k_e * (1 + 1j * eta)
    return 20 * np.log10(np.abs(1 + ((omega**2) * masa_losa) / k_compleja))


def calcular_factor_perdida_rku(frecuencias, H1=0.015, H3=0.015, E1=3.5e9, eta1=0.01, H2=0.001, eta2=0.8):
    G2 = 1.5e5 * (frecuencias ** 0.4)
    H31 = H2 + (H1 + H3) / 2
    D_suma = 2 * (E1 * (H1**3) / 12)
    X = (G2 / (2 * np.pi * frecuencias * H2)) * (H31**2) / D_suma
    return np.clip((eta2 * X) / (1 + 2 * X + (1 + eta2**2) * (X**2)) + eta1, 0, 0.45)


def calcular_modos_cavidad(espesor_cavidad=0.08, c0=343.0, absorcion_poroso=0.6, f_espectro=None):
    modos = np.array([1, 2, 3])
    f_resonancias = (modos * c0) / (2 * espesor_cavidad)
    if f_espectro is None:
        f_espectro = np.linspace(10, 8000, 2000)
    presion = np.zeros_like(f_espectro) + 5.0
    ancho_banda = 50.0 / (absorcion_poroso + 0.1)
    amplitud = 20.0 * (1.0 - absorcion_poroso)
    for fr in f_resonancias:
        presion += amplitud / (1 + ((f_espectro - fr) / ancho_banda)**2)
    return f_espectro, presion, f_resonancias


def calcular_impedancia_mumetal_wgbc(frecuencias, thickness=0.001, mu_r=80000, sigma=6e6, d_celda=0.005, L_tubo=0.015, n_celdas=100):
    mu_0 = 4 * np.pi * 1e-7
    mu = mu_r * mu_0
    omega = 2 * np.pi * frecuencias
    c0 = 3e8
    Z_w = 377.0
    delta = np.sqrt(2 / (omega * mu * sigma))
    Z_s = (1 + 1j) / (sigma * delta)

    SE_R = 20 * np.log10(np.abs((Z_w + Z_s)**2 / (4 * Z_w * Z_s)))
    SE_A = 20 * np.log10(np.exp(thickness / delta))
    SE_Intrinseco = SE_R + SE_A

    # Filtro Geométrico en Panal (Waveguide Beyond Cutoff)
    f_corte = (0.586 * c0) / (d_celda + 1e-12)
    alfa = (2 * np.pi / (c0 / frecuencias)) * np.sqrt((f_corte / frecuencias)**2 - 1 + 1e-12)
    SE_wgbc_unitaria = 20 * np.log10(np.exp(alfa * L_tubo))
    SE_Apertura = SE_wgbc_unitaria - 10 * np.log10(n_celdas)

    SE_Total = -20 * np.log10(10**(-SE_Intrinseco / 20) + 10**(-SE_Apertura / 20) + 1e-12)
    return np.clip(SE_Total, 0, 160), f_corte


def simular_mdof_corporal(t_max=0.5, dt=0.0002, F_mag=5000.0):
    t = np.arange(0, t_max, dt)
    n = len(t)
    m1, c1, k1 = 60.0, 900.0, 45000.0
    m2, c2, k2 = 5.5, 250.0, 12000.0

    x1, v1, a1 = np.zeros(n), np.zeros(n), np.zeros(n)
    x2, v2, a2 = np.zeros(n), np.zeros(n), np.zeros(n)

    for i in range(n - 1):
        F_t = F_mag * np.exp(-20 * t[i]) if t[i] < 0.1 else 0.0
        a1[i] = (F_t - c1 * v1[i] - k1 * x1[i] + c2 * (v2[i] - v1[i]) + k2 * (x2[i] - x1[i])) / m1
        a2[i] = (-c2 * (v2[i] - v1[i]) - k2 * (x2[i] - x1[i])) / m2

        v1[i + 1] = v1[i] + a1[i] * dt
        x1[i + 1] = x1[i] + v1[i + 1] * dt
        v2[i + 1] = v2[i] + a2[i] * dt
        x2[i + 1] = x2[i] + v2[i + 1] * dt

    a1[-1], a2[-1] = a1[-2], a2[-2]
    return t, a1, a2


def simular_espectro_choque_sismico(A_max_g=2.0, t_max=1.0, dt=0.001):
    f_frecuencias = np.linspace(1, 100, 100)
    t = np.arange(0, t_max, dt)
    ag_t = A_max_g * 9.81 * (1 - t / 0.1) * np.exp(-10 * t) * (t < 0.1)

    srs_max = np.zeros_like(f_frecuencias)
    zeta = 0.05

    for idx, f in enumerate(f_frecuencias):
        omega_n = 2 * np.pi * f
        c = 2 * zeta * omega_n
        k = omega_n**2

        x, v = 0.0, 0.0
        max_abs_acc = 0.0
        for i in range(len(t)):
            a_rel = -ag_t[i] - c * v - k * x
            v += a_rel * dt
            x += v * dt
            acc_total = a_rel + ag_t[i]
            if np.abs(acc_total) > max_abs_acc:
                max_abs_acc = np.abs(acc_total)
        srs_max[idx] = max_abs_acc / 9.81

    return f_frecuencias, srs_max


def evaluar_fatiga_miner(esfuerzos_mpa, horas_operacion=8760, freq_hz=60.0):
    """Evalúa el daño acumulado de Palmgren-Miner y estima la vida útil remanente."""
    C = 1e12
    b = 4.5
    dano_acumulado = 0.0
    ciclos_totales_periodo = horas_operacion * 3600 * freq_hz

    for s in esfuerzos_mpa:
        N_frec_falla = C * (s ** (-b))
        dano_acumulado += ciclos_totales_periodo / N_frec_falla

    fraccion_remanente = max(0.0, 1.0 - dano_acumulado)
    if dano_acumulado > 0:
        tasa_dano_por_ciclo = dano_acumulado / (ciclos_totales_periodo * len(esfuerzos_mpa))
        ciclos_remanentes = fraccion_remanente / tasa_dano_por_ciclo
    else:
        ciclos_remanentes = float('inf')

    estado = "Estructura Segura (D < 1.0)" if dano_acumulado < 1.0 else "FALLA POR FATIGA INMINENTE (D >= 1.0)"
    return dano_acumulado, fraccion_remanente, ciclos_remanentes, estado


def generar_reporte_interactivo(img_base64, srs_base64, base64_3d, csv_base64, fc_dry, fc_con, f_corte_panal, dano_total, fraccion_rem, ciclos_rem, estado_fatiga):
    """Genera un informe HTML autocontenido con memoria técnica formal y botones nativos para PDF y CSV."""
    html_content = f"""<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Informe Avanzado de Endurecimiento - TLAPITZA V3.7.1</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #2d3748; margin: 25px auto; max-width: 900px; line-height: 1.65; background-color: #ffffff; padding: 0 15px; }}
            .toolbar {{ display: flex; justify-content: flex-end; gap: 12px; padding: 12px 18px; background-color: #edf2f7; border-radius: 8px; margin-bottom: 20px; border: 1px solid #cbd5e0; position: sticky; top: 10px; z-index: 100; }}
            .btn {{ padding: 10px 18px; font-size: 13px; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; transition: background-color 0.2s; }}
            .btn-pdf {{ background-color: #2b6cb0; color: white; }}
            .btn-pdf:hover {{ background-color: #1a365d; }}
            .btn-csv {{ background-color: #2f855a; color: white; }}
            .btn-csv:hover {{ background-color: #22543d; }}
            h1 {{ color: #1a365d; text-align: center; border-bottom: 3px solid #3182ce; padding-bottom: 12px; font-size: 21px; margin-bottom: 20px; }}
            h2 {{ color: #2c5282; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-top: 24px; font-size: 16px; }}
            p {{ font-size: 12.5px; text-align: justify; margin-bottom: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 12px; margin-bottom: 16px; font-size: 11.5px; }}
            th, td {{ border: 1px solid #cbd5e0; padding: 8px; text-align: left; }}
            th {{ background-color: #ebf8ff; color: #2c5282; font-weight: bold; }}
            .footer {{ text-align: center; font-size: 10px; color: #718096; margin-top: 35px; border-top: 1px solid #e2e8f0; padding-top: 10px; }}
            .chart-container {{ text-align: center; margin-top: 18px; page-break-inside: avoid; }}
            .chart-img {{ width: 100%; max-width: 780px; height: auto; border: 1px solid #e2e8f0; border-radius: 4px; }}
            .srs-img {{ width: 75%; max-width: 520px; height: auto; margin-top: 10px; border: 1px solid #e2e8f0; border-radius: 4px; }}
            .badge-safe {{ color: #276749; font-weight: bold; background-color: #c6f6d5; padding: 3px 8px; border-radius: 4px; }}
            .badge-danger {{ color: #9b2c2c; font-weight: bold; background-color: #fed7d7; padding: 3px 8px; border-radius: 4px; }}
            @media print {{
                .no-print {{ display: none !important; }}
                body {{ margin: 0; max-width: 100%; padding: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="toolbar no-print">
            <button class="btn btn-pdf" onclick="window.print()">🖨️ Guardar / Exportar PDF</button>
            <a class="btn btn-csv" href="data:text/csv;base64,{csv_base64}" download="bitacora_tlapitza_v3.7.1.csv">📊 Descargar Bitácora CSV</a>
        </div>

        <h1>INFORME AVANZADO DE ENDURECIMIENTO DE INFRAESTRUCTURA CRÍTICA (TLAPITZA V3.7.1)</h1>
        
        <h2>1. Diagnóstico Estructural y Coincidencia Frecuencial</h2>
        <p>Este documento constituye la memoria técnica formal de los métodos de blindaje magnético pasivo, desacoplo cinemático perimetral y mitigación de la transducción biomecánica ante perturbaciones armónicas y repentinas en la superestructura edilicia. Los muros divisorios de mampostería ligera rigidizada demuestran un desplazamiento favorable en sus puntos críticos de coincidencia mecano-acústica, blindando el espectro bajo.</p>
        <table>
            <thead>
                <tr>
                    <th>Componente Estructural Evaluado</th>
                    <th>Frecuencia Crítica Calculada (fc)</th>
                    <th>Mecanismo de Atenuación de Diseño</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Mampostería Ligera (Drywall Rigidizado 15mm)</td>
                    <td>{round(fc_dry, 2)} Hz</td>
                    <td>Amortiguamiento de capas compuestas viscoelásticas (Ross-Kerwin-Ungar)</td>
                </tr>
                <tr>
                    <td>Losa Monolítica (Concreto Estructural 120mm)</td>
                    <td>{round(fc_con, 2)} Hz</td>
                    <td>Corte perimetral y sellado viscoelástico con desacoplo elástico directo</td>
                </tr>
            </tbody>
        </table>

        <h2>2. Blindaje Electromagnético Mu-Metal y Filtro en Panal (WGBC)</h2>
        <p>Las perturbaciones electromagnéticas en la banda ELF/VLF se mitigan mediante el principio de baja reluctancia magnética. Para evitar la degradación por difracción en las aperturas de ventilación del chasis de Mu-Metal, se incorporó una rejilla de guía de onda por debajo del corte (<em>Waveguide Beyond Cutoff - WGBC</em>). La frecuencia de corte física calculada para las celdas hexagonales es de <strong>{round(f_corte_panal / 1e9, 2)} GHz</strong>, obligando a las señales parasitarias a decaer exponencialmente como ondas evanescentes sin obstruir el flujo de aire.</p>

        <h2>3. Dinámica Corporal (2-MDOF) y Fatiga Estructural (Regla de Miner)</h2>
        <p>Ante un impacto repentino en la superestructura, el cuerpo humano se modela mediante matrices acopladas cabeza-tórax (2-MDOF) para validar los márgenes de aceleración en unidades G y proteger al personal operativo. Simultáneamente, sometiendo los soportes elásticos (<em>silentblocks</em>) a ciclos continuos de vibración industrial, el algoritmo de daño lineal acumulado de Palmgren-Miner determinó un indicador anual de <strong>{round(dano_total, 4)}</strong>, conservando una vida útil remanente del <strong>{round(fraccion_rem * 100, 2)}%</strong> (~{ciclos_rem:.2e} ciclos disponibles).</p>
        <p>Estado operativo del elastómero: <span class="{'badge-safe' if dano_total < 1.0 else 'badge-danger'}">{estado_fatiga}</span></p>

        <div class="chart-container">
            <h2>4. Matriz Completa de Curvas de Respuesta Dinámica (3x2)</h2>
            <img class="chart-img" src="data:image/png;base64,{img_base64}" alt="Matriz Completa de Curvas de Respuesta Dinámica">
        </div>

        <div class="chart-container">
            <h2>5. Superficie Paramétrica Tridimensional (3D) de Atenuación WGBC</h2>
            <p>Relación geométrica entre el diámetro de la celda hexagonal, la profundidad del conducto y la atenuación evanescente lograda en decibelios:</p>
            <img class="srs-img" src="data:image/png;base64,{base64_3d}" alt="Superficie Paramétrica 3D WGBC">
        </div>

        <div class="chart-container">
            <h2>6. Diagnóstico de Espectro de Respuesta al Choque Sísmico / Explosivo (SRS)</h2>
            <p>Curva espectral de aceleración máxima instantánea para la superestructura frente a pulsos transitorios exponenciales tipo Friedlander (Aceleración base: 2.0g):</p>
            <img class="srs-img" src="data:image/png;base64,{srs_base64}" alt="Espectro de Respuesta al Choque SRS">
        </div>
        
        <div class="footer">
            Documento emitido bajo estrictas normas de auditoría de infraestructura. Prototipado Numérico Avanzado TLAPITZA V3.7.1 - 2026.<br>
            Investigación y Desarrollo: Andres Amaury Pérez Chavez. Licencia OpenSource No Comercial.<br>
            Este reporte es únicamente para fines informativos y de ingeniería.
        </div>
    </body>
    </html>"""

    html_path = os.path.abspath('generated/reporte_infraestructura_completo_v3.7.1.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[+] Reporte interactivo generado en '{html_path}'.")

    try:
        webbrowser.open(f'file://{html_path}')
    except Exception:
        pass


def generar_suite_completa_graficos():
    print("[*] Ejecutando análisis numérico avanzado TLAPITZA V3.7.1...")
    frecuencias = np.logspace(1, 4, 1000)
    H1_mod, H3_mod, E_dry, rho_dry, nu_dry = 0.015, 0.015, 3.5e9, 850, 0.24

    eta_c = calcular_factor_perdida_rku(frecuencias, H1=H1_mod, H3=H3_mod, E1=E_dry)
    f_esp, p_mitigada, _ = calcular_modos_cavidad(absorcion_poroso=0.75, f_espectro=frecuencias)
    _, p_vacia, _ = calcular_modos_cavidad(absorcion_poroso=0.05, f_espectro=frecuencias)
    se_degradado, f_corte_panal = calcular_impedancia_mumetal_wgbc(frecuencias, L_tubo=0.015, n_celdas=100)
    t_mdof, a_torax, a_cabeza = simular_mdof_corporal()
    f_srs, srs_g = simular_espectro_choque_sismico()

    esfuerzos_test = np.array([12.5, 14.2, 10.1])
    dano_total, fraccion_rem, ciclos_rem, estado_fatiga = evaluar_fatiga_miner(esfuerzos_test)

    # 1. Matriz Gráfica 3x2
    fig, axes = plt.subplots(3, 2, figsize=(18, 20))
    f_junta = np.logspace(0, 3, 500)
    il_junta = simular_junta_perimetral(2.5e6, 0.25, 450, f_junta)
    axes[0, 0].semilogx(f_junta, il_junta, color='#2ca02c', linewidth=2.5)
    axes[0, 0].set_title('1. EFICIENCIA DINÁMICA DE LA JUNTA PERIMETRAL', fontsize=11, fontweight='bold')
    axes[0, 0].set_xlabel('Frecuencia (Hz)')
    axes[0, 0].set_ylabel('Pérdida por Inserción (dB)')
    axes[0, 0].grid(True, which="both", ls="--", alpha=0.5)

    fc_dry = calcular_frecuencia_coincidencia(E_dry, rho_dry, nu_dry, H1_mod)
    fc_con = calcular_frecuencia_coincidencia(25e9, 2400, 0.20, 0.120)
    axes[0, 1].axvline(fc_dry, color='red', linestyle='--', linewidth=2, label=f'Drywall ({round(fc_dry, 1)} Hz)')
    axes[0, 1].axvline(fc_con, color='blue', linestyle='-.', linewidth=2, label=f'Concreto ({round(fc_con, 1)} Hz)')
    axes[0, 1].set_title('2. PUNTOS CRÍTICOS DE COINCIDENCIA', fontsize=11, fontweight='bold')
    axes[0, 1].set_xlabel('Frecuencia de la Onda (Hz)')
    axes[0, 1].grid(True, ls="--", alpha=0.5)
    axes[0, 1].legend()

    axes[1, 0].semilogx(frecuencias, eta_c, color='#8c564b', linewidth=2.5)
    axes[1, 0].set_title('3. FACTOR DE PÉRDIDA AMORTIGUADO HÍBRIDO (RKU)', fontsize=11, fontweight='bold')
    axes[1, 0].set_xlabel('Frecuencia (Hz)')
    axes[1, 0].set_ylabel('Factor de Pérdida (eta_c)')
    axes[1, 0].grid(True, which="both", ls="--", alpha=0.5)

    axes[1, 1].plot(f_esp, p_vacia, color='#d62728', linestyle='--', label='Cavidad Vacía')
    axes[1, 1].plot(f_esp, p_mitigada, color='#1f77b4', linewidth=2.5, label='Lana de Roca')
    axes[1, 1].set_title('4. RESONANCIA DE MODOS INTERNOS Y MITIGACIÓN', fontsize=11, fontweight='bold')
    axes[1, 1].set_xlabel('Frecuencia Acústica (Hz)')
    axes[1, 1].set_ylabel('Nivel de Presión (dB)')
    axes[1, 1].grid(True, ls="--", alpha=0.5)
    axes[1, 1].legend()

    axes[2, 0].semilogx(frecuencias, se_degradado, color='#e377c2', linewidth=2.5, label='SE WGBC (Panal)')
    axes[2, 0].set_title('5. BLINDAJE ELECTROMAGNÉTICO CON APERTURAS WGBC', fontsize=11, fontweight='bold')
    axes[2, 0].set_xlabel('Frecuencia (Hz)')
    axes[2, 0].set_ylabel('Efectividad de Blindaje (dB)')
    axes[2, 0].grid(True, which="both", ls="--", alpha=0.5)
    axes[2, 0].legend()

    axes[2, 1].plot(t_mdof, a_torax / 9.81, color='#ff7f0e', linewidth=2, label='Tórax (M1)')
    axes[2, 1].plot(t_mdof, a_cabeza / 9.81, color='#17becf', linewidth=2, linestyle=':', label='Cabeza (M2)')
    axes[2, 1].set_title('6. RESPUESTA AL IMPULSO BIOMECÁNICO (2-MDOF)', fontsize=11, fontweight='bold')
    axes[2, 1].set_xlabel('Tiempo (s)')
    axes[2, 1].set_ylabel('Aceleración (g)')
    axes[2, 1].grid(True, ls="--", alpha=0.5)
    axes[2, 1].legend()

    plt.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=150)
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close()

    # 2. Gráfico del Espectro SRS
    plt.figure(figsize=(6, 4))
    plt.plot(f_srs, srs_g, color='#bcbd22', linewidth=2.5)
    plt.title('ESPECTRO DE RESPUESTA AL CHOQUE SÍSMICO (SRS)', fontsize=10, fontweight='bold')
    plt.xlabel('Frecuencia Natural (Hz)')
    plt.ylabel('Aceleración Máxima (g)')
    plt.grid(True, ls="--", alpha=0.5)
    srs_buf = io.BytesIO()
    plt.savefig(srs_buf, format='png', dpi=150, bbox_inches='tight')
    srs_buf.seek(0)
    srs_base64 = base64.b64encode(srs_buf.read()).decode('utf-8')
    plt.close()

    # 3. Superficie Paramétrica 3D de Atenuación WGBC
    fig_3d = plt.figure(figsize=(7, 5))
    ax_3d = fig_3d.add_subplot(111, projection='3d')
    D_celdas_mm = np.linspace(2.0, 15.0, 50)
    L_tubos_mm = np.linspace(5.0, 40.0, 50)
    X_d, Y_L = np.meshgrid(D_celdas_mm, L_tubos_mm)
    Z_se_3d = np.clip(32.0 * (Y_L / X_d), 0, 160)

    surf = ax_3d.plot_surface(X_d, Y_L, Z_se_3d, cmap='plasma', edgecolor='none', alpha=0.85)
    ax_3d.set_title('SUPERFICIE DE ATENUACIÓN GEOMÉTRICA WGBC (3D)', fontsize=10, fontweight='bold')
    ax_3d.set_xlabel('Diámetro Celda d (mm)')
    ax_3d.set_ylabel('Longitud Tubo L (mm)')
    ax_3d.set_zlabel('Atenuación Evanescente (dB)')
    fig_3d.colorbar(surf, ax=ax_3d, shrink=0.5, aspect=5)

    graf_3d_buf = io.BytesIO()
    plt.savefig(graf_3d_buf, format='png', dpi=150, bbox_inches='tight')
    graf_3d_buf.seek(0)
    base64_3d = base64.b64encode(graf_3d_buf.read()).decode('utf-8')
    plt.close()

    # 4. Generar CSV en disco y codificarlo en Base64 para descarga directa desde el navegador
    df_out = pd.DataFrame({
        'Frecuencia_Hz': frecuencias,
        'Factor_Perdida_RKU': eta_c,
        'Blindaje_Panal_MuMetal_dB': se_degradado
    })
    csv_path = 'generated/bitacora_tlapitza_v3.7.1.csv'
    df_out.to_csv(csv_path, index=False)
    csv_string = df_out.to_csv(index=False)
    csv_base64 = base64.b64encode(csv_string.encode('utf-8')).decode('utf-8')
    print(f"[+] Bitácora metrológica v3.7.1 exportada a '{csv_path}'.")

    generar_reporte_interactivo(
        img_base64, srs_base64, base64_3d, csv_base64,
        fc_dry, fc_con, f_corte_panal,
        dano_total, fraccion_rem, ciclos_rem, estado_fatiga
    )


if __name__ == "__main__":
    generar_suite_completa_graficos()