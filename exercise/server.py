"""השרת - תרגיל. קודם משלימים את protocol.py ועוברים את הבדיקות."""
import glob
import os
import socket

from protocol import recv_msg, send_msg

IP = "0.0.0.0"
PORT = 8820


def do_dir(path):
    """מחזיר מחרוזת עם רשימת הקבצים בתיקייה."""
    # TODO 5: אם התיקייה לא קיימת (os.path.isdir) החזר הודעת שגיאה
    # TODO 5: אחרת: glob.glob(os.path.join(path, "*.*")) והחזר את הרשימה כמחרוזת
    #         (רמז: "\n".join(...))
    pass


def handle_command(client_socket, command):
    """מבצע פקודה אחת. מחזיר False אם צריך לסגור את החיבור."""
    parts = command.strip().split()      # "DIR ." -> ["DIR", "."]
    name = parts[0].upper()              # שם הפקודה
    args = parts[1:]                     # הפרמטרים

    # TODO 4: אם name == "DIR" ויש פרמטר אחד: שלח send_msg עם do_dir(args[0])
    # TODO 4: אם name == "EXIT": שלח "להתראות" והחזר False
    # TODO 4: אחרת: שלח "פקודה לא מוכרת"
    return True


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print(f"השרת מאזין על פורט {PORT}")

    # TODO 6: לולאה חיצונית (while True): accept ללקוח חדש
    #   בתוכה לולאה פנימית: recv_msg, הדפסה, handle_command
    #   אם handle_command החזירה False - break
    #   לא לשכוח לסגור את client_socket בסוף (finally)
    pass


if __name__ == "__main__":
    main()
