# ARQUITECTURA DEL SISTEMA ESTANDARIZADO DE VALORACIÓN
## Diseño Técnico y Especificaciones

**Fecha:** 5 de agosto de 2025  
**Versión:** 1.0  
**Estado:** Diseño Conceptual

---

## 1. ARQUITECTURA GENERAL DEL SISTEMA

### 1.1 Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND WEB                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │  Cuestionario   │  │   Dashboard     │  │   Reportes    │ │
│  │   Adaptativo    │  │   Principal     │  │ Certificables │ │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE NEGOCIO                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │   Motor de      │  │   Validador     │  │   Generador   │ │
│  │   Valoración    │  │   de Datos      │  │   de Reportes │ │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DATOS                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │   Base de Datos │  │   Catálogo de   │  │   Histórico   │ │
│  │   Tecnologías   │  │   Estándares    │  │   de Valores  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Flujo de Procesamiento

```
1. INICIO → 2. CLASIFICACIÓN → 3. CUESTIONARIO → 4. CÁLCULO → 5. REPORTE
    │              │                │              │            │
    ▼              ▼                ▼              ▼            ▼
[Tipo SW]    [Tecnología]    [Respuestas]    [Algoritmos]  [Documento]
             [Complejidad]   [Validación]    [Factores]    [Certificado]
```

---

## 2. ESPECIFICACIONES DEL CUESTIONARIO ADAPTATIVO

### 2.1 Estructura Modular

#### A. **MÓDULO BASE (Obligatorio para todos)**
```json
{
  "seccion": "informacion_general",
  "preguntas": [
    {
      "id": "tipo_software",
      "tipo": "select",
      "opciones": ["web_app", "desktop_app", "sistema_gestion", "aplicativo_auditoria", "otro"],
      "obligatorio": true
    },
    {
      "id": "tecnologia_principal",
      "tipo": "select_cascada",
      "dependencia": "tipo_software",
      "opciones_dinamicas": true
    },
    {
      "id": "antiguedad_sistema",
      "tipo": "number",
      "rango": [0, 20],
      "unidad": "años"
    }
  ]
}
```

#### B. **MÓDULO TÉCNICO (Adaptativo según tecnología)**
```json
{
  "seccion": "caracteristicas_tecnicas",
  "condicion": "tipo_software != 'otro'",
  "preguntas_dinamicas": {
    "web_app": ["arquitectura", "frontend_framework", "backend_technology"],
    "desktop_app": ["plataforma", "lenguaje", "base_datos"],
    "access_app": ["version_access", "vba_complexity", "data_sources"]
  }
}
```

#### C. **MÓDULO CALIDAD ISO 25010 (Obligatorio)**
```json
{
  "seccion": "calidad_iso25010",
  "caracteristicas": [
    {
      "nombre": "security",
      "peso": 0.20,
      "subcaracteristicas": [
        "confidentiality", "integrity", "non_repudiation", 
        "accountability", "authenticity"
      ]
    },
    {
      "nombre": "functional_suitability", 
      "peso": 0.18,
      "subcaracteristicas": [
        "functional_completeness", "functional_correctness",
        "functional_appropriateness"
      ]
    }
  ]
}
```

### 2.2 Sistema de Scoring Dinámico

#### Algoritmo de Puntuación:
```javascript
function calcularScore(respuestas, tecnologia, contexto) {
    let scoreBase = obtenerScoreBase(tecnologia);
    let factorCalidad = calcularFactorCalidad(respuestas.iso25010);
    let factorComplejidad = calcularFactorComplejidad(respuestas.tecnicas);
    let factorNegocio = calcularFactorNegocio(respuestas.negocio);
    let factorColombia = aplicarFactorColombia(respuestas.cumplimiento);
    
    return scoreBase * factorCalidad * factorComplejidad * factorNegocio * factorColombia;
}
```

---

## 3. MOTOR DE VALORACIÓN

### 3.1 Algoritmos de Cálculo

