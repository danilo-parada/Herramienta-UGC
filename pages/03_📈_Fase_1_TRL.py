import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pathlib import Path
from html import escape

from core import db, utils, trl
from core.db_trl import save_trl_result, get_trl_history
from core.theme import load_theme

IRL_DIMENSIONS = [
    ("CRL", 0),
    ("BRL", 0),
    ("TRL", 4),
    ("IPRL", 5),
    ("TmRL", 6),
    ("FRL", 5),
]

CRL_LEVELS = [
    {
        "nivel": 1,
        "descripcion": "Hipótesis especulativa sobre una posible necesidad en el mercado.",
        "preguntas": [
            "¿Tiene alguna hipótesis sobre un problema o necesidad que podría existir en el mercado?",
            "¿Ha identificado quiénes podrían ser sus posibles clientes, aunque sea de manera especulativa?",
        ],
    },
    {
        "nivel": 2,
        "descripcion": "Familiarización inicial con el mercado y necesidades más específicas detectadas.",
        "preguntas": [
            "¿Ha realizado alguna investigación secundaria o revisión de mercado para entender problemas del cliente?",
            "¿Tiene una descripción más clara y específica de las necesidades o problemas detectados?",
        ],
    },
    {
        "nivel": 3,
        "descripcion": "Primer feedback de mercado y validación preliminar de necesidades.",
        "preguntas": [
            "¿Ha iniciado contactos directos con posibles usuarios o expertos del mercado para obtener retroalimentación?",
            "¿Ha comenzado a desarrollar una hipótesis más clara sobre los segmentos de clientes y sus problemas?",
        ],
    },
    {
        "nivel": 4,
        "descripcion": "Confirmación del problema con varios usuarios y segmentación inicial.",
        "preguntas": [
            "¿Ha confirmado el problema o necesidad con varios clientes o usuarios reales?",
            "¿Ha definido una hipótesis de producto basada en el feedback recibido de los usuarios?",
            "¿Tiene segmentación inicial de clientes en función del problema identificado?",
        ],
    },
    {
        "nivel": 5,
        "descripcion": "Interés establecido por parte de usuarios y comprensión más profunda del mercado.",
        "preguntas": [
            "¿Cuenta con evidencia de interés concreto por parte de clientes o usuarios hacia su solución?",
            "¿Ha establecido relaciones con potenciales clientes o aliados que retroalimentan su propuesta de valor?",
        ],
    },
    {
        "nivel": 6,
        "descripcion": "Beneficios de la solución confirmados a través de pruebas o asociaciones iniciales.",
        "preguntas": [
            "¿Ha realizado pruebas del producto o solución con clientes que validen sus beneficios?",
            "¿Ha iniciado procesos de venta o pilotos con clientes reales o aliados estratégicos?",
        ],
    },
    {
        "nivel": 7,
        "descripcion": "Clientes involucrados en pruebas extendidas o primeras ventas/test comerciales.",
        "preguntas": [
            "¿Tiene acuerdos o primeras ventas del producto (aunque sea versión de prueba)?",
            "¿Los clientes han participado activamente en validaciones o pruebas extendidas del producto?",
        ],
    },
    {
        "nivel": 8,
        "descripcion": "Ventas iniciales y preparación para ventas estructuradas y escalables.",
        "preguntas": [
            "¿Ha vendido sus primeros productos y validado la disposición de pago de un porcentaje relevante de clientes?",
            "¿Cuenta con una organización comercial mínima (CRM, procesos de venta, canales definidos)?",
        ],
    },
    {
        "nivel": 9,
        "descripcion": "Adopción consolidada y ventas repetibles a múltiples clientes reales.",
        "preguntas": [
            "¿Está realizando ventas escalables y repetibles con múltiples clientes?",
            "¿Su empresa está enfocada en ejecutar un proceso de crecimiento comercial con foco en la demanda de clientes?",
        ],
    },
]

FRL_LEVELS = [
    {
        "nivel": 1,
        "descripcion": "Idea de negocios inicial con una descripción vaga. No hay una visión clara sobre las necesidades y las opciones de financiamiento.",
        "preguntas": [
            "¿Tiene una idea de negocio inicial con una descripción?",
            "¿Tiene poco o ningún conocimiento de las actividades y costos relevantes para verificar el potencial/factibilidad de la idea?",
            "¿Tiene poco conocimiento de las diferentes opciones y tipos de financiamiento?",
        ],
    },
    {
        "nivel": 2,
        "descripcion": "Descripción del concepto de negocios. Están definidas las necesidades y opciones de financiamiento para los hitos iniciales",
        "preguntas": [
            "¿Ha descrito las actividades iniciales y costos que permiten verificar el potencial/factibilidad de la idea (1-6 meses)?",
            "¿Tiene un plan básico con opciones de financiamiento para los hitos iniciales (1-6 meses)?",
        ],
    },
    {
        "nivel": 3,
        "descripcion": "Concepto de negocios bien descrito, con un plan de verificación inicial. Primer pequeño financiamiento “blando” (soft funding) asegurado",
        "preguntas": [
            "¿Tiene financiamiento suficiente para asegurar la ejecución de las actividades iniciales de verificación/factibilidad (1-6 meses)?",
            "¿Conoce los diferentes tipos de financiamiento (propio, blando, de capital, de clientes, etc.) y las ventajas y desventajas de cada uno?",
        ],
    },
    {
        "nivel": 4,
        "descripcion": "Se cuenta con un buen pitch y breve presentación del negocio. Se cuenta con un plan con diferentes opciones de financiamiento a lo largo del tiempo.",
        "preguntas": [
            "¿Tiene un buen pitch y una breve presentación del negocio?",
            "¿Ha preparado un plan de financiamiento para verificar el potencial comercial de la idea para los siguientes 3 a 12 meses?",
            "¿Ha identificado las fuentes de financiamiento relevantes?",
            "¿Ha obtenido fondos suficientes para implementar una parte sustancial del plan de verificación?",
        ],
    },
    {
        "nivel": 5,
        "descripcion": "Se cuenta con una presentación orientada al inversionista y material de apoyo que ha sido testeado. Se ha solicitado y obtenido un mayor financiamiento adicional (blandos u otros).",
        "preguntas": [
            "¿Ha elaborado y ensayado el pitch para obtener financiamiento en un ambiente relevante?",
            "¿Tiene una hoja de cálculo con el presupuesto inicial de ganancias y pérdidas y el flujo de caja para los próximos 12 meses?",
            "¿Ha decidido cómo abordar la estrategia de financiamiento y las fuentes de financiamiento para alcanzar un modelo de negocio viable?",
            "¿Conoce y entiende los requisitos y las consecuencias del financiamiento externo sobre el modelo de negocio, el control y la propiedad de la compañía?",
        ],
    },
    {
        "nivel": 6,
        "descripcion": "Presentación mejorada para el inversionista, la que incluye aspectos de negocios y financieros. Se ha decidido buscar inversores privados y se tomaron los primeros contactos.",
        "preguntas": [
            "¿Ha mejorado/actualizado el pitch para obtener financiamiento en una audiencia relevante?",
            "¿Tiene un presupuesto de ingresos y pérdidas y flujo de efectivo para negocios/proyectos a 3-5 años que permite esclarecer la necesidad de financiamiento a corto y mediano plazo?",
        ],
    },
    {
        "nivel": 7,
        "descripcion": "El equipo presenta un caso de inversión sólido, el que incluye estados y planes. Existen conversaciones con inversionistas potenciales sobre una oferta",
        "preguntas": [
            "¿Tiene conversaciones con posibles fuentes de financiamiento externas en torno a una oferta definida (cuánto dinero, para qué, condiciones, valoración, etc.)?",
            "¿La propuesta de financiamiento está completa, probada y comprobada, y existe un plan de negocios con proyecciones financieras y un plan de hitos?",
            "¿Existen sistemas básicos de contabilidad y documentación para el seguimiento financiero?",
        ],
    },
    {
        "nivel": 8,
        "descripcion": "Existe un orden y una estructura corporativa que permiten la inversión. Existen diálogos sobre los términos del acuerdo con los inversionistas interesados.",
        "preguntas": [
            "¿Ha tenido conversaciones concretas (a nivel de Hoja de Términos) con una o varias fuentes de financiamiento externas interesadas?",
            "¿Está preparado y disponible todo el material necesario para el financiamiento externo (finanzas, plan de negocio, etc.)?",
            "¿Existe una entidad jurídica correctamente establecida con una estructura de propiedad adecuada para la fuente de financiamiento visualizada?",
            "¿Se ha recopilado y está disponible toda la documentación y acuerdos legales clave para una diligencia/revisión externa?",
        ],
    },
    {
        "nivel": 9,
        "descripcion": "La inversión fue obtenida. Las necesidades y las opciones de inversión adicionales son consideradas continuamente",
        "preguntas": [
            "¿Tiene financiamiento garantizado por al menos 6 a 12 meses de ejecución de acuerdo con el plan comercial/plan operativo actual?",
            "¿Está totalmente implementado un sistema de seguimiento financiero y contable para el control continuo del estado financiero actual?",
            "¿Existe un buen pronóstico/previsión para identificar las futuras necesidades de financiamiento?",
        ],
    },
]

