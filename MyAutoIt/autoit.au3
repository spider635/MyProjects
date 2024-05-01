#cs ----------------------------------------------------------------------------

 AutoIt Version: 3.3.16.1
 Author:         myName

 Script Function:
	Template AutoIt script.

#ce ----------------------------------------------------------------------------

; 包含文件为 $MB_OK 
#include <MsgBoxConstants.au3>
#include <Array.au3>
#include <AutoItConstants.au3>
#include <StringConstants.au3>
#include <SQLite.au3>
#include <SQLite.dll.au3>

; 为程序名称定义一个变量
Local $sProgramName = "C:\Users\Yanbang\AppData\Roaming\uBuyFirst\bin\uBuyFirst.exe"


#cs
; 打开程序界面
Run($sProgramName)

; 等待程序主窗口出现
WinWaitActive("uBuyFirst", "Make Offer")

; 等待10秒窗口内容加载
Sleep(10000)
#ce

Sleep(1000)
; 激活主窗口
WinActivate("uBuyFirst", "Make Offer")

; 调整窗口的位置和大小
; WinMove("uBuyFirst", "Make Offer", 0, 0, 1024, 768)

; 最大化主窗口
WinSetState("uBuyFirst", "Make Offer", @SW_MAXIMIZE)
Sleep(3000)

;Sleep(5000)

; 获取最大化时窗口的位置信息
;Local $aPosition = WinGetPos("uBuyFirst", "Make Offer")

;_ArrayDisplay($aPosition)

; 输出窗口位置信息
; MsgBox($MB_OK, "窗口位置信息", $aPosition[0])


; Click Start 
; MouseClick($MOUSE_CLICK_LEFT, 195, 668)

; Sleep(20000)

; Click Stop
; MouseClick($MOUSE_CLICK_LEFT, 195, 668)
; Sleep(5000)


MouseClick($MOUSE_CLICK_LEFT, 339, 343)
Sleep(2000)

; Send Ctrl a
Send("^a")
Sleep(2000)

; Send Ctrl c
Send("^c")
Sleep(2000)


Local $sResult = ClipGet()

$sResult = StringReplace($sResult, @TAB, "TABTAB")

Local $aArray = StringSplit($sResult, @CRLF, BitOr($STR_NOCOUNT, $STR_ENTIRESPLIT))

_ArrayDisplay($aArray)

;MsgBox($MB_OK, "Result", $sResult)

;StringRegExp

Local $sRow = ""
Local $aArrayDetail = []
Local $sTerm, $sThumbnail, $sTitle, $sTotalPrice, $sCondition, $sReturns, $sBestOffer, $sCommitToBuy, $sQuantity, $sPostedTime, $sFoundTime, $sStatus

_SQLite_Startup()
If @error Then
    MsgBox(16, "SQLite Error", "SQLite.dll Can't be Loaded!")
    Exit -1
EndIf
ConsoleWrite("_SQLite_LibVersion=" & _SQLite_LibVersion() & @CRLF)

_SQLite_Open() ; Open a :memory: database
If @error Then
    MsgBox(16, "SQLite Error", "Can't Load Database!")
    Exit -1
EndIf






Local $sInsertLine = ""

