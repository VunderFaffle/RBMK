from flask import Flask, render_template
from flask_socketio import SocketIO
import socket
import threading
import json

app = Flask(__name__)
socketio = SocketIO(app)

# --- TCP сервер ---
def tcp_server():
    HOST = "0.0.0.0"
    PORT = 9000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("TCP сервер запущен")

    while True:
        conn, addr = server.accept()
        print("Подключился:", addr)
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

def handle_client(conn):
    buffer = ""

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                try:
                    line = line.replace("=", ":")
                    line = line.replace("{", '{"').replace(",", ',"').replace(":", '":')
                    json_data = json.loads(line)

                    # 🔹 отправляем обновления на главную
                    state_data = {
                        "HULL_TEMP": json_data.get("HULL_TEMP"),
                        "CORE_TEMP": json_data.get("CORE_TEMP"),
                        "CONTROL_LEVEL": json_data.get("CONTROL_LEVEL")
                    }

                    socketio.emit("update", state_data)

                    # 🔹 если есть движение — отправляем в лог
                    if "MOVEMENT" in json_data:
                        socketio.emit("log", {
                            "MOVEMENT": json_data["MOVEMENT"]
                        })

                except Exception as e:
                    print("Кривой JSON:", line, e)

        except:
            break

    conn.close()

# --- WEB ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/log")
def log():
    return render_template("log.html")

if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000)