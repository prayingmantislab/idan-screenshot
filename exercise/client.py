"""הלקוח - תרגיל. הרצה: python3 client.py [כתובת-שרת]"""
import socket
import sys

from protocol import recv_msg, send_msg

IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 8820


def main():
    # TODO 7a: צור socket (AF_INET, SOCK_STREAM) והתחבר ל-(IP, PORT)
    # TODO 7b: לולאה (while True):
    #   - קרא פקודה מהמשתמש עם input("> ")
    #   - שלח אותה עם send_msg
    #   - קבל תשובה עם recv_msg והדפס אותה
    #   - אם הפקודה היא EXIT: break
    # TODO 7c: סגור את ה-socket
    pass


if __name__ == "__main__":
    main()
