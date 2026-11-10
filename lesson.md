# מערך שיעור – שרת פקודות מרוחק (תרגיל 2.7)

## 1. הרעיון הכללי
שני תהליכים רצים במקביל:
- **server** – מחכה לחיבור, מקבל פקודות טקסט ומבצע אותן על המחשב שלו.
- **client** – מתחבר לשרת, קורא פקודה מהמשתמש, שולח, ומציג את התשובה.

הם מדברים דרך **socket** (TCP). העבודה היא ברשתות, אבל הקוד נכתב בפייתון.

```
client ──"DIR C:\Cyber"──▶ server  (מבצע glob)
client ◀──רשימת קבצים────── server
```

הרצה: טרמינל 1: `python server.py` | טרמינל 2: `python client.py`

## 2. מבנה הפרויקט
| קובץ | תפקיד |
|---|---|
| `protocol.py` | פונקציות משותפות: שליחה/קבלה עם שדה אורך |
| `server.py` | ביצוע הפקודות |
| `client.py` | ממשק משתמש + שליחה |

## 3. סוקטים (תקשורת שרת-לקוח)
```python
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 + TCP
```
| צד שרת | צד לקוח |
|---|---|
| `bind((ip, port))` – קובע כתובת ופורט | `connect((ip, port))` – מתחבר |
| `listen()` – מתחיל להקשיב | |
| `accept()` – מחכה ללקוח, מחזיר `(socket_של_הלקוח, כתובת)` | |

משותף: `send()` / `sendall()` (שולח הכול), `recv(n)` (מקבל **עד** n בתים), `close()`.

⚠️ **הכי חשוב בתקשורת:** TCP הוא זרם בתים ללא גבולות הודעה. `recv(100)` יכול להחזיר 30 בתים. לכן:
1. לפני כל הודעה שולחים **את אורכה**.
2. מקבלים בלולאה עד שהגיע כל האורך:
```python
received_data = b""
while len(received_data) < size:
    received_data += sock.recv(size - len(received_data))
```

## 4. מחרוזות וקידוד
- רשת שולחת **bytes**, לא str: `"abc".encode()` → `b"abc"`, ו-`b"abc".decode()` → `"abc"`.
- `str(7).zfill(4)` → `"0007"` (ריפוד באפסים לשדה אורך קבוע).
- `"0007".isdigit()` → בדיקה שזה מספר; `int("0007")` → 7.
- `text[4:]` – slicing: הכול מהתו הרביעי והלאה.
- `text.startswith("DIR")`, `text.strip()` (מוריד רווחים בקצוות), `text.split()` (מפרק לרשימה), `" ".join(list)` (הפוך).
- f-string: `f"הקובץ {path} נמחק"`.
- raw string: `r"C:\Cyber\1.txt"` – ה-`\` לא נחשב תו בריחה (בלי r, `"\1"` או `"\f"` הם תווים מיוחדים!).

## 4א. הפרוטוקול שלנו
**הודעת טקסט:** `[אורך ב-4 ספרות][תוכן]` → `"DIR C:\\x"` נשלח כ-`0009DIR C:\x`.

**קובץ גדול (תמונה):** שדה של 4 ספרות מגביל ל-9999 בתים, אז עושים שתי שכבות:
`[מספר הספרות בגודל – 4 בתים][הגודל][הקובץ]`
לדוגמה גודל 2,000,000 → `0007` + `2000000` + הבתים.
הלקוח קורא 4 בתים (=7), אחר כך 7 בתים (=2000000), ואז לולאה שקוראת 2,000,000 בתים.

## 5. מבני נתונים והמרות
- רשימה `[]`: `parts = command.split()` → `["COPY", "a.txt", "b.txt"]`; `parts[0]` הפקודה, `parts[1:]` הפרמטרים.
- כפולה (tuple) `()`: `("127.0.0.1", 8820)` – כך מועברת כתובת ל-`bind`/`connect`; ו-`accept()` מחזיר tuple.
- `str()`, `int()`, `len()` – המרות ואורך.

## 6. ניהול קבצים
```python
with open("file.txt", "r") as f:    # טקסט
    f.read()
with open("file.jpg", "rb") as f:   # בינארי - קריאה
    data = f.read()
with open("file.jpg", "wb") as f:   # בינארי - כתיבה
    f.write(data)
for line in f:                      # שורה-שורה
    print(line)
```
`with` סוגר את הקובץ אוטומטית. תמונה **חייבת** מצב בינארי (`b`), אחרת היא תתקלקל.

## 7. לולאות
- `while True:` + `break` – השרת מחכה ללקוחות לנצח; הלולאה הפנימית עד `EXIT`.
- **while בתוך while:** חיצונית – לקוחות (`accept`), פנימית – פקודות של אותו לקוח.
- `while len(received_data) < size:` – קבלה מלאה.
- `for item in list:` מעבר על איברים.

## 8. תנאים וטיפול בשגיאות
```python
if name == "DIR": ...
elif name == "DELETE": ...
else: ...                       # פקודה לא מוכרת

try:
    os.remove(path)
except Exception as e:          # קובץ לא קיים, אין הרשאה...
    send_msg(sock, f"שגיאה: {e}")   # השרת לא קורס
```

## 9. המודולים וכל פקודה
| פקודה | מודול | קוד |
|---|---|---|
| `DIR path` | `glob` | `glob.glob(r"C:\Cyber\*.*")` – רשימת קבצים |
| `DELETE file` | `os` | `os.remove(path)` |
| `COPY a b` | `shutil` | `shutil.copy(a, b)` |
| `EXECUTE prog` | `subprocess` | `subprocess.call(["notepad.exe"])` |
| `TAKE_SCREENSHOT` | `pyautogui` | `pyautogui.screenshot().save("screen.jpg")` |
| `SEND_PHOTO` | `open(..,"rb")` + socket | שליחת הקובץ עם שדה גודל |
| `EXIT` | – | השרת עונה וסוגר את החיבור |

התקנה: `pip install pyautogui`. (`random`, `datetime` – מופיעים ברשימה; שימושיים להוספת חותמת זמן לשם הקובץ, למשל `datetime.datetime.now().strftime("%H%M%S")`.)

## 10. מה קורה בהרצה (SEND_PHOTO)
1. לקוח: `send_msg("TAKE_SCREENSHOT")` → שרת מצלם ושומר `screen.jpg`, עונה "נשמר".
2. לקוח: `send_msg("SEND_PHOTO")`.
3. שרת: קורא את הקובץ ב-`rb`, שולח `[ספרות הגודל][גודל][בתים]`.
4. לקוח: קורא ללולאה עד שהתקבל הכול, ושומר ב-`wb` כ-`screenshot.jpg`.

## 11. שאלות לתרגול
1. למה `recv(1000)` לא מבטיח לקבל 1000 בתים?
2. מה ההבדל בין `r"C:\new"` ל-`"C:\new"`?
3. למה צריך `"rb"`/`"wb"` ולא `"r"`/`"w"` לתמונה?
4. מה יקרה אם נשלח הודעה גדולה מ-9999 בתים בשדה אורך של 4 ספרות?
5. למה `accept()` מחזיר socket חדש ולא משתמש ב-socket של ההאזנה?