#### A. **ALGORITMO PRINCIPAL**
```python
class ValoracionEngine:
    def __init__(self):
        self.base_costs = BaseCostsDatabase()
        self.iso_weights = ISO25010Weights()
        self.colombia_factors = ColombiaFactors()
    
    def calcular_valor(self, software_data):
        # 1. Valor base por tecnología
        valor_base = self.calculate_base_value(software_data.technology)
        
        # 2. Factor de calidad ISO 25010
        factor_calidad = self.calculate_quality_factor(software_data.iso_responses)
        
        # 3. Factor de complejidad
        factor_complejidad = self.calculate_complexity_factor(software_data.technical_responses)
        
        # 4. Factor de negocio
        factor_negocio = self.calculate_business_factor(software_data.business_responses)
        
        # 5. Factor específico Colombia
        factor_colombia = self.calculate_colombia_factor(software_data.compliance_responses)
        
        # 6. Cálculo final
        valor_final = valor_base * factor_calidad * factor_complejidad * factor_negocio * factor_colombia
        
        return {
            'valor_total': valor_final,
            'desglose': self.generate_breakdown(),
            'confianza': self.calculate_confidence_level(),
            'recomendaciones': self.generate_recommendations()
        }
```

#### B. **SISTEMA DE FACTORES**
```python
# Factores de Tecnología (base_costs.py)
TECHNOLOGY_MULTIPLIERS = {
    'access_vba': 0.7,
    'vb_net': 0.8,
    'php_basic': 1.0,
    'javascript_modern': 1.1,
    'python_django': 1.2,
    'java_enterprise': 1.4,
    'dotnet_core': 1.3,
    'microservices': 1.8
}

# Factores de Complejidad
COMPLEXITY_FACTORS = {
    'very_low': 0.6,
    'low': 0.8,
    'medium': 1.0,
    'high': 1.3,
    'very_high': 1.7
}

# Factores específicos Colombia
COLOMBIA_FACTORS = {
    'compliance_basic': 1.0,
    'compliance_government': 1.3,
    'compliance_financial': 1.5,
    'compliance_critical': 1.8
}
```

### 3.2 Validación y Calibración

#### Sistema de Validación Cruzada:
```python
class ValidationEngine:
    def validate_estimation(self, software_data, estimated_value):
        validations = []
        
        # Validación por rango de mercado
        market_range = self.get_market_range(software_data.category)
        if not (market_range.min <= estimated_value <= market_range.max):
            validations.append("WARNING: Valor fuera del rango de mercado")
        
        # Validación por complejidad vs valor
        complexity_check = self.check_complexity_consistency(software_data)
        validations.append(complexity_check)
        
        # Validación por casos similares
        similar_cases = self.find_similar_cases(software_data)
        variance = self.calculate_variance(estimated_value, similar_cases)
        
        return {
            'validations': validations,
            'confidence_level': self.calculate_confidence(variance),
            'similar_cases': similar_cases
        }
```

---

## 4. BASE DE DATOS ESPECIALIZADA

### 4.1 Estructura de Datos

#### A. **Tabla de Tecnologías**
```sql
CREATE TABLE technologies (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category ENUM('frontend', 'backend', 'database', 'framework', 'language'),
    complexity_level ENUM('very_low', 'low', 'medium', 'high', 'very_high'),
    cost_multiplier DECIMAL(3,2),
    market_demand DECIMAL(3,2),
    colombia_availability DECIMAL(3,2),
    last_updated DATETIME,
    source_references TEXT
);
```

#### B. **Tabla de Casos de Referencia**
```sql
CREATE TABLE reference_cases (
    id INT PRIMARY KEY,
    project_name VARCHAR(200),
    technology_stack JSON,
    total_cost DECIMAL(12,2),
    development_hours INT,
    team_size INT,
    complexity_score DECIMAL(4,2),
    iso25010_scores JSON,
    colombia_sector ENUM('public', 'private', 'mixed'),
    validation_status ENUM('verified', 'estimated', 'theoretical'),
    created_date DATETIME
);
```

#### C. **Tabla de Factores de Ajuste**
```sql
CREATE TABLE adjustment_factors (
    id INT PRIMARY KEY,
    factor_type ENUM('technology', 'complexity', 'business', 'colombia'),
    factor_name VARCHAR(100),
    factor_value DECIMAL(4,3),
    applies_to JSON, -- Condiciones de aplicación
    effective_date DATE,
    expiry_date DATE,
    justification TEXT
);
```

### 4.2 Datos Precargados

#### Tecnologías Prioritarias para Colombia:
```json
{
  "web_technologies": [
    {
      "name": "PHP + Laravel",
      "cost_multiplier": 1.0,
      "colombia_popularity": 0.85,
      "typical_hourly_rate": 35000
    },
    {
      "name": "JavaScript + React",
      "cost_multiplier": 1.1,
      "colombia_popularity": 0.75,
      "typical_hourly_rate": 45000
    },
    {
      "name": "Python + Django",
      "cost_multiplier": 1.2,
      "colombia_popularity": 0.65,
      "typical_hourly_rate": 50000
    }
  ],
  "legacy_technologies": [
    {
      "name": "Access + VBA",
      "cost_multiplier": 0.7,
      "colombia_popularity": 0.90,
      "typical_hourly_rate": 25000,
      "migration_urgency": "medium"
    }
  ]
}
```

