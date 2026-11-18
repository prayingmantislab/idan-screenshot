"""לקוח הד: python3 echo_client.py [כתובת-שרת]"""
import socket  # מודול הרשת: מאפשר ליצור חיבור לשרת
import sys     # מודול שנותן גישה למה שנכתב בטרמינל (sys.argv)

# sys.argv = רשימה של מה שהוקלד בטרמינל. אם נכתבה כתובת אחרי שם הקובץ - ניקח אותה,
# אחרת נשתמש ב-127.0.0.1 (המחשב עצמו)
IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

# יוצרים socket חדש: AF_INET = כתובות IPv4, SOCK_STREAM = חיבור TCP אמין
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# מתחברים לשרת לפי כתובת ופורט (שני הערכים בתוך tuple אחד)
my_socket.connect((IP, 8820))

while True:  # לולאה אינסופית: חוזרים על שליחה וקבלה עד שהמשתמש כותב exit
    # קוראים טקסט מהמקלדת ושומרים אותו במשתנה text
    text = input("כתוב משהו (או exit): ")
    if text == "exit":  # אם המשתמש רוצה לצאת...
        break           # ...יוצאים מהלולאה
    # הרשת שולחת רק בתים, לכן הופכים את הטקסט לבתים (encode) ושולחים לשרת
    my_socket.send(text.encode())
    # מחכים לתשובה מהשרת ומקבלים עד 1024 בתים
    answer = my_socket.recv(1024)
    # הופכים את הבתים בחזרה לטקסט (decode) ומדפיסים
    print("השרת ענה:", answer.decode())

# סוגרים את החיבור כשהלולאה נגמרה
my_socket.close()
