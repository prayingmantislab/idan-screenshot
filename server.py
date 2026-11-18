"""השרת: מקבל פקודות מהלקוח ומבצע אותן על המחשב שלו."""
import glob        # חיפוש קבצים בתיקייה
import os          # פעולות מערכת ההפעלה (מחיקת קובץ, בדיקת תיקייה)
import shutil      # העתקת קבצים
import socket      # מודול הרשת
import subprocess  # הרצת תוכנות חיצוניות

# מייבאים את הפונקציות שכתבנו בקובץ protocol.py
from protocol import recv_msg, send_msg, send_file_bytes

IP = "0.0.0.0"                  # 0.0.0.0 = לקבל חיבורים מכל מחשב ברשת
PORT = 8820                     # הפורט שהשרת מאזין עליו
SCREENSHOT_PATH = "screen.jpg"  # במטלה: r"C:\screen.jpg"


def do_dir(path):
    # אם התיקייה לא קיימת, מחזירים הודעה במקום רשימה ריקה מבלבלת
    if not os.path.isdir(path):
        return f"התיקייה {path} לא קיימת (נתיב יחסי ל-{os.getcwd()})"
    # glob מחפש קבצים לפי תבנית: "*.*" = כל קובץ שיש לו נקודה בשם
    files_list = glob.glob(os.path.join(path, "*.*"))
    # join מחבר את הרשימה למחרוזת אחת, שורה לכל קובץ
    return "\n".join(files_list) if files_list else "אין קבצים"


def do_delete(path):
    os.remove(path)  # מוחק את הקובץ (שגיאה אם הוא לא קיים)
    return f"הקובץ {path} נמחק"


def do_copy(src, dst):
    shutil.copy(src, dst)  # מעתיק את הקובץ מ-src ל-dst
    return f"הקובץ הועתק מ-{src} אל {dst}"


def do_execute(program):
    subprocess.call(program)  # מריץ את התוכנה ומחכה שתסתיים
    return f"התוכנה {program} הורצה"


def do_take_screenshot():
    # הייבוא כאן ולא בראש הקובץ, כדי שהשרת ירוץ גם בלי pyautogui
    import pyautogui
    image = pyautogui.screenshot()  # מצלם את המסך
    # שומרים כ-jpg; convert("RGB") כי jpg לא תומך בשקיפות
    image.convert("RGB").save(SCREENSHOT_PATH)
    return "צילום המסך נשמר"


def handle_command(client_socket, command):
    """מבצע פקודה אחת. מחזיר False אם צריך לסגור את החיבור."""
    # split() מפרק את הפקודה לרשימה לפי רווחים: "COPY a b" -> ["COPY", "a", "b"]
    parts = command.strip().split()
    if not parts:  # רשימה ריקה = הפקודה הייתה ריקה
        send_msg(client_socket, "פקודה ריקה")
        return True  # ממשיכים לפקודה הבאה
    name = parts[0].upper()  # שם הפקודה, באותיות גדולות
    args = parts[1:]         # שאר החלקים הם הפרמטרים

    try:  # אם הפעולה נכשלת (קובץ לא קיים וכו') נתפוס את השגיאה
        # בודקים איזו פקודה התקבלה ושולחים ללקוח את התוצאה
        if name == "DIR" and len(args) == 1:
            send_msg(client_socket, do_dir(args[0]))
        elif name == "DELETE" and len(args) == 1:
            send_msg(client_socket, do_delete(args[0]))
        elif name == "COPY" and len(args) == 2:
            send_msg(client_socket, do_copy(args[0], args[1]))
        elif name == "EXECUTE" and len(args) >= 1:
            send_msg(client_socket, do_execute(args))
        elif name == "TAKE_SCREENSHOT":
            send_msg(client_socket, do_take_screenshot())
        elif name == "SEND_PHOTO":
            # פותחים לקריאה בינארית ("rb") כי תמונה היא בתים, לא טקסט
            with open(SCREENSHOT_PATH, "rb") as f:
                data = f.read()
            send_file_bytes(client_socket, data)  # שולחים עם שדה גודל
        elif name == "EXIT":
            send_msg(client_socket, "להתראות")
            return False  # מסמן שצריך לסגור את החיבור
        else:
            # שם פקודה לא מוכר, או מספר פרמטרים לא נכון
            send_msg(client_socket, "פקודה לא מוכרת או מספר פרמטרים שגוי")
    except Exception as e:
        if name == "SEND_PHOTO":
            # הלקוח מצפה לקובץ ולא לטקסט, לכן אין מה לשלוח; נסגור את החיבור
            print("שגיאה בשליחת תמונה:", e)
            return False
        # בשגיאה רגילה שולחים את הודעת השגיאה ללקוח והשרת ממשיך לעבוד
        send_msg(client_socket, f"שגיאה: {e}")
    return True  # הכול בסדר, ממשיכים לפקודה הבאה


def main():
    # יוצרים socket: IPv4 (AF_INET) וחיבור TCP אמין (SOCK_STREAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # מאפשר להפעיל מחדש את השרת מיד על אותו פורט
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))  # קושרים את ה-socket לכתובת ולפורט
    server_socket.listen()          # מתחילים להקשיב לחיבורים
    print(f"השרת מאזין על פורט {PORT}")

    while True:  # לולאה חיצונית: מחכה ללקוח אחד אחרי השני
        # accept מחכה עד שלקוח מתחבר, ומחזיר socket חדש רק לשיחה איתו
        client_socket, address = server_socket.accept()
        print("לקוח התחבר:", address)
        try:
            while True:  # לולאה פנימית: פקודה אחרי פקודה מאותו לקוח
                command = recv_msg(client_socket)  # מחכה לפקודה מהלקוח
                print("התקבלה פקודה:", command)
                # אם handle_command החזירה False (EXIT או שגיאה) - יוצאים
                if not handle_command(client_socket, command):
                    break
        except Exception as e:  # למשל: הלקוח התנתק באמצע
            print("שגיאה בתקשורת:", e)
        finally:
            # רץ תמיד: סוגרים את החיבור עם הלקוח וחוזרים לחכות לבא
            client_socket.close()
            print("הלקוח התנתק")


# הקוד הזה רץ רק כשמפעילים את הקובץ ישירות (python3 server.py)
if __name__ == "__main__":
    main()
