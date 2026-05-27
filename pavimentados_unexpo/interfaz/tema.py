# -*- coding: utf-8 -*-
"""
Theme and Custom CSS Stylesheet — Pavimentados UNEXPO.
Defines the official UNEXPO corporate color palette (Royal Blue / Golden Amber)
and premium glassmorphism styling rules for responsive and high-end interactive layouts.
"""

import gradio as gr

# Advanced CSS rules to achieve a premium, futuristic dark mechatronics # Estilos CSS avanzados para lograr una interfaz futurista y premium
CSS_UNEXPO = """
/* Carga de fuente de Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

body, .gradio-container {
    font-family: 'Outfit', sans-serif !important;
    background-color: #070a13 !important; /* Azul oscuro profundo de fondo */
    color: #f1f5f9 !important; /* Gris claro de alto contraste */
}

/* Títulos y textos generales de Gradio con alta legibilidad */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}

p, span, li, label {
    color: #f1f5f9 !important;
}

/* Encabezados y títulos con gradiente */
.header-unexpo h1 {
    background: linear-gradient(135deg, #ffb100 0%, #ff7700 100%) !important; /* Gradiente dorado/ámbar del corazón del logo */
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
    text-align: center;
}

/* Tarjetas con efecto Glassmorphism */
.glass-card {
    background: rgba(13, 19, 38, 0.75) !important; /* Translúcido en base al azul de la UNEXPO */
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(0, 85, 184, 0.25) !important; /* Borde sutil en azul UNEXPO */
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
    margin-bottom: 20px;
}

/* CORRECCIÓN CRÍTICA DE LEGIBILIDAD DE BOTONES Y ETIQUETAS (LABELS) SEGÚN EL LOGO DE LA UNEXPO */

/* 1. ETIQUETAS DE BLOQUE REDONDEADAS (Como 'Subir Archivo de Video Vial', 'Calzada Anotada', etc.) */
.block-label, 
span.block-label, 
.block-label span, 
.block-title, 
.block-title span, 
label.block-label,
div.block-label,
div.block-title,
.label-wrap,
.label-wrap span,
span.label-content,
span.label-val,
div[class*="label-wrap"] span,
div[class*="block-label"] span {
    background-color: #f1f5f9 !important; /* Fondo casi blanco nativo */
    color: #0055b8 !important; /* Letras azul oficial de la UNEXPO */
    border: 1px solid rgba(0, 85, 184, 0.25) !important;
    font-weight: 800 !important;
    font-size: 0.85rem !important;
    opacity: 1 !important;
    display: inline-flex !important;
}

/* Asegurar que las etiquetas de los sliders, checkbox y formularios independientes usen el dorado UNEXPO */
.gr-form label:not(.block-label),
.gr-box label:not(.block-label),
.gr-form span:not(.label-content):not(span.block-label),
.gr-box span:not(.label-content):not(span.block-label) {
    color: #ffb100 !important; /* Dorado UNEXPO para mayor visibilidad en textos y sliders */
    font-weight: 600 !important;
}

/* Forzar que los textos informativos o secundarios no pierdan legibilidad */
.block-info, .block-description, p.block-info, .info-text, span.info {
    color: #cbd5e1 !important; /* Gris plateado claro de alta legibilidad */
    font-size: 0.88rem !important;
    opacity: 0.95 !important;
}

/* 2. BOTONES SECUNDARIOS / CARGADORES (Como los botones dentro de gr.File para subir o arrastrar archivos) */
button:not(.btn-primary), 
button:not(.btn-primary) span, 
.gr-button-secondary, 
.gr-button-secondary span, 
.secondary,
.secondary span,
button.secondary,
button.secondary span,
.btn-secondary,
.btn-secondary span {
    background-color: #f1f5f9 !important; /* Fondo casi blanco nativo */
    color: #0055b8 !important; /* Letras azul oficial de la UNEXPO */
    font-weight: 800 !important;
    font-size: 14px !important;
    border: 1px solid rgba(0, 85, 184, 0.25) !important;
    opacity: 1 !important;
    padding: 10px 20px !important;
    cursor: pointer !important;
}

button:not(.btn-primary):hover, 
button:not(.btn-primary):hover span,
button.secondary:hover,
button.secondary:hover span,
.btn-secondary:hover,
.btn-secondary:hover span {
    background-color: #e2e8f0 !important; /* Gris un poco más oscuro al hover */
    color: #003f8a !important; /* Azul más oscuro al pasar el cursor */
    border-color: #0055b8 !important;
}

/* Textos dentro del formato Markdown (prose) de Gradio */
.prose, .prose p, .prose li, .prose strong, .prose h1, .prose h2, .prose h3 {
    color: #f8fafc !important; /* Blanco hueso de alto contraste */
}

.prose code {
    background-color: rgba(255, 177, 0, 0.12) !important;
    color: #ffb100 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
}

/* Inputs de texto, textareas y dropdowns de Gradio */
input, textarea, select, .gr-box {
    color: #ffffff !important; /* Texto de escritura en blanco total */
    background-color: #0d1326 !important;
    border: 1px solid rgba(0, 85, 184, 0.35) !important;
}

input::placeholder, textarea::placeholder {
    color: #64748b !important; /* Placeholder en gris legible */
}

/* Botones Primary Premium */
.btn-primary,
.btn-primary *,
button.btn-primary,
button.btn-primary span {
    background: linear-gradient(135deg, #0055b8 0%, #003f8a 100%) !important; /* Azul UNEXPO del círculo del logo */
    color: #ffffff !important; /* Texto blanco puro garantizado */
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 15px rgba(0, 85, 184, 0.35) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    padding: 12px 24px !important;
}

.btn-primary:hover,
.btn-primary:hover * {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255, 177, 0, 0.45) !important; /* Resplandor de hover dorado del logo */
    filter: brightness(1.15) !important;
    color: #ffffff !important;
}

.btn-primary:active {
    transform: translateY(1px) !important;
}

/* Personalización de los Tabs de Gradio */
.tabs {
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.tab-nav button {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #94a3b8 !important;
    transition: all 0.3s ease !important;
    padding: 12px 20px !important;
}

.tab-nav button.selected {
    color: #ffb100 !important; /* Pestaña seleccionada en color ámbar */
    border-bottom: 2px solid #ffb100 !important;
}

/* Área de código o traza (fuente Mono) */
.monospaced-trace {
    font-family: 'Fira Code', 'Courier New', monospace !important;
    background-color: #060912 !important;
    color: #a7f3d0 !important;
    border: 1px solid #0055b8 !important;
    border-radius: 8px !important;
    padding: 15px !important;
    line-height: 1.6 !important;
    font-size: 13px !important;
}

/* Tabla DataFrame */
.dataframe-container table {
    background-color: #0d1326 !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.dataframe-container th {
    background-color: rgba(0, 85, 184, 0.25) !important; /* Cabeceras en azul UNEXPO translúcido */
    color: #ffb100 !important; /* Texto en ámbar */
    font-weight: 700 !important;
    padding: 12px !important;
}

.dataframe-container td {
    padding: 10px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
}
"""

def obtener_tema_gradio():
    """Retorna el tema personalizado de Gradio basado en la paleta oscura oficial de la UNEXPO."""
    return gr.themes.Soft(
        primary_hue="blue",        # Azul UNEXPO principal
        secondary_hue="amber",     # Ámbar UNEXPO para destaques
        neutral_hue="slate"
    ).set(
        body_background_fill="#070a13",
        block_background_fill="#0d1326",
        block_label_text_color="#ffb100",
        button_primary_background_fill="#0055b8",
        button_primary_background_fill_hover="#00479e"
    )

