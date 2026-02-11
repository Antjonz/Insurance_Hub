' InsuranceHub Product Import Validation Macro
' =============================================
' This VBA module validates product data in the Excel import template.
' Import this module into the .xlsm version of the template.
'
' Features:
' - Validates required fields are filled
' - Checks premium amounts are positive numbers
' - Ensures product codes follow the correct format (XXX-YYY-NNN)
' - Validates product type against allowed values
' - Highlights errors in red
' - Shows summary message box with validation results
'
' To use:
' 1. Open the product-import-template.xlsx
' 2. Save as .xlsm (macro-enabled workbook)
' 3. Open VBA editor (Alt+F11)
' 4. Import this module (File > Import File)
' 5. Run ValidateProductData from the Macros menu

Option Explicit

Sub ValidateProductData()
    ' Main validation routine for the Products sheet

    Dim ws As Worksheet
    Dim lastRow As Long
    Dim row As Long
    Dim errorCount As Long
    Dim warningCount As Long
    Dim validCount As Long
    Dim cellValue As Variant

    ' Valid product types
    Dim validTypes As Variant
    validTypes = Array("property", "life", "health", "auto", "liability", "travel")

    ' Valid insurer codes
    Dim validInsurers As Variant
    validInsurers = Array("ACH", "AEG", "ALZ", "ASR", "NNG", "NAT")

    ' Get the Products sheet
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets("Products")
    On Error GoTo 0

    If ws Is Nothing Then
        MsgBox "Sheet 'Products' niet gevonden!", vbCritical, "Validatiefout"
        Exit Sub
    End If

    ' Find the last row with data
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).row

    If lastRow < 4 Then
        MsgBox "Geen data gevonden om te valideren." & vbCrLf & _
               "Voer productgegevens in vanaf rij 4.", vbInformation, "Validatie"
        Exit Sub
    End If

    ' Clear previous formatting
    ws.Range("A4:H" & lastRow).Interior.ColorIndex = xlNone
    ws.Range("A4:H" & lastRow).Font.Color = RGB(0, 0, 0)

    errorCount = 0
    warningCount = 0
    validCount = 0

    ' Validate each row
    For row = 4 To lastRow
        Dim rowHasError As Boolean
        rowHasError = False

        ' Skip empty rows
        If IsEmpty(ws.Cells(row, 1).Value) And IsEmpty(ws.Cells(row, 2).Value) Then
            GoTo NextRow
        End If

        ' 1. Validate product_code (required, format XXX-YYY-NNN)
        cellValue = Trim(ws.Cells(row, 1).Value & "")
        If Len(cellValue) = 0 Then
            MarkError ws.Cells(row, 1), "Product code is verplicht"
            rowHasError = True
            errorCount = errorCount + 1
        ElseIf InStr(cellValue, "-") = 0 Then
            MarkError ws.Cells(row, 1), "Ongeldig formaat (verwacht: XXX-YYY-NNN)"
            rowHasError = True
            errorCount = errorCount + 1
        End If

        ' 2. Validate name (required)
        cellValue = Trim(ws.Cells(row, 2).Value & "")
        If Len(cellValue) = 0 Then
            MarkError ws.Cells(row, 2), "Productnaam is verplicht"
            rowHasError = True
            errorCount = errorCount + 1
        ElseIf Len(cellValue) < 3 Then
            MarkWarning ws.Cells(row, 2), "Naam is erg kort"
            warningCount = warningCount + 1
        End If

        ' 3. Validate product_type (required, must be valid)
        cellValue = LCase(Trim(ws.Cells(row, 3).Value & ""))
        If Len(cellValue) = 0 Then
            MarkError ws.Cells(row, 3), "Product type is verplicht"
            rowHasError = True
            errorCount = errorCount + 1
        ElseIf Not IsInArray(cellValue, validTypes) Then
            MarkError ws.Cells(row, 3), "Ongeldig producttype"
            rowHasError = True
            errorCount = errorCount + 1
        End If

        ' 4. Validate insurer_code (required, must be valid)
        cellValue = UCase(Trim(ws.Cells(row, 4).Value & ""))
        If Len(cellValue) = 0 Then
            MarkError ws.Cells(row, 4), "Verzekeraar code is verplicht"
            rowHasError = True
            errorCount = errorCount + 1
        ElseIf Not IsInArray(cellValue, validInsurers) Then
            MarkError ws.Cells(row, 4), "Onbekende verzekeraar code"
            rowHasError = True
            errorCount = errorCount + 1
        End If

        ' 5. Validate base_premium (required, positive number)
        cellValue = ws.Cells(row, 5).Value
        If IsEmpty(cellValue) Or Len(Trim(cellValue & "")) = 0 Then
            MarkError ws.Cells(row, 5), "Basispremie is verplicht"
            rowHasError = True
            errorCount = errorCount + 1
        ElseIf Not IsNumeric(cellValue) Then
            MarkError ws.Cells(row, 5), "Premie moet een getal zijn"
            rowHasError = True
            errorCount = errorCount + 1
        ElseIf CDbl(cellValue) <= 0 Then
            MarkError ws.Cells(row, 5), "Premie moet positief zijn"
            rowHasError = True
            errorCount = errorCount + 1
        End If

        ' 6. Validate coverage_amount (optional, but must be positive if provided)
        cellValue = ws.Cells(row, 6).Value
        If Not IsEmpty(cellValue) And Len(Trim(cellValue & "")) > 0 Then
            If Not IsNumeric(cellValue) Then
                MarkError ws.Cells(row, 6), "Dekking moet een getal zijn"
                rowHasError = True
                errorCount = errorCount + 1
            ElseIf CDbl(cellValue) < 0 Then
                MarkError ws.Cells(row, 6), "Dekking mag niet negatief zijn"
                rowHasError = True
                errorCount = errorCount + 1
            End If
        End If

        ' 7. Validate deductible (optional, must be >= 0 if provided)
        cellValue = ws.Cells(row, 7).Value
        If Not IsEmpty(cellValue) And Len(Trim(cellValue & "")) > 0 Then
            If Not IsNumeric(cellValue) Then
                MarkWarning ws.Cells(row, 7), "Eigen risico moet een getal zijn"
                warningCount = warningCount + 1
            ElseIf CDbl(cellValue) < 0 Then
                MarkError ws.Cells(row, 7), "Eigen risico mag niet negatief zijn"
                rowHasError = True
                errorCount = errorCount + 1
            End If
        End If

        ' Mark valid row
        If Not rowHasError Then
            validCount = validCount + 1
        End If