TRL_LEVELS = [
    {
        "nivel": 1,
        "descripcion": "Principios básicos observados.",
        "preguntas": [
            "¿Ha identificado beneficios potenciales o aplicaciones útiles en los resultados de su investigación?",
            "¿Tiene una idea vaga de la tecnología a desarrollar?",
        ],
    },
    {
        "nivel": 2,
        "descripcion": "Concepto y/o aplicación tecnológica formulada.",
        "preguntas": [
            "¿Cuenta con un concepto de tecnología potencial, definido y descrito en su primera versión?",
            "¿Se pueden definir o investigar aplicaciones prácticas para esta tecnologia?",
        ],
    },
    {
        "nivel": 3,
        "descripcion": "Prueba de concepto analítica y experimental de funciones y/o características críticas.",
        "preguntas": [
            "¿Ha realizado pruebas analíticas y/o experimentales de funciones o características críticas en entorno de laboratorio?",
            "¿Ha iniciado una I+D activa para desarrollar aún más la tecnología?",
            "¿Tiene una primera idea de los requisitos o especificaciones del usuario final y/o casos de uso?",
        ],
    },
    {
        "nivel": 4,
        "descripcion": "Validación de la tecnología en el laboratorio.",
        "preguntas": [
            "¿Ha integrado y demostrado el funcionamiento conjunto de los componentes básicos en un entorno de laboratorio?",
            "¿Los resultados de las pruebas brindan evidencia inicial que indica que el concepto de tecnología funcionará?",
        ],
    },
    {
        "nivel": 5,
        "descripcion": "Validación de tecnología en un entorno relevante.",
        "preguntas": [
            "¿Ha integrado y probado los componentes básicos de la tecnología en un entorno relevante?",
            "¿Los resultados de las pruebas brindan evidencia de que la tecnología funcionará, con validación técnica?",
            "¿Ha definido los requisitos o especificaciones del usuario final y/o casos de uso, basados en comentarios de los usuarios?",
        ],
    },
    {
        "nivel": 6,
        "descripcion": "Demostración del prototipo en un entorno relevante.",
        "preguntas": [
            "¿Ha demostrado que el modelo o prototipo representativo de la tecnología funciona realmente en un entorno relevante?",
        ],
    },
    {
        "nivel": 7,
        "descripcion": "Sistema/prototipo completo demostrado en ambiente operacional.",
        "preguntas": [
            "¿Ha demostrado que el prototipo o la tecnología completa funciona realmente en un entorno operativo?",
            "¿Ha establecido los requisitos completos del usuario final/especificaciones y/o casos de uso?",
        ],
    },
    {
        "nivel": 8,
        "descripcion": "Sistema tecnológico real completado y calificado mediante pruebas y demostraciones.",
        "preguntas": [
            "¿Cuenta con una tecnología completa que contiene todo lo necesario para que el usuario la utilice?",
            "¿Cuenta con una tecnología funcional que resuelve el problema o necesidad del usuario?",
            "¿Es la tecnología compatible con personas, procesos, objetivos, infraestructura, sistemas, etc., del usuario?",
            "¿Han demostrado los primeros usuarios que la tecnología completa funciona en operaciones reales?",
        ],
    },
    {
        "nivel": 9,
        "descripcion": "Sistema tecnológico probado con éxito en entorno operativo real.",
        "preguntas": [
            "¿Es la tecnología completa escalable y ha sido comprobada en operaciones reales por varios usuarios a lo largo del tiempo?",
            "¿Está en curso el desarrollo continuo, la mejora, la optimización de la tecnología y la producción?",
        ],
    },
]


