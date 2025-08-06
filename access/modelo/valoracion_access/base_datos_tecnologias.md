# BASE DE DATOS DE TECNOLOGÍAS Y FACTORES DE COSTO
## Sistema Estandarizado de Valoración de Software - Colombia

**Fecha:** 5 de agosto de 2025  
**Versión:** 1.0  
**Fuente:** Análisis de mercado colombiano y estándares internacionales

---

## 1. CATEGORIZACIÓN DE TECNOLOGÍAS

### 1.1 Lenguajes de Programación

#### A. **NIVEL ENTERPRISE** (Factor: 1.3 - 1.5)
- **Java** (Enterprise Edition)
  - Complejidad: Alta
  - Costo/hora desarrollo: COL $45,000 - $70,000
  - Ecosistema: Spring, Hibernate, JSF
  - Casos de uso: Sistemas empresariales, bancos, gobierno

- **C#/.NET** (Framework completo)
  - Complejidad: Alta
  - Costo/hora desarrollo: COL $40,000 - $65,000
  - Ecosistema: ASP.NET, Entity Framework, Azure
  - Casos de uso: Aplicaciones corporativas, sistemas integrados

- **Python** (Django/Flask Enterprise)
  - Complejidad: Media-Alta
  - Costo/hora desarrollo: COL $35,000 - $60,000
  - Ecosistema: Django, Flask, FastAPI, SQLAlchemy
  - Casos de uso: ML, análisis de datos, APIs robustas

#### B. **NIVEL PROFESIONAL** (Factor: 1.0 - 1.3)
- **JavaScript/TypeScript** (Node.js, React, Angular)
  - Complejidad: Media
  - Costo/hora desarrollo: COL $30,000 - $55,000
  - Ecosistema: React, Angular, Vue, Express, NestJS
  - Casos de uso: Aplicaciones web modernas, SPAs

- **PHP** (Laravel, Symfony)
  - Complejidad: Media
  - Costo/hora desarrollo: COL $25,000 - $45,000
  - Ecosistema: Laravel, Symfony, CodeIgniter
  - Casos de uso: Sitios web, e-commerce, sistemas de gestión

- **Python** (Desarrollo general)
  - Complejidad: Media
  - Costo/hora desarrollo: COL $30,000 - $50,000
  - Ecosistema: General purpose, automatización
  - Casos de uso: Scripts, automatización, prototipado

#### C. **NIVEL BÁSICO/LEGACY** (Factor: 0.7 - 1.0)
- **Visual Basic .NET**
  - Complejidad: Baja-Media
  - Costo/hora desarrollo: COL $25,000 - $40,000
  - Ecosistema: Windows Forms, WPF (limitado)
  - Casos de uso: Aplicaciones de escritorio Windows

- **VBA (Visual Basic for Applications)**
  - Complejidad: Baja
  - Costo/hora desarrollo: COL $20,000 - $35,000
  - Ecosistema: Microsoft Office (Access, Excel, Word)
  - Casos de uso: Automatización Office, aplicaciones simples

- **Access + VBA**
  - Complejidad: Baja
  - Costo/hora desarrollo: COL $18,000 - $30,000
  - Ecosistema: Microsoft Access, limitado
  - Casos de uso: Bases de datos departamentales, reportes

#### D. **TECNOLOGÍAS ESPECIALIZADAS** (Factor: 1.2 - 1.8)
- **Go/Golang**
  - Complejidad: Media-Alta
  - Costo/hora desarrollo: COL $40,000 - $65,000
  - Casos de uso: Microservicios, APIs de alto rendimiento

- **Rust**
  - Complejidad: Alta
  - Costo/hora desarrollo: COL $50,000 - $80,000
  - Casos de uso: Sistemas críticos, alto rendimiento

- **Ruby** (Ruby on Rails)
  - Complejidad: Media
  - Costo/hora desarrollo: COL $35,000 - $55,000
  - Casos de uso: Desarrollo web rápido, startups

---

## 2. ARQUITECTURAS Y PATRONES

### 2.1 Arquitecturas de Aplicación

#### A. **MONOLÍTICA TRADICIONAL** (Factor: 0.8 - 1.0)
- **Características:**
  - Una sola base de código
  - Despliegue único
  - Base de datos centralizada
