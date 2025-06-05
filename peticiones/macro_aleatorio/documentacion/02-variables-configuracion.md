# 🔧 Variables y Configuración - Análisis Detallado

## 🎯 Variables Globales

### 📊 Variables de Alcance Module
```vba
Dim CantNum As Integer
Dim RangoNum As String
```

#### 🔍 `CantNum As Integer`
- **Propósito**: Almacena el número de la última fila para el rango de salida
- **Uso**: `CantNum = cantidadSolicitada + 6`
- **Ejemplo**: Si usuario pide 10 elementos → `CantNum = 16`

```
📊 Visualización:
Usuario solicita: 10 elementos
Fila inicial: 7 (A7)
CantNum = 10 + 6 = 16
Resultado: Rango A7:B16
```

#### 🔍 `RangoNum As String` 
- **Propósito**: Define el rango completo para seleccionar/copiar
- **Formato**: `"A7:B" & CantNum`
- **Ejemplo**: `"A7:B16"` para 10 elementos

---

## 🏗️ Variables Locales de la Subrutina

### 📋 Variables de Hoja de Trabajo
```vba
Dim wsDestino As Worksheet
Dim wsPoblacion As Worksheet
```

#### 🎯 `wsDestino As Worksheet`
```vba
Set wsDestino = ActiveSheet
```
- **Función**: Referencia a la hoja donde se escribirán los resultados
- **¿Por qué ActiveSheet?**: Permite flexibilidad - funciona en cualquier hoja activa
- **Uso posterior**: `wsDestino.Range("A7:B450").ClearContents`

#### 📊 `wsPoblacion As Worksheet`
```vba
Set wsPoblacion = Worksheets("Población inventario")
```
- **Función**: Referencia específica a la hoja con los datos fuente
- **Nombre fijo**: Siempre busca la hoja llamada "Población inventario"
- **Uso posterior**: `wsPoblacion.Range("A3:A47").Value`

### 🗂️ Variables de Datos
```vba
Dim datosOriginales As Variant
Dim datosSeleccionados() As Variant
```

#### 📦 `datosOriginales As Variant`
```vba
datosOriginales = wsPoblacion.Range("A3:A47").Value
```
- **Tipo**: Array bidimensional (45 x 1)
- **Contenido**: Todos los elementos de la población
- **Estructura**:
  ```
  datosOriginales(1,1) = Valor de A3
  datosOriginales(2,1) = Valor de A4
  ...
  datosOriginales(45,1) = Valor de A47
  ```

#### 🎲 `datosSeleccionados() As Variant`
```vba
ReDim datosSeleccionados(1 To cantidadSolicitada, 1 To 1)
```
- **Tipo**: Array dinámico bidimensional
- **Tamaño**: Se ajusta según la cantidad solicitada
- **Ejemplo para 3 elementos**:
  ```
  datosSeleccionados(1,1) = Primer elemento seleccionado
  datosSeleccionados(2,1) = Segundo elemento seleccionado  
  datosSeleccionados(3,1) = Tercer elemento seleccionado
  ```

### 🔐 Variable de Control de Duplicados
```vba
Dim numerosUsados As Object
Set numerosUsados = CreateObject("Scripting.Dictionary")
```

#### 🗝️ `numerosUsados As Object`
- **Tipo Real**: Dictionary (colección clave-valor)
- **Propósito**: Evitar seleccionar el mismo elemento dos veces
- **Funcionamiento**:
  ```vba
  ' Verificar si un número ya fue usado:
  If Not numerosUsados.Exists(numeroAleatorio) Then
      numerosUsados.Add numeroAleatorio, True
  End If
  ```

**📊 Ejemplo Visual del Dictionary**:
```
Iteración 1: numeroAleatorio = 15
Dictionary: {15: True}

Iteración 2: numeroAleatorio = 8  
Dictionary: {15: True, 8: True}

Iteración 3: numeroAleatorio = 15 (repetido!)
¿Exists(15)? → Sí → Generar otro número
```

### 🔢 Variables de Control y Contadores
```vba
Dim i As Integer
Dim fila As Integer  
Dim numeroAleatorio As Integer
Dim cantidadSolicitada As Integer
Dim totalDatos As Integer
```

#### 📏 Variables Detalladas

| Variable | Tipo | Propósito | Rango Típico |
|----------|------|-----------|--------------|
| `i` | Integer | Contador para bucle For | 1 a cantidadSolicitada |
| `fila` | Integer | Contador para bucle Do While | 1 a cantidadSolicitada |
| `numeroAleatorio` | Integer | Índice aleatorio generado | 1 a 45 |
| `cantidadSolicitada` | Integer | Input del usuario | 1 a 45 |
| `totalDatos` | Integer | Total elementos en población | 45 (fijo) |

---

## 🔄 Ciclo de Vida de las Variables