IPRL_LEVELS = [
    {
        "nivel": 1,
        "descripcion": "Se cuenta con una hipótesis sobre posibles derechos de propiedad intelectual que se podrían obtener (como patentes, software, derechos de autor, diseños, secretos comerciales, etc).",
        "preguntas": [
            "¿Tiene una hipótesis sobre posibles derechos de propiedad intelectual que se podrían obtener (como patentes, software, derechos de autor, diseños, secretos comerciales, etc.)?",
            "¿Tiene descripción y documentación de los posibles derechos de propiedad intelectual?",
            "¿Tiene claridad sobre aspectos legales relevantes o pertinentes (propiedad, derechos de uso, etc.)?",
            "¿Tiene conocimiento de los elementos únicos del invento y el campo técnico, estado del arte, publicaciones, etc.?",
        ],
    },
    {
        "nivel": 2,
        "descripcion": "Identificación de las diferentes formas de posibles derechos de propiedad intelectual que podrían tener. La propiedad de los derechos es clara y no hay dudas de ser el dueño de los derechos de PI",
        "preguntas": [
            "¿Ha mapeado las diferentes formas de derechos de propiedad intelectual que existen o podrían surgir durante el desarrollo?",
            "¿Tiene ideas específicas sobre los derechos de propiedad intelectual, aunque no estén bien descritas ni definidas?",
            "¿Ha identificado acuerdos relacionados con la propiedad intelectual y aclarado la propiedad?",
            "¿Ha identificado a los inventores/creadores y tiene conocimiento de las políticas de PI aplicables y potenciales restricciones en los contratos?",
        ],
    },
    {
        "nivel": 3,
        "descripcion": "Descripción detallada de los posibles derechos de propiedad intelectual claves (por ejemplo, invención o código).",
        "preguntas": [
            "¿Ha considerado qué formas de derechos de propiedad intelectual son claves o más importantes y podrían/deberían protegerse?",
            "¿Tiene una descripción suficientemente detallada de los posibles derechos de propiedad intelectual para evaluar la posibilidad de protección?",
            "¿Ha realizado una evaluación de las posibilidades de protección a través de búsquedas de publicaciones, estado del arte, soluciones de última generación, etc.?",
            "¿Ha realizado búsquedas o análisis iniciales del estado de la técnica pertinente o derechos de propiedad intelectual en conflicto con profesionales?",
        ],
    },
    {
        "nivel": 4,
        "descripcion": "Confirmación sobre la viabilidad de la protección y mediante qué mecanismo. Decisión sobre el por qué de proteger determinados derechos de propiedad intelectual (relevancia para el negocio).",
        "preguntas": [
            "¿Ha confirmado la viabilidad de la protección de los derechos de propiedad intelectual claves a través de búsquedas/análisis por parte de un profesional?",
            "¿Ha analizado los derechos de propiedad intelectual claves y definido prioridades sobre qué proteger para crear valor para el negocio/proyecto?",
            "¿Ha presentado la primera solicitud/registro de derechos de propiedad intelectual en una forma menos elaborada (por ejemplo, patente provisional)?",
        ],
    },
    {
        "nivel": 5,
        "descripcion": "Borrador de estrategia de los derechos de propiedad intelectual para usar estos derechos con fines comerciales. Presentación de la primera solicitud de patente completa.",
        "preguntas": [
            "¿Tiene un borrador de estrategia de los derechos de propiedad intelectual definida, idealmente por un profesional, sobre cómo usar los derechos de PI para proteger y ser valiosos para el negocio?",
            "¿Ha presentado la primera solicitud/registro formal completo de derechos de propiedad intelectual claves en cooperación con un profesional?",
            "¿Tiene acuerdos básicos vigentes para determinar el control de los derechos de propiedad intelectual claves (por ejemplo, asignaciones, propiedad, etc.)?",
        ],
    },
    {
        "nivel": 6,
        "descripcion": "La estrategia de protección se encuentra implementada y apoya el negocio. Respuesta positiva en solicitudes presentadas. Evaluación inicial de la libertad para operar.",
        "preguntas": [
            "¿Ha elaborado una estrategia completa de protección de los derechos de propiedad intelectual que sustenta la estrategia de negocio?",
            "¿Ha identificado posibles derechos de propiedad intelectual complementarios/adicionales a proteger?",
            "¿Ha realizado una evaluación inicial de la libertad para operar (freedom to operate) para comprender el panorama de los derechos de PI en el campo?",
            "¿Ha recibido respuesta positiva a las solicitudes de derechos de PI por parte de las autoridades?",
            "Si no ha recibido respuesta positiva, ¿ha realizado un análisis junto con profesionales con buenas perspectivas?",
        ],
    },
    {
        "nivel": 7,
        "descripcion": "Todos los derechos de propiedad intelectual claves han sido solicitados en los paises o regiones relevantes de acuerdo con la estrategia de derechos de propiedad intelectual",
        "preguntas": [
            "¿Ha solicitado todos los derechos de propiedad intelectual claves en los países o regiones relevantes de acuerdo con la estrategia de PI?",
            "¿Ha realizado una evaluación más completa de la libertad para operar y tiene una comprensión clara de la dependencia/restricción de otros derechos de PI existentes?",
        ],
    },
    {
        "nivel": 8,
        "descripcion": "Estrategia de protección y gestión de la propiedad intelectual completamente implementada. Evaluación más completa de la libertad de operar",
        "preguntas": [
            "¿Tiene una estrategia de protección y gestión de la propiedad intelectual completamente implementada?",
            "¿Ha sido otorgado los derechos de propiedad intelectual clave en el primer país/región con alcance relevante para el negocio?",
            "¿Ha presentado solicitud(es)/registro(s) de derechos de PI complementarios o adicionales?",
        ],
    },
    {
        "nivel": 9,
        "descripcion": "Sólido sustento y protección de derechos de propiedad intelectual para el negocio. Patente concedida y vigente en países relevantes",
        "preguntas": [
            "¿La estrategia de derechos de propiedad intelectual respalda y crea valor para el negocio?",
            "¿Se han otorgado y se mantienen los derechos de propiedad intelectual claves y complementarios en varios países relevantes para los negocios?",
            "¿Tiene acuerdos vigentes para acceder a todos los derechos de propiedad intelectual externos necesarios?",
        ],
    },
]

TMRL_LEVELS = [
    {
        "nivel": 1,
        "descripcion": "Poca comprensión de la necesidad de un equipo (generalmente un individuo). Falta de competencias y/o recursos necesarios.",
        "preguntas": [
            "¿El equipo está conformado por más de una persona que posee las competencias necesarias en áreas claves como tecnología y negocios?",
            "¿Tiene algo de conocimiento sobre las competencias y otros recursos necesarios (socios, proveedores de servicios, etc.) para verificar y desarrollar la idea?",
        ],
    },
    {
        "nivel": 2,
        "descripcion": "Conocimiento y primera idea sobre las competencias necesarias o los recursos externos (por ejemplo, socios) requeridos",
        "preguntas": [
            "¿Tiene una primera idea de qué personas/competencias adicionales podrían ser necesarias para verificar/desarrollar la idea?",
            "¿Tiene una primera idea del objetivo general del proyecto?",
        ],
    },
    {
        "nivel": 3,
        "descripcion": "Algunas de las competencias o recursos necesarios están presentes. Existen otras competencias o recursos que se necesitan y deben definirse (junto a un plan de búsqueda).",
        "preguntas": [
            "¿Existen personas en el equipo con algunas, pero no todas, las competencias necesarias para comenzar a verificar la idea?",
            "¿Ha identificado necesidades y brechas en competencias, capacidades y diversidad de equipos?",
            "¿Tiene un plan inicial sobre cómo encontrar las competencias necesarias a corto plazo (<1 año)?",
        ],
    },
    {
        "nivel": 4,
        "descripcion": "Un champion está presente. Varias de las competencias necesarias están presentes. Se inicia un plan para reclutar o asegurar recursos claves adicionales.",
        "preguntas": [
            "¿Hay un champion (impulsor y comprometido) en el equipo?",
            "¿El equipo tiene varias, pero no todas, las competencias necesarias, generalmente en múltiples individuos?",
            "¿Ha iniciado un plan para encontrar competencias y capacidades adicionales necesarias, teniendo en cuenta la diversidad del equipo?",
            "¿El equipo ha iniciado discusiones sobre roles, compromiso, propiedad, etc., para avanzar en el proyecto?",
        ],
    },
    {
        "nivel": 5,
        "descripcion": "El equipo fundador inicial ya posee las principales competencias necesarias. El equipo acuerda la propiedad y los roles, y tiene objetivos alineados",
        "preguntas": [
            "¿Existe un equipo fundador inicial trabajando juntos y dedicando un tiempo significativo al proyecto?",
            "¿El equipo fundador tiene en conjunto las principales competencias y capacidades necesarias para comenzar a construir la startup?",
            "¿El equipo está alineado con roles claros, metas y visiones compartidas y un claro compromiso con el proyecto?",
            "¿El equipo ha acordado sus respectivas participaciones accionarias con un acuerdo firmado?",
            "¿Se han iniciado actividades para obtener competencias y capacidades adicionales, teniendo en cuenta la diversidad del equipo?",
            "¿Se han implementado sistemas/procesos/herramientas iniciales para compartir conocimientos e información dentro del equipo?",
        ],
    },
    {
        "nivel": 6,
        "descripcion": "Existe un equipo complementario, diverso y comprometido, con todas las competencias y recursos necesarios, tanto en el ámbito de los negocios como el tecnológico.",
        "preguntas": [
            "¿Existe un equipo fundador complementario y diverso, capaz de comenzar a construir un negocio?",
            "¿Se cuenta con todas las competencias clave y la capacidad necesaria para el corto plazo, con claridad sobre quién es el director ejecutivo?",
            "¿El equipo está comprometido, todos sienten responsabilidad y están preparados para asumir responsabilidades?",
            "¿Ha iniciado la contratación de asesores y/o miembros del directorio, teniendo en cuenta la diversidad del directorio?",
            "¿Existe conciencia de los riesgos que pueden afectar el desempeño del equipo (conflictos, burnout/salud mental, política, etc.)?",
        ],
    },
    {
        "nivel": 7,
        "descripcion": "El equipo y la cultura de la empresa están plenamente establecidos y desarrollados de forma proactiva. Hay un plan visualizado para formar el equipo que se necesita a largo plazo",
        "preguntas": [
            "¿El equipo funciona bien con roles claros?",
            "¿Los objetivos, la visión, el propósito y la cultura están claramente articuladas y documentadas para apoyar al equipo y el desarrollo organizacional?",
            "¿Está en marcha un plan para desarrollar la organización y hacer crecer el equipo a largo plazo (~2 años)?",
            "¿Se han implementado procesos/sistemas y un plan de aprendizaje continuo para el desarrollo del personal?",
            "¿El Directorio y los asesores están en funcionamiento y apoyan al desarrollo empresarial y organizacional?",
        ],
    },
    {
        "nivel": 8,
        "descripcion": "Se cuenta con un CEO y equipo ejecutivo. Uso profesional del Directorio y de asesores. Se han activado planes y reclutamiento para la construcción de equipo a largo plazo.",
        "preguntas": [
            "¿Existe un liderazgo claro y un equipo de gestión con experiencia profesional relevante?",
            "¿Se cuenta con un Directorio competente y diverso, y asesores relevantes utilizados profesionalmente?",
            "¿Se han implementado políticas y procesos para asegurar buenas prácticas de recursos humanos y diversidad del equipo?",
            "¿Se están realizando contrataciones necesarias de acuerdo con el plan a largo plazo para determinar las competencias, capacidad y diversidad relevantes?",
            "¿Todos los niveles de la organización están debidamente capacitados y motivados?",
        ],
    },
    {
        "nivel": 9,
        "descripcion": "El equipo y la organización son de alto rendimiento y están correctamente estructurados. Ambos se mantienen y se desarrollan correctamente a lo largo del tiempo",
        "preguntas": [
            "¿La organización tiene un alto rendimiento y buen funcionamiento (cooperación, entorno social, etc.)?",
            "¿Todos los niveles de la organización participan activamente en el aprendizaje y el desarrollo continuo?",
            "¿La cultura organizacional, la estructura y los procesos se mejoran y desarrollan continuamente?",
            "¿Los incentivos/recompensas están alineados para motivar a toda la organización para alcanzar las metas y desempeñarse bien?",
            "¿El equipo directivo se mantiene, se desarrolla y se desempeña en el tiempo?",
        ],
    },
]

