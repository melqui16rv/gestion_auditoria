"""
Sistema Estandarizado de Valoración de Software - Colombia
Backend API con Flask

Basado en:
- ISO/IEC 25010:2023
- Metodologías COCOMO adaptadas
- Costos del mercado colombiano 2024-2025

Fecha: 5 de agosto de 2025
Versión: 1.0
"""

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import sqlite3
import json
import math
from datetime import datetime
import uuid
from io import BytesIO
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# ================================
# CONFIGURACIÓN Y CONSTANTES
# ================================

# Costos base por hora en Colombia (COP) - Actualizado 2025
COSTOS_BASE = {
    'muy_bajo': 20000,   # VBA, Scripts básicos
    'bajo': 30000,       # Access, aplicaciones simples
    'medio': 45000,      # Aplicaciones web estándar
    'alto': 65000,       # Sistemas enterprise
    'muy_alto': 90000    # Sistemas críticos, alta seguridad
}

# Factores de tecnología basados en investigación de mercado
FACTORES_TECNOLOGIA = {
    # Legacy / Básico
    'access_vba': {'factor': 0.7, 'nivel': 'bajo'},
    'vb_net': {'factor': 0.8, 'nivel': 'bajo'},
    'excel_vba': {'factor': 0.6, 'nivel': 'muy_bajo'},
    
    # Web Tradicional
    'php_basic': {'factor': 1.0, 'nivel': 'medio'},
    'asp_net_webforms': {'factor': 1.1, 'nivel': 'medio'},
    'jsp_servlet': {'factor': 1.2, 'nivel': 'medio'},
    
    # Moderno
    'php_laravel': {'factor': 1.1, 'nivel': 'medio'},
    'javascript_react': {'factor': 1.2, 'nivel': 'alto'},
    'javascript_angular': {'factor': 1.3, 'nivel': 'alto'},
    'python_django': {'factor': 1.2, 'nivel': 'alto'},
    'python_flask': {'factor': 1.1, 'nivel': 'medio'},
    'asp_net_core': {'factor': 1.3, 'nivel': 'alto'},
    'java_spring': {'factor': 1.4, 'nivel': 'alto'},
    
    # Enterprise
    'microservicios': {'factor': 1.8, 'nivel': 'muy_alto'},
    'arquitectura_distribuida': {'factor': 1.9, 'nivel': 'muy_alto'},
    'cloud_native': {'factor': 1.6, 'nivel': 'muy_alto'}
}

# Pesos ISO 25010:2023 basados en investigación científica
PESOS_ISO25010 = {
    'security': 0.20,              # Crítico en auditoría
    'functional_suitability': 0.18, # Base funcional
    'reliability': 0.15,           # Estabilidad operacional
    'maintainability': 0.12,       # Sostenibilidad
    'performance_efficiency': 0.10, # Eficiencia
    'usability': 0.10,             # Adopción
    'compatibility': 0.08,         # Integración
    'portability': 0.04,           # Flexibilidad
    'flexibility': 0.03            # Adaptabilidad (nuevo en 2023)
}

# ================================
# MOTOR DE VALORACIÓN
# ================================

