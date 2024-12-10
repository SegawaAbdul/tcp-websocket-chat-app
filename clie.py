import socket
import threading


alias = input("Enter your alias: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect(('0.0.0.0', 5555)) 
    print("Connected to the server!")
except Exception as e:
    print(f"Connection error: {e}")
    exit()

def receive():
    try:
        while True:
            message = client.recv(1024).decode('ascii')
            if not message:
                break
            if message == "ALIAS":
                client.send(alias.encode('ascii'))
            else:
                print(message)
    except Exception as e:
        print(f"Error receiving messages: {e}")
        client.close()


def send():
    """Send messages to the server."""
    while True:
        try:
            message = input("")
            client.send(f"{alias}: {message}".encode('ascii'))
        except Exception as e:
            print(f"Error sending messages: {e}")
            client.close()
            break

# Start threads for sending and receiving messages
receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()

send_thread = threading.Thread(target=send, daemon=True)
send_thread.start()

# Prevent the main thread from exiting
receive_thread.join()
send_thread.join()

