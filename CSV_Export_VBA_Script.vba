Sub ExportCleanHistoricBookingData()
'
' Clean CSV Export for Historic Booking Data
' Exports only the data range with proper formatting for forecasting system
' Created for Paul Sanett - Millennium Parking Garages
'

    Dim ws As Worksheet
    Dim lastRow As Long
    Dim lastCol As Long
    Dim dataRange As Range
    Dim exportPath As String
    Dim fileName As String
    Dim fullPath As String
    
    ' Error handling
    On Error GoTo ErrorHandler
    
    ' Get the active worksheet (assumes your data is on the active sheet)
    Set ws = ActiveSheet
    
    ' Find the actual data range (not the entire columns)
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    ' Validate that we have data
    If lastRow < 2 Then
        MsgBox "No data found to export. Please ensure your data starts in row 1 with headers.", vbExclamation
        Exit Sub
    End If
    
    ' Set the data range (from A1 to the last row/column with data)
    Set dataRange = ws.Range(ws.Cells(1, 1), ws.Cells(lastRow, lastCol))
    
    ' Display info about what will be exported
    Dim response As VbMsgBoxResult
    response = MsgBox("Export Range: " & dataRange.Address & vbCrLf & _
                     "Rows: " & lastRow & vbCrLf & _
                     "Columns: " & lastCol & vbCrLf & vbCrLf & _
                     "Continue with export?", vbYesNo + vbQuestion, "Confirm Export")
    
    If response = vbNo Then
        Exit Sub
    End If
    
    ' Set export path and filename
    exportPath = Application.ActiveWorkbook.Path
    fileName = "Historic_Booking_Data_Clean.csv"
    fullPath = exportPath & "\" & fileName
    
    ' Create a new workbook for the clean export
    Dim newWb As Workbook
    Dim newWs As Worksheet
    
    Set newWb = Workbooks.Add
    Set newWs = newWb.Sheets(1)
    
    ' Copy the data to the new workbook
    dataRange.Copy
    newWs.Range("A1").PasteSpecial Paste:=xlPasteValues
    
    ' Clean up the headers (remove extra spaces and special characters)
    Dim col As Long
    For col = 1 To lastCol
        Dim headerText As String
        headerText = Trim(newWs.Cells(1, col).Value)
        
        ' Remove common problematic characters
        headerText = Replace(headerText, Chr(160), " ") ' Non-breaking space
        headerText = Replace(headerText, "  ", " ")      ' Double spaces
        headerText = Trim(headerText)
        
        ' Clean up specific known headers
        If InStr(headerText, "Total Revenue") > 0 Then
            headerText = "Total Revenue"
        ElseIf InStr(headerText, "Grant Park North") > 0 And InStr(headerText, "Total") > 0 Then
            headerText = "Grant Park North Revenue"
        ElseIf InStr(headerText, "Grant Park South") > 0 And InStr(headerText, "Total") > 0 Then
            headerText = "Grant Park South Revenue"
        ElseIf InStr(headerText, "Lakeside") > 0 And InStr(headerText, "Total") > 0 Then
            headerText = "Lakeside Revenue"
        ElseIf InStr(headerText, "Millennium") > 0 And InStr(headerText, "Total") > 0 Then
            headerText = "Millennium Revenue"
        ElseIf InStr(headerText, "Day of Week") > 0 Then
            headerText = "Day of Week"
        ElseIf InStr(headerText, "Date") > 0 And Len(headerText) < 10 Then
            headerText = "Date"
        End If
        
        newWs.Cells(1, col).Value = headerText
    Next col
    
    ' Format the data properly
    ' Ensure dates are in consistent format
    Dim dateCol As Long
    dateCol = 0
    
    ' Find the date column
    For col = 1 To lastCol
        If InStr(UCase(newWs.Cells(1, col).Value), "DATE") > 0 Then
            dateCol = col
            Exit For
        End If
    Next col
    
    ' Format date column if found
    If dateCol > 0 Then
        Dim dataRowRange As Range
        Set dataRowRange = newWs.Range(newWs.Cells(2, dateCol), newWs.Cells(lastRow, dateCol))
        
        ' Format as MM/DD/YYYY
        dataRowRange.NumberFormat = "mm/dd/yyyy"
    End If
    
    ' Format revenue columns (remove any text formatting)
    For col = 1 To lastCol
        Dim headerValue As String
        headerValue = UCase(newWs.Cells(1, col).Value)
        
        If InStr(headerValue, "REVENUE") > 0 Or InStr(headerValue, "TOTAL") > 0 Then
            Dim revenueRange As Range
            Set revenueRange = newWs.Range(newWs.Cells(2, col), newWs.Cells(lastRow, col))
            
            ' Clean up revenue values
            Dim row As Long
            For row = 2 To lastRow
                Dim cellValue As String
                cellValue = CStr(newWs.Cells(row, col).Value)
                
                ' Remove currency symbols and clean up
                cellValue = Replace(cellValue, "$", "")
                cellValue = Replace(cellValue, ",", "")
                cellValue = Trim(cellValue)
                
                ' Handle empty or invalid values
                If cellValue = "" Or cellValue = "-" Or cellValue = " - " Then
                    cellValue = "0"
                End If
                
                ' Try to convert to number
                If IsNumeric(cellValue) Then
                    newWs.Cells(row, col).Value = CDbl(cellValue)
                Else
                    newWs.Cells(row, col).Value = 0
                End If
            Next row
            
            ' Format as number with 2 decimal places
            revenueRange.NumberFormat = "0.00"
        End If
    Next col
    
    ' Save as CSV with proper settings
    Application.DisplayAlerts = False
    
    ' Use SaveAs with specific CSV format
    newWb.SaveAs fileName:=fullPath, _
                  FileFormat:=xlCSV, _
                  CreateBackup:=False, _
                  Local:=False
    
    ' Close the temporary workbook
    newWb.Close SaveChanges:=False
    
    Application.DisplayAlerts = True
    Application.CutCopyMode = False
    
    ' Success message
    MsgBox "Clean CSV export completed successfully!" & vbCrLf & vbCrLf & _
           "File saved as: " & fullPath & vbCrLf & vbCrLf & _
           "This file is optimized for your forecasting system and will load much faster.", _
           vbInformation, "Export Complete"
    
    Exit Sub
    
