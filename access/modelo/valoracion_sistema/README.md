# 🚀 SISTEMA ESTANDARIZADO DE VALORACIÓN DE SOFTWARE
## Guía de Instalación y Uso

### 📋 **DESCRIPCIÓN**
Sistema web completo para valorar económicamente proyectos de software basado en:
- **ISO/IEC 25010:2023** (Estándares internacionales de calidad)
- **Metodologías COCOMO** (Estimación científica)
- **Costos del mercado colombiano 2024-2025**

### ⚡ **CARACTERÍSTICAS PRINCIPALES**
✅ **Cuestionario adaptativo** - Se ajusta según el tipo de software  
✅ **Rangos de valor** - No valores absolutos, sino rangos realistas  
✅ **Base científica** - Cada cálculo fundamentado y trazable  
✅ **Multi-tecnología** - Desde Access hasta arquitecturas modernas  
✅ **Específico Colombia** - Costos y regulaciones locales  

---

## 🛠️ **INSTALACIÓN**

### **Requisitos:**
- Python 3.8+ instalado
- Navegador web moderno
- 50MB de espacio en disco

### **Pasos de instalación:**

#### 1. **Navegar al directorio del proyecto**
```bash
cd c:\GitHub_28_07_2025\gestion_auditoria\access\modelo\valoracion_sistema\backend
```

#### 2. **Instalar dependencias de Python**
```bash
pip install Flask Flask-CORS
```

#### 3. **Ejecutar el servidor**
```bash
python app.py
```

#### 4. **Abrir en el navegador**
```
http://localhost:5000
```

---

## 🎯 **CÓMO USAR EL SISTEMA**

### **Paso 1: Información General**
- Seleccionar tipo de software a evaluar
- Elegir tecnología principal utilizada
- Indicar antigüedad del sistema
- Especificar sector de aplicación

### **Paso 2: Características Técnicas**
- Usuarios concurrentes y totales
- Tipo de base de datos
- Número de integraciones externas
- Funcionalidades implementadas

### **Paso 3: Evaluación ISO 25010**
- Calificar 6 características de calidad (1-5)
- Cada característica tiene peso científico específico
- **Seguridad** (20%) - **Funcionalidad** (18%) - **Fiabilidad** (15%)

### **Paso 4: Valor de Negocio**
- Criticidad para el negocio
- Ahorro anual estimado
- Cumplimiento normativo colombiano

### **Paso 5: Resultados**
- **Rango de valor** (mínimo - máximo)
- **Desglose detallado** de cálculos
- **Nivel de confianza** de la estimación

---

## 💰 **EJEMPLOS DE VALORACIÓN**

### **Caso 1: Sistema Access Básico**
- **Tipo:** Aplicativo de gestión
- **Tecnología:** Access + VBA
- **Usuarios:** 5 concurrentes
- **Resultado esperado:** $800,000 - $1,200,000 COP

### **Caso 2: Sistema Web Moderno**
- **Tipo:** Sistema web corporativo
- **Tecnología:** PHP + Laravel
- **Usuarios:** 50 concurrentes
- **Resultado esperado:** $3,500,000 - $5,200,000 COP

### **Caso 3: Sistema Enterprise**
- **Tipo:** Sistema de auditoría
- **Tecnología:** Java + Spring
- **Usuarios:** 200 concurrentes
- **Resultado esperado:** $8,000,000 - $12,000,000 COP

---

## 🧮 **METODOLOGÍA DE CÁLCULO**

### **Fórmula Base:**
```
Valor Total = (Horas × Costo/Hora × Factor_Tecnología × Factor_Calidad × Factor_Negocio × Factor_Colombia) ± 20%
```

### **Factores de Tecnología:**
- **Access/VBA:** 0.7x (menor complejidad)
- **PHP/JavaScript:** 1.0-1.2x (estándar)
- **Java/Python Enterprise:** 1.4x (mayor complejidad)
- **Microservicios:** 1.8x (alta complejidad)

### **Factores ISO 25010:**
- Basado en evaluación de 9 características
- Pesos científicos según importancia
- Rango de factor: 0.5x - 2.0x

### **Factores Colombia:**
- **Reportes oficiales:** +25%
- **Sector público:** +20%
- **Sector financiero:** +30%
- **Auditoría logs:** +15%