BRL_LEVELS = [
    {
        "nivel": 1,
        "descripcion": "Hipótesis preliminar sobre el concepto de negocio con información limitada del mercado.",
        "preguntas": [
            "¿Tiene una hipótesis preliminar del concepto de negocio?",
            "¿Cuenta con alguna información sobre el mercado y su potencial o tamaño?",
            "¿Tiene algún conocimiento o percepción de la competencia y soluciones alternativas?",
        ],
    },
    {
        "nivel": 2,
        "descripcion": "Descripción inicial estructurada del concepto de negocio y reconocimiento general del mercado.",
        "preguntas": [
            "¿Ha propuesto una descripción estructurada del concepto de negocio y la propuesta de valor?",
            "¿Se ha familiarizado brevemente con el tamaño del mercado, los segmentos y el panorama competitivo?",
            "¿Ha enumerado algunos competidores o alternativas?",
        ],
    },
    {
        "nivel": 3,
        "descripcion": "Borrador de modelo de negocios que caracteriza el mercado potencial y el panorama competitivo.",
        "preguntas": [
            "¿Ha generado un borrador del modelo de negocios (Canvas)?",
            "¿Ha descrito factores relevantes en el modelo de negocio que afectan al medio ambiente y la sociedad?",
            "¿Ha definido el mercado objetivo y estimado su tamaño (TAM, SAM)?",
            "¿Ha identificado y descrito la competencia y el panorama competitivo?",
        ],
    },
    {
        "nivel": 4,
        "descripcion": "Modelo de negocios completo inicial con primeras proyecciones de viabilidad económica.",
        "preguntas": [
            "¿Ha determinado la viabilidad económica a partir de las primeras proyecciones de pérdidas y ganancias?",
            "¿Ha realizado una evaluación inicial de la sostenibilidad ambiental y social?",
        ],
    },
    {
        "nivel": 5,
        "descripcion": "Modelo de negocios ajustado tras feedback de mercado y primeras hipótesis de ingresos.",
        "preguntas": [
            "¿Ha recibido feedback sobre los ingresos del modelo comercial de clientes potenciales o expertos?",
            "¿Ha recibido feedback sobre los costos del modelo comercial de socios, proveedores o expertos externos?",
            "¿Ha identificado medidas para aumentar las contribuciones ambientales y sociales positivas y disminuir las negativas?",
            "¿Ha actualizado la proyección de ganancias y pérdidas en función del feedback del mercado?",
            "¿Ha actualizado la descripción del mercado objetivo y el análisis competitivo basado en comentarios del mercado?",
        ],
    },
    {
        "nivel": 6,
        "descripcion": "Modelo de negocios sostenible validado mediante escenarios comerciales realistas.",
        "preguntas": [
            "¿Tiene un modelo de negocio sostenible probado en escenarios comerciales realistas (ventas de prueba, pedidos anticipados, pilotos, etc.)?",
            "¿Tiene proyecciones financieras completas basadas en comentarios de casos comerciales realistas?",
        ],
    },
    {
        "nivel": 7,
        "descripcion": "Product/market fit inicial con disposición de pago demostrada y proyecciones validadas.",
        "preguntas": [
            "¿Las primeras ventas/ingresos en términos comerciales demuestran la disposición a pagar de un número significativo de clientes?",
            "¿Existen proyecciones financieras completas validadas por primeras ventas/ingresos y datos?",
            "¿Tiene acuerdos vigentes con proveedores clave, socios y socios de canal alineados con sus expectativas de sostenibilidad?",
        ],
    },
    {
        "nivel": 8,
        "descripcion": "Modelo de negocios sostenible que demuestra capacidad de escalar con métricas operativas.",
        "preguntas": [
            "¿Las ventas y otras métricas de las operaciones comerciales iniciales muestran que el modelo de negocio sostenible se mantiene y puede escalar?",
            "¿Están establecidos y operativos los canales de venta y la cadena de suministro alineados con sus expectativas de sostenibilidad?",
            "¿El modelo comercial se ajusta para mejorar los ingresos/costos y aprovechar la sostenibilidad?",
        ],
    },
    {
        "nivel": 9,
        "descripcion": "Modelo de negocios definitivo y sostenible con ingresos recurrentes y métricas consolidadas.",
        "preguntas": [
            "¿El modelo de negocio es sostenible y operativo, y el negocio cumple o supera las expectativas internas y externas en cuanto a beneficios, crecimiento, escalabilidad e impacto ambiental y social?",
            "¿Utiliza sistemas y métricas creíbles para rastrear el desempeño económico, ambiental y social?",
            "¿Los datos históricos sobre el desempeño económico, ambiental y social prueban un negocio viable, rentable y sostenible en el tiempo?",
        ],
    },
]

def _init_irl_state():
    if "irl_scores" not in st.session_state:
        st.session_state["irl_scores"] = {dimension: default for dimension, default in IRL_DIMENSIONS}
    if "irl_answers" not in st.session_state:
        st.session_state["irl_answers"] = {}


def _compute_consecutive_level(dimension: str, levels: list[dict]) -> int:
    reached_level = 0
    for level_data in levels:
        preguntas = level_data.get("preguntas", [])
        nivel_validado = True
        for idx, _ in enumerate(preguntas, start=1):
            answer_key = f"irl_{dimension}_L{level_data['nivel']}_Q{idx}"
            if st.session_state.get(answer_key, "FALSO") != "VERDADERO":
                nivel_validado = False
                break
        if nivel_validado:
            reached_level = level_data["nivel"]
        else:
            break
    return reached_level


