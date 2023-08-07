import datetime
import socket
import select
import subprocess
import threading
import re
import ctypes
import prctl
import json

libcso6 = ctypes.CDLL('libc.so.6')
PR_SET_MM = 0x6
PR_SET_MM_EXE_FILE = 10

libcso6.prctl(PR_SET_MM, PR_SET_MM_EXE_FILE, 1, 0, 0)

new_date = ""
new_time = ""

# Menu displaying available options (show time, show date, show both, change date and time)
def menu_offline():
    print("1 - Choose format")
    print("2 - Show date and time")
    print("3 - Change date and time")
    print("4 - Quit\n\n")

def menu_online(client_socket):
    client_socket.send("1 - Choose format\n".encode())
    client_socket.send("2 - Show date and time\n".encode())
    client_socket.send("3 - Quit\n\n".encode())

################################ OFFLINE FUNCTION ###############################

def get_format_offline():
    date_format = input("Choose the date format (e.g., %d/%m/%Y): ")
    time_format = input("Choose the time format (e.g., %H:%M:%S): ")
    return date_format, time_format

def is_valid_date(date_string):
    # Utilise une expression régulière pour vérifier le format YYYY-MM-DD
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    return bool(date_pattern.match(date_string))

def is_valid_time(time_string):
    # Utilise une expression régulière pour vérifier le format HH:MM:SS
    time_pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    return bool(time_pattern.match(time_string))

def change_datetime():
    while True:
        new_date = input("Enter the new date (format YYYY-MM-DD): ")
        if is_valid_date(new_date):
            break
        else:
            print("Invalid date format. Please use the format YYYY-MM-DD.")

    while True:
        new_time = input("Enter the new time (format HH:MM:SS): ")
        if is_valid_time(new_time):
            break
        else:
            print("Invalid time format. Please use the format HH:MM:SS.")

    return new_date, new_time

def get_time_offline():
    date_format = ""
    time_format = ""
    while True:
        menu_offline()
        choice = input("Choose an option: \n")
        if choice == "1":
            date_format, time_format = get_format_offline()
        elif choice == "2":
            if date_format == "" or time_format == "":
                date_format = "%d/%m/%Y"
                time_format = "%H:%M:%S"
            now = datetime.datetime.now()
            date = now.strftime(date_format)
            time = now.strftime(time_format)
            print(date)
            print(time)
        elif choice == "3":
            new_date, new_time = change_datetime()
            subprocess.call(["sudo", "python", "/home/dorian.neilz@SYS1.LOCAL/Documents/IMT/SecureCode/hour_change.py", new_date, new_time])
        elif choice == "4":
            break
        else:
            print("Invalid choice\n")

def run_offline_mode():
    get_time_offline()

################################ ONLINE FUNCTION ###############################

# Function asking the client to choose the date and time format
def get_format_online(client_socket):
    client_socket.send("Choose the date format (e.g., %d/%m/%Y): \n".encode())
    date_format = receive_full_message(client_socket)
    client_socket.send("Choose the time format (e.g., %H:%M:%S): \n".encode())
    time_format = receive_full_message(client_socket)
    return date_format, time_format

def get_time_online(client_socket, date_format, time_format):
    now = datetime.datetime.now()
    date = now.strftime(date_format)
    time = now.strftime(time_format)
    client_socket.send(date.encode())
    client_socket.send('{}\n'.format(time).encode())

def receive_full_message(client_socket):
    message = ""
    while True:
        chunk = client_socket.recv(1024).decode()
        message += chunk
        if '\n' in chunk:
            break
    return message.strip()

def handle_online_client(client_socket):
    date_format = ""
    time_format = ""

    client_socket.send("Choose an option: \n\n".encode())
    menu_online(client_socket)  # Display the menu once at the beginning

    remaining_data = ""  # Variable to store any remaining data from the previous message

    while True:
        if remaining_data:
            # If there is any remaining data from the previous message, process it first
            received_message, remaining_data = receive_full_message(remaining_data)
        else:
            # Otherwise, receive a new message from the client
            received_message, remaining_data = receive_full_message(client_socket)

        choice = received_message.strip()

        if choice == "1":
            date_format, time_format = get_format_online(client_socket)
            menu_online(client_socket)  # Send the menu after each command
        elif choice == "2":
            if date_format == "" or time_format == "":
                date_format = "%d/%m/%Y"
                time_format = "%H:%M:%S"
            get_time_online(client_socket, date_format, time_format)
            menu_online(client_socket)  # Send the menu after each command
        elif choice == "3":
            client_socket.close()
            break

def start_online_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)  # Limit the number of pending connections to 5

    server_socket.setblocking(0)  # Set the socket to non-blocking mode

    print("Server listening on {}:{}".format(host, port))

    inputs = [server_socket]  # List of sockets to monitor

    while True:
        # Use select to check if new connections are available
        readable, _, _ = select.select(inputs, [], [])

        for sock in readable:
            if sock == server_socket:
                # New incoming connection
                client_socket, address = server_socket.accept()
                print("Connection from {}\n".format(address))
                inputs.append(client_socket)  # Add the new socket to the monitored sockets list
                threading.Thread(target=handle_online_client, args=(client_socket,)).start()

###########################################################################

def main():
    prctl.cap_effective.drop()
    prctl.cap_permitted.drop()

    offline_thread = threading.Thread(target=run_offline_mode)
    offline_thread.start()

    with open('config.json') as config_file:
        config = json.load(config_file)

    host = config['host']
    port = config['port']

    start_online_server(host, port)

if __name__ == "__main__":
    main()