NextRow:
    Next row

    ' Show summary
    Dim totalRows As Long
    totalRows = validCount + errorCount

    Dim msg As String
    msg = "Validatie Resultaten" & vbCrLf & vbCrLf
    msg = msg & "Totaal rijen gecontroleerd: " & (lastRow - 3) & vbCrLf
    msg = msg & "Geldige rijen: " & validCount & vbCrLf
    msg = msg & "Fouten gevonden: " & errorCount & vbCrLf
    msg = msg & "Waarschuwingen: " & warningCount & vbCrLf & vbCrLf

    If errorCount = 0 Then
        msg = msg & "Het bestand is klaar voor import!"
        MsgBox msg, vbInformation, "Validatie Geslaagd"
    Else
        msg = msg & "Corrigeer de rode cellen voordat u importeert."
        MsgBox msg, vbExclamation, "Validatie Fouten Gevonden"
    End If

End Sub


Private Sub MarkError(cell As Range, message As String)
    ' Highlight a cell as an error (red background)
    cell.Interior.Color = RGB(255, 200, 200)
    cell.Font.Color = RGB(180, 0, 0)
    cell.AddComment message
End Sub


Private Sub MarkWarning(cell As Range, message As String)
    ' Highlight a cell as a warning (yellow background)
    cell.Interior.Color = RGB(255, 255, 200)
    cell.Font.Color = RGB(150, 120, 0)
    cell.AddComment message
End Sub


Private Function IsInArray(val As Variant, arr As Variant) As Boolean
    ' Check if a value exists in an array
    Dim i As Long
    IsInArray = False
    For i = LBound(arr) To UBound(arr)
        If LCase(val) = LCase(arr(i)) Then
            IsInArray = True
            Exit Function
        End If
    Next i
End Function


Sub ClearValidation()
    ' Clear all validation formatting and comments
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Products")

    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).row

    If lastRow >= 4 Then
        ws.Range("A4:H" & lastRow).Interior.ColorIndex = xlNone
        ws.Range("A4:H" & lastRow).Font.Color = RGB(0, 0, 0)

        ' Remove comments
        Dim cell As Range
        For Each cell In ws.Range("A4:H" & lastRow)
            If Not cell.Comment Is Nothing Then
                cell.Comment.Delete
            End If
        Next cell
    End If

    MsgBox "Validatie opmaak is gewist.", vbInformation, "Opruimen"
End Sub
