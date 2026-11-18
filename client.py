"""הלקוח: קורא פקודות מהמקלדת, שולח לשרת ומציג את התשובה."""
import socket  # מודול הרשת: מאפשר להתחבר לשרת
import sys     # מאפשר לקרוא את מה שנכתב בטרמינל (sys.argv)

# מייבאים את הפונקציות שכתבנו בקובץ protocol.py
from protocol import recv_msg, send_msg, recv_file_bytes

# שימוש: python3 client.py [כתובת-שרת]   (ברירת מחדל: אותו מחשב)
# אם נכתבה כתובת אחרי שם הקובץ - ניקח אותה, אחרת 127.0.0.1 (המחשב עצמו)
IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 8820                       # הפורט של השרת (חייב להיות זהה לפורט בשרת)
OUTPUT_FILE = "screenshot.jpg"    # השם של הקובץ שבו נשמור את התמונה שנקבל

# טקסט העזרה שמוצג בהתחלה (מחרוזת של כמה שורות)
HELP = """פקודות:
  DIR <תיקייה>
  DELETE <קובץ>
  COPY <מקור> <יעד>
  EXECUTE <תוכנה>
  TAKE_SCREENSHOT
  SEND_PHOTO   (שומר את התמונה ל-screenshot.jpg)
  EXIT"""


def main():
    # יוצרים socket: IPv4 (AF_INET) וחיבור TCP אמין (SOCK_STREAM)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # מתחברים לשרת (כתובת ופורט בתוך tuple)
    my_socket.connect((IP, PORT))
    print(HELP)  # מציגים למשתמש את הפקודות האפשריות

    try:  # כל שגיאה בתקשורת תיתפס ב-except למטה
        while True:  # חוזרים על קריאת פקודה ושליחתה עד EXIT
            # קוראים פקודה מהמקלדת; strip מוריד רווחים בהתחלה ובסוף
            command = input("> ").strip()
            if not command:  # אם המשתמש לחץ Enter בלי לכתוב כלום...
                continue     # ...חוזרים לתחילת הלולאה
            # שולחים את הפקודה לשרת (עם שדה אורך, כמו ב-protocol.py)
            send_msg(my_socket, command)

            if command.upper() == "SEND_PHOTO":  # upper מאפשר גם אותיות קטנות
                # התשובה לפקודה הזו היא קובץ ולא טקסט, לכן קוראים אותו אחרת
                data = recv_file_bytes(my_socket)
                # פותחים קובץ לכתיבה בינארית ("wb") כי תמונה היא בתים
                with open(OUTPUT_FILE, "wb") as f:
                    f.write(data)  # כותבים את הבתים שהתקבלו לקובץ
                print(f"התמונה נשמרה ב-{OUTPUT_FILE} ({len(data)} בתים)")
            else:
                # לכל שאר הפקודות התשובה היא טקסט: מקבלים ומדפיסים
                print(recv_msg(my_socket))

            if command.upper() == "EXIT":  # אחרי שהשרת ענה, יוצאים מהלולאה
                break
    except Exception as e:  # למשל: השרת נסגר או החיבור נפל
        print("שגיאה:", e)
    finally:
        # finally רץ תמיד, גם אחרי שגיאה: סוגרים את החיבור
        my_socket.close()


# הקוד הזה רץ רק כשמפעילים את הקובץ ישירות (python3 client.py),
# ולא כשמייבאים אותו מקובץ אחר
if __name__ == "__main__":
    main()
