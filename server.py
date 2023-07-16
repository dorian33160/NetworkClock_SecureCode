import datetime
import socket
import select
import threading
import subprocess
import shlex

# Menu qui affiche les options disponibles (afficher l'heure, afficher la date, afficher les deux, changer la date et l'heure)
def menu_offline():
    print("1 - Choisir le format")
    print("2 - Afficher la date et l'heure")
    print("3 - Changer la date et l'heure")
    print("4 - Quitter\n\n")

def menu_online(client_socket):
    client_socket.send("1 - Choisir le format\n".encode())
    client_socket.send("2 - Afficher la date et l'heure\n".encode())
    client_socket.send("3 - Quitter\n\n".encode())

################################ FONCTION OFFLINE ###############################

def get_format_offline():
    date_format = input("Choisissez le format de la date (ex: %d/%m/%Y): ")
    heure_format = input("Choisissez le format de l'heure (ex: %H:%M:%S): ")
    return date_format, heure_format

def change_date_time():
    new_date = input("Entrez la nouvelle date (format YYYY-MM-DD) : ")
    new_time = input("Entrez la nouvelle heure (format HH:MM:SS) : ")
    date_format = input("Entrez le format de date souhaité : ")
    time_format = input("Entrez le format d'heure souhaité : ")
    try:
        # Vérification des entrées utilisateur pour éviter les injections de commandes
        if not all(isinstance(param, str) for param in [new_date, new_time, date_format, time_format]):
            raise ValueError("Les paramètres de date, d'heure, de format et de format d'heure doivent être des chaînes de caractères.")

        # Échapper les caractères spéciaux dans les arguments de commande
        date = shlex.quote(new_date)
        time = shlex.quote(new_time)

        # Construire les commandes pour changer la date et l'heure en utilisant le format spécifié
        date_command = f"date -s '{date} {time}' +'{date_format}'"
        time_command = f"date -s '{time}' +'{time_format}'"

        subprocess.call(['sudo', 'python', '/home/dorian.neilz@SYS1.LOCAL/Documents/IMT/SecureCode/hour_change.py', date_command, time_command])
    except ValueError as e:
        print(f"Une erreur s'est produite lors de la modification de l'heure et de la date : {e}")
    except Exception as e:
        print(f"Une erreur inattendue s'est produite lors de la modification de l'heure et de la date : {e}")

def get_time_offline():
    date_format = ""
    heure_format = ""
    while True:
        menu_offline()
        choix = input("Choisissez une option: \n")
        if choix == "1":
            date_format, heure_format = get_format_offline()
        elif choix == "2":
            if date_format == "" or heure_format == "":
                date_format = "%d/%m/%Y"
                heure_format = "%H:%M:%S"
            maintenant = datetime.datetime.now()
            date = maintenant.strftime(date_format)
            heure = maintenant.strftime(heure_format)
            print(date)
            print(heure)
        elif choix == "3":
            change_date_time()
        elif choix == "4":
            break
        else:
            print("Choix invalide\n")

def run_offline_mode():
    get_time_offline()

################################ FONCTION ONLINE ###############################

# Fonction qui demande au client de choisir le format de la date et de l'heure
def get_format_online(client_socket):
    client_socket.send("Choisissez le format de la date (ex: %d/%m/%Y): \n".encode())
    date_format = client_socket.recv(1024).decode()
    client_socket.send("Choisissez le format de l'heure (ex: %H:%M:%S): \n".encode())
    heure_format = client_socket.recv(1024).decode()
    return date_format, heure_format

def get_time_online(client_socket, date_format, heure_format):
    maintenant = datetime.datetime.now()
    date = maintenant.strftime(date_format)
    heure = maintenant.strftime(heure_format)
    client_socket.send(date.encode())
    client_socket.send('{}\n'.format(heure).encode())

def handle_online_client(client_socket):
    date_format = ""
    heure_format = ""

    client_socket.send("Choisissez une option: \n\n".encode())
    menu_online(client_socket)  # Afficher le menu une fois au début

    while True:
        choix = client_socket.recv(1024).decode('utf-8').strip()

        if choix == "1":
            date_format, heure_format = get_format_online(client_socket)
            menu_online(client_socket)  # Envoyer le menu après chaque commande
        elif choix == "2":
            if date_format == "" or heure_format == "":
                date_format = "%d/%m/%Y"
                heure_format = "%H:%M:%S"
            get_time_online(client_socket, date_format, heure_format)
            menu_online(client_socket)  # Envoyer le menu après chaque commande
        elif choix == "3":
            client_socket.close()
            break

def start_online_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)  # Limite le nombre de connexions en attente à 5

    server_socket.setblocking(0)  # Définit le socket en mode non bloquant

    print("Serveur en écoute sur {}:{}".format(host, port))

    inputs = [server_socket]  # Liste des sockets à surveiller

    while True:
        # Utilise select pour vérifier si de nouvelles connexions sont disponibles
        readable, _, _ = select.select(inputs, [], [])

        for sock in readable:
            if sock == server_socket:
                # Nouvelle connexion entrante
                client_socket, address = server_socket.accept()
                print("Connexion de {}\n".format(address))
                inputs.append(client_socket)  # Ajoute le nouveau socket à la liste des sockets surveillés
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