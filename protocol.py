"""פונקציות משותפות לשרת וללקוח: פרוטוקול ההודעות.

כל הודעת טקסט נשלחת כך:  [אורך ב-4 ספרות][התוכן]
למשל: "DIR C:\\Cyber"  ->  b"0012DIR C:\\Cyber"
"""

LENGTH_FIELD = 4  # אורך שדה האורך בבתים (מקסימום 9999)


def recv_exact(sock, size):
    """מקבל בדיוק size בתים. recv יכול להחזיר פחות ממה שביקשנו, ולכן לולאה."""
    received_data = b""
    while len(received_data) < size:
        chunk = sock.recv(size - len(received_data))
        if not chunk:  # הצד השני סגר את החיבור
            raise ConnectionError("החיבור נסגר")
        received_data += chunk
    return received_data


def send_msg(sock, text):
    """שולח הודעת טקסט עם שדה אורך."""
    data = text.encode()
    if len(data) > 9999:
        data = data[:9999]  # השדה מכיל רק 4 ספרות
    sock.sendall(str(len(data)).zfill(LENGTH_FIELD).encode() + data)


def recv_msg(sock):
    """מקבל הודעת טקסט עם שדה אורך."""
    length = recv_exact(sock, LENGTH_FIELD).decode()
    if not length.isdigit():
        raise ValueError("שדה אורך לא תקין")
    return recv_exact(sock, int(length)).decode()


def send_file_bytes(sock, data):
    """שולח קובץ בינארי (תמונה) שגדלו יכול להגיע למיליונים.

    שדה האורך הרגיל (4 בתים) אומר כמה *ספרות* יש בגודל,
    ואז נשלח הגודל עצמו, ואז הקובץ.
    דוגמה: גודל 2000000 -> "0007" + "2000000" + <הבתים>
    """
    size_str = str(len(data))
    sock.sendall(str(len(size_str)).zfill(LENGTH_FIELD).encode() + size_str.encode())
    sock.sendall(data)


def recv_file_bytes(sock):
    digits = int(recv_exact(sock, LENGTH_FIELD).decode())
    size = int(recv_exact(sock, digits).decode())
    return recv_exact(sock, size)
