import time
import requests
import socket

# Config
CALLSIGN = "SP0ABC"                 # Your callsign
SHARE_TNC_HOST = "127.0.0.1"        # share-tnc host address
SHARE_TNC_PORT = 8111               # Port TCP share-tnc
CHECK_INTERVAL = 900                # Check interval (15 min) 

# Poland gridsquare
GRID_SQUARES = {
    "JO74", "JO84", "JO94", "KO04", "KO14", "JO73", "JO83", "JO93", "KO03",
    "KO13", "JO72", "JO82", "JO92", "KO02", "KO12", "JO71", "JO81", "JO91",
    "KO01", "KO11", "JO70", "JO80", "JO90", "KO00", "KO10", "JN79", "JN89",
    "JN99", "KN09", "KN19"
}

URL_250KM = "https://vhf.dxview.org/map/text_display?dist=250&reg=Europe"
URL_500KM = "https://vhf.dxview.org/map/text_display?dist=500&reg=Europe"

# Functions

def fetch_vhf_data(url):
    """Downloading data from vhf.dxview.org and check gridsquares."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        text = response.text
        grids_found = set()
        for line in text.split("<div>"):
            if ":" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    grid = parts[0].strip()
                    if len(grid) == 4:  # np. JO74
                        grids_found.add(grid)
        return grids_found
    except Exception as e:
        print(f"Error data: {e}")
        return set()

def determine_propagation():
    """Określa stan propagacji."""
    squares_250km = fetch_vhf_data(URL_250KM)
    squares_500km = fetch_vhf_data(URL_500KM)

    if GRID_SQUARES & squares_500km:
        return ">Propagation 2m: VERY HIGH"
    elif GRID_SQUARES & squares_250km:
        return ">Propagation 2m: High"
    else:
        return ">Propagation 2m: Normal"

def encode_ax25_address(callsign, ssid, last=False):
    """Coding address AX.25 to 7 bites."""
    addr = bytearray(7)
    for i in range(6):
        if i < len(callsign):
            addr[i] = ord(callsign[i]) << 1
        else:
            addr[i] = ord(' ') << 1
    addr[6] = (ssid & 0x0F) << 1
    addr[6] |= 0x60  # Set reserved bits
    if last:
        addr[6] |= 0x01  # End of address field
    return addr

def send_aprs_message(message):
    """Building and sending APRS KISS packet to share-tnc."""
    try:
        destination = encode_ax25_address('APRS', 0)          # Destination: APRS
        source = encode_ax25_address(CALLSIGN, 0)             # Source: SP0ABC
        path1 = encode_ax25_address('WIDE2', 2, last=True)    # Path WIDE2-2

        frame = destination + source + path1
        frame += b'\x03'  # Control field: UI frame
        frame += b'\xF0'  # PID: No Layer 3
        frame += message.encode('ascii')  # Payload

        kiss_frame = b'\xC0\x00' + frame + b'\xC0'

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((SHARE_TNC_HOST, SHARE_TNC_PORT))
            sock.sendall(kiss_frame)

        print(f"Send APRS: {message}")
    except Exception as e:
        print(f"Sending error to share-tnc: {e}")

# Main loop

def main():
    """Main loop."""
    while True:
        propagation_message = determine_propagation()
        send_aprs_message(propagation_message)
        print("Waiting 15 minutes...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
