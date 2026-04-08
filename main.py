from flask import Flask, render_template
from flask_socketio import SocketIO
import socket
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# --- TCP сервер ---
def tcp_server():
    HOST = "0.0.0.0"
    PORT = 9000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"TCP сервер запущен на {PORT}")

    while True:
        conn, addr = server.accept()
        print(f"Подключение: {addr}")

        threading.Thread(target=handle_client, args=(conn,)).start()

def handle_client(conn):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode().strip()
            print("Получено:", message)

            # отправляем в браузер
            socketio.emit("update", {"value": message})

        except:
            break

    conn.close()

# --- Web ---
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000)