### 📈 Diagrama de Flujo de Datos
```
🏁 INICIO
├── 📋 wsDestino = ActiveSheet
├── 📊 wsPoblacion = "Población inventario"  
├── 🗝️ numerosUsados = Dictionary vacío
│
🎯 ENTRADA DE DATOS
├── 💬 cantidadSolicitada = InputBox()
├── 📦 datosOriginales = Range("A3:A47")
├── 📏 totalDatos = UBound(datosOriginales)
│
🎲 PROCESAMIENTO  
├── 🔄 ReDim datosSeleccionados(1 To cantidad, 1 To 1)
├── 🎯 fila = 1
└── 🔁 Do While fila <= cantidadSolicitada
    ├── 🎲 numeroAleatorio = Int(Rnd() * totalDatos) + 1
    ├── ❓ If Not numerosUsados.Exists(numeroAleatorio)
    ├── ✅ numerosUsados.Add(numeroAleatorio, True)
    ├── 📝 datosSeleccionados(fila,1) = datosOriginales(numeroAleatorio,1)
    └── ⬆️ fila = fila + 1
│
📤 SALIDA
├── 🔢 CantNum = cantidadSolicitada + 6
├── 📍 RangoNum = "A7:B" & CantNum
└── 🔁 For i = 1 To cantidadSolicitada
    ├── 📝 wsDestino.Cells(6+i, 1) = i
    └── 📝 wsDestino.Cells(6+i, 2) = datosSeleccionados(i,1)
```

---

## 🧮 Cálculos y Transformaciones

### 🎯 Fórmula del Rango Dinámico
```vba
CantNum = cantidadSolicitada + 6
RangoNum = "A7:B" & CantNum
```

**¿Por qué +6?**
- Los datos comienzan en la fila 7 (no en la 1)
- Si queremos 10 elementos: filas 7,8,9,10,11,12,13,14,15,16
- Última fila = 6 + 10 = 16
- Rango = "A7:B16"

### 🎲 Generación de Números Aleatorios
```vba
numeroAleatorio = Int(Rnd() * totalDatos) + 1
```

**Desglose matemático**:
1. `Rnd()` → Número decimal entre 0 y 1 (ej: 0.7234)
2. `Rnd() * totalDatos` → Multiplicar por 45 (ej: 32.553)
3. `Int(...)` → Parte entera (ej: 32)
4. `... + 1` → Sumar 1 para rango 1-45 (ej: 33)

**Distribución**:
```
Rnd() = 0.0000 → numeroAleatorio = 1
Rnd() = 0.2222 → numeroAleatorio = 10  
Rnd() = 0.5555 → numeroAleatorio = 25
Rnd() = 0.8888 → numeroAleatorio = 40
Rnd() = 0.9999 → numeroAleatorio = 45
```

---

## 🛡️ Validaciones y Controles de Error

### ✅ Validación de Entrada
```vba
If cantidadSolicitada <= 0 Then
    MsgBox "Por favor ingrese un número válido mayor que 0"
    Exit Sub
End If
```
**Casos que captura**:
- Números negativos (-5)
- Cero (0)
- Texto que se convierte a 0 ("abc" → 0)

### 📊 Validación de Capacidad
```vba
If cantidadSolicitada > totalDatos Then
    MsgBox "La cantidad solicitada (" & cantidadSolicitada & ") es mayor que los datos disponibles (" & totalDatos & ")"
    Exit Sub
End If
```
**Ejemplo de error**:
```
Usuario solicita: 50 elementos
Datos disponibles: 45 elementos  
Resultado: Error + Salida del programa
```

---

## 🧹 Limpieza de Memoria

### 🗑️ Liberación de Objetos
```vba
Set numerosUsados = Nothing
Set wsDestino = Nothing  
Set wsPoblacion = Nothing
```

**¿Por qué es importante?**
- Libera memoria RAM
- Evita referencias colgantes
- Buena práctica en VBA
- Previene errores en ejecuciones posteriores

---

## 💡 Optimizaciones Posibles

### 🚀 Variables que se podrían mejorar

| Variable Actual | Tipo Actual | Tipo Optimizado | Beneficio |
|-----------------|-------------|-----------------|-----------|
| `i As Integer` | Integer (-32,768 a 32,767) | Long | Soporta más elementos |
| `fila As Integer` | Integer | Long | Mayor capacidad |
| `numeroAleatorio As Integer` | Integer | Long | Poblaciones más grandes |
| `CantNum As Integer` | Integer | Long | Más filas |

### 📊 Constantes vs Variables
```vba
' Actual (hardcoded):
datosOriginales = wsPoblacion.Range("A3:A47").Value

' Optimizado (configurable):
Const INICIO_POBLACION As String = "A3"
Const FIN_POBLACION As String = "A47"
datosOriginales = wsPoblacion.Range(INICIO_POBLACION & ":" & FIN_POBLACION).Value
```

---

**¡Continúa con [🎲 Algoritmo de Selección](03-algoritmo-seleccion.md) para entender la lógica central!**
