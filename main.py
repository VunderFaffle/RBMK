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

    print("TCP сервер запущен на порту", PORT)

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
                line = line.strip()

                if not line:
                    continue

                try:
                    line = line.replace("=", ":")
                    line = line.replace("{", '{"').replace(",", ',"').replace(":", '":')
                    json_data = json.loads(line)

                    # --- формируем данные для главной ---
                    state_data = {}

                    fields = [
                        "HULL_TEMP",
                        "CORE_TEMP",
                        "CONTROL_LEVEL",
                        "REACTOR_UPTIME",
                        "WATER_LEVEL",
                        "XENON",
                        "EMERGENCY"
                    ]

                    for field in fields:
                        if field in json_data:
                            state_data[field] = json_data[field]

                    # отправляем на главную
                    if state_data:
                        socketio.emit("update", state_data)

                    # --- лог (только MOVEMENT) ---
                    if "MOVEMENT" in json_data:
                        socketio.emit("log", {
                            "MOVEMENT": json_data["MOVEMENT"]
                        })

                except Exception as e:
                    print("Кривой JSON:", line)
                    print("Ошибка:", e)

        except Exception as e:
            print("Ошибка соединения:", e)
            break

    conn.close()
    print("Клиент отключился")


# --- WEB ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/log")
def log():
    return render_template("log.html")


# --- запуск ---
if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000)
    
#line = line.replace("=", ":")
#line = line.replace("{", '{"').replace(",", ',"').replace(":", '":')