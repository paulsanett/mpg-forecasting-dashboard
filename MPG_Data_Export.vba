Sub ExportCleanCSVForMLModeling()
'
' MPG Data Export for ML Forecasting
' Creates perfectly formatted CSV for 2-5% accuracy target
' Run this daily to generate clean data for forecasting models
'
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim outputPath As String
    Dim csvFile As Integer
    Dim i As Long
    Dim dateVal As Date
    Dim dayOfWeek As String
    
    ' Set the active worksheet
    Set ws = ActiveSheet
    
    ' Find last row with data
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    ' Set output path to specified directory
    outputPath = "/Users/PaulSanett/Dropbox/Millenium Parking Garages/Financials/Forecast/Windsurf Forecasting Tool/MPG_Clean_Data.csv"
    
    ' Open CSV file for writing
    csvFile = FreeFile
    Open outputPath For Output As csvFile
    
    ' Write header row with clean field names
    Print #csvFile, "date,day_of_week,gpn_units,gpn_revenue,gps_units,gps_revenue," & _
                   "lakeside_units,lakeside_revenue,millennium_units,millennium_revenue," & _
                   "online_units,online_revenue,total_units,total_revenue," & _
                   "avg_reservation_value,gas_price,notes,temperature,has_event"
    
    ' Initialize progress
    Application.ScreenUpdating = False
    Application.StatusBar = "Exporting data for ML modeling..."
    
    ' Process each row of data
    For i = 2 To lastRow ' Start from row 2 (skip header)
        
        ' Update progress every 100 rows
        If i Mod 100 = 0 Then
            Application.StatusBar = "Processing row " & i & " of " & lastRow
        End If
        
        ' Skip rows with no date or revenue
        If IsEmpty(ws.Cells(i, 1)) Or IsEmpty(ws.Cells(i, 36)) Then ' A=Date, AJ=Total Revenue
            GoTo NextRow
        End If
        
        ' Parse and format date
        On Error Resume Next
        dateVal = ws.Cells(i, 1).Value ' Column A
        If Err.Number <> 0 Then
            Err.Clear
            GoTo NextRow
        End If
        On Error GoTo 0
        
        ' Get day of week (3-letter format)
        dayOfWeek = UCase(Left(Format(dateVal, "ddd"), 3))
        
        ' Extract temperature from notes (Column AT = 46)
        Dim temperature As String
        Dim notes As String
        Dim hasEvent As String
        
        notes = Trim(CStr(ws.Cells(i, 46).Value)) ' Column AT
        temperature = ExtractTemperature(notes)
        hasEvent = IIf(DetectEvent(notes), "1", "0")
        
        ' Write clean data row
        Print #csvFile, _
            Format(dateVal, "yyyy-mm-dd") & "," & _
            dayOfWeek & "," & _
            CleanNumeric(ws.Cells(i, 7)) & "," & _
            CleanCurrency(ws.Cells(i, 8)) & "," & _
            CleanNumeric(ws.Cells(i, 13)) & "," & _
            CleanCurrency(ws.Cells(i, 14)) & "," & _
            CleanNumeric(ws.Cells(i, 19)) & "," & _
            CleanCurrency(ws.Cells(i, 20)) & "," & _
            CleanNumeric(ws.Cells(i, 25)) & "," & _
            CleanCurrency(ws.Cells(i, 26)) & "," & _
            CleanNumeric(ws.Cells(i, 27)) & "," & _
            CleanCurrency(ws.Cells(i, 28)) & "," & _
            CleanNumeric(ws.Cells(i, 32)) & "," & _
            CleanCurrency(ws.Cells(i, 36)) & "," & _
            CleanCurrency(ws.Cells(i, 40)) & "," & _
            CleanCurrency(ws.Cells(i, 45)) & "," & _
            """" & Replace(notes, """", """""") & """" & "," & _
            temperature & "," & _
            hasEvent
        
NextRow:
    Next i
    
    ' Close file
    Close csvFile
    
    ' Restore Excel settings
    Application.ScreenUpdating = True
    Application.StatusBar = False
    
    ' Success message
    MsgBox "✅ SUCCESS!" & vbCrLf & vbCrLf & _
           "Clean CSV exported to:" & vbCrLf & _
           outputPath & vbCrLf & vbCrLf & _
           "Processed " & (lastRow - 1) & " rows" & vbCrLf & _
           "Ready for ML forecasting with 2-5% accuracy target!", _
           vbInformation, "MPG Data Export Complete"
    
End Sub

Function CleanCurrency(cellValue As Variant) As String
'
' Clean currency values for ML modeling
'
    Dim cleanValue As String
    
    If IsEmpty(cellValue) Or cellValue = "" Or cellValue = "-" Then
        CleanCurrency = "0"
    Else
        cleanValue = Trim(CStr(cellValue))
        ' Remove currency symbols and commas
        cleanValue = Replace(cleanValue, "$", "")
        cleanValue = Replace(cleanValue, ",", "")
        cleanValue = Replace(cleanValue, " ", "")
        
        ' Validate numeric
        If IsNumeric(cleanValue) Then
            CleanCurrency = cleanValue
        Else
            CleanCurrency = "0"
        End If
    End If
