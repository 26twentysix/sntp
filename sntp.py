import ntplib
import socket
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--delay", type=int, default=0)
parser.add_argument("-p", "--port", type=int, default=123)
args = parser.parse_args()

delay = args.delay
port = args.port
ntp = ntplib.NTPClient()


def handle_client(message, address):
    print(f'Client {address[0]} connected')
    # do request to stratum2 ntp server
    ntp_req = ntp.request('ntp1.stratum2.ru')

    # create and set up response
    ntp_resp = ntplib.NTPStats()
    ntp_resp.leap = ntp_req.leap
    ntp_resp.mode = 4
    ntp_resp.stratum = 3

    # copy stratum2 info to response
    ntp_resp.poll = ntp_req.poll
    ntp_resp.precision = ntp_req.precision
    ntp_resp.root_delay = ntp_req.root_delay
    ntp_resp.root_dispersion = ntp_req.root_dispersion
    ntp_resp.ref_id = ntp_req.ref_id

    # copy last sync time
    ntp_resp.ref_timestamp = ntp_req.ref_timestamp
    # changing resp receive time
    ntp_resp.recv_timestamp = ntp_req.recv_timestamp + delay
    # changing resp send time
    ntp_resp.tx_timestamp = ntp_req.tx_timestamp + delay

    # send response
    ntp_resp = bytearray(ntp_resp.to_data())
    ntp_resp[24:32] = message[40:48]
    ntp_resp[0] = (ntp_resp[0] & 0b11000111) + (message[0] & 0b00111000)
    sock.sendto(ntp_resp, address)


sock = socket.socket(type=socket.SOCK_DGRAM)
try:
    sock.bind(('', port))
except PermissionError:
    print("Permission denied.")
    sock.close()
    exit(1)

print('Server is up!')
print(f'Delay is {delay} seconds')

try:
    while True:
        message, address = sock.recvfrom(1024)
        threading.Thread(target=handle_client, args=(message, address)).start()
finally:
    sock.close()
