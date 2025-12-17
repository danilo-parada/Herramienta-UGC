"""Utilidades para manejo de estado en Streamlit.

Este módulo proporciona funciones auxiliares para:
1. Manejo seguro del session_state
2. Normalización de valores 
3. Sincronización entre widgets y estado interno
"""

import streamlit as st
from typing import Any, TypeVar, Optional

T = TypeVar('T')

def ensure_state_key(key: str, default: Any = None) -> None:
    """Asegura que una clave exista en session_state.
    
    Args:
        key: La clave a verificar
        default: Valor por defecto si no existe
    """
    if key not in st.session_state:
        st.session_state[key] = default

def get_state(key: str, default: T = None) -> T:
    """Obtiene un valor del session_state de forma segura.
    
    Args:
        key: La clave a obtener
        default: Valor por defecto si no existe
        
    Returns:
        El valor almacenado o el default
    """
    return st.session_state.get(key, default)

def set_state(key: str, value: Any) -> None:
    """Establece un valor en session_state.
    
    Args:
        key: La clave a establecer
        value: El valor a guardar
    """
    st.session_state[key] = value

def normalize_string(value: Any) -> str:
    """Normaliza un valor a string.
    
    Args:
        value: El valor a normalizar
        
    Returns:
        String normalizado
    """
    if value is None:
        return ""
    return str(value).strip()

def normalize_bool(value: Any) -> bool:
    """Normaliza un valor a booleano.
    
    Args:
        value: El valor a normalizar
        
    Returns:
        Valor booleano
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {'true', 'verdadero', '1', 'yes', 'si'}
    return bool(value)

def sync_toggle_answer(
    toggle_key: str,
    answer_key: str,
    default: bool = False
) -> None:
    """Sincroniza un toggle con su respuesta textual.
    
    Args:
        toggle_key: Key del widget toggle
        answer_key: Key de la respuesta textual 
        default: Valor por defecto del toggle
    """
    # Asegurar que existe el toggle
    ensure_state_key(toggle_key, default)
    
    # Obtener estado actual
    toggle_value = normalize_bool(get_state(toggle_key))
    
    # Convertir a texto y actualizar
    text_value = "VERDADERO" if toggle_value else "FALSO"
    set_state(answer_key, text_value)

def normalize_evidence(evidence: Optional[str], required: bool = True) -> tuple[bool, str]:
    """Normaliza y valida una evidencia.
    
    Args:
        evidence: Texto de la evidencia
        required: Si se requiere evidencia
        
    Returns:
        Tupla con:
        - bool: Si la evidencia es válida
        - str: Texto normalizado
    """
    clean_text = normalize_string(evidence)
    
    if required and not clean_text:
        return False, ""
        
    return True, clean_text

def sync_answer_evidence(
    answer_key: str,
    evidence_key: str,
    required_when_true: bool = True
) -> tuple[bool, Optional[str]]:
    """Sincroniza una respuesta con su evidencia.
    
    Args:
        answer_key: Key de la respuesta
        evidence_key: Key de la evidencia
        required_when_true: Si se requiere evidencia para VERDADERO
        
    Returns:
        Tupla con:
        - bool: Si es válido
        - str: Mensaje de error si hay
    """
    # NOTE: This function only *validates* the pair (answer, evidence)
    # and returns validation results. It MUST NOT modify
    # `st.session_state` keys because widgets with the same keys may
    # already be instantiated (Streamlit forbids later writes).
    answer = get_state(answer_key)
    evidence = get_state(evidence_key, "")

    if answer == "VERDADERO":
        valid, clean_text = normalize_evidence(
            evidence,
            required=required_when_true
        )
        if not valid and required_when_true:
            return False, "Se requiere evidencia para respuesta VERDADERO"
        # Do not write back into session_state here; caller should read
        # the widget value directly and persist/clean as needed.
        return True, None

    if answer == "FALSO":
        # If answer is FALSO we consider evidence not required. Do not
        # modify session_state here to avoid Streamlit write-after-widget
        # errors; the caller can clean the value when persisting.
        return True, None

    return False, "Respuesta inválida"