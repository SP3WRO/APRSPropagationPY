🇵🇱 Instrukcja instalacji i konfiguracji skryptu VHF + APRS
✅ Wymagania:

Linux
Python 3
Działający fizyczny TNC w trybie KISS (np. VP-DIGI przez port szeregowy /dev/rfcomm0)


1. Instalacja zależności

Zainstaluj Python 3 i pip (jeśli nie masz):

<code>sudo apt install python3 python3-pip</code>

Zainstaluj bibliotekę requests:

pip3 install requests

2. Instalacja share-tnc

Pobierz i skompiluj share-tnc:

git clone https://github.com/trasukg/share-tnc.git
cd share-tnc
make

Uruchom share-tnc z połączeniem do fizycznego TNC (np. /dev/rfcomm0):

./share-tnc /dev/rfcomm0

To utworzy port TCP domyślnie na localhost:8001.
3. Utwórz skrypt vhf_propagation.py

Utwórz plik:

nano ~/vhf_propagation.py

Wklej pełną wersję skryptu, który pobiera dane z https://vhf.dxview.org i wysyła ramki APRS przez socket TCP na localhost:8001.

Zapisz i nadaj uprawnienia:

chmod +x ~/vhf_propagation.py

Uruchom testowo:

python3 ~/vhf_propagation.py

4. (Opcjonalnie) Utwórz usługę systemową (systemd)

Utwórz plik:

sudo nano /etc/systemd/system/vhf-propagation.service

Wklej zawartość:

[Unit]
Description=VHF Propagation Monitor Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/<użytkownik>/vhf_propagation.py
Restart=on-failure
User=<użytkownik>
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target

Zamień <użytkownik> na swoją nazwę użytkownika.

Następnie załaduj i uruchom usługę:

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable --now vhf-propagation.service

Możesz obserwować logi:

journalctl -u vhf-propagation -f

📡 Efekt działania

Skrypt będzie co 30 minut:

Pobierał dane o propagacji w paśmie 2m z dwóch źródeł na dystansach 250 i 500km
Sprawdzał obecność łączności w określonych kwadratach
Generował gotową ramkę APRS przez protokół KISS
Wysyłał ją do share-tnc.