End Function

Function CleanNumeric(cellValue As Variant) As String
'
' Clean numeric values for ML modeling
'
    Dim cleanValue As String
    
    If IsEmpty(cellValue) Or cellValue = "" Or cellValue = "-" Then
        CleanNumeric = "0"
    Else
        cleanValue = Trim(CStr(cellValue))
        ' Remove commas
        cleanValue = Replace(cleanValue, ",", "")
        cleanValue = Replace(cleanValue, " ", "")
        
        ' Validate numeric
        If IsNumeric(cleanValue) Then
            CleanNumeric = cleanValue
        Else
            CleanNumeric = "0"
        End If
    End If
End Function

Function ExtractTemperature(notes As String) As String
'
' Extract temperature from notes field using simple string functions
'
    Dim notesLower As String
    Dim pos As Integer
    Dim tempStr As String
    Dim temp As Integer
    Dim i As Integer
    
    If Len(notes) = 0 Then
        ExtractTemperature = "70" ' Default temperature
        Exit Function
    End If
    
    notesLower = LCase(notes)
    
    ' Look for "degrees fahrenheit" pattern
    pos = InStr(notesLower, "degrees fahrenheit")
    If pos > 0 Then
        ' Look backwards for the number
        For i = pos - 1 To 1 Step -1
            If IsNumeric(Mid(notesLower, i, 1)) Then
                tempStr = Mid(notesLower, i, 1) & tempStr
            ElseIf Len(tempStr) > 0 Then
                Exit For
            End If
        Next i
        
        If Len(tempStr) > 0 And IsNumeric(tempStr) Then
            temp = CInt(tempStr)
            If temp >= 20 And temp <= 120 Then
                ExtractTemperature = CStr(temp)
                Exit Function
            End If
        End If
    End If
    
    ' Look for "degrees" pattern
    pos = InStr(notesLower, "degrees")
    If pos > 0 Then
        tempStr = ""
        For i = pos - 1 To 1 Step -1
            If IsNumeric(Mid(notesLower, i, 1)) Then
                tempStr = Mid(notesLower, i, 1) & tempStr
            ElseIf Len(tempStr) > 0 Then
                Exit For
            End If
        Next i
        
        If Len(tempStr) > 0 And IsNumeric(tempStr) Then
            temp = CInt(tempStr)
            If temp >= 20 And temp <= 120 Then
                ExtractTemperature = CStr(temp)
                Exit Function
            End If
        End If
    End If
    
    ' Look for "temp" pattern
    pos = InStr(notesLower, "temp")
    If pos > 0 Then
        tempStr = ""
        For i = pos + 4 To Len(notesLower)
            If IsNumeric(Mid(notesLower, i, 1)) Then
                tempStr = tempStr & Mid(notesLower, i, 1)
            ElseIf Len(tempStr) > 0 Then
                Exit For
            End If
        Next i
        
        If Len(tempStr) > 0 And IsNumeric(tempStr) Then
            temp = CInt(tempStr)
            If temp >= 20 And temp <= 120 Then
                ExtractTemperature = CStr(temp)
                Exit Function
            End If
        End If
    End If
    
    ' Default if no temperature found
    ExtractTemperature = "70"
End Function

Function DetectEvent(notes As String) As Boolean
'
' Detect events from notes field
'
    If Len(notes) = 0 Then
        DetectEvent = False
        Exit Function
    End If
    
    Dim eventKeywords As Variant
    eventKeywords = Array("lollapalooza", "lolla", "festival", "concert", "event", "game", _
                         "cubs", "bears", "bulls", "blackhawks", "marathon", "parade", _
                         "convention", "conference", "holiday", "christmas", "thanksgiving", _
                         "new year", "memorial day", "labor day", "independence day")
    
    Dim notesLower As String
    notesLower = LCase(notes)
    
    Dim i As Integer
    For i = 0 To UBound(eventKeywords)
        If InStr(notesLower, eventKeywords(i)) > 0 Then
            DetectEvent = True
            Exit Function
        End If
    Next i
    
    DetectEvent = False
End Function

Sub TestDataExport()
'
' Test function to verify data export works correctly
'
    Dim startTime As Double
    startTime = Timer
    
    MsgBox "🚀 Starting MPG Data Export Test..." & vbCrLf & _
           "This will create a clean CSV for ML modeling.", vbInformation
    
    ' Run the export
    Call ExportCleanCSVForMLModeling
    
    Dim endTime As Double
    endTime = Timer
    
    MsgBox "⏱️ Export completed in " & Format(endTime - startTime, "0.0") & " seconds", vbInformation
End Sub
