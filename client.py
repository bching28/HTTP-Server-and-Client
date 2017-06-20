#!/usr/bin/env python3

# HTTP CLIENT
#
# Set script as executable via: chmod +x client.py
# Run via:  ./client.py <IP> <PORT>
#
# To connect to a server on the same computer, <IP> could
# either be 127.0.0.1 or localhost (they have the same meaning)

import socket
import sys
import argparse
import os

def header(url, size, ip):
	message = ""
	put = "PUT " + url + " HTTP/1.1\r\n"
	host = "Host: " + ip + "\r\n"
	content_len = "Content-Length: " + str(size) + "\r\n"
	user_agent = "User-Agent: 177 Midterm Exam\r\n"
	expect = "Expect: 100-Continue\r\n"
	message = put + host + content_len + user_agent + expect + "\r\n"
	return message

def main():
	if not sys.version_info[:2] == (3,3):
		print("Error: need Python 3.3 to run program")
		sys.exit(1)
	else:
		print("Using Python 3.3 to run program")
    
	parser = argparse.ArgumentParser()
	parser.add_argument("--url", type=str, dest="url", help="specify the URL") #http://10.10.5.203/students/bching1/x.jpg
	parser.add_argument("--file", type=str, dest="u_file", help="specify the file to upload") #apollo-17-1.jpg & apollo-17-8.jpg
	arg=parser.parse_args()

    # Create TCP socket
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as msg:
		print("Error: could not create socket")
		print("Description: " + str(msg))
		sys.exit()

	ip = arg.url.split('//')[1].split('/')[0]
	print("IP: ", ip)

	print("Connecting to server at " + ip)
     
    # Connect to server
	try:
		port = 80
		s.connect((ip , port)) #port 0 so that OS picks port for me
	except socket.error as msg:
		print("Error: Could not open connection")
		print("Description: " + str(msg))
		sys.exit()
 
	print("Connection established")
    
	# Send HTTP PUT request to server
	stat_info = os.stat(arg.u_file)
	size = stat_info.st_size # size of file returned in bytes
	req_header = header(arg.url, size, ip)
	# testing
	print(req_header)
	en_header = req_header.encode()
	try:
		header_sent = s.send(en_header)
	except socket.error as msg:
		print("Error: send() failed")
		print("Description: " + str(msg))
		sys.exit()

	print("Sent header to server")

	# Wait for Server Response
	try:
		buffer_size=4096
		server_resp = s.recv(buffer_size)
	except:
		print("Error: unable to recv()")
		print("Description: " + str(msg))
		sys.exit()

	string_unicode = server_resp.decode('ascii')
	# testing
	print("Response: ", string_unicode)

    	# Send message to server

	content = open(arg.u_file,'rb')	
	data = content.read()
	content.close()
	try:
		# Send the string
		bytes_sent = s.sendall(data)
	except socket.error as msg:
		print("Error: send() failed")
		print("Description: " + str(msg))
		sys.exit()

    # Close socket
	try:
		s.close()
	except socket.error as msg:
		print("Error: unable to close() socket")
		print("Description: " + str(msg))
		sys.exit()

	print("Sockets closed, now exiting")

if __name__ == "__main__":
    sys.exit(main())