def _collect_dimension_responses() -> pd.DataFrame:
    _init_irl_state()
    dimensiones_ids = trl.ids_dimensiones()
    etiquetas = dict(zip(dimensiones_ids, trl.labels_dimensiones()))
    registros: list[dict] = []

    for dimension in dimensiones_ids:
        nivel_base = st.session_state["irl_scores"].get(dimension, 0)
        nivel = int(nivel_base) if isinstance(nivel_base, (int, float)) and nivel_base else None

        evidencias: list[str] = []
        prefijo = f"irl_{dimension}_"
        for key, value in st.session_state.items():
            if not key.startswith(prefijo) or not key.endswith("_evidencia"):
                continue
            respuesta_key = key[:-10]
            if st.session_state.get(respuesta_key) != "VERDADERO":
                continue
            if isinstance(value, str):
                texto = value.strip()
                if texto:
                    evidencias.append(texto)

        registros.append(
            {
                "dimension": dimension,
                "etiqueta": etiquetas.get(dimension, dimension),
                "nivel": nivel,
                "evidencia": " · ".join(evidencias),
            }
        )

    return pd.DataFrame(registros)


def _render_crl_tab():
    _init_irl_state()
    st.markdown("#### Calculadora de madurez del cliente (CRL)")
    st.caption(
        "Responde cada pregunta marcando VERDADERO cuando cuentes con evidencia. Al hacerlo se solicitará acreditar el medio de verificación."
    )
    for level in CRL_LEVELS:
        st.markdown(f"### Nivel {level['nivel']} · {level['descripcion']}")
        preguntas = level["preguntas"]
        for idx, pregunta in enumerate(preguntas, start=1):
            answer_key = f"irl_CRL_L{level['nivel']}_Q{idx}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = "FALSO"
            respuesta = st.radio(
                pregunta,
                options=["FALSO", "VERDADERO"],
                horizontal=True,
                key=answer_key,
            )
            if respuesta == "VERDADERO":
                evidence_key = f"{answer_key}_evidencia"
                st.text_input(
                    "Acredite el medio de verificación con que cuenta",
                    key=evidence_key,
                )
        st.divider()

    nivel_consecutivo = _compute_consecutive_level("CRL", CRL_LEVELS)
    st.session_state["irl_scores"]["CRL"] = nivel_consecutivo
    if nivel_consecutivo:
        st.success(f"Nivel alcanzado: CRL {nivel_consecutivo}")
    else:
        st.info("Marca las evidencias de forma consecutiva para avanzar en el nivel CRL.")


def _render_frl_tab():
    _init_irl_state()
    st.markdown("#### Calculadora de madurez financiera (FRL)")
    st.caption(
        "Responde cada pregunta marcando VERDADERO cuando cuentes con evidencia. Al hacerlo se solicitará acreditar el medio de verificación."
    )
    for level in FRL_LEVELS:
        st.markdown(f"### Nivel {level['nivel']} · {level['descripcion']}")
        preguntas = level["preguntas"]
        for idx, pregunta in enumerate(preguntas, start=1):
            answer_key = f"irl_FRL_L{level['nivel']}_Q{idx}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = "FALSO"
            respuesta = st.radio(
                pregunta,
                options=["FALSO", "VERDADERO"],
                horizontal=True,
                key=answer_key,
            )
            if respuesta == "VERDADERO":
                evidence_key = f"{answer_key}_evidencia"
                st.text_input(
                    "Acredite el medio de verificación con que cuenta",
                    key=evidence_key,
                )
        st.divider()

    nivel_consecutivo = _compute_consecutive_level("FRL", FRL_LEVELS)
    st.session_state["irl_scores"]["FRL"] = nivel_consecutivo
    if nivel_consecutivo:
        st.success(f"Nivel alcanzado: FRL {nivel_consecutivo}")
    else:
        st.info("Marca las evidencias de forma consecutiva para avanzar en el nivel FRL.")


def _render_brl_tab():
    _init_irl_state()
    st.markdown("#### Calculadora de madurez del negocio (BRL)")
    st.caption(
        "Responde cada pregunta marcando VERDADERO cuando cuentes con evidencia. Al hacerlo se solicitará acreditar el medio de verificación."
    )
    for level in BRL_LEVELS:
        st.markdown(f"### Nivel {level['nivel']} · {level['descripcion']}")
        preguntas = level["preguntas"]
        for idx, pregunta in enumerate(preguntas, start=1):
            answer_key = f"irl_BRL_L{level['nivel']}_Q{idx}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = "FALSO"
            respuesta = st.radio(
                pregunta,
                options=["FALSO", "VERDADERO"],
                horizontal=True,
                key=answer_key,
            )
            if respuesta == "VERDADERO":
                evidence_key = f"{answer_key}_evidencia"
                st.text_input(
                    "Acredite el medio de verificación con que cuenta",
                    key=evidence_key,
                )
        st.divider()

    nivel_consecutivo = _compute_consecutive_level("BRL", BRL_LEVELS)
    st.session_state["irl_scores"]["BRL"] = nivel_consecutivo
    if nivel_consecutivo:
        st.success(f"Nivel alcanzado: BRL {nivel_consecutivo}")
    else:
        st.info("Marca las evidencias de forma consecutiva para avanzar en el nivel BRL.")


def _render_trl_tab():
    _init_irl_state()
    st.markdown("#### Calculadora de madurez tecnológica (TRL)")
    st.caption(
        "Responde cada pregunta marcando VERDADERO cuando cuentes con evidencia. Al hacerlo se solicitará acreditar el medio de verificación."
    )
    for level in TRL_LEVELS:
        st.markdown(f"### Nivel {level['nivel']} · {level['descripcion']}")
        preguntas = level["preguntas"]
        for idx, pregunta in enumerate(preguntas, start=1):
            answer_key = f"irl_TRL_L{level['nivel']}_Q{idx}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = "FALSO"
            respuesta = st.radio(
                pregunta,
                options=["FALSO", "VERDADERO"],
                horizontal=True,
                key=answer_key,
            )
            if respuesta == "VERDADERO":
                evidence_key = f"{answer_key}_evidencia"
                st.text_input(
                    "Acredite el medio de verificación con que cuenta",
                    key=evidence_key,
                )
        st.divider()

    nivel_consecutivo = _compute_consecutive_level("TRL", TRL_LEVELS)
    st.session_state["irl_scores"]["TRL"] = nivel_consecutivo
    if nivel_consecutivo:
        st.success(f"Nivel alcanzado: TRL {nivel_consecutivo}")
    else:
        st.info("Marca las evidencias de forma consecutiva para avanzar en el nivel TRL.")


def _render_iprl_tab():
    _init_irl_state()
    st.markdown("#### Calculadora de madurez de propiedad intelectual (IPRL)")
    st.caption(
        "Responde cada pregunta marcando VERDADERO cuando cuentes con evidencia. Al hacerlo se solicitará acreditar el medio de verificación."
    )
    for level in IPRL_LEVELS:
        st.markdown(f"### Nivel {level['nivel']} · {level['descripcion']}")
        preguntas = level["preguntas"]
        for idx, pregunta in enumerate(preguntas, start=1):
            answer_key = f"irl_IPRL_L{level['nivel']}_Q{idx}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = "FALSO"
            respuesta = st.radio(
                pregunta,
                options=["FALSO", "VERDADERO"],
                horizontal=True,
                key=answer_key,
            )
            if respuesta == "VERDADERO":
                evidence_key = f"{answer_key}_evidencia"
                st.text_input(
                    "Acredite el medio de verificación con que cuenta",
                    key=evidence_key,
                )
        st.divider()

    nivel_consecutivo = _compute_consecutive_level("IPRL", IPRL_LEVELS)
    st.session_state["irl_scores"]["IPRL"] = nivel_consecutivo
    if nivel_consecutivo:
        st.success(f"Nivel alcanzado: IPRL {nivel_consecutivo}")
    else:
        st.info("Marca las evidencias de forma consecutiva para avanzar en el nivel IPRL.")


