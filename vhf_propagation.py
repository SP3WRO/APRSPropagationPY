#!/usr/bin/env python3
import time
import socket
import requests
import re
from html import unescape

# ===== Konfiguracja =====
CALLSIGN = "SP0ABC"
SHARE_TNC_HOST = "127.0.0.1"
SHARE_TNC_PORT = 8111           # <- Twój port share-tnc
CHECK_INTERVAL = 900            # 15 minut

# Nowe endpointy (Europa, >=250 i >=500 km)
URL_250KM = "https://vhf.dxview.org/text_display?reg=Europe&dist=250"
URL_500KM = "https://vhf.dxview.org/text_display?reg=Europe&dist=500"

# Lista monitorowanych lokatorów
GRID_SQUARES = {
    "JO74", "JO84", "JO94", "KO04", "KO14", "JO73", "JO83", "JO93", "KO03",
    "KO13", "JO72", "JO82", "JO92", "KO02", "KO12", "JO71", "JO81", "JO91",
    "KO01", "KO11", "JO70", "JO80", "JO90", "KO00", "KO10", "JN79", "JN89",
    "JN99", "KN09", "KN19"
}

# Parser: akceptuje dwukropek lub jego brak po pierwszym lokatorze
LINE_RE = re.compile(
    r"\b([A-R]{2}\d{2})\s*:?\s*[A-Z]{1,3}\s+(\d{2,4})\s*km\s*to\s*([A-R]{2}\d{2})\b",
    re.IGNORECASE
)

# Sesja HTTP z nagłówkiem, żeby uniknąć odrzucenia przez serwer
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) vhf-propagation/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

# ===== Pobieranie i parsing =====
def fetch(url: str, timeout: int = 12) -> str:
    r = SESSION.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text

def parse_entries(html: str):
    """Zwraca listę (grid_a, distance_km, grid_b) z całego tekstu."""
    txt = unescape(html.replace("</div>", "\n"))
    txt = re.sub(r"<[^>]+>", " ", txt)
    entries = []
    for m in LINE_RE.finditer(txt):
        a = m.group(1).upper()
        dist = int(m.group(2))
        b = m.group(3).upper()
        entries.append((a, dist, b))
    return entries

def pick_hits(entries):
    """Zatrzymaj tylko wpisy, gdzie A lub B należy do naszej listy."""
    return [(a,d,b) for (a,d,b) in entries if (a in GRID_SQUARES or b in GRID_SQUARES)]

def determine_payload(hits_250, hits_500):
    if hits_500:
        return ">Propagacja 2m: BARDZO WYSOKA"
    if hits_250:
        return ">Propagacja 2m: Podwyzszona"
    return ">Propagacja 2m: normalna"

# ===== AX.25 + KISS (sprawdzona metoda) =====
def encode_ax25_address(callsign: str, ssid: int, last: bool = False) -> bytes:
    """Koduje adres AX.25 do 7 bajtów (callsign <<1, SSID + bity, ewentualny bit 'last')."""
    cs = callsign.upper().ljust(6)[:6]
    addr = bytearray(7)
    for i, ch in enumerate(cs):
        addr[i] = (ord(ch) & 0x7F) << 1
    addr[6] = 0x60 | ((ssid & 0x0F) << 1)   # bity zarezerwowane + SSID
    if last:
        addr[6] |= 0x01                     # koniec adresów
    return bytes(addr)

def send_aprs_message(message: str):
    """
    Buduje pełną ramkę AX.25 UI i wysyła ją jako KISS (typ 0x00) do share-tnc.
    DEST=APRS-0, SRC=CALLSIGN-0, PATH=WIDE2-2 (jeden wpis, ostatni).
    """
    try:
        dest = encode_ax25_address("APRS", 0)               # APRS-0
        src  = encode_ax25_address(CALLSIGN, 0)             # SR3WR-0
        path = encode_ax25_address("WIDE2", 2, last=True)   # WIDE2-2 (ostatni)

        frame  = dest + src + path
        frame += b'\x03'            # Control: UI
        frame += b'\xF0'            # PID: No Layer 3
        frame += message.encode('ascii', 'ignore')  # INFO (ASCII)

        kiss_frame = b'\xC0\x00' + frame + b'\xC0'  # KISS start + TX(0x00) + end

        with socket.create_connection((SHARE_TNC_HOST, SHARE_TNC_PORT), timeout=6) as sock:
            sock.sendall(kiss_frame)

        print(f"📡 Wysłano APRS: {message}")
    except Exception as e:
        print(f"❌ Błąd wysyłania do share-tnc: {e}")

# ===== Główna logika =====
def one_cycle():
    html250 = fetch(URL_250KM)
    html500 = fetch(URL_500KM)

    e250 = parse_entries(html250)
    e500 = parse_entries(html500)

    h250 = pick_hits(e250)
    h500 = pick_hits(e500)

    # Podgląd (opcjonalny)
    print(f"Znaleziono wpisów: >=250 km: {len(e250)}, >=500 km: {len(e500)}")
    for a,d,b in h250[:10]:
        print(f"[HIT 250] {a} — {d} km — {b}")
    for a,d,b in h500[:10]:
        print(f"[HIT 500] {a} — {d} km — {b}")

    payload = determine_payload(h250, h500)
    send_aprs_message(payload)

def main():
    while True:
        try:
            one_cycle()
        except Exception as e:
            print(f"❌ Błąd cyklu: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
