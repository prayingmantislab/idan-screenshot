"""בדיקות ל-protocol.py. הרצה: python3 test_protocol.py

משתמש ב-socketpair: שני socket מחוברים זה לזה בתוך המחשב, בלי שרת ובלי פורט.
"""
import socket

import protocol


def run(name, test):
    """מריץ בדיקה אחת. כל תקלה (שגיאה, timeout, תוצאה שגויה) נחשבת כשלון."""
    a, b = socket.socketpair()
    a.settimeout(2)  # בלי timeout, פונקציה לא מוכנה תגרום לתוכנית להיתקע
    b.settimeout(2)
    try:
        ok = test(a, b)
        reason = ""
    except socket.timeout:
        ok, reason = False, "  (נתקע - אולי הפונקציה עדיין לא ממומשת?)"
    except Exception as e:
        ok, reason = False, f"  ({type(e).__name__}: {e})"
    finally:
        a.close()
        b.close()
    print(("עבר  " if ok else "נכשל ") + name + reason)
    return ok


def test_send_format(a, b):
    protocol.send_msg(a, "DIR .")
    return b.recv(100) == b"0005DIR ."


def test_recv(a, b):
    a.sendall(b"0004EXIT")
    return protocol.recv_msg(b) == "EXIT"


def test_two_messages(a, b):
    protocol.send_msg(a, "hello")
    protocol.send_msg(a, "world")
    return (protocol.recv_msg(b), protocol.recv_msg(b)) == ("hello", "world")


def test_hebrew(a, b):
    protocol.send_msg(a, "שלום")
    return b.recv(100).startswith(b"0008")  # 4 תווים = 8 בתים


def test_recv_exact(a, b):
    a.sendall(b"abc")
    a.sendall(b"def")
    return protocol.recv_exact(b, 6) == b"abcdef"


def main():
    tests = [
        ('send_msg("DIR .") שולח b"0005DIR ."', test_send_format),
        ('recv_msg מחזיר "EXIT"', test_recv),
        ("שתי הודעות ברצף מתקבלות בנפרד", test_two_messages),
        ('"שלום" נשלח עם אורך 0008 (8 בתים)', test_hebrew),
        ("recv_exact(6) מחזיר את כל 6 הבתים", test_recv_exact),
    ]
    results = [run(name, test) for name, test in tests]
    print(f"\n{sum(results)} מתוך {len(results)} בדיקות עברו")


if __name__ == "__main__":
    main()
