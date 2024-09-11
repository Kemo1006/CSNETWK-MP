# PG8 S11
# Ong, Kyle edward M.
# Soan, Brent Jan F.

import socket
import os

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_name = '127.0.0.1'
    server_port = 12345

    print('''D' XCHANGER - The File Exchange System
Welcome User! Before you can send other commands to the server, you must first connect to it. Enter '/join 127.0.0.1 12345' to connect to the server.''')

    # Connecting to the server
    while True:
        request = input('> ').split()

        try:
            if request[0] == '/join' and request[1] == server_name and int(request[2]) == server_port:
                client_socket.connect((server_name, server_port))
                break
            else:
                print('Invalid command. Enter \'/join 127.0.0.1 12345\' to connect to the server.')
        except Exception as e:
            print('Server has not started. Please try again later.')

    print('''Connected to server. 
Enter \'/?\' to learn more about the commands.''')

    connected = True
    server_online = True
    handle = None

    while connected:
        if not server_online:
            print("Error - Server is not online")
            break
        request = input('> ').split()

        try:
            command = request[0]
            if command == '/leave':
                client_socket.send(command.encode())
                print('From server:', client_socket.recv(1024).decode())
                connected = False

            elif command == '/get':
                client_socket.send(" ".join(request).encode('utf-8'))               
                if handle is None or len(request) >= 3 or len(request) == 1:
                    print('From server:', client_socket.recv(1024).decode())
                elif len(request) == 2:
                    toProceed = client_socket.recv(1024).decode()
                    message = None

                    if toProceed == 'True':
                        filename = request[1]                        
                        with open(filename, 'wb') as file:
                            file_bytes = b''
                            while True:
                                data = client_socket.recv(1024)
                                if not data:
                                    break
                                file_bytes += data

                                if b'<END>' in file_bytes:
                                    split = file_bytes.split(b'<END>')
                                    message = split[1].decode('utf-8')
                                    file_bytes = split[0]
                                    break
                            file.write(file_bytes)
                        print('From server:', message)
                    else:
                        print('From server:', data.decode('utf-8'))

            elif command == '/store' and len(request) == 2:
                filename = request[1]
                if not os.path.isfile(filename):
                    print(f"Error: File {filename} not found.")
                    continue

                try:
                    with open(filename, 'rb') as file:
                        client_socket.send(f"/store {os.path.basename(filename)}".encode())
                        ack = client_socket.recv(1024).decode()

                        if ack == "ACK":
                            while True:
                                data = file.read(1024)
                                if not data:
                                    break
                                client_socket.send(data)
                            client_socket.send(b'EOF')
                            response = client_socket.recv(1024).decode()
                            print('From server:', response)
                        else:
                            print(f"{ack}")

                except Exception as e:
                    print(f"Error: {e}")

            elif command == '/register':
                client_socket.send(" ".join(request).encode('utf-8'))
                response = client_socket.recv(1024).decode()

                if response.split()[0] == 'Welcome':
                    handle = request[1]
                print('From server:', response)

            else:
                client_socket.send(" ".join(request).encode('utf-8'))
                response = client_socket.recv(1024).decode()

                if response == "Server is shutting down":
                    server_online = False
                print('From server:', response)

        except socket.error as e:
            if e.errno == 10053:  # Specifically handle WinError 10053
                print('Error - Server has shut down. Connection aborted by the server.')
            else:
                print(f'Error - {e}')
            server_online = False

    client_socket.close()

if __name__ == '__main__':
    main()