- **Ejemplos:** Aplicaciones Access, sistemas legacy
- **Ventajas:** Simplicidad, desarrollo inicial rápido
- **Desventajas:** Escalabilidad limitada, mantenimiento complejo

#### B. **ARQUITECTURA EN CAPAS** (Factor: 1.1 - 1.3)
- **Características:**
  - Separación lógica (presentación, negocio, datos)
  - Mejor organización del código
  - Facilita mantenimiento
- **Ejemplos:** Aplicaciones .NET, Java Spring
- **Ventajas:** Mantenibilidad, testeo independiente
- **Desventajas:** Posible overhead de rendimiento

#### C. **MICROSERVICIOS** (Factor: 1.4 - 1.8)
- **Características:**
  - Servicios independientes
  - Comunicación via APIs
  - Despliegue independiente
- **Ejemplos:** Sistemas distribuidos modernos
- **Ventajas:** Escalabilidad, tecnologías heterogéneas
- **Desventajas:** Complejidad operacional, latencia de red

#### D. **SERVERLESS/CLOUD NATIVE** (Factor: 1.2 - 1.6)
- **Características:**
  - Funciones como servicio
  - Escalamiento automático
  - Pago por uso
- **Ejemplos:** AWS Lambda, Azure Functions
- **Ventajas:** Costo operacional, escalabilidad automática
- **Desventajas:** Vendor lock-in, arquitectura específica

---

## 3. BASES DE DATOS

### 3.1 Sistemas de Gestión de Bases de Datos

#### A. **BASES DE DATOS LOCALES/SIMPLES** (Factor: 0.6 - 0.9)
- **Microsoft Access**
  - Usuarios concurrentes: < 10
  - Volumen de datos: < 2GB
  - Complejidad: Baja
  - Costo desarrollo: Bajo

- **SQLite**
  - Usuarios concurrentes: Limitado
  - Volumen de datos: < 1TB teórico, práctico < 100GB
  - Complejidad: Baja-Media
  - Costo desarrollo: Bajo

#### B. **BASES DE DATOS PROFESIONALES** (Factor: 1.0 - 1.3)
- **SQL Server** (Express/Standard)
  - Usuarios concurrentes: < 100
  - Volumen de datos: < 10GB (Express)
  - Complejidad: Media
  - Costo desarrollo: Medio

- **MySQL/PostgreSQL**
  - Usuarios concurrentes: 100-1000+
  - Volumen de datos: Escalable
  - Complejidad: Media
  - Costo desarrollo: Medio

#### C. **BASES DE DATOS ENTERPRISE** (Factor: 1.3 - 1.8)
- **SQL Server Enterprise**
  - Usuarios concurrentes: 1000+
  - Volumen de datos: Ilimitado
  - Complejidad: Alta
  - Costo desarrollo: Alto

- **Oracle Database**
  - Usuarios concurrentes: 1000+
  - Volumen de datos: Ilimitado
  - Complejidad: Muy Alta
  - Costo desarrollo: Muy Alto

#### D. **BASES DE DATOS NoSQL** (Factor: 1.1 - 1.5)
- **MongoDB, Cassandra, Redis**
  - Casos especializados
  - Complejidad variable
  - Requiere experticia específica

---

## 4. FACTORES DE COMPLEJIDAD ADICIONALES

### 4.1 Integración y Conectividad

#### A. **SIN INTEGRACIÓN** (Factor: 1.0)
- Aplicación aislada
- Sin conexiones externas
- Datos autónomos

#### B. **INTEGRACIÓN BÁSICA** (Factor: 1.2 - 1.4)
- Conexión a 1-3 sistemas externos
- APIs REST simples
- Formatos estándar (JSON, XML)

#### C. **INTEGRACIÓN COMPLEJA** (Factor: 1.5 - 2.0)
- Múltiples sistemas (4+ integraciones)
- Protocolos diversos (SOAP, REST, GraphQL)
- Transformación de datos compleja
- Orquestación de servicios

### 4.2 Seguridad y Cumplimiento

#### A. **SEGURIDAD BÁSICA** (Factor: 1.0)
- Autenticación simple
- Sin datos sensibles
- Acceso local únicamente