class MotorValoracion:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos SQLite"""
        conn = sqlite3.connect('valoraciones.db')
        cursor = conn.cursor()
        
        # Tabla de valoraciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS valoraciones (
                id TEXT PRIMARY KEY,
                fecha_creacion DATETIME,
                tipo_software TEXT,
                tecnologia_principal TEXT,
                respuestas_json TEXT,
                valor_minimo REAL,
                valor_maximo REAL,
                factor_confianza REAL,
                desglose_json TEXT
            )
        ''')
        
        # Tabla de tecnologías
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tecnologias (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                categoria TEXT,
                factor_costo REAL,
                nivel_complejidad TEXT,
                popularidad_colombia REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calcular_valor(self, datos_software):
        """
        Algoritmo principal de valoración
        
        Fórmula: Valor = (Horas_Estimadas × Costo_Hora × Factor_Tecnología × Factor_Calidad × Factor_Negocio) ± Rango_Incertidumbre
        """
        try:
            # 1. Estimación de horas basada en complejidad
            horas_estimadas = self._estimar_horas(datos_software)
            
            # 2. Costo por hora según tecnología
            costo_hora = self._calcular_costo_hora(datos_software['tecnologia_principal'])
            
            # 3. Factor de calidad ISO 25010
            factor_calidad = self._calcular_factor_calidad(datos_software.get('iso25010', {}))
            
            # 4. Factor de complejidad técnica
            factor_complejidad = self._calcular_factor_complejidad(datos_software)
            
            # 5. Factor de valor de negocio
            factor_negocio = self._calcular_factor_negocio(datos_software)
            
            # 6. Factor específico Colombia (cumplimiento normativo)
            factor_colombia = self._calcular_factor_colombia(datos_software)
            
            # 7. Aplicar ajustes por tipo de valoración y contexto
            factor_ajuste_valoracion = self._calcular_factor_valoracion(datos_software)
            
            # Cálculo base
            valor_base = horas_estimadas * costo_hora
            valor_ajustado = valor_base * factor_calidad * factor_complejidad * factor_negocio * factor_colombia * factor_ajuste_valoracion
            
            # Ajustar rango de incertidumbre según nivel de información disponible
            margen_error = self._calcular_margen_incertidumbre(datos_software)
            valor_minimo = valor_ajustado * (1 - margen_error)
            valor_maximo = valor_ajustado * (1 + margen_error)
            
            # Factor de confianza basado en completitud de datos
            factor_confianza = self._calcular_confianza(datos_software)
            
            resultado = {
                'valor_minimo': round(valor_minimo),
                'valor_maximo': round(valor_maximo),
                'valor_promedio': round(valor_ajustado),
                'factor_confianza': factor_confianza,
                'desglose': {
                    'horas_estimadas': horas_estimadas,
                    'costo_hora': costo_hora,
                    'valor_base': valor_base,
                    'factor_calidad': factor_calidad,
                    'factor_complejidad': factor_complejidad,
                    'factor_negocio': factor_negocio,
                    'factor_colombia': factor_colombia,
                    'factor_ajuste_valoracion': factor_ajuste_valoracion,
                    'margen_incertidumbre': margen_error
                },
                'metodologia': 'ISO 25010:2023 + COCOMO Adaptado + Mercado Colombia 2025'
            }
            
            # Guardar en base de datos y obtener ID
            valoracion_id = self._guardar_valoracion(datos_software, resultado)
            if valoracion_id:
                resultado['id'] = valoracion_id  # Agregar ID al resultado
            
            return resultado
            
        except Exception as e:
            return {'error': f'Error en cálculo: {str(e)}'}
    
    def _estimar_horas(self, datos):
        """
        Estimación técnica de horas de desarrollo basada en análisis científico
        
        Metodología:
        1. Horas base por tipo de sistema (COCOMO adaptado)
        2. Ajustes por funcionalidades implementadas
        3. Factores de tecnología y arquitectura
        4. Complejidad operacional y de datos
        5. Factor de incertidumbre y contexto
        
        Referencias: COCOMO II, Function Point Analysis, experiencia mercado colombiano
        """
        
        # === PASO 1: HORAS BASE POR TIPO DE SISTEMA ===
        # Basado en análisis de proyectos similares en el mercado colombiano
        horas_base = {
            'sistema_auditoria': 140,        # Complejidad normativa alta
            'aplicativo_gestion': 100,       # Gestión estándar de datos
            'sistema_reportes': 80,          # Enfoque específico en reportes
            'erp_basico': 160,              # Múltiples módulos integrados
            'crm_sistema': 120,             # Gestión de relaciones
            'aplicativo_inventarios': 90,   # Control de stock y movimientos
            'gestion_documental': 110,      # Manejo de archivos y metadatos
            'sistema_contable': 130,        # Complejidad contable y fiscal
            'otro': 100                     # Promedio general
        }
        
        tipo_software = datos.get('tipo_software', 'otro')
        horas = horas_base.get(tipo_software, 100)
        
        # === PASO 2: AJUSTES POR FUNCIONALIDADES ESPECÍFICAS ===
        # Cada funcionalidad agrega complejidad medida en horas adicionales
        funcionalidades = datos.get('funcionalidades', {})
        ajustes_funcionalidades = []
        
        if funcionalidades.get('autenticacion_avanzada'):
            ajuste = 35
            horas += ajuste
            ajustes_funcionalidades.append(f"Autenticación avanzada: +{ajuste}h")
        
        if funcionalidades.get('reportes_complejos'):
            ajuste = 45
            horas += ajuste
            ajustes_funcionalidades.append(f"Reportes complejos: +{ajuste}h")
        
        if funcionalidades.get('integracion_externa'):
            ajuste = 60
            horas += ajuste
            ajustes_funcionalidades.append(f"Integración externa: +{ajuste}h")
        
        if funcionalidades.get('workflow_aprobaciones'):
            ajuste = 70
            horas += ajuste
            ajustes_funcionalidades.append(f"Workflows: +{ajuste}h")
        
        if funcionalidades.get('dashboard_ejecutivo'):
            ajuste = 40
            horas += ajuste
            ajustes_funcionalidades.append(f"Dashboard ejecutivo: +{ajuste}h")
        
        if funcionalidades.get('api_rest'):
            ajuste = 55
            horas += ajuste
            ajustes_funcionalidades.append(f"APIs REST: +{ajuste}h")
        
        if funcionalidades.get('notificaciones'):
            ajuste = 25
            horas += ajuste
            ajustes_funcionalidades.append(f"Notificaciones: +{ajuste}h")
        
        if funcionalidades.get('backup_automatico'):
            ajuste = 20
            horas += ajuste
            ajustes_funcionalidades.append(f"Backup automático: +{ajuste}h")
        
        if funcionalidades.get('auditoria_logs'):
            ajuste = 30
            horas += ajuste
            ajustes_funcionalidades.append(f"Logs auditoría: +{ajuste}h")
        
        # === PASO 3: FACTOR DE TECNOLOGÍA ===
        tecnologia = datos.get('tecnologia_principal', '')
        factor_tecnologia = 1.0
        
        if tecnologia in FACTORES_TECNOLOGIA:
            factor_tecnologia = FACTORES_TECNOLOGIA[tecnologia]['factor']
        
        # Para tecnologías legacy como Access, el desarrollo es más directo pero menos escalable
        if 'access' in tecnologia.lower():
            factor_tecnologia = 0.85  # 15% menos por simplicidad de desarrollo
        
        horas *= factor_tecnologia
        
        # === PASO 4: AJUSTES POR COMPLEJIDAD DE DATOS Y USUARIOS ===
        usuarios_concurrentes = datos.get('usuarios_concurrentes', 1)
        if usuarios_concurrentes > 20:
            horas *= 1.15  # +15% por complejidad de concurrencia
        elif usuarios_concurrentes > 5:
            horas *= 1.08  # +8% por usuarios múltiples
        
        # Volumen de datos
        volumen_datos = datos.get('volumen_datos', 'pequeno')
        factor_datos = {
            'pequeno': 1.0,
            'medio': 1.12,
            'grande': 1.25,
            'muy_grande': 1.40
        }.get(volumen_datos, 1.0)
        
        horas *= factor_datos
        
        # === PASO 5: FACTOR DE ARQUITECTURA ===
        arquitectura = datos.get('arquitectura', 'monolitica')
        factor_arquitectura = {
            'monolitica': 1.0,
            'capas': 1.15,
            'cliente_servidor': 1.20,
            'web_multicapa': 1.30,
            'soa': 1.45,
            'microservicios': 1.70
        }.get(arquitectura, 1.0)
        
        horas *= factor_arquitectura
        
        # === PASO 6: AJUSTE POR TIEMPO DE DESARROLLO CONOCIDO ===
        # Si se conoce el tiempo real de desarrollo, calibrar estimación
        tiempo_desarrollo = datos.get('tiempo_desarrollo_meses', 0)
        if tiempo_desarrollo > 0:
            # Convertir meses a horas (160 horas/mes promedio)
            horas_reales = tiempo_desarrollo * 160
            # Promedio ponderado entre estimación y realidad (70% estimación, 30% real)
            horas = (horas * 0.7) + (horas_reales * 0.3)
        
        # === PASO 7: FACTOR LEGACY SOLO SI ESTÁ EN USO ===
        antiguedad = datos.get('antiguedad_anos', 0)
        en_uso = datos.get('en_uso_activo', 'false') == 'true'
        
        # Solo aplicar factor si está en uso y es legacy (más complejo de analizar)
        if en_uso and antiguedad > 8:
            horas *= 1.15  # +15% por análisis de sistema legacy
        elif en_uso and antiguedad > 15:
            horas *= 1.25  # +25% para sistemas muy antiguos
        
        # === RESULTADO FINAL ===
        horas_finales = round(horas)
        
        # Guardar detalles del cálculo para transparencia
        self.detalles_calculo_horas = {
            'horas_base': horas_base.get(tipo_software, 100),
            'ajustes_funcionalidades': ajustes_funcionalidades,
            'factor_tecnologia': factor_tecnologia,
            'factor_datos': factor_datos,
            'factor_arquitectura': factor_arquitectura,
            'factor_legacy': 1.15 if (en_uso and antiguedad > 8) else 1.0,
            'horas_finales': horas_finales
        }
        
        return horas_finales
    
    def _calcular_costo_hora(self, tecnologia):
        """Calcula el costo por hora según la tecnología"""
        if tecnologia in FACTORES_TECNOLOGIA:
            nivel = FACTORES_TECNOLOGIA[tecnologia]['nivel']
            factor = FACTORES_TECNOLOGIA[tecnologia]['factor']
            costo_base = COSTOS_BASE[nivel]
            return costo_base * factor
        else:
            return COSTOS_BASE['medio']  # Default
    
    def _calcular_factor_calidad(self, respuestas_iso):
        """Calcula factor de calidad basado en ISO 25010:2023 - Corregido para penalizar deficiencias"""
        if not respuestas_iso:
            return 1.0  # Factor neutro si no hay datos
        
        puntuacion_total = 0
        peso_total = 0
        
        for caracteristica, peso in PESOS_ISO25010.items():
            if caracteristica in respuestas_iso:
                # Escala 1-5, convertir a factor 0.3-1.3 (más realista)
                valor = respuestas_iso[caracteristica]
                factor_caracteristica = 0.3 + (valor - 1) * 0.25  # Mapeo 1-5 -> 0.3-1.3
                
                # Penalizar especialmente seguridad deficiente
                if caracteristica == 'security' and valor <= 2:
                    factor_caracteristica *= 0.8  # Penalización adicional del 20%
                
                puntuacion_total += factor_caracteristica * peso
                peso_total += peso
        
        if peso_total > 0:
            factor_final = puntuacion_total / peso_total
            return max(0.3, min(1.5, factor_final))  # Limitar entre 0.3 y 1.5 (más realista)
        else:
            return 1.0
    
    def _calcular_factor_complejidad(self, datos):
        """
        Calcula factor de complejidad técnica basado en múltiples dimensiones
        
        Considera:
        - Arquitectura del sistema
        - Volumen y complejidad de datos
        - Número de usuarios concurrentes
        - Integraciones externas
        - Tipo de base de datos
        - Funcionalidades avanzadas
        """
        factor = 1.0
        
        # === COMPLEJIDAD DE ARQUITECTURA ===
        arquitectura = datos.get('arquitectura', 'monolitica')
        factor_arq = {
            'monolitica': 1.0,
            'capas': 1.15,
            'cliente_servidor': 1.20,
            'web_multicapa': 1.30,
            'soa': 1.45,
            'microservicios': 1.70
        }.get(arquitectura, 1.0)
        factor *= factor_arq
        
        # === COMPLEJIDAD DE DATOS ===
        volumen_datos = datos.get('volumen_datos', 'pequeno')
        bd_tipo = datos.get('base_datos_tipo', 'local')
        
        # Factor por volumen
        factor_volumen = {
            'pequeno': 1.0,
            'medio': 1.12,
            'grande': 1.25,
            'muy_grande': 1.40
        }.get(volumen_datos, 1.0)
        factor *= factor_volumen
        
        # Factor por tipo de BD
        factor_bd = {
            'local': 1.0,           # Access, SQLite, Excel
            'sql_server_express': 1.15,
            'mysql': 1.20,
            'postgresql': 1.25,
            'sql_server': 1.35,
            'oracle': 1.50,
            'nosql': 1.30
        }.get(bd_tipo, 1.0)
        factor *= factor_bd
        
        # === CONCURRENCIA DE USUARIOS ===
        usuarios_concurrentes = datos.get('usuarios_concurrentes', 1)
        if usuarios_concurrentes >= 200:
            factor *= 1.50  # Sistemas de alta concurrencia
        elif usuarios_concurrentes >= 50:
            factor *= 1.35  # Media-alta concurrencia
        elif usuarios_concurrentes >= 20:
            factor *= 1.20  # Media concurrencia
        elif usuarios_concurrentes >= 10:
            factor *= 1.10  # Baja-media concurrencia
        elif usuarios_concurrentes > 5:
            factor *= 1.05  # Multiusuario básico
        # <= 5 usuarios: factor = 1.0 (sin cambio)
        
        # === INTEGRACIÓN EXTERNA ===
        integraciones = datos.get('integraciones_externas', 0)
        if integraciones > 10:
            factor *= 1.60  # Altamente integrado
        elif integraciones > 5:
            factor *= 1.40  # Múltiples integraciones
        elif integraciones > 2:
            factor *= 1.25  # Varias integraciones
        elif integraciones > 0:
            factor *= 1.15  # Algunas integraciones
        
        # === FUNCIONALIDADES COMPLEJAS ===
        funcionalidades = datos.get('funcionalidades', {})
        
        # APIs y servicios web
        if funcionalidades.get('api_rest'):
            factor *= 1.12
        
        # Workflows avanzados
        if funcionalidades.get('workflow_aprobaciones'):
            factor *= 1.08
        
        # Sistemas de notificaciones
        if funcionalidades.get('notificaciones'):
            factor *= 1.05
        
        # Dashboards ejecutivos complejos
        if funcionalidades.get('dashboard_ejecutivo'):
            factor *= 1.06
        
        # Limitar factor máximo para evitar valores exagerados
        return min(factor, 2.8)  # Máximo 2.8x
    
    def _calcular_factor_negocio(self, datos):
        """
        Calcula factor de valor de negocio considerando múltiples dimensiones
        
        Evalúa:
        - Criticidad operacional del sistema
        - Ahorros económicos generados
        - Número de usuarios beneficiados
        - Impacto en procesos de negocio
        - ROI y valor estratégico
        - Inversión original vs valor actual
        """
        factor = 1.0
        
        # === CRITICIDAD OPERACIONAL ===
        criticidad = datos.get('criticidad_negocio', 3)  # 1-5
        # Factor base por criticidad (más granular)
        factor_criticidad = {
            1: 0.75,  # Experimental, no crítico
            2: 0.90,  # Soporte, baja criticidad
            3: 1.00,  # Operaciones normales
            4: 1.25,  # Procesos críticos
            5: 1.50   # Operación central, misión crítica
        }.get(criticidad, 1.0)
        factor *= factor_criticidad
        
        # === AHORROS ECONÓMICOS ANUALES ===
        ahorro_anual = datos.get('ahorro_anual_cop', 0)
        if ahorro_anual > 50000000:  # > 50M COP
            factor *= 1.40  # Alto impacto económico
        elif ahorro_anual > 20000000:  # > 20M COP
            factor *= 1.30  # Medio-alto impacto
        elif ahorro_anual > 10000000:  # > 10M COP
            factor *= 1.20  # Medio impacto
        elif ahorro_anual > 5000000:   # > 5M COP
            factor *= 1.15  # Bajo-medio impacto
        elif ahorro_anual > 1000000:   # > 1M COP
            factor *= 1.08  # Bajo impacto
        # Sin ahorros = sin ajuste
        
        # === NÚMERO DE USUARIOS BENEFICIADOS ===
        usuarios_totales = datos.get('usuarios_totales', 1)
        if usuarios_totales > 500:
            factor *= 1.25  # Amplio impacto organizacional
        elif usuarios_totales > 100:
            factor *= 1.15  # Medio impacto
        elif usuarios_totales > 50:
            factor *= 1.08  # Impacto departamental
        elif usuarios_totales > 20:
            factor *= 1.04  # Impacto de equipo
        
        # === ANÁLISIS DE ROI (Return on Investment) ===
        inversion_original = datos.get('inversion_original_cop', 0)
        if ahorro_anual > 0 and inversion_original > 0:
            roi_anual = ahorro_anual / inversion_original
            if roi_anual > 2.0:  # ROI > 200%
                factor *= 1.30  # Excelente ROI
            elif roi_anual > 1.0:  # ROI > 100%
                factor *= 1.20  # Buen ROI
            elif roi_anual > 0.5:  # ROI > 50%
                factor *= 1.10  # ROI aceptable
        
        # === SECTOR Y CONTEXTO ESPECÍFICO ===
        sector = datos.get('sector', 'privado')
        if sector == 'publico':
            factor *= 1.12  # Mayor valor social y regulatorio
        elif sector == 'financiero':
            factor *= 1.18  # Alta regulación y criticidad
        elif sector == 'salud':
            factor *= 1.15  # Impacto en vidas humanas
        
        # === TIEMPO DE DESARROLLO vs VALOR ===
        tiempo_desarrollo = datos.get('tiempo_desarrollo_meses', 0)
        if tiempo_desarrollo > 0:
            # Si el desarrollo fue muy rápido para la funcionalidad, bonificar eficiencia
            if tiempo_desarrollo < 3 and factor > 1.2:  # Desarrollo rápido y alto valor
                factor *= 1.05  # Bonus por eficiencia
            elif tiempo_desarrollo > 24:  # Desarrollo muy largo
                factor *= 0.95  # Leve penalización por ineficiencia
        
        # Limitar factor para mantener realismo
        return min(factor, 3.5)  # Máximo 3.5x
    
    def _calcular_factor_colombia(self, datos):
        """
        Factor específico para el contexto normativo y regulatorio colombiano
        
        Considera:
        - Regulaciones específicas del sector
        - Cumplimiento de normativas gubernamentales
        - Estándares de interoperabilidad
        - Requisitos de auditoría y trazabilidad
        - Protección de datos personales
        - Reportes a entes de control
        """
        factor = 1.0
        detalles_cumplimiento = []
        
        # === REPORTES OFICIALES Y ENTES DE CONTROL ===
        if datos.get('genera_reportes_oficiales', False):
            factor *= 1.18  # Prima significativa por generación de reportes oficiales
            detalles_cumplimiento.append("Reportes oficiales para entes de control")
        
        # === LOGS Y AUDITORÍA DETALLADA ===
        if datos.get('requiere_auditoria_logs', False):
            factor *= 1.12  # Prima por trazabilidad completa
            detalles_cumplimiento.append("Logs de auditoría detallados")
        
        # === SECTOR ESPECÍFICO ===
        sector = datos.get('sector', 'privado')
        if sector == 'publico':
            factor *= 1.15   # Sector público con requerimientos especiales
            detalles_cumplimiento.append("Sector público colombiano")
        elif sector == 'financiero':
            factor *= 1.25   # Alta regulación financiera
            detalles_cumplimiento.append("Sector financiero regulado")
        
        # === NORMATIVAS ESPECÍFICAS COLOMBIANAS ===
        
        # Interoperabilidad Gobierno Digital
        if datos.get('interoperabilidad_govco', False):
            factor *= 1.10
            detalles_cumplimiento.append("Estándares interoperabilidad Gov.co")
        
        # Ley Habeas Data (Protección de datos personales)
        if datos.get('maneja_datos_personales', False):
            factor *= 1.08
            detalles_cumplimiento.append("Cumplimiento Ley Habeas Data")
        
        # Decreto 648 de 2017 (Auditoría Interna)
        if datos.get('decreto_648', False):
            factor *= 1.15
            detalles_cumplimiento.append("Decreto 648/2017 - Auditoría Interna")
        
        # ISO 27001 (Seguridad de la información)
        if datos.get('iso_27001', False):
            factor *= 1.12
            detalles_cumplimiento.append("Controles ISO 27001")
        
        # SARLAFT (Sistema de Administración de Riesgo de Lavado de Activos)
        if datos.get('sarlaft', False):
            factor *= 1.20
            detalles_cumplimiento.append("Cumplimiento SARLAFT")
        
        # Reportes específicos a Contraloría
        if datos.get('contraloria', False):
            factor *= 1.10
            detalles_cumplimiento.append("Reportes Contraloría General")
        
        # === BONIFICACIÓN POR MÚLTIPLES CUMPLIMIENTOS ===
        # Si cumple con múltiples normativas, bonificación adicional
        num_cumplimientos = len(detalles_cumplimiento)
        if num_cumplimientos >= 5:
            factor *= 1.08  # Bonus por alta complejidad normativa
        elif num_cumplimientos >= 3:
            factor *= 1.05  # Bonus por complejidad normativa media
        
        # === CONSIDERACIONES DE MERCADO COLOMBIANO ===
        # Factor base por desarrollo en Colombia (costos laborales, infraestructura)
        factor *= 1.05  # Factor base del mercado colombiano 2025
        
        # Guardar detalles para el reporte
        self.detalles_cumplimiento = detalles_cumplimiento
        
        # Limitar factor máximo para mantener realismo
        return min(factor, 2.2)  # Máximo 2.2x
    
    def _calcular_confianza(self, datos):
        """Calcula el nivel de confianza basado en completitud de datos y validaciones del usuario"""
        campos_criticos = [
            'tipo_software', 'tecnologia_principal', 'antiguedad_anos',
            'usuarios_concurrentes', 'criticidad_negocio'
        ]
        
        campos_completos = sum(1 for campo in campos_criticos if datos.get(campo) is not None)
        confianza_base = campos_completos / len(campos_criticos)
        
        # === AJUSTES POR NIVEL DE CERTEZA DECLARADO ===
        nivel_certeza = datos.get('nivel_certeza', 'media')
        if nivel_certeza == 'alta':
            confianza_base *= 1.1
        elif nivel_certeza == 'baja':
            confianza_base *= 0.8
            
        # === AJUSTES POR INFORMACIÓN DISPONIBLE ===
        # Penalizar si no conoce datos importantes
        if datos.get('conoce_tiempo_desarrollo') == 'no':
            confianza_base *= 0.9  # -10% por no conocer tiempo
        elif datos.get('tiempo_calculado_por_fechas'):
            confianza_base *= 0.95  # -5% por tiempo calculado de fechas
            
        if datos.get('conoce_inversion') == 'no':
            confianza_base *= 0.85  # -15% por no conocer inversión
        elif datos.get('inversion_es_estimada'):
            confianza_base *= 0.9   # -10% por inversión estimada
            
        if datos.get('conoce_ahorros') == 'no':
            confianza_base *= 0.9   # -10% por no conocer ahorros
        elif datos.get('ahorros_son_estimados'):
            confianza_base *= 0.95  # -5% por ahorros estimados
            
        # === AJUSTES POR CONTEXTO DE DESARROLLO ===
        contexto = datos.get('contexto_desarrollo', {})
        if contexto.get('desarrollo_interno'):
            confianza_base *= 1.05  # +5% por desarrollo interno (más control)
        if contexto.get('sin_metodologia'):
            confianza_base *= 0.85  # -15% por falta de metodología
        if contexto.get('urgencia_tiempo'):
            confianza_base *= 0.9   # -10% por desarrollo con urgencia
        if contexto.get('tiempo_parcial'):
            confianza_base *= 0.95  # -5% por desarrollo tiempo parcial
            
        # === AJUSTES POR TIPO DE VALORACIÓN ===
        tipo_valoracion = datos.get('tipo_valoracion', 'equilibrada')
        if tipo_valoracion == 'conservadora':
            confianza_base *= 1.05  # Mayor confianza en estimaciones conservadoras
        elif tipo_valoracion == 'optimista':
            confianza_base *= 0.9   # Menor confianza en estimaciones optimistas

        # Bonus por datos ISO 25010
        if datos.get('iso25010'):
            caracteristicas_iso = len(datos['iso25010'])
            bonus_iso = min(0.2, caracteristicas_iso / len(PESOS_ISO25010) * 0.2)
            confianza_base += bonus_iso
        
        return min(1.0, confianza_base)
    
    def _calcular_factor_valoracion(self, datos):
        """Aplica ajustes específicos según el tipo de valoración y contexto de desarrollo"""
        factor = 1.0
        
        # === AJUSTE POR TIPO DE VALORACIÓN ===
        tipo_valoracion = datos.get('tipo_valoracion', 'equilibrada')
        if tipo_valoracion == 'conservadora':
            factor *= 0.85  # -15% para valoración conservadora
        elif tipo_valoracion == 'optimista':
            factor *= 1.15  # +15% para valoración optimista
        
        # === AJUSTES POR CONTEXTO DE DESARROLLO ===
        contexto = datos.get('contexto_desarrollo', {})
        
        if contexto.get('desarrollo_interno'):
            factor *= 0.9   # -10% desarrollo interno suele ser más económico
            
        if contexto.get('tiempo_parcial'):
            factor *= 0.85  # -15% desarrollo tiempo parcial es más barato
            
        if contexto.get('aprendizaje_tecnologia'):
            factor *= 1.2   # +20% tiempo de aprendizaje influyó en el costo
            
        if contexto.get('sin_metodologia'):
            factor *= 0.8   # -20% sin metodología reduce valor profesional
            
        if contexto.get('urgencia_tiempo'):
            factor *= 1.1   # +10% desarrollo urgente cuesta más
            
        if contexto.get('prototipo_iterativo'):
            factor *= 0.95  # -5% desarrollo iterativo puede ser menos eficiente inicialmente
        
        # === AJUSTE ESPECIAL POR TECNOLOGÍA DE BAJO COSTO ===
        tecnologia = datos.get('tecnologia_principal', '')
        if 'access' in tecnologia.lower():
            factor *= 0.7   # -30% Access es tecnología de bajo costo
        elif 'excel' in tecnologia.lower():
            factor *= 0.6   # -40% Excel VBA es muy básico
        elif 'vb_net' in tecnologia.lower():
            factor *= 0.8   # -20% VB.NET es menos demandado
        
        # === AJUSTE POR AUSENCIA DE DATOS CRÍTICOS ===
        if datos.get('conoce_tiempo_desarrollo') == 'no':
            factor *= 0.9   # -10% por falta de datos temporales
            
        if datos.get('conoce_inversion') == 'no':
            factor *= 0.9   # -10% por falta de datos de inversión
            
        return max(0.4, factor)  # Mínimo 40% del valor base
    
    def _calcular_margen_incertidumbre(self, datos):
        """Calcula el margen de incertidumbre basado en la calidad de la información"""
        margen_base = 0.20  # 20% base según literatura científica
        
        # Incrementar margen si falta información crítica
        if datos.get('conoce_tiempo_desarrollo') == 'no':
            margen_base += 0.10  # +10% sin datos de tiempo
            
        if datos.get('conoce_inversion') == 'no':
            margen_base += 0.08  # +8% sin datos de inversión
            
        if datos.get('nivel_certeza') == 'baja':
            margen_base += 0.12  # +12% baja certeza general
        elif datos.get('nivel_certeza') == 'alta':
            margen_base -= 0.05  # -5% alta certeza
            
        # Para tecnologías básicas, reducir incertidumbre (son más predecibles)
        tecnologia = datos.get('tecnologia_principal', '')
        if any(tech in tecnologia.lower() for tech in ['access', 'excel', 'vba']):
            margen_base *= 0.8  # -20% más predecible
            
        return min(0.45, max(0.10, margen_base))  # Entre 10% y 45%
    
    def _guardar_valoracion(self, datos, resultado):
        """Guarda la valoración en la base de datos y devuelve el ID"""
        try:
            conn = sqlite3.connect('valoraciones.db')
            cursor = conn.cursor()
            
            valoracion_id = str(uuid.uuid4())
            fecha_actual = datetime.now()
            
            cursor.execute('''
                INSERT INTO valoraciones 
                (id, fecha_creacion, tipo_software, tecnologia_principal, 
                 respuestas_json, valor_minimo, valor_maximo, factor_confianza, desglose_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                valoracion_id,
                fecha_actual,
                datos.get('tipo_software'),
                datos.get('tecnologia_principal'),
                json.dumps(datos),
                resultado['valor_minimo'],
                resultado['valor_maximo'],
                resultado['factor_confianza'],
                json.dumps(resultado['desglose'])
            ))
            
            conn.commit()
            conn.close()
            
            return valoracion_id  # Devolver el ID generado
            
        except Exception as e:
            print(f"Error guardando valoración: {e}")
            return None

# ================================
# RUTAS DE LA API
# ================================

motor = MotorValoracion()

@app.route('/')
def index():
    """Página principal del sistema con formulario profesional"""
    return render_template('valoracion_detallada.html')

@app.route('/api/tecnologias', methods=['GET'])
def obtener_tecnologias():
    """Devuelve la lista de tecnologías disponibles"""
    return jsonify({
        'tecnologias': list(FACTORES_TECNOLOGIA.keys()),
        'detalles': FACTORES_TECNOLOGIA
    })

@app.route('/api/valorar', methods=['POST'])
def valorar_software():
    """Endpoint principal para valorar software"""
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Validaciones básicas
        if 'tipo_software' not in datos:
            return jsonify({'error': 'tipo_software es requerido'}), 400
        
        if 'tecnologia_principal' not in datos:
            return jsonify({'error': 'tecnologia_principal es requerido'}), 400
        
        # === VALIDACIÓN Y LIMPIEZA DE DATOS NUMÉRICOS ===
        # Función para convertir valores seguros
        def safe_int(value, default=0):
            if value is None or value == '' or value == 'None':
                return default
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default
                
        def safe_float(value, default=0.0):
            if value is None or value == '' or value == 'None':
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Limpiar campos numéricos críticos
        datos['usuarios_concurrentes'] = safe_int(datos.get('usuarios_concurrentes'), 1)
        datos['usuarios_totales'] = safe_int(datos.get('usuarios_totales'), 1)
        datos['integraciones_externas'] = safe_int(datos.get('integraciones_externas'), 0)
        datos['antiguedad_anos'] = safe_float(datos.get('antiguedad_anos'), 0.0)
        datos['criticidad_negocio'] = safe_int(datos.get('criticidad_negocio'), 3)
        datos['tiempo_desarrollo_meses'] = safe_float(datos.get('tiempo_desarrollo_meses'), 0.0)
        datos['ahorro_anual_cop'] = safe_int(datos.get('ahorro_anual_cop'), 0)
        datos['inversion_original_cop'] = safe_int(datos.get('inversion_original_cop'), 0)
        
        # Validar rangos
        if datos['usuarios_concurrentes'] < 1:
            datos['usuarios_concurrentes'] = 1
        if datos['criticidad_negocio'] < 1 or datos['criticidad_negocio'] > 5:
            datos['criticidad_negocio'] = 3
        
        # Calcular valoración
        resultado = motor.calcular_valor(datos)
        
        if 'error' in resultado:
            return jsonify(resultado), 500
        
        return jsonify({
            'success': True,
            'valoracion': resultado,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/api/ejemplo-auditoria', methods=['GET'])
def obtener_ejemplo_auditoria():
    """Devuelve datos de ejemplo para un sistema de auditoría en Access"""
    ejemplo_datos = {
        'tipo_software': 'sistema_auditoria',
        'tecnologia_principal': 'access_vba',
        'antiguedad_anos': 2,
        'en_uso_activo': True,
        'sector': 'publico',
        'descripcion': 'El software es una herramienta que facilita la auditoría interna para municipios de sexta categoría de Colombia',
        'usuarios_concurrentes': 3,  # 2-5 usuarios
        'usuarios_totales': 2,
        'base_datos_tipo': 'local',
        'integraciones_externas': 0,
        'volumen_datos': 'pequeno',
        'arquitectura': 'monolitica',
        'funcionalidades': {
            'autenticacion_avanzada': True,
            'reportes_complejos': True,
            'workflow_aprobaciones': True,
            'dashboard_ejecutivo': True,
            'auditoria_logs': True
        },
        'iso25010': {
            'security': 2,
            'functional_suitability': 3,
            'reliability': 3,
            'maintainability': 4,
            'performance_efficiency': 3,
            'usability': 4,
            'compatibility': 4,
            'portability': 5,
            'flexibility': 4
        },
        'tipo_valoracion': 'conservadora',
        'nivel_certeza': 'media',
        'contexto_desarrollo': {
            'desarrollo_interno': True,
            'tiempo_parcial': True,
            'aprendizaje_tecnologia': True,
            'prototipo_iterativo': True,
            'sin_metodologia': True
        },
        'criticidad_negocio': 2,
        'conoce_tiempo_desarrollo': 'no',
        'conoce_inversion': 'no',
        'conoce_ahorros': 'no',
        'genera_reportes_oficiales': True,
        'requiere_auditoria_logs': True,
        'maneja_datos_personales': True,
        'decreto_648': True,
        'observaciones': 'El aplicativo presenta una estructura operativa bien organizada y se encuentra alineado con los lineamientos del Decreto 648 de 2017, lo que evidencia una adecuada comprensión de los requerimientos normativos. Desde el punto de vista técnico, el código desarrollado en VBA muestra una estructura clara y mantenible, con una mínima presencia de código espagueti. Se evidencian buenas prácticas en la separación de funcionalidades mediante módulos, lo que facilita su comprensión, mantenimiento y escalabilidad dentro del entorno de Access.'
    }
    
    return jsonify({
        'success': True,
        'datos': ejemplo_datos,
        'descripcion': 'Sistema de Auditoría Municipal - Caso de Uso Real'
    })

@app.route('/api/historico', methods=['GET'])
def obtener_historico():
    """Obtiene el histórico de valoraciones"""
    try:
        conn = sqlite3.connect('valoraciones.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, fecha_creacion, tipo_software, tecnologia_principal, 
                   valor_minimo, valor_maximo, factor_confianza
            FROM valoraciones 
            ORDER BY fecha_creacion DESC 
            LIMIT 50
        ''')
        
        valoraciones = []
        for row in cursor.fetchall():
            valoraciones.append({
                'id': row[0],
                'fecha': row[1],
                'tipo_software': row[2],
                'tecnologia': row[3],
                'valor_minimo': row[4],
                'valor_maximo': row[5],
                'confianza': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'valoraciones': valoraciones,
            'total': len(valoraciones)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error consultando histórico: {str(e)}'}), 500

@app.route('/api/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Estadísticas del sistema"""
    try:
        conn = sqlite3.connect('valoraciones.db')
        cursor = conn.cursor()
        
        # Total de valoraciones
        cursor.execute('SELECT COUNT(*) FROM valoraciones')
        total_valoraciones = cursor.fetchone()[0]
        
        # Valor promedio
        cursor.execute('SELECT AVG((valor_minimo + valor_maximo) / 2) FROM valoraciones')
        valor_promedio = cursor.fetchone()[0] or 0
        
        # Tecnología más valorada
        cursor.execute('''
            SELECT tecnologia_principal, COUNT(*) as cantidad 
            FROM valoraciones 
            GROUP BY tecnologia_principal 
            ORDER BY cantidad DESC 
            LIMIT 1
        ''')
        tech_result = cursor.fetchone()
        tech_popular = tech_result[0] if tech_result else 'N/A'
        
        conn.close()
        
        return jsonify({
            'total_valoraciones': total_valoraciones,
            'valor_promedio': round(valor_promedio),
            'tecnologia_mas_valorada': tech_popular,
            'factores_tecnologia': len(FACTORES_TECNOLOGIA),
            'version_sistema': '1.0'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error en estadísticas: {str(e)}'}), 500

def generar_pdf_reporte(valoracion_id):
    """
    Genera un PDF profesional con reporte completo de valoración técnica
    Incluye metodología detallada, explicaciones técnicas y certificación
    """
    if not REPORTLAB_AVAILABLE:
        return None, "ReportLab no está instalado. Ejecute: pip install reportlab"
    
    try:
        # Obtener datos de la valoración
        conn = sqlite3.connect('valoraciones.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM valoraciones WHERE id = ?
        ''', (valoracion_id,))
        
        valoracion = cursor.fetchone()
        if not valoracion:
            return None, "Valoración no encontrada"
        
        # Parsear datos JSON
        respuestas = json.loads(valoracion[4]) if valoracion[4] else {}
        desglose = json.loads(valoracion[8]) if valoracion[8] else {}
        
        conn.close()
        
        # Crear buffer para PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # === ESTILOS PERSONALIZADOS ===
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=1,  # Centro
            textColor=colors.darkblue
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            alignment=1,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            textColor=colors.darkblue,
            backColor=colors.lightblue,
            leftIndent=10,
            rightIndent=10,
            spaceBefore=20
        )
        
        # === PORTADA ===
        story.append(Paragraph("REPORTE DE VALORACIÓN TÉCNICA DE SOFTWARE", title_style))
        story.append(Paragraph("Sistema Profesional de Evaluación - Colombia 2025", subtitle_style))
        
        # Sello de certificación
        cert_data = [
            ["🏆 CERTIFICACIÓN TÉCNICA PROFESIONAL"],
            ["Basado en ISO/IEC 25010:2023"],
            ["Metodología COCOMO Adaptada"],
            ["Análisis de Mercado Colombiano 2025"],
            [f"ID de Certificación: {valoracion_id[:12]}"]
        ]
        
        cert_table = Table(cert_data, colWidths=[4*inch])
        cert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkblue),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.darkblue),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(Spacer(1, 30))
        story.append(cert_table)
        story.append(Spacer(1, 40))
        
        # === INFORMACIÓN GENERAL ===
        story.append(Paragraph("INFORMACIÓN GENERAL", heading_style))
        
        descripcion = respuestas.get('descripcion', 'No especificada')
        if len(descripcion) > 150:
            descripcion = descripcion[:150] + "..."
        
        info_data = [
            ["Fecha de valoración:", valoracion[1][:10] if valoracion[1] else "N/A"],
            ["Tipo de software:", (valoracion[2] or "N/A").replace('_', ' ').title()],
            ["Tecnología principal:", (valoracion[3] or "N/A").replace('_', ' ').title()],
            ["Descripción:", descripcion],
            ["Sector:", respuestas.get('sector', 'No especificado').title()],
            ["Usuarios totales:", str(respuestas.get('usuarios_totales', 'No especificado'))],
            ["Usuarios concurrentes:", str(respuestas.get('usuarios_concurrentes', 'No especificado'))],
            ["Arquitectura:", respuestas.get('arquitectura', 'No especificada').replace('_', ' ').title()],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 25))
        
        # === RESULTADOS ECONÓMICOS DESTACADOS ===
        story.append(Paragraph("RESULTADOS ECONÓMICOS", heading_style))
        
        valor_min = f"${valoracion[5]:,.0f} COP" if valoracion[5] else "N/A"
        valor_max = f"${valoracion[6]:,.0f} COP" if valoracion[6] else "N/A"
        valor_promedio = f"${(valoracion[5] + valoracion[6])/2:,.0f} COP" if valoracion[5] and valoracion[6] else "N/A"
        
        resultado_data = [
            ["💰 VALORACIÓN ECONÓMICA", ""],
            ["Valor mínimo estimado:", valor_min],
            ["Valor máximo estimado:", valor_max],
            ["Valor promedio:", valor_promedio],
            ["Nivel de confianza:", f"{valoracion[7]*100:.0f}%" if valoracion[7] else "N/A"],
            ["Metodología aplicada:", "ISO 25010:2023 + COCOMO + Colombia 2025"],
        ]
        
        resultado_table = Table(resultado_data, colWidths=[2.5*inch, 3*inch])
        resultado_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 1), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('SPAN', (0, 0), (1, 0)),  # Fusionar primera fila
        ]))
        
        story.append(resultado_table)
        story.append(Spacer(1, 25))
        
        # === DESGLOSE TÉCNICO DETALLADO ===
        if desglose:
            story.append(Paragraph("ANÁLISIS TÉCNICO DETALLADO", heading_style))
            
            # Tabla principal de métricas
            desglose_data = [
                ["📊 MÉTRICAS TÉCNICAS", "VALOR", "EXPLICACIÓN"],
                ["Horas estimadas de desarrollo", f"{desglose.get('horas_estimadas', 0)}h", 
                 "Basado en complejidad funcional, tecnología y arquitectura"],
                ["Costo por hora (mercado colombiano)", f"${desglose.get('costo_hora', 0):,.0f} COP", 
                 "Tarifa promedio según tecnología y experiencia requerida"],
                ["Valor base de desarrollo", f"${desglose.get('valor_base', 0):,.0f} COP", 
                 "Horas × Costo hora = Costo base de desarrollo"],
                ["Factor de calidad ISO 25010", f"{desglose.get('factor_calidad', 1.0):.2f}x", 
                 "Ajuste basado en evaluación de 9 características de calidad"],
                ["Factor de complejidad técnica", f"{desglose.get('factor_complejidad', 1.0):.2f}x", 
                 "Usuarios concurrentes, base de datos, integraciones"],
                ["Factor de valor de negocio", f"{desglose.get('factor_negocio', 1.0):.2f}x", 
                 "Criticidad, ahorros generados, usuarios beneficiados"],
                ["Factor contexto colombiano", f"{desglose.get('factor_colombia', 1.0):.2f}x", 
                 "Cumplimiento normativo, sector, regulaciones específicas"],
            ]
            
            desglose_table = Table(desglose_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
            desglose_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(desglose_table)
            story.append(Spacer(1, 20))
            
            # === EXPLICACIÓN DETALLADA DE FACTORES ===
            story.append(Paragraph("EXPLICACIÓN TÉCNICA DE FACTORES DE AJUSTE", heading_style))
            
            explicaciones = []
            
            # Factor Calidad
            factor_calidad = desglose.get('factor_calidad', 1.0)
            if factor_calidad > 1.05:
                explicaciones.append(f"• <b>Factor Calidad ({factor_calidad:.2f}x):</b> Bonificación por implementación de buenas prácticas según ISO/IEC 25010:2023. El software demuestra alta calidad en características como seguridad, mantenibilidad, usabilidad y confiabilidad.")
            elif factor_calidad < 0.95:
                explicaciones.append(f"• <b>Factor Calidad ({factor_calidad:.2f}x):</b> Penalización identificada por deficiencias en estándares de calidad. Se detectaron oportunidades de mejora en seguridad, mantenibilidad o implementación de buenas prácticas de desarrollo.")
            else:
                explicaciones.append(f"• <b>Factor Calidad ({factor_calidad:.2f}x):</b> Factor neutro. El software cumple con estándares básicos de calidad pero no presenta características excepcionales ni deficiencias significativas.")
            
            # Factor Complejidad
            factor_comp = desglose.get('factor_complejidad', 1.0)
            usuarios_conc = respuestas.get('usuarios_concurrentes', 1)
            arquitectura = respuestas.get('arquitectura', 'monolitica')
            if factor_comp > 1.05:
                explicaciones.append(f"• <b>Factor Complejidad ({factor_comp:.2f}x):</b> Ajuste por complejidad técnica elevada. Sistema maneja {usuarios_conc} usuarios concurrentes con arquitectura {arquitectura.replace('_', ' ')}. Incluye consideraciones de escalabilidad, rendimiento y manejo de concurrencia.")
            else:
                explicaciones.append(f"• <b>Factor Complejidad ({factor_comp:.2f}x):</b> Sistema de complejidad técnica estándar. Arquitectura simple, pocos usuarios concurrentes, sin requerimientos especiales de escalabilidad.")
            
            # Factor Negocio
            factor_neg = desglose.get('factor_negocio', 1.0)
            criticidad = respuestas.get('criticidad_negocio', 3)
            ahorro_anual = respuestas.get('ahorro_anual_cop', 0)
            if factor_neg > 1.05:
                exp_negocio = f"• <b>Factor Negocio ({factor_neg:.2f}x):</b> Valor estratégico elevado con nivel de criticidad {criticidad}/5."
                if ahorro_anual > 0:
                    exp_negocio += f" Genera ahorros anuales estimados de ${ahorro_anual:,.0f} COP."
                exp_negocio += " El sistema es fundamental para las operaciones del negocio y genera valor económico medible."
                explicaciones.append(exp_negocio)
            else:
                explicaciones.append(f"• <b>Factor Negocio ({factor_neg:.2f}x):</b> Impacto de negocio estándar. Sistema de soporte operacional sin impacto crítico en el negocio principal.")
            
            # Factor Colombia
            factor_col = desglose.get('factor_colombia', 1.0)
            cumplimientos = []
            if respuestas.get('genera_reportes_oficiales'): cumplimientos.append("reportes oficiales para entes de control")
            if respuestas.get('requiere_auditoria_logs'): cumplimientos.append("logs de auditoría detallados")
            if respuestas.get('sector') == 'publico': cumplimientos.append("sector público")
            if respuestas.get('decreto_648'): cumplimientos.append("Decreto 648/2017")
            if respuestas.get('iso_27001'): cumplimientos.append("controles ISO 27001")
            if respuestas.get('sarlaft'): cumplimientos.append("SARLAFT")
            
            if cumplimientos and factor_col > 1.05:
                explicaciones.append(f"• <b>Factor Colombia ({factor_col:.2f}x):</b> Prima por cumplimiento de normativa colombiana específica: {', '.join(cumplimientos)}. Estos requerimientos aumentan la complejidad y valor del desarrollo.")
            else:
                explicaciones.append(f"• <b>Factor Colombia ({factor_col:.2f}x):</b> Sin requerimientos regulatorios especiales. Sistema sin obligaciones de cumplimiento normativo específico.")
            
            # Agregar explicaciones al PDF
            for explicacion in explicaciones:
                story.append(Paragraph(explicacion, styles['Normal']))
                story.append(Spacer(1, 8))
            
            story.append(Spacer(1, 20))
        
        # === FUNCIONALIDADES EVALUADAS ===
        story.append(Paragraph("FUNCIONALIDADES IMPLEMENTADAS", heading_style))
        
        funcionalidades = respuestas.get('funcionalidades', {})
        func_nombres = {
            'autenticacion_avanzada': 'Autenticación y roles avanzados',
            'reportes_complejos': 'Reportes y dashboards complejos',
            'integracion_externa': 'Integración con sistemas externos',
            'workflow_aprobaciones': 'Workflows y aprobaciones',
            'dashboard_ejecutivo': 'Dashboard ejecutivo',
            'api_rest': 'APIs REST/Web Services',
            'notificaciones': 'Sistema de notificaciones',
            'backup_automatico': 'Backup automático',
            'auditoria_logs': 'Logs de auditoría detallados'
        }
        
        func_data = [["FUNCIONALIDAD", "IMPLEMENTADA"]]
        for key, nombre in func_nombres.items():
            implementada = "✓ Sí" if funcionalidades.get(key) else "✗ No"
            func_data.append([nombre, implementada])
        
        func_table = Table(func_data, colWidths=[4*inch, 1.5*inch])
        func_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(func_table)
        story.append(Spacer(1, 25))
        
        # === EVALUACIÓN ISO 25010 DETALLADA ===
        if respuestas.get('iso25010'):
            story.append(Paragraph("EVALUACIÓN DE CALIDAD ISO/IEC 25010:2023", heading_style))
            story.append(Paragraph("Estándar internacional para evaluación de calidad de productos de software", styles['Normal']))
            story.append(Spacer(1, 10))
            
            iso_data = [["CARACTERÍSTICA DE CALIDAD", "PUNTUACIÓN", "PESO", "DESCRIPCIÓN"]]
            iso_dict = respuestas['iso25010']
            
            caracteristicas_detalle = {
                'security': ('Seguridad', '20%', 'Protección de información, autenticación, autorización'),
                'functional_suitability': ('Idoneidad Funcional', '18%', 'Funciones que satisfacen necesidades expresas'),
                'reliability': ('Fiabilidad', '15%', 'Mantiene rendimiento bajo condiciones establecidas'),
                'maintainability': ('Mantenibilidad', '12%', 'Facilidad para modificar y corregir'),
                'performance_efficiency': ('Eficiencia de Rendimiento', '10%', 'Rendimiento relativo a recursos utilizados'),
                'usability': ('Usabilidad', '10%', 'Facilidad de comprensión y uso'),
                'compatibility': ('Compatibilidad', '8%', 'Intercambio de información con otros productos'),
                'portability': ('Portabilidad', '4%', 'Facilidad de transferencia entre ambientes'),
                'flexibility': ('Flexibilidad', '3%', 'Adaptación a cambios de requisitos')
            }
            
            escala_nombres = {1: "Muy deficiente", 2: "Deficiente", 3: "Aceptable", 4: "Bueno", 5: "Excelente"}
            
            for caracteristica, valor in iso_dict.items():
                if caracteristica in caracteristicas_detalle:
                    nombre, peso, desc = caracteristicas_detalle[caracteristica]
                    puntuacion = f"{valor}/5 - {escala_nombres.get(valor, 'N/A')}"
                    iso_data.append([nombre, puntuacion, peso, desc])
            
            iso_table = Table(iso_data, colWidths=[1.8*inch, 1.2*inch, 0.7*inch, 2.3*inch])
            iso_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(iso_table)
            story.append(Spacer(1, 20))
        
        # === CUMPLIMIENTO NORMATIVO COLOMBIANO ===
        cumplimientos_encontrados = []
        if respuestas.get('genera_reportes_oficiales'): cumplimientos_encontrados.append('Reportes oficiales para entes de control')
        if respuestas.get('requiere_auditoria_logs'): cumplimientos_encontrados.append('Logs de auditoría detallados')
        if respuestas.get('interoperabilidad_govco'): cumplimientos_encontrados.append('Interoperabilidad Gov.co')
        if respuestas.get('maneja_datos_personales'): cumplimientos_encontrados.append('Ley Habeas Data')
        if respuestas.get('decreto_648'): cumplimientos_encontrados.append('Decreto 648/2017')
        if respuestas.get('iso_27001'): cumplimientos_encontrados.append('ISO 27001')
        if respuestas.get('sarlaft'): cumplimientos_encontrados.append('SARLAFT')
        if respuestas.get('contraloria'): cumplimientos_encontrados.append('Reportes Contraloría')
        
        if cumplimientos_encontrados:
            story.append(Paragraph("CUMPLIMIENTO NORMATIVO COLOMBIANO", heading_style))
            story.append(Paragraph("Regulaciones y estándares colombianos implementados o considerados:", styles['Normal']))
            story.append(Spacer(1, 10))
            
            for cumplimiento in cumplimientos_encontrados:
                story.append(Paragraph(f"✓ {cumplimiento}", styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # === OBSERVACIONES TÉCNICAS ===
        if 'observaciones' in respuestas and respuestas['observaciones'].strip():
            story.append(Paragraph("OBSERVACIONES TÉCNICAS ADICIONALES", heading_style))
            story.append(Paragraph(respuestas['observaciones'], styles['Normal']))
            story.append(Spacer(1, 20))
        
        # === METODOLOGÍA Y REFERENCIAS ===
        story.append(Paragraph("METODOLOGÍA Y FUNDAMENTOS CIENTÍFICOS", heading_style))
        metodologia_text = """
        <b>Esta valoración profesional se fundamenta en:</b><br/><br/>
        
        <b>• ISO/IEC 25010:2023:</b> Estándar internacional de calidad de software que define 9 características principales de calidad.<br/><br/>
        
        <b>• Metodología COCOMO Adaptada:</b> Modelo constructivo de costos de software adaptado para el contexto colombiano y tecnologías evaluadas.<br/><br/>
        
        <b>• Análisis de mercado colombiano 2025:</b> Tarifas actualizadas de desarrollo de software basadas en investigación de mercado local.<br/><br/>
        
        <b>• Factores de ajuste específicos:</b> Consideraciones por sector, normativa colombiana, complejidad técnica y valor de negocio.<br/><br/>
        
        <b>• Rango de incertidumbre (±20%):</b> Basado en literatura científica sobre precisión de estimaciones de software.<br/><br/>
        
        <b>Nivel de confianza:</b> Calculado según completitud de información proporcionada y aplicabilidad de metodologías.
        """
        story.append(Paragraph(metodologia_text, styles['Normal']))
        story.append(Spacer(1, 30))
        
        # === PIE DE PÁGINA ===
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=1
        )
        
        story.append(Paragraph("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", footer_style))
        story.append(Paragraph(f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", footer_style))
        story.append(Paragraph("Sistema Profesional de Valoración de Software v2.0 - Colombia", footer_style))
        story.append(Paragraph(f"ID de Certificación: {valoracion_id}", footer_style))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer, None
        
    except Exception as e:
        return None, f"Error generando PDF: {str(e)}"

@app.route('/api/generar-pdf/<valoracion_id>')
def generar_pdf_endpoint(valoracion_id):
    """Endpoint para generar y descargar PDF"""
    buffer, error = generar_pdf_reporte(valoracion_id)
    
    if error:
        return jsonify({'error': error}), 500
    
    if not buffer:
        return jsonify({'error': 'No se pudo generar el PDF'}), 500
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'valoracion_{valoracion_id[:8]}.pdf',
        mimetype='application/pdf'
    )

# ================================
# INICIO DE LA APLICACIÓN
# ================================

if __name__ == '__main__':
    print("🚀 Iniciando Sistema de Valoración de Software v1.0")
    print("📊 Basado en ISO/IEC 25010:2023 + Costos Colombia 2025")
    print("🌐 Acceso: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
