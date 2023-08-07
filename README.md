# NetworkClock_SecureCode

Ptyhon app that changes date and hour on a linux system with security approach

## Introduction

To use it, you have to configure the config.json for the socket. By default it works on localhost:12345.
You can run server.py and interact with the menu.

## To connect to the app with a client

You have to launch a telnet connection with IP and Port that you configured in config.json. The menu will appear but you won't be able to change date and time of the server for questions of security :)

## Change date and time

**BEFORE EXECUTING THE PROGRAMME YOU HAVE TO CHANGE THE PATH OF HOUR_CHANGE.PY IN SERVER.PY**

Changing date and time will call hour_change.py with sudo. For this to be secure, I used capabilities to delimit sudo to only being capable to change date and time.

**You may have to import modules as prctl for example**
