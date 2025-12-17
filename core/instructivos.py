"""
Componentes de instructivos visuales interactivos
Sistema modular de ayuda contextual con CSS atractivo
"""

import streamlit as st
from typing import List, Dict, Optional


def render_mode_selector_guide(current_mode: str = "conectado") -> str:
    """
    Renderiza guía visual para selector de modo con animaciones CSS
    """
    html = f"""
    <style>
    .mode-guide {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }}
    
    .mode-guide::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }}
    
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); opacity: 0.5; }}
        50% {{ transform: scale(1.1); opacity: 0.8; }}
    }}
    
    .mode-guide__title {{
        color: white;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 0 16px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
        z-index: 1;
    }}
    
    .mode-guide__content {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        position: relative;
        z-index: 1;
    }}
    
    .mode-card {{
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 3px solid transparent;
        cursor: pointer;
        position: relative;
    }}
    
    .mode-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        border-color: #667eea;
    }}
    
    .mode-card.active {{
        border-color: #4CAF50;
        background: linear-gradient(135deg, #f5fff6 0%, #e8f5e9 100%);
    }}
    
    .mode-card.active::after {{
        content: '✓ ACTIVO';
        position: absolute;
        top: 12px;
        right: 12px;
        background: #4CAF50;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    
    .mode-card__icon {{
        font-size: 2.5rem;
        margin-bottom: 12px;
        display: block;
    }}
    
    .mode-card__title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: #1a237e;
        margin: 0 0 8px 0;
    }}
    
    .mode-card__desc {{
        font-size: 0.9rem;
        color: #424242;
        line-height: 1.5;
        margin-bottom: 12px;
    }}
    
    .mode-card__features {{
        list-style: none;
        padding: 0;
        margin: 12px 0 0 0;
    }}
    
    .mode-card__features li {{
        padding: 6px 0;
        color: #616161;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .mode-card__features li::before {{
        content: '✓';
        color: #4CAF50;
        font-weight: 700;
        font-size: 1rem;
    }}
    
    @media (max-width: 768px) {{
        .mode-guide__content {{
            grid-template-columns: 1fr;
        }}
    }}
    </style>
    
    <div class="mode-guide">
        <div class="mode-guide__title">
            <span>🔀</span>
            <span>Selecciona tu Modo de Trabajo</span>
        </div>
        <div class="mode-guide__content">
            <div class="mode-card {'active' if current_mode == 'conectado' else ''}">
                <span class="mode-card__icon">🔗</span>
                <h3 class="mode-card__title">Modo Conectado</h3>
                <p class="mode-card__desc">Flujo integrado con validación automática</p>
                <ul class="mode-card__features">
                    <li>Usa datos de Fase 0</li>
                    <li>Solo proyectos priorizados</li>
                    <li>Validación automática</li>
                    <li>Navegación continua</li>
                </ul>
            </div>
            
            <div class="mode-card {'active' if current_mode == 'individual' else ''}">
                <span class="mode-card__icon">🔓</span>
                <h3 class="mode-card__title">Modo Individual</h3>
                <p class="mode-card__desc">Trabajo independiente sin dependencias</p>
                <ul class="mode-card__features">
                    <li>Todos los proyectos</li>
                    <li>Sin depender de ranking</li>
                    <li>Carga archivos directos</li>
                    <li>Máxima flexibilidad</li>
                </ul>
            </div>
        </div>
    </div>
    """
    return html


