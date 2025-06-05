Dim CantNum As Integer
Dim RangoNum As String

Sub ALEATORIO()

    Dim wsDestino As Worksheet
    Dim wsPoblacion As Worksheet
    Dim datosOriginales As Variant
    Dim datosSeleccionados() As Variant
    Dim numerosUsados As Object
    Dim i As Integer
    Dim fila As Integer
    Dim numeroAleatorio As Integer
    Dim cantidadSolicitada As Integer
    Dim totalDatos As Integer
    
    Set wsDestino = ActiveSheet
    Set wsPoblacion = Worksheets("Población inventario")
    Set numerosUsados = CreateObject("Scripting.Dictionary")
    
    ' Limpiar datos anteriores
    wsDestino.Range("A7:B450").ClearContents 'Borrar datos seleccionados'
    
    ' Obtener cantidad solicitada
    cantidadSolicitada = InputBox("Indique la cantidad de números a generar")
    
    ' Verificar que se ingresó un número válido
    If cantidadSolicitada <= 0 Then
        MsgBox "Por favor ingrese un número válido mayor que 0"
        Exit Sub
    End If
    
    ' Obtener datos de la hoja "Población inventario"
    datosOriginales = wsPoblacion.Range("A3:A47").Value
    totalDatos = UBound(datosOriginales, 1)
    
    ' Verificar que hay suficientes datos
    If cantidadSolicitada > totalDatos Then
        MsgBox "La cantidad solicitada (" & cantidadSolicitada & ") es mayor que los datos disponibles (" & totalDatos & ")"
        Exit Sub
    End If
      ' Redimensionar array para datos seleccionados
    ReDim datosSeleccionados(1 To cantidadSolicitada, 1 To 1)
    
    ' Seleccionar números aleatorios sin repetición
    Randomize ' Inicializar generador de números aleatorios
    fila = 1
    
    Do While fila <= cantidadSolicitada
        numeroAleatorio = Int(Rnd() * totalDatos) + 1
        
        ' Verificar que no se haya usado este índice
        If Not numerosUsados.Exists(numeroAleatorio) Then
            numerosUsados.Add numeroAleatorio, True
            datosSeleccionados(fila, 1) = datosOriginales(numeroAleatorio, 1)
            fila = fila + 1
        End If
    Loop
      ' Escribir datos seleccionados en el rango destino
    CantNum = cantidadSolicitada + 6 'Para iniciar desde la fila 7'
    RangoNum = "A7:B" & CantNum
    
    For i = 1 To cantidadSolicitada
        wsDestino.Cells(6 + i, 1).Value = i ' Columna A - números secuenciales (1, 2, 3, etc.)
        wsDestino.Cells(6 + i, 2).Value = datosSeleccionados(i, 1) ' Columna B - números aleatorios de la población
    Next i
    
    ' Seleccionar rango y convertir a valores
    wsDestino.Range(RangoNum).Select
    Selection.Copy 'Copiar'
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False 'Pegar'
    wsDestino.Range("B7").Select 'Volver a posición'
    Application.CutCopyMode = False 'Salir'
    
    ' Limpiar objetos
    Set numerosUsados = Nothing
    Set wsDestino = Nothing
    Set wsPoblacion = Nothing
End Sub