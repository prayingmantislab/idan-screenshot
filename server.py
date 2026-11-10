"""השרת: מקבל פקודות מהלקוח ומבצע אותן על המחשב שלו."""
import glob
import os
import shutil
import socket
import subprocess

from protocol import recv_msg, send_msg, send_file_bytes

IP = "0.0.0.0"
PORT = 8820
SCREENSHOT_PATH = "screen.jpg"  # במטלה: r"C:\screen.jpg"


def do_dir(path):
    if not os.path.isdir(path):
        return f"התיקייה {path} לא קיימת (נתיב יחסי ל-{os.getcwd()})"
    files_list = glob.glob(os.path.join(path, "*.*"))
    return "\n".join(files_list) if files_list else "אין קבצים"


def do_delete(path):
    os.remove(path)
    return f"הקובץ {path} נמחק"


def do_copy(src, dst):
    shutil.copy(src, dst)
    return f"הקובץ הועתק מ-{src} אל {dst}"


def do_execute(program):
    subprocess.call(program)
    return f"התוכנה {program} הורצה"


def do_take_screenshot():
    import pyautogui  # מיובא כאן כדי שהשרת ירוץ גם בלי pyautogui
    image = pyautogui.screenshot()
    image.convert("RGB").save(SCREENSHOT_PATH)  # jpg לא תומך בשקיפות
    return "צילום המסך נשמר"


def handle_command(client_socket, command):
    """מבצע פקודה אחת. מחזיר False אם צריך לסגור את החיבור."""
    # split(" ", 1) / split() מפרק את הפקודה לחלקים
    parts = command.strip().split()
    if not parts:
        send_msg(client_socket, "פקודה ריקה")
        return True
    name = parts[0].upper()
    args = parts[1:]

    try:
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
            with open(SCREENSHOT_PATH, "rb") as f:
                data = f.read()
            send_file_bytes(client_socket, data)
        elif name == "EXIT":
            send_msg(client_socket, "להתראות")
            return False
        else:
            send_msg(client_socket, "פקודה לא מוכרת או מספר פרמטרים שגוי")
    except Exception as e:
        # בשגיאה בביצוע (קובץ לא קיים וכו') נשלח את השגיאה ללקוח
        if name == "SEND_PHOTO":
            # הלקוח מצפה לקובץ ולא לטקסט, לכן אין מה לשלוח; נסגור את החיבור
            print("שגיאה בשליחת תמונה:", e)
            return False
        send_msg(client_socket, f"שגיאה: {e}")
    return True


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print(f"השרת מאזין על פורט {PORT}")

    while True:
        client_socket, address = server_socket.accept()
        print("לקוח התחבר:", address)
        try:
            while True:
                command = recv_msg(client_socket)
                print("התקבלה פקודה:", command)
                if not handle_command(client_socket, command):
                    break
        except Exception as e:
            print("שגיאה בתקשורת:", e)
        finally:
            client_socket.close()
            print("הלקוח התנתק")


if __name__ == "__main__":
    main()