def render_stepper_guide(steps: List[Dict[str, str]], current_step: int = 0) -> str:
    """
    Renderiza guía paso a paso con diseño moderno
    
    Args:
        steps: Lista de diccionarios con 'icon', 'title', 'description'
        current_step: Índice del paso actual (0-based)
    """
    steps_html = ""
    for i, step in enumerate(steps):
        status_class = "completed" if i < current_step else ("active" if i == current_step else "pending")
        steps_html += f"""
        <div class="step-item {status_class}">
            <div class="step-number">
                <span class="step-icon">{step.get('icon', i+1)}</span>
            </div>
            <div class="step-content">
                <h4 class="step-title">{step.get('title', f'Paso {i+1}')}</h4>
                <p class="step-desc">{step.get('description', '')}</p>
            </div>
            <div class="step-status">
                {'✓' if i < current_step else ('⏵' if i == current_step else '○')}
            </div>
        </div>
        """
    
    html = f"""
    <style>
    .stepper-container {{
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }}
    
    .stepper-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: #1a237e;
        margin: 0 0 24px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    
    .step-item {{
        display: grid;
        grid-template-columns: 60px 1fr 40px;
        gap: 16px;
        padding: 20px;
        margin-bottom: 12px;
        border-radius: 12px;
        transition: all 0.3s ease;
        position: relative;
    }}
    
    .step-item::before {{
        content: '';
        position: absolute;
        left: 30px;
        top: 70px;
        width: 2px;
        height: calc(100% + 12px);
        background: #e0e0e0;
    }}
    
    .step-item:last-child::before {{
        display: none;
    }}
    
    .step-item.completed {{
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
        border-left: 4px solid #4CAF50;
    }}
    
    .step-item.completed::before {{
        background: #4CAF50;
    }}
    
    .step-item.active {{
        background: linear-gradient(135deg, #e3f2fd 0%, #f5f9ff 100%);
        border-left: 4px solid #2196F3;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
    }}
    
    .step-item.active::before {{
        background: #2196F3;
        animation: pulse-line 2s ease-in-out infinite;
    }}
    
    @keyframes pulse-line {{
        0%, 100% {{ opacity: 0.5; }}
        50% {{ opacity: 1; }}
    }}
    
    .step-item.pending {{
        background: #fafafa;
        opacity: 0.7;
    }}
    
    .step-number {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: white;
        font-size: 1.5rem;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        position: relative;
        z-index: 1;
    }}
    
    .step-item.completed .step-number {{
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
    }}
    
    .step-item.active .step-number {{
        background: linear-gradient(135deg, #2196F3 0%, #42A5F5 100%);
        color: white;
        animation: pulse-number 2s ease-in-out infinite;
    }}
    
    @keyframes pulse-number {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.1); }}
    }}
    
    .step-item.pending .step-number {{
        background: #e0e0e0;
        color: #9e9e9e;
    }}
    
    .step-content {{
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    
    .step-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a237e;
        margin: 0 0 6px 0;
    }}
    
    .step-item.pending .step-title {{
        color: #9e9e9e;
    }}
    
    .step-desc {{
        font-size: 0.9rem;
        color: #616161;
        margin: 0;
        line-height: 1.4;
    }}
    
    .step-status {{
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: #4CAF50;
    }}
    
    .step-item.active .step-status {{
        color: #2196F3;
    }}
    
    .step-item.pending .step-status {{
        color: #bdbdbd;
    }}
    </style>
    
    <div class="stepper-container">
        <div class="stepper-title">
            <span>📋</span>
            <span>Guía Paso a Paso</span>
        </div>
        {steps_html}
    </div>
    """
    return html


