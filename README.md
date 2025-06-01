🇵🇱 Instrukcja instalacji i konfiguracji skryptu VHF + APRS
✅ Wymagania:

Linux
Python 3
Działający fizyczny TNC w trybie KISS (np. VP-DIGI przez port szeregowy /dev/rfcomm0)


1. Instalacja zależności

Zainstaluj Python 3 i pip (jeśli nie masz):

<code>sudo apt install python3 python3-pip</code>

Zainstaluj bibliotekę requests:

<code>pip3 install requests</code>

2. Instalacja share-tnc

Pobierz i skompiluj share-tnc:

<code>git clone https://github.com/trasukg/share-tnc.git
cd share-tnc
make
</code>
Uruchom share-tnc z połączeniem do fizycznego TNC (np. /dev/rfcomm0):

<code>./share-tnc /dev/rfcomm0</code>

To utworzy port TCP domyślnie na localhost:8001.
3. Utwórz skrypt vhf_propagation.py

Utwórz plik:

<code>nano ~/vhf_propagation.py</code>

Wklej pełną wersję skryptu, który pobiera dane z https://vhf.dxview.org i wysyła ramki APRS przez socket TCP na localhost:8001.

Zapisz i nadaj uprawnienia:

<code>chmod +x ~/vhf_propagation.py</code>

Uruchom testowo:

<code>python3 ~/vhf_propagation.py</code>

4. (Opcjonalnie) Utwórz usługę systemową (systemd)

Utwórz plik:
<code>
sudo nano /etc/systemd/system/vhf-propagation.service
</code>
Wklej zawartość:
<code>

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

</code>

Zamień <użytkownik> na swoją nazwę użytkownika.

Następnie załaduj i uruchom usługę:
<code>
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable --now vhf-propagation.service
</code>
Możesz obserwować logi:
<code>
journalctl -u vhf-propagation -f
</code>
📡 Efekt działania

Skrypt będzie co 15 minut:

Pobierał dane o propagacji w paśmie 2m z dwóch źródeł na dystansach 250 i 500km
Sprawdzał obecność łączności w określonych kwadratach
Generował gotową ramkę APRS przez protokół KISS
Wysyłał ją do share-tnc.