For $sRow In $aArray
	If StringInStr($sRow, "TermTABTABThumbnail") Then
		Sleep(100)
	ElseIf StringLen($sRow) = 0 Then
		Sleep(100)
	Else
		$aArrayDetail = StringSplit($sRow, "TABTAB", BitOr($STR_NOCOUNT, $STR_ENTIRESPLIT))
		_ArrayDisplay($aArrayDetail)
		
		 $sTerm = $aArrayDetail[0]
		 $sThumbnail = $aArrayDetail[1]
		 $sTitle = $aArrayDetail[2]
		 $sTotalPrice = $aArrayDetail[3]
		 $sCondition = $aArrayDetail[4]
		 $sReturns = $aArrayDetail[5]
		 $sBestOffer = $aArrayDetail[6]
		 $sCommitToBuy = $aArrayDetail[7]
		 $sQuantity = $aArrayDetail[8]
		 $sPostedTime = $aArrayDetail[9]
		 $sFoundTime = $aArrayDetail[10]
		 $sStatus = $aArrayDetail[11]
		
		
		If Not _SQLite_Exec(-1, "CREATE TEMP TABLE results (sTerm, sThumbnail, sTitle, sTotalPrice, sCondition, sReturns, sBestOffer, sCommitToBuy, sQuantity, sPostedTime, sFoundTime, sStatus);") = $SQLITE_OK Then _
			MsgBox(16, "SQLite Error", _SQLite_ErrMsg())
		
		$sInsertLine = "INSERT INTO persons VALUES ("  & $sTerm & "," & $sThumbnail & "," & $sTitle & "," & $sTotalPrice & "," & $sCondition & "," & $sReturns & "," & $sBestOffer & "," & $sCommitToBuy & "," & $sQuantity & "," & $sPostedTime & "," & $sFoundTime & "," & $sStatus & ");"             
		
		
		;If Not _SQLite_Exec(-1, "INSERT INTO persons VALUES (1,'Alice','43');") = $SQLITE_OK Then _
		If Not _SQLite_Exec(-1, $sInsertLine) = $SQLITE_OK Then _
			MsgBox(16, "SQLite Error", _SQLite_ErrMsg())
		
	EndIf
Next

; Query

; $iRval = _SQLite_GetTable2d(-1, "SELECT * FROM results;", $sTerm, $sThumbnail, $sTitle, $sTotalPrice, $sCondition, $sReturns, $sBestOffer, $sCommitToBuy, $sQuantity, $sPostedTime, $sFoundTime, $sStatus)

$iRval = _SQLite_GetTable2d(-1, "SELECT * FROM persons;", $aResult, $iRows, $iColumns)

If $iRval = $SQLITE_OK Then
    _SQLite_Display2DResult($aResult)

Else
    MsgBox(16, "SQLite Error: " & $iRval, _SQLite_ErrMsg())
EndIf

_SQLite_Close()
_SQLite_Shutdown()






	


























; 提示程序结束
MsgBox($MB_OK, "Warm Reminder", "Your program ended.")
; Warm Reminder
WinWait("Warm Reminder")
Sleep(2000)
WinActivate("Warm Reminder")



#cs
; Script Start - Add your code below here
#include <MsgBoxConstants.au3>
MsgBox($MB_ICONINFORMATION , "Tutorial", "Hello World!")
Run("Notepad.exe")
WinWaitActive("Untitled - Notepad")
Send("This is some text.")
WinClose("*Untitled - Notepad")
WinWaitActive("Notepad", "Save")
Send("!n")

Run("C:\Users\Yanbang\AppData\Roaming\uBuyFirst\bin\uBuyFirst.exe")
WinWaitActive("uBuyFirst")
WinSetState("uBuyFirst", "Make Offer", @SW_MAXIMIZE)
Sleep(5000)
ControlTreeView("uBuyFirst", "Make Offer", 395048, "Check")
Sleep(1000)
ControlTreeView("uBuyFirst", "Make Offer", 395048, "Uncheck")
; WinClose("uBuyFirst")
; click ENTER -> Send("{ENTER}") 
; plays back a beep noise, at the frequency 500 for 1 second

;Local $sText
;WinWaitActive("*Untitled - Notepad")
;Local $sText = WinGetText("*Untitled - Notepad")
;$sText = "123"
;MsgBox($MB_SYSTEMMODAL, "", $sText)

#include <MsgBoxConstants.au3>

Example()

Func Example()
        ; Retrieve the window text of the active window.
        ;Local $sText = ControlGetText("uBuyFirst", "", 1443412)
		Local $sText = ClipGet()

        ; Display the window text.
        MsgBox($MB_SYSTEMMODAL, "", $sText)
EndFunc   ;==>Example

#ce