---

## 📊 **INTERPRETACIÓN DE RESULTADOS**

### **Nivel de Confianza:**
- **90-100%:** Información muy completa, resultado altamente confiable
- **70-89%:** Información buena, resultado confiable
- **50-69%:** Información básica, resultado orientativo
- **<50%:** Información insuficiente, completar más datos

### **Rango de Valores:**
- El **rango** refleja la incertidumbre natural en estimaciones
- **Valor mínimo:** Escenario conservador
- **Valor máximo:** Escenario con complejidades adicionales
- **Valor promedio:** Estimación más probable

---

## 🔧 **CONFIGURACIÓN AVANZADA**

### **Modificar Costos Base:**
Editar en `app.py`, línea 24:
```python
COSTOS_BASE = {
    'muy_bajo': 20000,   # Ajustar según mercado
    'bajo': 30000,
    'medio': 45000,
    'alto': 65000,
    'muy_alto': 90000
}
```

### **Ajustar Factores de Tecnología:**
Editar en `app.py`, línea 33:
```python
FACTORES_TECNOLOGIA = {
    'access_vba': {'factor': 0.7, 'nivel': 'bajo'},
    # Agregar nuevas tecnologías aquí
}
```

### **Modificar Pesos ISO 25010:**
Editar en `app.py`, línea 67:
```python
PESOS_ISO25010 = {
    'security': 0.20,              # Ajustar pesos
    'functional_suitability': 0.18,
    # etc...
}
```

---

## 📈 **FUNCIONALIDADES DEL SISTEMA**

### **Base de Datos Integrada:**
- Almacena todas las valoraciones realizadas
- Histórico para análisis de tendencias
- Estadísticas de uso del sistema

### **API REST Completa:**
- `GET /api/tecnologias` - Lista de tecnologías
- `POST /api/valorar` - Calcular valoración
- `GET /api/historico` - Histórico de valoraciones
- `GET /api/estadisticas` - Estadísticas del sistema

### **Validaciones Automáticas:**
- Verificación de datos requeridos
- Rangos lógicos de valores
- Consistencia entre respuestas

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Error: "Module not found"**
```bash
pip install Flask Flask-CORS
```

### **Error: "Port already in use"**
- Cambiar puerto en `app.py`, última línea:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Cambiar a 5001
```

### **Error: "Database locked"**
- Cerrar todas las instancias del servidor
- Eliminar archivo `valoraciones.db` si existe
- Reiniciar el servidor

### **Resultados inconsistentes:**
- Verificar que todos los campos requeridos estén completos
- Revisar que las evaluaciones ISO 25010 sean realistas
- Consultar el nivel de confianza del resultado

---

## 📚 **REFERENCIAS CIENTÍFICAS**

### **Estándares Aplicados:**
- **ISO/IEC 25010:2023** - Modelo de calidad de software
- **COCOMO** - Modelo de estimación de costos
- **COSMIC Function Points** - Medición funcional

### **Fuentes de Costos:**
- **PayScale Colombia 2025** - Salarios de desarrolladores
- **Análisis de mercado local** - Tarifas por hora
- **Factores de overhead** - Costos patronales y empresariales

### **Literatura Académica:**
- Análisis de precisión en estimación de software
- Factores de ajuste por contexto geográfico
- Metodologías de valoración híbridas

---

## 📞 **SOPORTE Y DESARROLLO**

### **Características Futuras:**
- ✨ Generación de reportes PDF
- ✨ Comparación con casos similares
- ✨ Análisis de sensibilidad
- ✨ Integración con APIs de costos en tiempo real

### **Datos de la Versión:**
- **Versión:** 1.0
- **Fecha:** Agosto 2025
- **Base científica:** ISO/IEC 25010:2023
- **Mercado objetivo:** Colombia

---

## ✅ **VALIDACIÓN FINAL**

Antes de usar en producción, se recomienda:

1. **Calibrar** con 3-5 proyectos conocidos
2. **Validar rangos** con expertos del sector
3. **Ajustar factores** según contexto específico
4. **Documentar** decisiones de configuración

**¡El sistema está listo para valorar software de manera científica y estandarizada!**