#### B. **SEGURIDAD ESTÁNDAR** (Factor: 1.3 - 1.5)
- Autenticación robusta
- Autorización por roles
- Cifrado básico
- Logs de auditoría

#### C. **SEGURIDAD AVANZADA** (Factor: 1.6 - 2.2)
- Cumplimiento ISO 27001
- Cifrado extremo a extremo
- Auditoría completa
- Certificaciones de seguridad
- Datos altamente sensibles

---

## 5. TABLA DE MULTIPLICADORES POR TIPO DE SOFTWARE

### 5.1 Aplicaciones de Gestión Interna

| Característica | Factor Mínimo | Factor Máximo | Justificación |
|---|---|---|---|
| **ERP Básico** | 1.2 | 1.8 | Complejidad de módulos integrados |
| **CRM Simple** | 0.9 | 1.3 | Funcionalidad estándar |
| **Sistema de Inventarios** | 1.0 | 1.4 | Según integración con otros sistemas |
| **Gestión Documental** | 1.1 | 1.6 | Según volumen y seguridad requerida |

### 5.2 Aplicaciones de Auditoría y Control

| Característica | Factor Mínimo | Factor Máximo | Justificación |
|---|---|---|---|
| **Sistema de Auditoría** | 1.4 | 2.0 | Requerimientos de trazabilidad |
| **Control de Gestión** | 1.2 | 1.7 | Reportería avanzada |
| **Compliance/Cumplimiento** | 1.5 | 2.2 | Normativas específicas |

### 5.3 Aplicaciones Web y Móviles

| Característica | Factor Mínimo | Factor Máximo | Justificación |
|---|---|---|---|
| **Sitio Web Corporativo** | 0.8 | 1.2 | Según funcionalidad |
| **Aplicación Web Compleja** | 1.3 | 1.9 | SPA, múltiples usuarios |
| **App Móvil Nativa** | 1.4 | 2.1 | Desarrollo para múltiples plataformas |

---

## 6. VALORES BASE POR COMPLEJIDAD (Colombia 2025)

### 6.1 Valores por Hora de Desarrollo

| Complejidad | Costo/Hora (COP) | Descripción |
|---|---|---|
| **Muy Baja** | $18,000 - $25,000 | VBA, scripts simples |
| **Baja** | $25,000 - $35,000 | Access, aplicaciones básicas |
| **Media** | $35,000 - $50,000 | Aplicaciones web estándar |
| **Alta** | $50,000 - $70,000 | Sistemas enterprise |
| **Muy Alta** | $70,000 - $100,000 | Sistemas críticos, alta seguridad |

### 6.2 Estimación de Horas por Funcionalidad Básica

| Funcionalidad | Horas (Simple) | Horas (Compleja) |
|---|---|---|
| **CRUD básico** | 8 - 16 | 24 - 40 |
| **Autenticación** | 16 - 24 | 40 - 80 |
| **Reportes** | 8 - 16 | 24 - 48 |
| **Dashboard** | 16 - 32 | 48 - 96 |
| **Integración API** | 16 - 24 | 40 - 80 |
| **Workflow** | 24 - 48 | 80 - 160 |

---

## 7. ACTUALIZACIÓN Y MANTENIMIENTO

### 7.1 Factores de Depreciación Tecnológica

| Antigüedad | Factor de Valor | Comentario |
|---|---|---|
| **0-1 años** | 1.0 | Valor completo |
| **1-3 años** | 0.9 - 0.95 | Depreciación mínima |
| **3-5 años** | 0.7 - 0.85 | Depreciación moderada |
| **5-10 años** | 0.4 - 0.65 | Tecnología desactualizada |
| **10+ años** | 0.2 - 0.4 | Legacy, requiere migración |

### 7.2 Costo de Mantenimiento Anual

| Tipo de Software | % del Valor Inicial | Justificación |
|---|---|---|
| **Aplicaciones simples** | 15% - 20% | Mantenimiento básico |
| **Aplicaciones complejas** | 20% - 30% | Actualizaciones frecuentes |
| **Sistemas críticos** | 25% - 40% | Soporte 24/7, alta disponibilidad |

---

**Última actualización:** 5 de agosto de 2025  
**Próxima revisión:** Febrero 2026  
**Responsable:** Sistema de Valoración Científica de Software