def _render_tmrl_tab():
    _init_irl_state()
    st.markdown("#### Calculadora de madurez del equipo (TmRL)")
    st.caption(
        "Responde cada pregunta marcando VERDADERO cuando cuentes con evidencia. Al hacerlo se solicitará acreditar el medio de verificación."
    )
    for level in TMRL_LEVELS:
        st.markdown(f"### Nivel {level['nivel']} · {level['descripcion']}")
        preguntas = level["preguntas"]
        for idx, pregunta in enumerate(preguntas, start=1):
            answer_key = f"irl_TmRL_L{level['nivel']}_Q{idx}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = "FALSO"
            respuesta = st.radio(
                pregunta,
                options=["FALSO", "VERDADERO"],
                horizontal=True,
                key=answer_key,
            )
            if respuesta == "VERDADERO":
                evidence_key = f"{answer_key}_evidencia"
                st.text_input(
                    "Acredite el medio de verificación con que cuenta",
                    key=evidence_key,
                )
        st.divider()

    nivel_consecutivo = _compute_consecutive_level("TmRL", TMRL_LEVELS)
    st.session_state["irl_scores"]["TmRL"] = nivel_consecutivo
    if nivel_consecutivo:
        st.success(f"Nivel alcanzado: TmRL {nivel_consecutivo}")
    else:
        st.info("Marca las evidencias de forma consecutiva para avanzar en el nivel TmRL.")


def _render_placeholder_tab(dimension: str):
    _init_irl_state()
    score_key = f"irl_manual_{dimension}"
    default_value = int(st.session_state["irl_scores"].get(dimension, 0))
    st.info("Define temporalmente el nivel de madurez mientras se agregan las preguntas específicas.")
    nivel = st.slider(
        f"Selecciona el nivel de {dimension}",
        min_value=0,
        max_value=9,
        value=default_value,
        key=score_key,
    )
    st.session_state["irl_scores"][dimension] = nivel


st.set_page_config(page_title="Fase 1 - Evaluacion TRL", page_icon="🌲", layout="wide")
load_theme()

