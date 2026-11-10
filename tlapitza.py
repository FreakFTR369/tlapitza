# -*- coding: utf-8 -*-
"""
SUITE TOTAL DE SIMULACIÓN Y ENDURECIMIENTO DE INFRAESTRUCTURA CRÍTICA (V3.0)
Módulos: RKU, Coincidencia, Junta, Cavidad, Blindaje Degradado por Ranuras, MDOF Biomecánico y Espectro de Choque (SRS).
Compila reportes automatizados en PDF nativo formateado y bitácoras metrológicas CSV.
"""
import os
import io
import base64
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import weasyprint

# Crear directorio base para salidas de auditoría
os.makedirs('generated', exist_ok=True)

def calcular_resonancia_placa(largo, ancho, thickness, material="concreto", frontera="apoyado"):
    propiedades = {
        "concreto": {"E": 25e9, "rho": 2400, "nu": 0.20},
        "acero":    {"E": 200e9, "rho": 7850, "nu": 0.30},
        "ladrillo": {"E": 14e9,  "rho": 1800, "nu": 0.15},
        "tablaroca":{"E": 3e9,   "rho": 800,  "nu": 0.25}
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
    return np.clip((eta2 * X) / (1 + 2*X + (1 + eta2**2)*(X**2)) + eta1, 0, 0.45)

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

def calcular_impedancia_mumetal_degradado(frecuencias, thickness=0.001, mu_r=80000, sigma=6e6, L_ranura=0.05, n_ranuras=4):
    mu_0 = 4 * np.pi * 1e-7
    mu = mu_r * mu_0
    omega = 2 * np.pi * frecuencias
    c0 = 3e8
    Z_w = 377.0 
    delta = np.sqrt(2 / (omega * mu * sigma))
    Z_s = (1 + 1j) / (sigma * delta)
    
    # Blindaje Intrínseco
    SE_R = 20 * np.log10(np.abs((Z_w + Z_s)**2 / (4 * Z_w * Z_s)))
    SE_A = 20 * np.log10(np.exp(thickness / delta))
    SE_Intrinseco = SE_R + SE_A
    
    # Penalización por Ranuras Acopladas
    wavelength = c0 / frecuencias
    SE_Apertura = 20 * np.log10(wavelength / (2 * L_ranura + 1e-6)) - 10 * np.log10(n_ranuras)
    
    SE_Total = -20 * np.log10(10**(-SE_Intrinseco/20) + 10**(-SE_Apertura/20) + 1e-12)
    return np.clip(SE_Total, 0, 160), delta

def simular_mdof_corporal(t_max=0.5, dt=0.0002, F_mag=5000.0):
    t = np.arange(0, t_max, dt)
    n = len(t)
    m1, c1, k1 = 60.0, 900.0, 45000.0
    m2, c2, k2 = 5.5, 250.0, 12000.0
    
    x1, v1, a1 = np.zeros(n), np.zeros(n), np.zeros(n)
    x2, v2, a2 = np.zeros(n), np.zeros(n), np.zeros(n)
    
    for i in range(n-1):
        F_t = F_mag * np.exp(-20 * t[i]) if t[i] < 0.1 else 0.0
        a1[i] = (F_t - c1*v1[i] - k1*x1[i] + c2*(v2[i]-v1[i]) + k2*(x2[i]-x1[i])) / m1
        a2[i] = (-c2*(v2[i]-v1[i]) - k2*(x2[i]-x1[i])) / m2
        
        v1[i+1] = v1[i] + a1[i] * dt
        x1[i+1] = x1[i] + v1[i+1] * dt
        v2[i+1] = v2[i] + a2[i] * dt
        x2[i+1] = x2[i] + v2[i+1] * dt
        
    a1[-1], a2[-1] = a1[-2], a2[-2]
    return t, a1, a2

def simular_espectro_choque_sismico(A_max_g=2.0, t_max=1.0, dt=0.001):
    f_frecuencias = np.linspace(1, 100, 100)
    t = np.arange(0, t_max, dt)
    ag_t = A_max_g * 9.81 * (1 - t/0.1) * np.exp(-10 * t) * (t < 0.1)
    
    srs_max = np.zeros_like(f_frecuencias)
    zeta = 0.05
    
    for idx, f in enumerate(f_frecuencias):
        omega_n = 2 * np.pi * f
        c = 2 * zeta * omega_n
        k = omega_n**2
        
        x, v = 0.0, 0.0
        max_abs_acc = 0.0
        for i in range(len(t)):
            a_rel = -ag_t[i] - c*v - k*x
            v += a_rel * dt
            x += v * dt
            acc_total = a_rel + ag_t[i]
            if np.abs(acc_total) > max_abs_acc:
                max_abs_acc = np.abs(acc_total)
        srs_max[idx] = max_abs_acc / 9.81
        
    return f_frecuencias, srs_max

def generar_reporte_pdf(img_base64, srs_base64, fc_dry, fc_con):
    """Genera el reporte ejecutivo en PDF usando WeasyPrint."""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Manual de Seguridad Física y Mitigación Estructural</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #2d3748; margin: 25px; line-height: 1.6; }}
            h1 {{ color: #1a365d; text-align: center; border-bottom: 3px solid #3182ce; padding-bottom: 12px; font-size: 22px; margin-bottom: 20px; }}
            h2 {{ color: #2c5282; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-top: 22px; font-size: 16px; }}
            p {{ font-size: 12px; text-align: justify; margin-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 11px; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 7px; text-align: left; }}
            th {{ background-color: #ebf8ff; color: #2c5282; font-weight: bold; }}
            .footer {{ text-align: center; font-size: 9px; color: #718096; margin-top: 35px; border-top: 1px solid #e2e8f0; padding-top: 8px; }}
            .chart-container {{ text-align: center; margin-top: 15px; page-break-inside: avoid; }}
            .chart-img {{ width: 100%; max-width: 720px; height: auto; }}
            .srs-img {{ width: 65%; max-width: 450px; height: auto; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <h1>Manual de Seguridad Física y Mitigación Estructural (V3.0)</h1>
        <h2>1. Resumen de Puntos de Coincidencia Frecuencial</h2>
        <p>Drywall (15mm): <strong>{round(fc_dry, 2)} Hz</strong> | Concreto (120mm): <strong>{round(fc_con, 2)} Hz</strong></p>
        
        <div class="chart-container">
            <h2>2. Suite Gráfica de Simulación Unificada</h2>
            <img class="chart-img" src="data:image/png;base64,{img_base64}" alt="Gráficos Principales">
        </div>

        <div class="chart-container">
            <h2>3. Espectro de Respuesta al Choque (SRS)</h2>
            <img class="srs-img" src="data:image/png;base64,{srs_base64}" alt="Espectro SRS">
        </div>
        
        <div class="footer">
            Generado automáticamente por la Suite de Simulación de Infraestructura Crítica V3.0
        </div>
    </body>
    </html>
    """
    pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
    with open('generated/reporte_infraestructura_critica.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print("[+] Reporte PDF generado exitosamente en 'generated/reporte_infraestructura_critica.pdf'.")

def generar_suite_completa_graficos():
    print("[*] Ejecutando análisis numérico avanzado de tenacidad estructural...")
    frecuencias = np.logspace(1, 4, 1000)
    
    H1_mod, H3_mod, E_dry, rho_dry, nu_dry = 0.015, 0.015, 3.5e9, 850, 0.24
    
    eta_c = calcular_factor_perdida_rku(frecuencias, H1=H1_mod, H3=H3_mod, E1=E_dry)
    f_esp, p_mitigada, _ = calcular_modos_cavidad(absorcion_poroso=0.75, f_espectro=frecuencias)
    _, p_vacia, _ = calcular_modos_cavidad(absorcion_poroso=0.05, f_espectro=frecuencias)
    
    se_degradado, _ = calcular_impedancia_mumetal_degradado(frecuencias, L_ranura=0.08, n_ranuras=4)
    t_mdof, a_torax, a_cabeza = simular_mdof_corporal()
    f_srs, srs_g = simular_espectro_choque_sismico()
    
    # Matriz gráfica unificada 3x2
    fig, axes = plt.subplots(3, 2, figsize=(18, 20))
    
    # 1. Junta Perimetral
    f_junta = np.logspace(0, 3, 500)
    il_junta = simular_junta_perimetral(2.5e6, 0.25, 450, f_junta)
    axes[0, 0].semilogx(f_junta, il_junta, color='#2ca02c', linewidth=2.5)
    axes[0, 0].set_title('1. EFICIENCIA DINÁMICA DE LA JUNTA PERIMETRAL', fontsize=11, fontweight='bold')
    axes[0, 0].set_xlabel('Frecuencia Externa (Hz)'); axes[0, 0].set_ylabel('Pérdida por Inserción (dB)')
    axes[0, 0].grid(True, which="both", ls="--", alpha=0.5)

    # 2. Coincidencia Frecuencial
    fc_dry = calcular_frecuencia_coincidencia(E_dry, rho_dry, nu_dry, H1_mod)
    fc_con = calcular_frecuencia_coincidencia(25e9, 2400, 0.20, 0.120)
    axes[0, 1].axvline(fc_dry, color='red', linestyle='--', linewidth=2, label=f'Drywall 15mm ({round(fc_dry,1)} Hz)')
    axes[0, 1].axvline(fc_con, color='blue', linestyle='-.', linewidth=2, label=f'Concreto 120mm ({round(fc_con,1)} Hz)')
    axes[0, 1].set_title('2. PUNTOS CRÍTICOS DE COINCIDENCIA', fontsize=11, fontweight='bold')
    axes[0, 1].set_xlabel('Frecuencia de la Onda (Hz)'); axes[0, 1].get_yaxis().set_visible(False)
    axes[0, 1].grid(True, ls="--", alpha=0.5); axes[0, 1].legend(loc='upper right')

    # 3. Factor RKU Amortiguado
    axes[1, 0].semilogx(frecuencias, eta_c, color='#8c564b', linewidth=2.5)
    axes[1, 0].set_title('3. FACTOR DE PÉRDIDA AMORTIGUADO HÍBRIDO (RKU)', fontsize=11, fontweight='bold')
    axes[1, 0].set_xlabel('Frecuencia Espectral (Hz)'); axes[1, 0].set_ylabel('Factor de Pérdida Compuesto (eta_c)')
    axes[1, 0].grid(True, which="both", ls="--", alpha=0.5)

    # 4. Modos Cavidad Excitada
    axes[1, 1].plot(f_esp, p_vacia, color='#d62728', linestyle='--', label='Cavidad Vacía')
    axes[1, 1].plot(f_esp, p_mitigada, color='#1f77b4', linewidth=2.5, label='Lana de Roca Optimizada')
    axes[1, 1].set_title('4. RESONANCIA DE MODOS INTERNOS Y MITIGACIÓN', fontsize=11, fontweight='bold')
    axes[1, 1].set_xlabel('Frecuencia Acústica (Hz)'); axes[1, 1].set_ylabel('Nivel de Presión Relativa (dB)')
    axes[1, 1].grid(True, ls="--", alpha=0.5); axes[1, 1].legend(loc='upper right')

    # 5. Impedancia Mu-Metal Degradado
    axes[2, 0].semilogx(frecuencias, se_degradado, color='#e377c2', linewidth=2.5, label='SE Sistema Real (Con Ranuras)')
    axes[2, 0].set_title('5. BLINDAJE ELECTROMAGNÉTICO CON APERTURAS (80mm)', fontsize=11, fontweight='bold')
    axes[2, 0].set_xlabel('Frecuencia (Hz)'); axes[2, 0].set_ylabel('Efectividad de Blindaje Real - SE (dB)')
    axes[2, 0].grid(True, which="both", ls="--", alpha=0.5); axes[2, 0].legend(loc='lower left')

    # 6. MDOF Biomecánico Corporal
    axes[2, 1].plot(t_mdof, a_torax / 9.81, color='#ff7f0e', linewidth=2, label='Tórax (M1)')
    axes[2, 1].plot(t_mdof, a_cabeza / 9.81, color='#17becf', linewidth=2, linestyle=':', label='Cabeza (M2)')
    axes[2, 1].set_title('6. RESPUESTA AL IMPULSO BIOMECÁNICO (2-MDOF)', fontsize=11, fontweight='bold')
    axes[2, 1].set_xlabel('Tiempo (s)'); axes[2, 1].set_ylabel('Aceleración Inducida (g)')
    axes[2, 1].grid(True, ls="--", alpha=0.5); axes[2, 1].legend(loc='upper right')

    plt.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=150)
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close()
    
    # Gráfico independiente para el apéndice técnico: Espectro SRS
    plt.figure(figsize=(6, 4))
    plt.plot(f_srs, srs_g, color='#bcbd22', linewidth=2.5)
    plt.title('ESPECTRO DE RESPUESTA AL CHOQUE SÍSMICO/EXPLOSIVO (SRS)', fontsize=10, fontweight='bold')
    plt.xlabel('Frecuencia Natural de la Estructura (Hz)'); plt.ylabel('Aceleración Máxima de Respuesta (g)')
    plt.grid(True, ls="--", alpha=0.5)
    srs_buf = io.BytesIO()
    plt.savefig(srs_buf, format='png', dpi=150, bbox_inches='tight')
    srs_buf.seek(0)
    srs_base64 = base64.b64encode(srs_buf.read()).decode('utf-8')
    plt.close()
    
    # Volcado metrológico estructurado a CSV
    df_out = pd.DataFrame({
        'Frecuencia_Hz': frecuencias,
        'Factor_Perdida_RKU': eta_c,
        'Blindaje_Real_MuMetal_dB': se_degradado
    })
    df_out.to_csv('generated/bitacora_rku_espectro.csv', index=False)
    print("[+] Bitácora CSV generada en 'generated/bitacora_rku_espectro.csv'.")
    
    # Llamada correcta a la función del PDF (ahora declarada previamente)
    generar_reporte_pdf(img_base64, srs_base64, fc_dry, fc_con)

if __name__ == "__main__":
    generar_suite_completa_graficos()