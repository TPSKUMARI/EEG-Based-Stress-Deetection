import csv
import socket
import time

# CSV file path and UDP server details
csv_file_path = 'C:\\Users\\SAMANTHIKA\\Desktop\\EEG_Demo\\EEG_Recordings.csv'
udp_ip = '192.168.1.7'  # IP address of the UDP server (use '127.0.0.1' for local testing)
udp_port = 12345      # Port number of the UDP server

def read_csv_and_send_udp(csv_file_path, udp_ip, udp_port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open(csv_file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)  # Skip header

        for row in csvreader:
            data_str = ','.join(row)
            # Send the data over UDP
            print(f"send message: {data_str}")
            sock.sendto(data_str.encode('utf-8'), (udp_ip, udp_port))
            # Sleep for a short interval to simulate real-time streaming
            time.sleep(1)  # Adjust the sleep time as needed

    sock.close()

if __name__ == "__main__":
    read_csv_and_send_udp(csv_file_path, udp_ip, udp_port)
