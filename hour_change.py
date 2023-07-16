import os
import subprocess
import sys
import prctl

def drop_privileges():
    # Vérifier si l'application est déjà exécutée avec les privilèges du superutilisateur
    if os.getuid() == 0:
        try:
            # Dropping les capabilities du superutilisateur
            prctl.cap_effective.drop()
            prctl.cap_permitted.drop()
            prctl.cap_inheritable.drop()

            # Définir explicitement les capabilities nécessaires (CAP_SYS_TIME) pour le changement de date et d'heure
            prctl.cap_effective.limit(prctl.CAP_SYS_TIME)
            prctl.cap_permitted.limit(prctl.CAP_SYS_TIME)
        except PermissionError as e:
            print("Impossible de réduire les privilèges du superutilisateur :", e)

def change_datetime(date_command, time_command):
    # Exécuter les commandes en utilisant subprocess.Popen sans shell
    try:
        subprocess.Popen(date_command, shell=True)
        subprocess.Popen(time_command, shell=True)
    except ValueError as e:
        print(f"Une erreur s'est produite lors de la modification de l'heure et de la date : {e}")
    except Exception as e:
        print(f"Une erreur inattendue s'est produite lors de la modification de l'heure et de la date : {e}")

# Abandonner les privilèges du superutilisateur avant d'appeler la fonction change_datetime
drop_privileges()
change_datetime(sys.argv[1],sys.argv[2])