# PG8 S11
# Ong, Kyle edward M.
# Soan, Brent Jan F.

import socket
import threading
import os
from datetime import datetime

# Server Configuration
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024
DIRECTORY = 'server_files'

clients = {}
shutdown_event = threading.Event()
server_socket = None
active_connections = 0

def handle_client(client_socket, client_address):
    global active_connections
    print(f"[+] New connection from {client_address}")
    connected = True
    handle = None
    active_connections += 1
    print(f"[+] Active connections: {active_connections}")

    while connected:
        try:
            if shutdown_event.is_set():
                client_socket.send(
                    "Error - Server is not online".encode('utf-8'))
                continue
            
            message = client_socket.recv(BUFFER_SIZE).decode('utf-8')
            if not message:
                break

            command, *params = message.split()
            response = ''

            if command == '/leave':
                response = "Connection closed. Thank you!"
                connected = False

            elif command == '/register':
                if len(params) != 1:
                    response = "Error - Registration failed. Use the format '/register <handle>'"
                else:
                    handle = params[0]
                    if handle in clients:
                        response = "Error - Registration failed. Handle or alias already exists."
                    elif client_socket in clients.values():
                        response = "Error - You are already registered."
                    else:
                        clients[handle] = client_socket
                        response = f"Welcome {handle}!"

            elif command == '/store':
                if handle is None:
                    response = "Error: Please register first using /register <handle>"
                else:
                    if len(params) != 1:
                        response = "Error: Store failed. Use the format /store <filename>"
                    else:
                        filename = params[0]
                        file_path = os.path.join(DIRECTORY, filename)
                        client_socket.send(b"ACK")

                        with open(file_path, 'wb') as f:
                            while True:
                                data = client_socket.recv(BUFFER_SIZE)
                                if data == b'EOF':
                                    break
                                f.write(data)

                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        response = f"{handle} <{timestamp}>: Uploaded {filename}"
                        client_socket.send(response.encode('utf-8'))

            elif command == '/dir':
                if handle is None:
                    response = "Error - Please register first using /register <handle>"
                else:
                    files = os.listdir(DIRECTORY)
                    response = "\n".join(files)

            elif command == '/get':
                if handle is None:
                    response = "Error - Please register first using /register <handle>"
                else:
                    if len(params) != 1:
                        response = "Error - Get failed. Use the format /get <filename>"
                    else:
                        filename = params[0]
                        file_path = os.path.join(DIRECTORY, filename)

                        if os.path.exists(file_path):
                            client_socket.send('True'.encode('utf-8'))

                            file = open(file_path, 'rb')
                            data = file.read()

                            client_socket.sendall(data)
                            client_socket.send(b'<END>')

                            response = f"File received from Server - {filename}"
                        else:
                            client_socket.send('False'.encode('utf-8'))
                            response = "Error - File not found in the server."

            elif command == '/?':
                response = ("/join <server_ip_add> <port>\n"
                            "/leave\n"
                            "/register <handle>\n"
                            "/store <filename>\n"
                            "/dir\n"
                            "/get <filename>\n"
                            "/?")

            elif command == '/join':
                response = "Error - You are already connected."

            else:
                response = "Error - Command not found.\nEnter \'/?\' to learn more about the commands."

            client_socket.send(response.encode('utf-8'))

        except Exception as e:
            print(f"[-] Error - {e}")
            break

    client_socket.close()

    if handle and handle in clients:
        del clients[handle]
    active_connections -= 1
    print(f"[-] Connection from {client_address} closed")
    print(f"[+] Active connections: {active_connections}")

def notify_clients():
    for client_socket in clients.values():
        try:
            client_socket.send("Error - Server is shutting down".encode('utf-8'))
        except Exception as e:
            print(f"[-] Error notifying client: {e}")

def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"[+] Server started on {SERVER_IP}:{SERVER_PORT}")

    def server_command_handler():
        while not shutdown_event.is_set():
            command = input()
            if command == '/shutdown':
                shutdown_event.set()
                notify_clients()
                server_socket.close()
                print("[+] Server shutting down...")
                break

    threading.Thread(target=server_command_handler).start()

    while not shutdown_event.is_set():
        try:
            client_socket, client_address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.start()
        except OSError:
            break

if __name__ == '__main__':
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
    start_server()