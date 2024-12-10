import socket
import threading


HOST = '0.0.0.0'
PORT = 5555

# Create and configure the server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

clients = []
aliases = []
lock = threading.Lock()

def broadcast(message, sender=None):
    """Send a message to all connected clients, except the sender."""
    with lock:
        for client in clients:
            if client != sender: 
                try:
                    client.send(message)
                except Exception:
                    client.close()
                    if client in clients:
                        clients.remove(client)

def handle(user):
    ####Handle communication with a single client.
    index = clients.index(user)
    alias = aliases[index]
    try:
        while True:
            message = user.recv(1024)
            if message:
                print(f"[{alias}] {message.decode('ascii')}")
                broadcast(f"[{alias}]: {message.decode('ascii')}".encode('ascii'), sender=user)
            else:
                break
    except Exception as e:
        print(f"Error handling client {alias}: {e}")
    finally:
        with lock:
            if user in clients:
                clients.remove(user)
                aliases.pop(index)
                print(f"{alias} has disconnected.")
                broadcast(f"{alias} has left the chat.".encode('ascii'))
                user.close()

def accept_connections():
    ####Accept incoming client connections.
    print(f"Server running on {HOST}:{PORT}")
    while True:
        client, address = server.accept()
        print(f"New connection from {address}")

        client.send("ALIAS".encode('ascii'))
        alias = client.recv(1024).decode('ascii')

        with lock:
            aliases.append(alias)
            clients.append(client)

        print(f"Alias: {alias}")
        broadcast(f"{alias} has joined the chat! Welcome!".encode('ascii'))
        client.send("Welcome to the chat!".encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def server_messages():
    ### Allow the server admin to send messages.
    while True:
        try:
            message = input("Server: ")
            broadcast(f"Server: {message}".encode('ascii'))
        except Exception as e:
            print(f"Error sending server message: {e}")

# Start server threads
server_thread = threading.Thread(target=accept_connections)
server_thread.start()

admin_thread = threading.Thread(target=server_messages)
admin_thread.start()

server_thread.join()
admin_thread.join()