def render_action_card(title: str, description: str, icon: str, actions: List[Dict[str, str]], color: str = "blue") -> str:
    """
    Renderiza tarjeta de acción con botones interactivos
    
    Args:
        title: Título de la tarjeta
        description: Descripción breve
        icon: Emoji o ícono
        actions: Lista de acciones con 'label', 'type', 'help'
        color: blue, green, purple, orange
    """
    color_schemes = {
        "blue": {"primary": "#2196F3", "light": "#e3f2fd", "dark": "#1976D2"},
        "green": {"primary": "#4CAF50", "light": "#e8f5e9", "dark": "#388E3C"},
        "purple": {"primary": "#9C27B0", "light": "#f3e5f5", "dark": "#7B1FA2"},
        "orange": {"primary": "#FF9800", "light": "#fff3e0", "dark": "#F57C00"},
    }
    
    scheme = color_schemes.get(color, color_schemes["blue"])
    
    actions_html = ""
    for action in actions:
        action_type = action.get('type', 'primary')
        actions_html += f"""
        <div class="action-btn-wrapper">
            <button class="action-btn action-btn-{action_type}">
                {action.get('label', 'Acción')}
            </button>
            {f'<span class="action-help">{action.get("help", "")}</span>' if action.get('help') else ''}
        </div>
        """
    
    html = f"""
    <style>
    .action-card {{
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border-left: 5px solid {scheme['primary']};
        transition: all 0.3s ease;
    }}
    
    .action-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }}
    
    .action-card__header {{
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
    }}
    
    .action-card__icon {{
        font-size: 2.5rem;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: {scheme['light']};
        border-radius: 12px;
    }}
    
    .action-card__text {{
        flex: 1;
    }}
    
    .action-card__title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: #1a237e;
        margin: 0 0 4px 0;
    }}
    
    .action-card__desc {{
        font-size: 0.9rem;
        color: #616161;
        margin: 0;
    }}
    
    .action-card__actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 16px;
    }}
    
    .action-btn-wrapper {{
        display: flex;
        flex-direction: column;
        gap: 4px;
    }}
    
    .action-btn {{
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .action-btn-primary {{
        background: {scheme['primary']};
        color: white;
    }}
    
    .action-btn-primary:hover {{
        background: {scheme['dark']};
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }}
    
    .action-btn-secondary {{
        background: white;
        color: {scheme['primary']};
        border: 2px solid {scheme['primary']};
    }}
    
    .action-btn-secondary:hover {{
        background: {scheme['light']};
        transform: translateY(-2px);
    }}
    
    .action-help {{
        font-size: 0.75rem;
        color: #757575;
        font-style: italic;
    }}
    </style>
    
    <div class="action-card">
        <div class="action-card__header">
            <div class="action-card__icon">{icon}</div>
            <div class="action-card__text">
                <h3 class="action-card__title">{title}</h3>
                <p class="action-card__desc">{description}</p>
            </div>
        </div>
        <div class="action-card__actions">
            {actions_html}
        </div>
    </div>
    """
    return html


def render_flow_diagram(flow_type: str = "conectado") -> str:
    """
    Renderiza diagrama de flujo animado según el tipo
    """
    if flow_type == "conectado":
        html = """
        <style>
        .flow-diagram {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 32px;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
        }
        
        .flow-diagram::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: shimmer 3s infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .flow-title {
            color: white;
            font-size: 1.3rem;
            font-weight: 700;
            text-align: center;
            margin: 0 0 24px 0;
        }
        
        .flow-steps {
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 1;
        }
        
        .flow-step {
            flex: 1;
            text-align: center;
            position: relative;
        }
        
        .flow-step__circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: white;
            margin: 0 auto 12px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            animation: bounce 2s ease-in-out infinite;
        }
        
        .flow-step:nth-child(2) .flow-step__circle {
            animation-delay: 0.2s;
        }
        
        .flow-step:nth-child(3) .flow-step__circle {
            animation-delay: 0.4s;
        }
        
        .flow-step:nth-child(4) .flow-step__circle {
            animation-delay: 0.6s;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .flow-step__label {
            color: white;
            font-size: 0.9rem;
            font-weight: 600;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .flow-arrow {
            position: absolute;
            top: 40px;
            left: 60%;
            width: 80%;
            height: 2px;
            background: white;
            opacity: 0.5;
        }
        
        .flow-arrow::after {
            content: '▶';
            position: absolute;
            right: -10px;
            top: -8px;
            color: white;
            font-size: 1rem;
        }
        
        @media (max-width: 768px) {
            .flow-steps {
                flex-direction: column;
                gap: 20px;
            }
            
            .flow-arrow {
                display: none;
            }
        }
        </style>
        
        <div class="flow-diagram">
            <div class="flow-title">🔗 Flujo Modo Conectado</div>
            <div class="flow-steps">
                <div class="flow-step">
                    <div class="flow-step__circle">📂</div>
                    <div class="flow-step__label">Portafolio</div>
                    <div class="flow-arrow"></div>
                </div>
                <div class="flow-step">
                    <div class="flow-step__circle">📈</div>
                    <div class="flow-step__label">IRL</div>
                    <div class="flow-arrow"></div>
                </div>
                <div class="flow-step">
                    <div class="flow-step__circle">🧭</div>
                    <div class="flow-step__label">EBCT</div>
                    <div class="flow-arrow"></div>
                </div>
                <div class="flow-step">
                    <div class="flow-step__circle">📊</div>
                    <div class="flow-step__label">Indicadores</div>
                </div>
            </div>
        </div>
        """
    else:  # individual
        html = """
        <style>
        .flow-diagram-ind {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 16px;
            padding: 32px;
            margin: 20px 0;
        }
        
        .flow-boxes {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin-top: 20px;
        }
        
        .flow-box {
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .flow-box:hover {
            transform: scale(1.05);
        }
        
        .flow-box__icon {
            font-size: 2.5rem;
            margin-bottom: 8px;
        }
        
        .flow-box__label {
            font-weight: 600;
            color: #1a237e;
        }
        </style>
        
        <div class="flow-diagram-ind">
            <div class="flow-title">🔓 Flujo Modo Individual</div>
            <div class="flow-boxes">
                <div class="flow-box">
                    <div class="flow-box__icon">📥</div>
                    <div class="flow-box__label">Descarga Plantilla</div>
                </div>
                <div class="flow-box">
                    <div class="flow-box__icon">📝</div>
                    <div class="flow-box__label">Completa Offline</div>
                </div>
                <div class="flow-box">
                    <div class="flow-box__icon">📤</div>
                    <div class="flow-box__label">Sube Archivo</div>
                </div>
                <div class="flow-box">
                    <div class="flow-box__icon">🔗</div>
                    <div class="flow-box__label">Consolida Después</div>
                </div>
            </div>
        </div>
        """
    
    return html


