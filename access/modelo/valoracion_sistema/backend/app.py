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
            
            # Cálculo base
            valor_base = horas_estimadas * costo_hora
            valor_ajustado = valor_base * factor_calidad * factor_complejidad * factor_negocio * factor_colombia
            
            # Rango de incertidumbre (±20% basado en literatura científica)
            margen_error = 0.20
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
                    'factor_colombia': factor_colombia
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
        """Estimación de horas basada en funcionalidades y complejidad - Corregida para ser más realista"""
        # Horas base más realistas
        horas_base = {
            'aplicativo_gestion': 80,      # Reducido de 120
            'sistema_auditoria': 120,      # Reducido de 200  
            'aplicativo_reportes': 60,     # Reducido de 80
            'sistema_web': 150,            # Mantiene (no aplica para Access)
            'aplicativo_escritorio': 80,   # Reducido de 100
            'sistema_integracion': 180,    # Mantiene (no aplica para Access)
            'otro': 80                     # Reducido de 100
        }
        
        tipo_software = datos.get('tipo_software', 'otro')
        horas = horas_base.get(tipo_software, 80)
        
        # Ajustes por funcionalidades específicas - más conservadores
        funcionalidades = datos.get('funcionalidades', {})
        
        if funcionalidades.get('autenticacion_avanzada'):
            horas += 25  # Reducido de 40
        if funcionalidades.get('reportes_complejos'):
            horas += 35  # Reducido de 60
        if funcionalidades.get('integracion_externa'):
            horas += 50  # Reducido de 80 (para Access es limitado)
        if funcionalidades.get('workflow_aprobaciones'):
            horas += 60  # Reducido de 100
        if funcionalidades.get('dashboard_ejecutivo'):
            horas += 30  # Reducido de 50
        
        # Factor de tecnología: Access/VBA es más simple de desarrollar
        tecnologia = datos.get('tecnologia_principal', '')
        if 'access' in tecnologia.lower():
            horas *= 0.8  # 20% menos para Access por ser más directo
        
        # Ajuste por tiempo de desarrollo (no antigüedad del sistema terminado)
        # La antigüedad solo se considera si el sistema sigue en uso y necesita mantenimiento
        antiguedad = datos.get('antiguedad_anos', 0)
        en_uso = datos.get('en_uso_activo', True)  # Por defecto asumimos que está en uso
        
        # Solo aplicar factor de antigüedad si el sistema está en uso y es legacy
        if en_uso and antiguedad > 5:
            # Factor mínimo para sistemas legacy en uso (requieren más análisis)
            horas *= 1.1  # Solo 10% más por complejidad de legacy
        elif en_uso and antiguedad > 10:
            horas *= 1.2  # Solo 20% más para sistemas muy antiguos en uso
        
        return round(horas)
    
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
        """Factor de complejidad técnica"""
        factor = 1.0
        
        # Complejidad de base de datos
        bd_tipo = datos.get('base_datos', {}).get('tipo', 'simple')
        if bd_tipo == 'enterprise':
            factor *= 1.3
        elif bd_tipo == 'distribuida':
            factor *= 1.5
        
        # Número de usuarios concurrentes
        usuarios = datos.get('usuarios_concurrentes', 1)
        if usuarios > 100:
            factor *= 1.4
        elif usuarios > 50:
            factor *= 1.2
        elif usuarios > 10:
            factor *= 1.1
        
        # Integración con sistemas externos
        integraciones = datos.get('integraciones_externas', 0)
        factor *= (1 + integraciones * 0.1)  # 10% por integración
        
        return min(factor, 2.5)  # Máximo 2.5x
    
    def _calcular_factor_negocio(self, datos):
        """Factor de valor de negocio"""
        factor = 1.0
        
        # Criticidad del sistema
        criticidad = datos.get('criticidad_negocio', 3)  # 1-5
        factor *= (0.7 + criticidad * 0.15)  # 0.85 - 1.45
        
        # Ahorro estimado anual
        ahorro_anual = datos.get('ahorro_anual_cop', 0)
        if ahorro_anual > 10000000:  # > 10M COP
            factor *= 1.3
        elif ahorro_anual > 5000000:  # > 5M COP
            factor *= 1.2
        elif ahorro_anual > 1000000:  # > 1M COP
            factor *= 1.1
        
        # Número de usuarios beneficiados
        usuarios_total = datos.get('usuarios_totales', 1)
        if usuarios_total > 100:
            factor *= 1.2
        elif usuarios_total > 50:
            factor *= 1.1
        
        return min(factor, 3.0)  # Máximo 3x
    
    def _calcular_factor_colombia(self, datos):
        """Factor específico para el contexto colombiano - Corregido para ser más justo"""
        factor = 1.0
        
        # Cumplimiento normativo - reducir factores excesivos
        if datos.get('genera_reportes_oficiales', False):
            factor *= 1.15  # Reducido de 1.25 a 1.15 (15% en lugar de 25%)
        
        if datos.get('requiere_auditoria_logs', False):
            factor *= 1.10  # Reducido de 1.15 a 1.10 (10% en lugar de 15%)
        
        if datos.get('sector') == 'publico':
            factor *= 1.10   # Reducido de 1.20 a 1.10 (10% en lugar de 20%)
        elif datos.get('sector') == 'financiero':
            factor *= 1.15   # Reducido de 1.30 a 1.15 (15% en lugar de 30%)
        
        # Interoperabilidad gobierno digital
        if datos.get('interoperabilidad_govco', False):
            factor *= 1.05   # Reducido de 1.10 a 1.05 (5% en lugar de 10%)
        
        return min(factor, 1.5)  # Reducido máximo de 2.0x a 1.5x
    
    def _calcular_confianza(self, datos):
        """Calcula el nivel de confianza basado en completitud de datos"""
        campos_criticos = [
            'tipo_software', 'tecnologia_principal', 'antiguedad_anos',
            'usuarios_concurrentes', 'criticidad_negocio'
        ]
        
        campos_completos = sum(1 for campo in campos_criticos if datos.get(campo) is not None)
        confianza_base = campos_completos / len(campos_criticos)
        
        # Bonus por datos ISO 25010
        if datos.get('iso25010'):
            caracteristicas_iso = len(datos['iso25010'])
            bonus_iso = min(0.2, caracteristicas_iso / len(PESOS_ISO25010) * 0.2)
            confianza_base += bonus_iso
        
        return min(1.0, confianza_base)
    
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
    """Página principal del sistema"""
    return render_template('index.html')

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
    """Genera un PDF con el reporte completo de valoración"""
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
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Centro
        )
        
        story.append(Paragraph("REPORTE DE VALORACIÓN DE SOFTWARE", title_style))
        story.append(Paragraph("Sistema Estandarizado - Colombia 2025", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Información general
        story.append(Paragraph("INFORMACIÓN GENERAL", styles['Heading2']))
        
        # Obtener descripción del software
        descripcion = respuestas.get('descripcion', 'No especificada')
        if len(descripcion) > 100:
            descripcion = descripcion[:100] + "..."
        
        info_data = [
            ["Fecha de valoración:", valoracion[1][:10]],
            ["ID de valoración:", valoracion[0]],
            ["Tipo de software:", valoracion[2]],
            ["Tecnología principal:", valoracion[3]],
            ["Descripción:", descripcion],
            ["Sector:", respuestas.get('sector', 'No especificado')],
            ["Usuarios totales:", str(respuestas.get('usuarios_totales', 'No especificado'))],
            ["Usuarios concurrentes:", str(respuestas.get('usuarios_concurrentes', 'No especificado'))],
        ]
        
        info_table = Table(info_data)
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # FUNCIONALIDADES EVALUADAS
        story.append(Paragraph("FUNCIONALIDADES EVALUADAS", styles['Heading2']))
        
        funcionalidades = respuestas.get('funcionalidades', {})
        func_data = [
            ["Autenticación y roles avanzados:", "✓ Sí" if funcionalidades.get('autenticacion_avanzada') else "✗ No"],
            ["Reportes y dashboards complejos:", "✓ Sí" if funcionalidades.get('reportes_complejos') else "✗ No"],
            ["Integración con sistemas externos:", "✓ Sí" if funcionalidades.get('integracion_externa') else "✗ No"],
            ["Workflows y aprobaciones:", "✓ Sí" if funcionalidades.get('workflow_aprobaciones') else "✗ No"],
            ["Dashboard ejecutivo:", "✓ Sí" if funcionalidades.get('dashboard_ejecutivo') else "✗ No"],
        ]
        
        func_table = Table(func_data)
        func_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(func_table)
        story.append(Spacer(1, 20))
        
        # EVALUACIÓN ISO 25010 DETALLADA
        if respuestas.get('iso25010'):
            story.append(Paragraph("EVALUACIÓN DE CALIDAD ISO/IEC 25010:2023", styles['Heading2']))
            
            iso_data = []
            iso_dict = respuestas['iso25010']
            
            caracteristicas_nombres = {
                'security': 'Seguridad (20%)',
                'functional_suitability': 'Idoneidad Funcional (18%)',
                'reliability': 'Fiabilidad (15%)',
                'maintainability': 'Mantenibilidad (12%)',
                'performance_efficiency': 'Eficiencia de Rendimiento (10%)',
                'usability': 'Usabilidad (10%)',
                'compatibility': 'Compatibilidad (8%)',
                'portability': 'Portabilidad (4%)',
                'flexibility': 'Flexibilidad (3%)'
            }
            
            escala_nombres = {1: "Muy deficiente", 2: "Deficiente", 3: "Aceptable", 4: "Bueno", 5: "Excelente"}
            
            for caracteristica, valor in iso_dict.items():
                if caracteristica in caracteristicas_nombres:
                    nombre = caracteristicas_nombres[caracteristica]
                    descripcion = f"{valor}/5 - {escala_nombres.get(valor, 'N/A')}"
                    iso_data.append([nombre, descripcion])
            
            iso_table = Table(iso_data)
            iso_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(iso_table)
            story.append(Spacer(1, 20))
        
        # Resultados económicos
        story.append(Paragraph("RESULTADOS ECONÓMICOS", styles['Heading2']))
        
        valor_min = f"${valoracion[5]:,.0f} COP"
        valor_max = f"${valoracion[6]:,.0f} COP"
        valor_promedio = f"${(valoracion[5] + valoracion[6])/2:,.0f} COP"
        
        resultado_data = [
            ["Valor mínimo estimado:", valor_min],
            ["Valor máximo estimado:", valor_max],
            ["Valor promedio:", valor_promedio],
            ["Nivel de confianza:", f"{valoracion[7]*100:.0f}%"],
        ]
        
        resultado_table = Table(resultado_data)
        resultado_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(resultado_table)
        story.append(Spacer(1, 20))
        
        # Desglose técnico
        if desglose:
            story.append(Paragraph("DESGLOSE TÉCNICO DETALLADO", styles['Heading2']))
            
            if 'horas_estimadas' in desglose:
                tecnico_data = [
                    ["Horas estimadas:", f"{desglose.get('horas_estimadas', 0)}h"],
                    ["Costo por hora:", f"${desglose.get('costo_hora', 0):,.0f} COP"],
                    ["Valor base:", f"${desglose.get('valor_base', 0):,.0f} COP"],
                    ["Factor calidad:", f"{desglose.get('factor_calidad', 1.0):.2f}x"],
                    ["Factor complejidad:", f"{desglose.get('factor_complejidad', 1.0):.2f}x"],
                    ["Factor negocio:", f"{desglose.get('factor_negocio', 1.0):.2f}x"],
                    ["Factor Colombia:", f"{desglose.get('factor_colombia', 1.0):.2f}x"],
                ]
                
                tecnico_table = Table(tecnico_data)
                tecnico_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('BACKGROUND', (1, 0), (1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(tecnico_table)
                story.append(Spacer(1, 15))
                
                # EXPLICACIÓN DE FACTORES
                story.append(Paragraph("EXPLICACIÓN DE FACTORES DE AJUSTE", styles['Heading3']))
                
                explicaciones = []
                
                # Factor Calidad
                factor_calidad = desglose.get('factor_calidad', 1.0)
                if factor_calidad > 1.0:
                    explicaciones.append(f"• Factor Calidad ({factor_calidad:.2f}x): Bonificación por buenas prácticas y calidad según ISO 25010")
                elif factor_calidad < 1.0:
                    explicaciones.append(f"• Factor Calidad ({factor_calidad:.2f}x): Penalización por deficiencias en seguridad o calidad")
                else:
                    explicaciones.append(f"• Factor Calidad ({factor_calidad:.2f}x): Factor neutro - calidad estándar")
                
                # Factor Complejidad
                factor_comp = desglose.get('factor_complejidad', 1.0)
                usuarios_conc = respuestas.get('usuarios_concurrentes', 1)
                bd_tipo = respuestas.get('base_datos', {}).get('tipo', 'simple')
                if factor_comp > 1.0:
                    explicaciones.append(f"• Factor Complejidad ({factor_comp:.2f}x): Ajuste por {usuarios_conc} usuarios concurrentes y BD tipo {bd_tipo}")
                else:
                    explicaciones.append(f"• Factor Complejidad ({factor_comp:.2f}x): Sistema de baja complejidad técnica")
                
                # Factor Negocio
                factor_neg = desglose.get('factor_negocio', 1.0)
                criticidad = respuestas.get('criticidad_negocio', 3)
                if factor_neg > 1.0:
                    explicaciones.append(f"• Factor Negocio ({factor_neg:.2f}x): Valor estratégico con criticidad nivel {criticidad}/5")
                else:
                    explicaciones.append(f"• Factor Negocio ({factor_neg:.2f}x): Impacto de negocio estándar o bajo")
                
                # Factor Colombia
                factor_col = desglose.get('factor_colombia', 1.0)
                cumplimientos = []
                if respuestas.get('genera_reportes_oficiales'): cumplimientos.append("reportes oficiales")
                if respuestas.get('requiere_auditoria_logs'): cumplimientos.append("logs de auditoría")
                if respuestas.get('sector') == 'publico': cumplimientos.append("sector público")
                
                if cumplimientos:
                    explicaciones.append(f"• Factor Colombia ({factor_col:.2f}x): Cumplimiento normativo por: {', '.join(cumplimientos)}")
                else:
                    explicaciones.append(f"• Factor Colombia ({factor_col:.2f}x): Sin requisitos regulatorios especiales")
                
                for explicacion in explicaciones:
                    story.append(Paragraph(explicacion, styles['Normal']))
                
                story.append(Spacer(1, 20))
        
        # Observaciones
        if 'observaciones' in respuestas and respuestas['observaciones'].strip():
            story.append(Paragraph("OBSERVACIONES ADICIONALES", styles['Heading2']))
            story.append(Paragraph(respuestas['observaciones'], styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Metodología
        story.append(Paragraph("METODOLOGÍA APLICADA", styles['Heading2']))
        metodologia_text = """
        Esta valoración se basa en estándares internacionales y análisis del mercado colombiano:
        
        • ISO/IEC 25010:2023: Estándar internacional de calidad de software
        • COCOMO Adaptado: Metodología de estimación de costos
        • Análisis de mercado colombiano 2025
        • Factores de ajuste por sector y complejidad
        
        El rango de valor (±20%) refleja la incertidumbre típica en estimaciones de software según la literatura científica.
        """
        story.append(Paragraph(metodologia_text, styles['Normal']))
        
        # Pie de página
        story.append(Spacer(1, 40))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph(f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Sistema de Valoración v1.0", footer_style))
        
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