ErrorHandler:
    Application.DisplayAlerts = True
    Application.CutCopyMode = False
    
    If Not newWb Is Nothing Then
        newWb.Close SaveChanges:=False
    End If
    
    MsgBox "An error occurred during export: " & Err.Description, vbCritical, "Export Error"
End Sub

Sub QuickAddTodaysData()
'
' Quick Add Today's Data
' Prompts for today's revenue and adds it to the end of the data
'

    Dim ws As Worksheet
    Dim lastRow As Long
    Dim todayDate As Date
    Dim todayRevenue As String
    Dim response As String
    
    ' Error handling
    On Error GoTo ErrorHandler
    
    Set ws = ActiveSheet
    todayDate = Date
    
    ' Find the last row with data
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    
    ' Check if today's date already exists
    Dim dateCol As Long
    dateCol = 1 ' Assume date is in column A
    
    Dim i As Long
    For i = 2 To lastRow
        If ws.Cells(i, dateCol).Value = todayDate Then
            MsgBox "Today's date (" & Format(todayDate, "mm/dd/yyyy") & ") already exists in the data.", vbExclamation
            Exit Sub
        End If
    Next i
    
    ' Prompt for today's revenue
    response = InputBox("Enter today's total revenue (numbers only, no $ or commas):", _
                       "Add Today's Data - " & Format(todayDate, "mm/dd/yyyy"))
    
    If response = "" Then
        Exit Sub ' User cancelled
    End If
    
    ' Validate the input
    If Not IsNumeric(response) Then
        MsgBox "Please enter a valid number for revenue.", vbExclamation
        Exit Sub
    End If
    
    todayRevenue = response
    
    ' Add the new row
    Dim newRow As Long
    newRow = lastRow + 1
    
    ' Add today's data
    ws.Cells(newRow, 1).Value = todayDate
    ws.Cells(newRow, 1).NumberFormat = "mm/dd/yyyy"
    
    ' Add day of week (assuming column 2)
    ws.Cells(newRow, 2).Value = UCase(Format(todayDate, "dddd"))
    
    ' Add revenue (find the total revenue column)
    Dim revenueCol As Long
    revenueCol = 0
    
    For i = 1 To 20 ' Check first 20 columns
        If InStr(UCase(ws.Cells(1, i).Value), "TOTAL REVENUE") > 0 Then
            revenueCol = i
            Exit For
        End If
    Next i
    
    If revenueCol > 0 Then
        ws.Cells(newRow, revenueCol).Value = CDbl(todayRevenue)
        ws.Cells(newRow, revenueCol).NumberFormat = "0.00"
    End If
    
    ' Success message
    MsgBox "Today's data added successfully!" & vbCrLf & vbCrLf & _
           "Date: " & Format(todayDate, "mm/dd/yyyy") & vbCrLf & _
           "Revenue: $" & Format(CDbl(todayRevenue), "#,##0.00"), _
           vbInformation, "Data Added"
    
    Exit Sub
    
ErrorHandler:
    MsgBox "An error occurred: " & Err.Description, vbCritical, "Error"
End Sub
