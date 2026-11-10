"""הלקוח: קורא פקודות מהמקלדת, שולח לשרת ומציג את התשובה."""
import socket

from protocol import recv_msg, send_msg, recv_file_bytes

IP = "127.0.0.1"
PORT = 8820
OUTPUT_FILE = "screenshot.jpg"

HELP = """פקודות:
  DIR <תיקייה>
  DELETE <קובץ>
  COPY <מקור> <יעד>
  EXECUTE <תוכנה>
  TAKE_SCREENSHOT
  SEND_PHOTO   (שומר את התמונה ל-screenshot.jpg)
  EXIT"""


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))
    print(HELP)

    try:
        while True:
            command = input("> ").strip()
            if not command:
                continue
            send_msg(my_socket, command)

            if command.upper() == "SEND_PHOTO":
                data = recv_file_bytes(my_socket)
                with open(OUTPUT_FILE, "wb") as f:
                    f.write(data)
                print(f"התמונה נשמרה ב-{OUTPUT_FILE} ({len(data)} בתים)")
            else:
                print(recv_msg(my_socket))

            if command.upper() == "EXIT":
                break
    except Exception as e:
        print("שגיאה:", e)
    finally:
        my_socket.close()


if __name__ == "__main__":
    main()
