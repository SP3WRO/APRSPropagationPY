📦 Opis instalacji i konfiguracji (PL / Polish)
✅ Wymagania wstępne:

    System operacyjny: Linux (np. Raspberry Pi OS, Ubuntu, Debian)

    Zainstalowany Python 3:

sudo apt install python3 python3-pip

Zainstalowanie pakietu requests:

pip3 install requests

Działający TNC w trybie KISS (np. VP-DIGI) podłączony przez Bluetooth:

    Port szeregowy: /dev/rfcomm0

    Upewnij się, że TNC działa i odbiera ramki (np. użyj minicom albo aprx)

share-tnc – multiplexer KISS na TCP:

    Źródło: https://github.com/trasukg/share-tnc

    Kompilacja:

git clone https://github.com/trasukg/share-tnc.git
cd share-tnc
make

Uruchomienie:

        ./share-tnc /dev/rfcomm0

        Domyślnie nasłuchuje na porcie 8001 TCP

📜 Instalacja i uruchomienie skryptu

    Pobierz plik vhf_propagation.py:

        Skopiuj zawartość pełnej wersji skryptu (którą Ci podałem wcześniej) do pliku:

    nano ~/vhf_propagation.py

Nadaj plikowi uprawnienia do uruchamiania:

chmod +x ~/vhf_propagation.py

Testowe uruchomienie:

    python3 ~/vhf_propagation.py

        Skrypt sprawdzi propagację i wyśle ramkę APRS przez share-tnc do VP-DIGI.

⚙️ Opcjonalnie: utwórz usługę systemową (systemd)

Utwórz plik:

sudo nano /etc/systemd/system/vhf-propagation.service

Wklej:

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

Zamień <użytkownik> na swoją nazwę użytkownika systemu.

Potem aktywuj:

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable --now vhf-propagation.service

🌐 English version — Installation & Configuration Guide
✅ Prerequisites:

    OS: Linux (e.g. Raspberry Pi OS, Ubuntu, Debian)

    Python 3 installed:

sudo apt install python3 python3-pip

Install required library:

pip3 install requests

Working KISS-compatible TNC (e.g. VP-DIGI) connected via Bluetooth:

    Serial port: /dev/rfcomm0

    Make sure it’s working (use minicom or aprx to test)

share-tnc – KISS multiplexer to TCP:

    Source: https://github.com/trasukg/share-tnc

    Compile:

git clone https://github.com/trasukg/share-tnc.git
cd share-tnc
make

Run:

        ./share-tnc /dev/rfcomm0

        It will listen on port 8001 by default

📜 Installing and running the script

    Create the script:

nano ~/vhf_propagation.py

    Paste the final version of the script provided

Make it executable:

chmod +x ~/vhf_propagation.py

Run manually to test:

    python3 ~/vhf_propagation.py

⚙️ (Optional) Run as systemd service

Create:

sudo nano /etc/systemd/system/vhf-propagation.service

Content:

[Unit]
Description=VHF Propagation Monitor Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/<username>/vhf_propagation.py
Restart=on-failure
User=<username>
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target

Replace <username> with your actual Linux username.

Then enable it:

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable --now vhf-propagation.service

✅ Gotowe! / Done!

Skrypt automatycznie:

    sprawdza propagację co 30 minut

    wysyła ramkę APRS (KISS/AX.25)

    działa przez share-tnc z Twoim VP-DIGI

Masz system produkcyjny działający 24/7! 🚀📡
