"""שרת הד: מחזיר ללקוח בדיוק את מה שהוא שלח."""
import socket  # מודול הרשת: מאפשר ליצור שרת שמקבל חיבורים

# יוצרים socket חדש: AF_INET = כתובות IPv4, SOCK_STREAM = חיבור TCP אמין
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# מאפשר להפעיל את השרת מחדש מיד על אותו פורט, בלי לחכות שהמערכת תשחרר אותו
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# קושרים את ה-socket לכתובת ופורט. 0.0.0.0 = לקבל חיבורים מכל מחשב ברשת
server_socket.bind(("0.0.0.0", 8820))
# מתחילים להקשיב: מעכשיו אפשר להתחבר לשרת
server_socket.listen()
print("מחכה ללקוח...")

# מחכים עד שלקוח מתחבר. מקבלים socket חדש רק לשיחה איתו, והכתובת שלו
client_socket, address = server_socket.accept()
print("התחבר:", address)

while True:  # לולאה אינסופית: מקבלים ומחזירים עד שהלקוח מתנתק
    # מחכים למידע מהלקוח ומקבלים עד 1024 בתים
    data = client_socket.recv(1024)
    if not data:  # אם לא התקבל כלום, הלקוח סגר את החיבור
        break     # יוצאים מהלולאה
    # הופכים את הבתים לטקסט (decode) ומדפיסים כדי לראות מה התקבל
    print("קיבלתי:", data.decode())
    # שולחים ללקוח בדיוק את מה שקיבלנו (ההד). המידע כבר בבתים, אז אין צורך ב-encode
    client_socket.send(data)

# סוגרים את החיבור עם הלקוח
client_socket.close()
# סוגרים את socket ההאזנה של השרת
server_socket.close()