---

## 5. SISTEMA DE REPORTES CERTIFICABLES

### 5.1 Estructura del Reporte

#### A. **Portada Ejecutiva**
- Valor económico total
- Nivel de confianza
- Resumen ejecutivo
- Firma digital del sistema

#### B. **Metodología Aplicada**
- Estándares utilizados (ISO 25010:2023)
- Fuentes de datos
- Algoritmos aplicados
- Factores de ajuste

#### C. **Análisis Detallado**
- Desglose por componentes
- Comparación con casos similares
- Análisis de riesgos
- Recomendaciones

#### D. **Anexos Técnicos**
- Respuestas del cuestionario
- Cálculos step-by-step
- Referencias bibliográficas
- Código de verificación

### 5.2 Formato de Salida

```json
{
  "reporte_valoracion": {
    "metadata": {
      "version_sistema": "1.0",
      "fecha_calculo": "2025-08-05T10:30:00Z",
      "codigo_verificacion": "SVS-2025-08-001",
      "auditor": "Sistema de Valoración Científica"
    },
    "valor_economico": {
      "total_cop": 15750000,
      "desglose": {
        "valor_base": 10000000,
        "factor_calidad": 1.15,
        "factor_complejidad": 1.1,
        "factor_negocio": 1.25,
        "factor_colombia": 1.0
      },
      "nivel_confianza": 0.85
    },
    "analisis_tecnico": {
      "tecnologia_principal": "access_vba",
      "puntuacion_iso25010": {
        "security": 2.5,
        "functional_suitability": 4.0,
        "reliability": 3.0
      },
      "complejidad_estimada": "medium"
    },
    "recomendaciones": [
      "Considerar migración a tecnología más moderna",
      "Implementar sistema de backups automáticos",
      "Mejorar documentación técnica"
    ]
  }
}
```

---

## 6. PLAN DE IMPLEMENTACIÓN

### 6.1 Cronograma de Desarrollo

#### **FASE 2A: Core del Sistema (2 semanas)**
- [ ] Estructura base de datos
- [ ] Motor de valoración básico
- [ ] Cuestionario adaptativo v1
- [ ] Interfaz web inicial

#### **FASE 2B: Funcionalidades Avanzadas (2 semanas)**
- [ ] Sistema de reportes
- [ ] Validación cruzada
- [ ] Base de datos de casos
- [ ] Sistema de calibración

#### **FASE 2C: Refinamiento (1 semana)**
- [ ] Testing con casos reales
- [ ] Ajuste de algoritmos
- [ ] Documentación completa
- [ ] Preparación para producción

### 6.2 Stack Tecnológico Propuesto

#### **Frontend:**
- **Framework:** React + TypeScript
- **UI Library:** Material-UI o Tailwind CSS
- **Formularios:** React Hook Form + Yup validation

#### **Backend:**
- **Framework:** Node.js + Express o Python + FastAPI
- **Base de datos:** PostgreSQL + Prisma ORM
- **Autenticación:** JWT + bcrypt

#### **Infraestructura:**
- **Hosting:** Vercel/Netlify (Frontend) + Railway/Heroku (Backend)
- **Base de datos:** PostgreSQL (managed)
- **Almacenamiento:** AWS S3 (reportes PDF)

---

## 7. CONSIDERACIONES DE SEGURIDAD Y COMPLIANCE

### 7.1 Seguridad de Datos
- **Cifrado:** TLS 1.3 para transmisión
- **Almacenamiento:** Datos sensibles cifrados en reposo
- **Acceso:** Autenticación multifactor opcional
- **Auditoría:** Logs completos de todas las operaciones

### 7.2 Compliance Colombia
- **HABEAS DATA:** Cumplimiento Ley 1581 de 2012
- **Gobierno Digital:** Compatibilidad con estándares MinTIC
- **Auditoría:** Preparado para revisión de entes de control

---

**Estado:** ✅ Diseño Completado  
**Próximo hito:** Inicio Fase 2A - Desarrollo Core  
**Fecha estimada entrega:** Septiembre 2025
