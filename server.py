import datetime
import socket
import select
import threading
import subprocess
import shlex

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

def change_date_time():
    new_date = input("Enter the new date (format YYYY-MM-DD): ")
    new_time = input("Enter the new time (format HH:MM:SS): ")
    date_format = input("Enter the desired date format: ")
    time_format = input("Enter the desired time format: ")
    try:
        # Checking user inputs to avoid command injections
        if not all(isinstance(param, str) for param in [new_date, new_time, date_format, time_format]):
            raise ValueError("Date, time, format, and time format parameters must be strings.")

        # Escaping special characters in command arguments
        date = shlex.quote(new_date)
        time = shlex.quote(new_time)

        # Building commands to change the date and time using the specified format
        date_command = f"date -s '{date} {time}' +'{date_format}'"
        time_command = f"date -s '{time}' +'{time_format}'"

        subprocess.call(['sudo', 'python', '/home/dorian.neilz@SYS1.LOCAL/Documents/IMT/SecureCode/hour_change.py', date_command, time_command])
    except ValueError as e:
        print(f"An error occurred while changing the date and time: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while changing the date and time: {e}")

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
            change_date_time()
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
    date_format = client_socket.recv(1024).decode()
    client_socket.send("Choose the time format (e.g., %H:%M:%S): \n".encode())
    time_format = client_socket.recv(1024).decode()
    return date_format, time_format

def get_time_online(client_socket, date_format, time_format):
    now = datetime.datetime.now()
    date = now.strftime(date_format)
    time = now.strftime(time_format)
    client_socket.send(date.encode())
    client_socket.send('{}\n'.format(time).encode())

def handle_online_client(client_socket):
    date_format = ""
    time_format = ""

    client_socket.send("Choose an option: \n\n".encode())
    menu_online(client_socket)  # Display the menu once at the beginning

    while True:
        choice = client_socket.recv(1024).decode('utf-8').strip()

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
    offline_thread = threading.Thread(target=run_offline_mode)
    offline_thread.start()

    host = "localhost"
    port = 12345
    start_online_server(host, port)

if __name__ == "__main__":
    main()