def render_tooltip_help(text: str, tooltip: str) -> str:
    """
    Renderiza texto con tooltip interactivo
    """
    html = f"""
    <style>
    .tooltip-wrapper {{
        display: inline-block;
        position: relative;
        cursor: help;
    }}
    
    .tooltip-trigger {{
        color: #2196F3;
        text-decoration: underline;
        text-decoration-style: dotted;
    }}
    
    .tooltip-content {{
        visibility: hidden;
        opacity: 0;
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background: #1a237e;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        width: 250px;
        text-align: center;
        z-index: 1000;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }}
    
    .tooltip-content::after {{
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #1a237e transparent transparent transparent;
    }}
    
    .tooltip-wrapper:hover .tooltip-content {{
        visibility: visible;
        opacity: 1;
        bottom: 135%;
    }}
    </style>
    
    <span class="tooltip-wrapper">
        <span class="tooltip-trigger">{text}</span>
        <span class="tooltip-content">{tooltip}</span>
    </span>
    """
    return html


def render_quick_tips(tips: List[str], color: str = "blue") -> str:
    """
    Renderiza panel de tips rápidos
    """
    color_map = {
        "blue": "#2196F3",
        "green": "#4CAF50",
        "orange": "#FF9800",
        "purple": "#9C27B0"
    }
    
    tips_html = "".join([f"<li class='tip-item'>{tip}</li>" for tip in tips])
    
    html = f"""
    <style>
    .tips-panel {{
        background: linear-gradient(135deg, {color_map.get(color, '#2196F3')}15 0%, {color_map.get(color, '#2196F3')}05 100%);
        border-left: 4px solid {color_map.get(color, '#2196F3')};
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
    }}
    
    .tips-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {color_map.get(color, '#2196F3')};
        margin: 0 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .tips-list {{
        list-style: none;
        padding: 0;
        margin: 0;
    }}
    
    .tip-item {{
        padding: 8px 0;
        color: #424242;
        font-size: 0.9rem;
        display: flex;
        align-items: start;
        gap: 12px;
    }}
    
    .tip-item::before {{
        content: '💡';
        font-size: 1.2rem;
        flex-shrink: 0;
    }}
    </style>
    
    <div class="tips-panel">
        <div class="tips-title">
            <span>⚡</span>
            <span>Tips Rápidos</span>
        </div>
        <ul class="tips-list">
            {tips_html}
        </ul>
    </div>
    """
    return html