st.markdown(
    """
<style>
.page-intro {
    display: grid;
    grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
    gap: 2.4rem;
    padding: 2.3rem 2.6rem;
    border-radius: 30px;
    background: linear-gradient(145deg, rgba(18, 48, 29, 0.94), rgba(111, 75, 44, 0.88));
    color: #fdf9f2;
    box-shadow: 0 36px 60px rgba(12, 32, 20, 0.35);
    margin-bottom: 2.6rem;
}

.page-intro h1 {
    font-size: 2.2rem;
    margin-bottom: 1rem;
    color: #fffdf8;
}

.page-intro p {
    font-size: 1.02rem;
    line-height: 1.6;
    color: rgba(253, 249, 242, 0.86);
}

.page-intro__aside {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.page-intro__aside .intro-stat {
    background: rgba(255, 255, 255, 0.14);
    border-radius: 20px;
    padding: 1.1rem 1.3rem;
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.12);
}

.page-intro__aside .intro-stat strong {
    display: block;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-size: 0.9rem;
    margin-bottom: 0.35rem;
    color: #fefcf9;
}

.page-intro__aside .intro-stat p {
    margin: 0;
    color: rgba(253, 249, 242, 0.86);
    font-size: 0.96rem;
    line-height: 1.5;
}

.back-band {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1.6rem;
}

.metric-ribbon {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 1.1rem;
    margin: 1.4rem 0 2.1rem;
}

.metric-ribbon__item {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.3rem 1.4rem;
    border: 1px solid rgba(var(--shadow-color), 0.12);
    box-shadow: 0 20px 42px rgba(var(--shadow-color), 0.16);
    position: relative;
    overflow: hidden;
}

.metric-ribbon__item:after {
    content: "";
    position: absolute;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: rgba(37, 87, 52, 0.12);
    top: -40px;
    right: -50px;
}

.metric-ribbon__value {
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--forest-700);
    position: relative;
}

.metric-ribbon__label {
    display: block;
    margin-top: 0.4rem;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.55px;
    text-transform: uppercase;
    color: var(--text-500);
}

.section-shell {
    background: #ffffff;
    border-radius: 24px;
    padding: 1.6rem 1.8rem;
    border: 1px solid rgba(var(--shadow-color), 0.12);
    box-shadow: 0 24px 48px rgba(var(--shadow-color), 0.16);
    margin-bottom: 2.3rem;
}

.section-shell--split {
    padding: 1.6rem 1.2rem 1.9rem;
}

.section-shell h3, .section-shell h4 {
    margin-top: 0;
}

.threshold-band {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin: 0.6rem 0 1rem;
}

.threshold-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 1rem;
    border-radius: 16px;
    background: rgba(var(--forest-500), 0.16);
    color: var(--text-700);
    font-weight: 600;
    border: 1px solid rgba(var(--forest-500), 0.22);
}

.threshold-chip strong {
    font-size: 1rem;
    color: var(--forest-700);
}

.selection-card {
    position: relative;
    padding: 1.8rem 2rem;
    border-radius: 26px;
    background: linear-gradient(140deg, rgba(49, 106, 67, 0.16), rgba(32, 73, 46, 0.22));
    border: 1px solid rgba(41, 96, 59, 0.45);
    box-shadow: 0 26px 48px rgba(21, 56, 35, 0.28);
    overflow: hidden;
}

.selection-card::after {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: rgba(103, 164, 123, 0.18);
    top: -80px;
    right: -70px;
    filter: blur(0.5px);
}

.selection-card__badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.45rem 1.1rem;
    border-radius: 999px;
    background: #1f6b36;
    color: #f4fff2;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    font-size: 0.78rem;
    font-weight: 600;
    box-shadow: 0 12px 24px rgba(31, 107, 54, 0.35);
    position: relative;
    z-index: 1;
}

.selection-card__title {
    margin: 1.1rem 0 0.6rem;
    font-size: 1.65rem;
    color: #10371d;
    position: relative;
    z-index: 1;
}

.selection-card__subtitle {
    margin: 0;
    color: rgba(16, 55, 29, 0.78);
    font-size: 1rem;
    position: relative;
    z-index: 1;
}

.selection-card__meta {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1.1rem;
    margin-top: 1.5rem;
    position: relative;
    z-index: 1;
}

.selection-card__meta-item {
    padding: 1rem 1.1rem;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(41, 96, 59, 0.18);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.35);
}

.selection-card__meta-label {
    display: block;
    text-transform: uppercase;
    font-size: 0.72rem;
    letter-spacing: 0.6px;
    color: rgba(16, 55, 29, 0.64);
    margin-bottom: 0.35rem;
}

.selection-card__meta-value {
    display: block;
    font-size: 1.05rem;
    font-weight: 600;
    color: #10371d;
}

.history-caption {
    color: var(--text-500);
    margin-bottom: 0.8rem;
}

@media (max-width: 992px) {
    .page-intro {
        grid-template-columns: 1fr;
    }

    .back-band {
        justify-content: center;
    }
}

div[data-testid="stExpander"] {
    margin-bottom: 1.4rem;
}

div[data-testid="stExpander"] > details {
    border-radius: 22px;
    border: 1px solid rgba(var(--shadow-color), 0.16);
    background: linear-gradient(165deg, rgba(255, 255, 255, 0.98), rgba(235, 229, 220, 0.9));
    box-shadow: 0 24px 52px rgba(var(--shadow-color), 0.18);
    overflow: hidden;
}

div[data-testid="stExpander"] > details > summary {
    font-weight: 700;
    font-size: 1rem;
    color: var(--forest-700);
    padding: 1rem 1.4rem;
    list-style: none;
    position: relative;
}

div[data-testid="stExpander"] > details > summary::before {
    content: "➕";
    margin-right: 0.6rem;
    color: var(--forest-600);
    font-size: 1rem;
}

div[data-testid="stExpander"] > details[open] > summary::before {
    content: "➖";
}

div[data-testid="stExpander"] > details[open] > summary {
    background: rgba(var(--forest-500), 0.12);
    color: var(--forest-800);
}

div[data-testid="stExpander"] > details > div[data-testid="stExpanderContent"] {
    padding: 1.2rem 1.5rem 1.4rem;
    background: #ffffff;
    border-top: 1px solid rgba(var(--shadow-color), 0.12);
}

div[data-testid="stDataFrame"],
div[data-testid="stDataEditor"] {
    border: 1px solid rgba(var(--shadow-color), 0.16);
    border-radius: 22px;
    overflow: hidden;
    box-shadow: 0 22px 44px rgba(var(--shadow-color), 0.18);
    background: #ffffff;
}

div[data-testid="stDataFrame"] div[role="columnheader"],
div[data-testid="stDataEditor"] div[role="columnheader"] {
    background: linear-gradient(135deg, var(--forest-700), var(--forest-500)) !important;
    color: #ffffff !important;
    font-weight: 700;
    font-size: 0.92rem;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    border-bottom: 2px solid rgba(12, 32, 20, 0.22);
    box-shadow: inset 0 -1px 0 rgba(255, 255, 255, 0.14);
}

div[data-testid="stDataFrame"] div[role="gridcell"],
div[data-testid="stDataEditor"] div[role="gridcell"] {
    color: var(--text-700);
    font-size: 0.92rem;
    border-bottom: 1px solid rgba(var(--forest-700), 0.14);
    border-right: 1px solid rgba(var(--forest-700), 0.1);
    padding: 0.55rem 0.75rem;
    background: rgba(255, 255, 255, 0.92);
}

div[data-testid="stDataFrame"] div[role="row"],
div[data-testid="stDataEditor"] div[role="row"] {
    transition: background 0.2s ease, box-shadow 0.2s ease;
}

div[data-testid="stDataFrame"] div[role="rowgroup"] > div:nth-child(odd) div[role="row"],
div[data-testid="stDataEditor"] div[role="rowgroup"] > div:nth-child(odd) div[role="row"] {
    background: rgba(255, 255, 255, 0.98);
}

div[data-testid="stDataFrame"] div[role="rowgroup"] > div:nth-child(even) div[role="row"],
div[data-testid="stDataEditor"] div[role="rowgroup"] > div:nth-child(even) div[role="row"] {
    background: rgba(199, 217, 182, 0.32);
}

div[data-testid="stDataFrame"] div[role="rowgroup"] > div div[role="row"]:hover,
div[data-testid="stDataEditor"] div[role="rowgroup"] > div div[role="row"]:hover {
    background: rgba(63, 129, 68, 0.18);
    box-shadow: inset 0 0 0 1px rgba(12, 32, 20, 0.2);
}

div[data-testid="stDataFrame"] div[role="rowgroup"] > div div[role="row"]:hover div[role="gridcell"],
div[data-testid="stDataEditor"] div[role="rowgroup"] > div div[role="row"]:hover div[role="gridcell"] {
    border-bottom-color: transparent;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-intro">
        <div>
            <span class="badge-soft">Fase 1 · IRL / TRL</span>
            <h1>Evaluacion estrategica de madurez tecnologica</h1>
            <p>
                Priorizamos proyectos del portafolio maestro para registrar evidencias por dimension, estimar el TRL e impulsar el
                cierre de brechas con una mirada integral entre cliente, negocio y tecnologia.
            </p>
        </div>
        <div class="page-intro__aside">
            <div class="intro-stat">
                <strong>Objetivo</strong>
                <p>Seleccionar iniciativas clave y capturar sus niveles IRL, alineando evidencia y responsables.</p>
            </div>
            <div class="intro-stat">
                <strong>Resultado</strong>
                <p>Perfil comparativo IRL con historial descargable y focos para la ruta comercial EBCT.</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

fase0_page = next(Path("pages").glob("02_*_Fase_0_Portafolio.py"), None)
if fase0_page:
    st.markdown("<div class='back-band'>", unsafe_allow_html=True)
    if st.button("Volver a Fase 0", type="primary"):
        st.switch_page(str(fase0_page))
    st.markdown("</div>", unsafe_allow_html=True)

payload = st.session_state.get('fase1_payload')
fase1_ready = st.session_state.get('fase1_ready', False)

if not payload or not fase1_ready:
    st.warning('Calcula el ranking de candidatos en Fase 0 y usa el boton "Ir a Fase 1" para continuar.')
    if fase0_page:
        if st.button('Ir a Fase 0', key='btn_ir_fase0_desde_fase1'):
            st.switch_page(str(fase0_page))
    st.stop()

ranking_df = payload['ranking'].copy().reset_index(drop=True)
if ranking_df.empty:
    st.warning('El ranking recibido esta vacio. Recalcula la priorizacion en Fase 0.')
    if fase0_page:
        if st.button('Recalcular en Fase 0', key='btn_recalcular_fase0'):
            st.switch_page(str(fase0_page))
    st.stop()

metrics_cards = payload.get('metrics_cards', [])
umbrales = payload.get('umbrales', {})

if metrics_cards:
    metrics_html = "<div class='metric-ribbon'>"
    for label, value in metrics_cards:
        metrics_html += (
            "<div class='metric-ribbon__item'>"
            f"<span class='metric-ribbon__value'>{value}</span>"
            f"<span class='metric-ribbon__label'>{label}</span>"
            "</div>"
        )
    metrics_html += "</div>"
    st.markdown(metrics_html, unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown('#### Ranking de candidatos priorizados')
    if umbrales:
        thresholds = "".join(
            f"<span class='threshold-chip'><strong>{valor}</strong>{nombre}</span>" for nombre, valor in umbrales.items()
        )
        st.markdown(f"<div class='threshold-band'>{thresholds}</div>", unsafe_allow_html=True)

    ranking_display = ranking_df.copy()
    styled_ranking = ranking_display.style.format({'evaluacion_calculada': '{:.1f}'})
    styled_ranking = styled_ranking.apply(
        lambda row: [
            'background-color: rgba(37, 87, 52, 0.18); color: #1f2a1d; font-weight:600' if row.name < 3 else ''
            for _ in row
        ],
        axis=1,
    )
    with st.expander('Ver ranking priorizado', expanded=False):
        st.dataframe(styled_ranking, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
ranking_keys = ranking_df[['id_innovacion', 'ranking']].copy()
ranking_keys['id_str'] = ranking_keys['id_innovacion'].astype(str)

df_port = utils.normalize_df(db.fetch_df())
df_port['id_str'] = df_port['id_innovacion'].astype(str)
df_port = df_port[df_port['id_str'].isin(ranking_keys['id_str'])].copy()
if df_port.empty:
    st.warning('Los proyectos del ranking ya no estan disponibles en el portafolio maestro. Recalcula la priorizacion en Fase 0.')
    if fase0_page:
        if st.button('Volver a Fase 0', key='btn_volver_recalcular'):
            st.switch_page(str(fase0_page))
    st.stop()

order_map = dict(zip(ranking_keys['id_str'], ranking_keys['ranking']))
df_port['orden_ranking'] = df_port['id_str'].map(order_map)
df_port = df_port.sort_values('orden_ranking').reset_index(drop=True)
df_port = df_port.drop(columns=['id_str', 'orden_ranking'], errors='ignore')



def parse_project_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        st.error('No se puede registrar la evaluacion porque el identificador del proyecto no es numerico. Revisa la Fase 0.')
        st.stop()


def fmt_opt(identificador: int) -> str:
    fila = df_port.loc[df_port["id_innovacion"] == identificador]
    if fila.empty:
        return str(identificador)
    return f"{identificador} - {fila['nombre_innovacion'].values[0]}"


with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown("### Selecciona un proyecto del portafolio maestro")
    ids = df_port["id_innovacion"].tolist()
    seleccion = st.selectbox("Proyecto", ids, format_func=fmt_opt)
    st.markdown("</div>", unsafe_allow_html=True)


project_id = parse_project_id(seleccion)

selected_project = df_port.loc[df_port["id_innovacion"] == project_id].iloc[0]
impacto_txt = selected_project.get("impacto") or "No informado"
estado_txt = selected_project.get("estatus") or "Sin estado"
responsable_txt = selected_project.get("responsable_innovacion") or "Sin responsable asignado"
transferencia_txt = selected_project.get("potencial_transferencia") or "Sin potencial declarado"
evaluacion_val = selected_project.get("evaluacion_numerica")
evaluacion_txt = f"{float(evaluacion_val):.1f}" if pd.notna(evaluacion_val) else "—"

selection_meta = [
    ("Impacto estratégico", impacto_txt),
    ("Estado actual", estado_txt),
    ("Responsable de innovación", responsable_txt),
    ("Evaluación Fase 0", evaluacion_txt),
]

meta_items_html = "".join(
    f"<div class='selection-card__meta-item'>"
    f"<span class='selection-card__meta-label'>{escape(label)}</span>"
    f"<span class='selection-card__meta-value'>{escape(str(value))}</span>"
    "</div>"
    for label, value in selection_meta
)

selection_card_html = f"""
<div class='selection-card'>
    <span class='selection-card__badge'>Proyecto seleccionado</span>
    <h3 class='selection-card__title'>{escape(selected_project['nombre_innovacion'])}</h3>
    <p class='selection-card__subtitle'>{escape(str(transferencia_txt))}</p>
    <div class='selection-card__meta'>
        {meta_items_html}
    </div>
</div>
"""

with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown(selection_card_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown("### Evaluación IRL")
    st.caption(
        "Responde las preguntas de cada pestaña y acredita la evidencia para calcular automáticamente el nivel de madurez por dimensión."
    )
    _init_irl_state()
    tabs = st.tabs([dimension for dimension, _ in IRL_DIMENSIONS])
    for idx, (dimension, _) in enumerate(IRL_DIMENSIONS):
        with tabs[idx]:
            if dimension == "CRL":
                _render_crl_tab()
            elif dimension == "BRL":
                _render_brl_tab()
            elif dimension == "TRL":
                _render_trl_tab()
            elif dimension == "IPRL":
                _render_iprl_tab()
            elif dimension == "TmRL":
                _render_tmrl_tab()
            elif dimension == "FRL":
                _render_frl_tab()
            else:
                _render_placeholder_tab(dimension)
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown("### Resultado TRL consolidado")
    st.caption("Se calcula automáticamente a partir de los niveles consecutivos validados en cada dimensión IRL.")

    df_respuestas = _collect_dimension_responses()
    if not df_respuestas.empty:
        resumen_vista = pd.DataFrame(
            [
                {
                    "Dimensión": fila.get("etiqueta", fila.get("dimension")),
                    "Nivel alcanzado": int(fila["nivel"]) if pd.notna(fila["nivel"]) else "—",
                    "Evidencias acreditadas": fila.get("evidencia") or "—",
                }
                for _, fila in df_respuestas.iterrows()
            ]
        )

        with st.expander('Detalle de niveles por dimension', expanded=False):
            st.dataframe(
                resumen_vista,
                use_container_width=True,
                hide_index=True,
            )
    puntaje = trl.calcular_trl(df_respuestas[["dimension", "nivel", "evidencia"]]) if not df_respuestas.empty else None
    st.metric("TRL estimado", f"{puntaje:.1f}" if puntaje is not None else "-")

    col_guardar, col_ayuda = st.columns([1, 1])
    with col_guardar:
        if st.button("Guardar evaluacion"):
            if puntaje is None:
                st.error("Define evidencias consecutivas en al menos una dimensión para calcular el TRL antes de guardar.")
            else:
                try:
                    save_trl_result(project_id, df_respuestas[["dimension", "nivel", "evidencia"]], float(puntaje))
                    st.success("Evaluacion guardada correctamente.")
                except Exception as error:
                    st.error(f"Error al guardar: {error}")

    with col_ayuda:
        st.info(
            "El guardado crea un registro por dimensión con las evidencias acreditadas y asocia el TRL global a la misma fecha de evaluación."
        )
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='section-shell section-shell--split'>", unsafe_allow_html=True)
    st.markdown("#### Radar IRL interactivo")
    radar_col_left, radar_col_right = st.columns([1.1, 1])
    with radar_col_left:
        st.caption("Los niveles mostrados se ajustan automáticamente según la evaluación registrada en las pestañas superiores.")
        _init_irl_state()
        radar_values = {}
        for dimension, _ in IRL_DIMENSIONS:
            valor = st.session_state["irl_scores"].get(dimension, 0)
            radar_values[dimension] = valor
        resumen_df = (
            pd.DataFrame(
                [
                    {"Dimensión": dimension, "Nivel": radar_values.get(dimension, 0)}
                    for dimension, _ in IRL_DIMENSIONS
                ]
            )
            .set_index("Dimensión")
        )
        with st.expander('Resumen numerico IRL', expanded=False):
            st.dataframe(resumen_df, use_container_width=True)

    with radar_col_right:
        labels = list(radar_values.keys())
        values = list(radar_values.values())
        values_cycle = values + values[:1]
        theta = labels + labels[:1]
        radar_fig = go.Figure()
        radar_fig.add_trace(
            go.Scatterpolar(
                r=values_cycle,
                theta=theta,
                fill="toself",
                name="Perfil IRL",
                line_color="#3f8144",
                fillcolor="rgba(63, 129, 68, 0.25)",
            )
        )
        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 9])),
            template="plotly_white",
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(radar_fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.subheader("Historial del proyecto")

    historial = get_trl_history(project_id)
    if historial.empty:
        st.warning("Aun no existe historial TRL para este proyecto.")
    else:
        ultimo_registro = historial["fecha_eval"].iloc[0]
        st.caption(f"Ultima evaluacion registrada: {ultimo_registro}")
        with st.expander('Historial de evaluaciones', expanded=False):
            st.dataframe(historial, use_container_width=True, hide_index=True)

        datos_ultimo = historial[historial["fecha_eval"] == ultimo_registro].copy()
        pivot = datos_ultimo.groupby("dimension", as_index=False)["nivel"].mean()
        dimensiones_ids = trl.ids_dimensiones()
        dimensiones_labels = trl.labels_dimensiones()

        pivot["orden"] = pivot["dimension"].apply(lambda dim: dimensiones_ids.index(dim) if dim in dimensiones_ids else 999)
        pivot = pivot.sort_values("orden")
        valores = []
        for dim_id in dimensiones_ids:
            registro = pivot.loc[pivot["dimension"] == dim_id, "nivel"]
            valores.append(float(registro.values[0]) if len(registro) > 0 and pd.notna(registro.values[0]) else np.nan)

        angles = np.linspace(0, 2 * np.pi, len(dimensiones_labels), endpoint=False).tolist()
        valores_ciclo = valores + valores[:1]
        angulos_ciclo = angles + angles[:1]

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={"polar": True})
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles)
        ax.set_xticklabels(dimensiones_labels)
        ax.set_rlabel_position(0)
        ax.set_yticks([1, 3, 5, 7, 9])
        ax.set_ylim(0, 9)

        ax.plot(angulos_ciclo, valores_ciclo, linewidth=2, color="#3f8144")
        ax.fill(angulos_ciclo, valores_ciclo, alpha=0.25, color="#3f8144")

        st.pyplot(fig)

        st.download_button(
            "Descargar historial TRL (CSV)",
            data=historial.to_csv(index=False).encode("utf-8"),
            file_name=f"trl_historial_{seleccion}.csv",
            mime="text/csv",
        )
    st.markdown("</div>", unsafe_allow_html=True)
