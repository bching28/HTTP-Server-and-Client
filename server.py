#!/usr/bin/env python3

# Project 2: HTTP Server Part 2
# By: Bryan Ching
#
# Create TCP Socket --> Bind to Listening Port --> Listening on Port --> 
# Loop to Accept Multiple Requests --> Receive Data --> Obtain Request Method -->
# Try to Open Files --> Close Client Socket --> Repeat
# 

import socket
import sys
import argparse
import time
import mimetypes
import datetime
import os

#for multiprocesses
import multiprocessing
import queue
import time

# Python-Style Process Class
class ProcessReq(multiprocessing.Process):
	def __init__(self, name, recv_size, base_dir, verbose, q):
		multiprocessing.Process.__init__(self)
        
	# Variables for constructor
		self.name = name
		self.recv_size = recv_size
		self.base_dir = base_dir
		self.verbose = verbose
		self.q = q

	# run()
	def run(self):
		while (1):
			try:
				q_value = self.q.get(block=True)
				print("Process '%s' has obtained value from Q: '%s'" % (self.name, q_value))
				time.sleep(0.01)   # Minimal sleep to let other process run
			except queue.Empty as msg:
				print(msg)
				pass		
			
			if (self.verbose==1):
				print("Q Value: ", q_value)

			#setting 30 second timeout
			q_value.settimeout(30)

			# Receive data
			recv_len=1
			raw_bytes=b""
			no_data=0 #no_data=0: There is data; no_data=1: There is NO data
			while(no_data==0):
				recv_len=1
				raw_bytes=b""
				while(recv_len!=0):
					no_data=0 #resetting no_data
					buffer_size=self.recv_size
					if (self.verbose==1):
						print("Process '%s'" % (self.name))
					try:
						recv_bytes = q_value.recv(buffer_size)
					except socket.timeout as msg:
						print("Timeout on recv()")
						print("Description: " + str(msg))
						no_data=1
						recv_len=0
						break
					except socket.error as msg:
						print("Error: unable to recv()")
						print("Description: " + str(msg))
						sys.exit()

					# If recv_bytes has no data, then set no_data to 1
					if (len(recv_bytes)==0):
						no_data=1 #true
						recv_len=0 #set to 0 so it doesn't go back to while(recv_len!=0)
					# If recv_bytes has data, then set no_data to 0
					else:
						no_data=0 #false (if actually has data)
					
					# Normal process if there is data present
					if (no_data==0):
						raw_bytes = raw_bytes + recv_bytes
						check_str = raw_bytes.decode('ascii').endswith("\r\n\r\n")
						if (check_str==True):
							recv_len=0 #end of request
						else:
							recv_len = len(raw_bytes)
							if (self.verbose==1):
								print("Received %d bytes from client" % recv_len)

					if (self.verbose==1):
						print("Recv Part: ", recv_bytes.decode('ascii'))
			
				# Process Request IF done receiving data AND there was data to receive
				if (recv_len==0 and no_data==0):
					string_unicode = raw_bytes.decode('ascii')
					# obtaining request method from client response
					req_method = string_unicode.split(' ')[0]
					
					if (self.verbose==1):
						print("Request Method: ", req_method)

					# Opening File
					# Create header with HTTP/1.1, status type, and data
					if (req_method == "GET"):
						file_open = string_unicode.split(' ')[1]

						# Printing out file to open
						# If there is no file listed, open index file
						if (file_open == "/"):
							file_open = "/index.html"
						if (self.verbose==1):
							print("File to open: ", file_open)
						
						# Trying to open website files
						try:
							if (self.verbose==1):
								print("Location of File: ")
								print(self.base_dir+file_open)
							content = open(self.base_dir + file_open,'rb')	
							resp_data = content.read()
							content.close()
							resp_header = header(200, len(resp_data), self.base_dir+file_open)

						# If I cannot open the website file, raise exception
						except Exception as msg:
							print(msg)
							resp_header = header(404, 0, self.base_dir+file_open)
							# the "b" converts str to byte
							resp_data = b"Error 404: File not found"
						# .encode() fixes issue of not being able to convert str to byte
						serv_resp = resp_header.encode()
						serv_resp += resp_data
						q_value.sendall(serv_resp)	

					# Handling 501 error
					else:
						resp_header = header(501, 0, self.base_dir+file_open)
						resp_data = b"Error 501: Request method not implemented in server"
						serv_resp = resp_header.encode()
						serv_resp += resp_data
						q_value.sendall(serv_resp)

			# Closing client socket
			if (self.verbose==1):
				print("closing socket!")
			q_value.close()


def header(status_code, content_len, file_path):
	message = ""
	if (status_code == 200):
		# Collecting Date/Time Information
		date = datetime.date.today().strftime("%a, %d %b %Y")
		GMT_time = datetime.datetime.now() + datetime.timedelta(hours=7) # add 7 hours to current time for GMT
		GMT_time_str = GMT_time.strftime("%H:%M:%S") # formatting time into str
		exp_time = GMT_time + datetime.timedelta(hours=12) # add 12 hours to current time for expire time
		exp_time_str = exp_time.strftime("%H:%M:%S") # formatting time into str
		# Date Header
		date_header = "Date: " + date + " " + GMT_time_str + " GMT\r\n"
		# Expires Header
		expire_header = "Expires: " + date + " " + exp_time_str + " GMT\r\n"
		
		# Content-Length Header
		content_len_header = "Content-Length: " + str(content_len) + "\r\n" # passed in length of resp_data

		# Content-Type Header
		content_type_header = ("Content-Type: %s\r\n" % mimetypes.guess_type(file_path)[0]) # passed in path to file that is being downloaded

		# Collecting File's Last Modified Date/Time
		statbuf = os.stat(file_path).st_mtime
		statbuf_date_time = datetime.datetime.fromtimestamp(statbuf)
		# Last-Modified Header		
		last_mod = ("Last-Modified: %s\r\n" % statbuf_date_time)
		
		message = "HTTP/1.1 200 OK\r\n" + date_header + "Server: HTTP Server/(Python 3.3)\r\n" + content_len_header +  content_type_header + last_mod + expire_header + "\r\n"	
	elif (status_code == 404):
		message = "HTTP/1.1 404 Error\r\n\r\n"
	elif (status_code == 501):
		message = "HTTP/1.1 501 Error\r\n\r\n"
	return message

def main():
	i=0
	if not sys.version_info[:2] == (3,3):
		print("Error: need Python 3.3 to run program")
		sys.exit(1)
	else:
		print("Using Python 3.3 to run program")

	parser = argparse.ArgumentParser()
	parser.add_argument("--port", type=int, dest="port", help="specify your port number")
	parser.add_argument("--base", type=str, dest="base_dir", help="specify file directory")
	parser.add_argument("--recv", type=int, dest="recv_size", default="65536", help="specify max number of bytes at a time when downloading file") # set default to 64kB
	parser.add_argument("--verbose", type=int, dest="verbose", default=0, help="set value to '1' to initiate verbose mode")
	arg=parser.parse_args()

	# Creating Processing Queue
	q = multiprocessing.Queue()

	recv_size=arg.recv_size
	base_dir=arg.base_dir
	verbose=arg.verbose

	#Processes = 8 #4 cores times 2
	#pool = multiprocessing.Pool(Processes)
	# Creating Pool of Processes
	print("Launching a pool of eight processes...")
	process1 = ProcessReq("Process 1", recv_size, base_dir, verbose, q)
	process1.start()
	process2 = ProcessReq("Process 2", recv_size, base_dir, verbose, q)
	process2.start()
	process3 = ProcessReq("Process 3", recv_size, base_dir, verbose, q)
	process3.start()
	process4 = ProcessReq("Process 4", recv_size, base_dir, verbose, q)
	process4.start()
	process5 = ProcessReq("Process 5", recv_size, base_dir, verbose, q)
	process5.start()
	process6 = ProcessReq("Process 6", recv_size, base_dir, verbose, q)
	process6.start()
	process7 = ProcessReq("Process 7", recv_size, base_dir, verbose, q)
	process7.start()
	process8 = ProcessReq("Process 8", recv_size, base_dir, verbose, q)
	process8.start()
	print("Launched eight processes...")

	all_processes=[]
	all_processes.append(process1)
	all_processes.append(process2)
	all_processes.append(process3)
	all_processes.append(process4)
	all_processes.append(process5)
	all_processes.append(process6)
	all_processes.append(process7)
	all_processes.append(process8)

	# Create TCP Socket
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as msg:
		print("Error: could not create socket")
		print("Description: " + str(msg))
		sys.exit()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	# Bind to Listening Port
	try:
		host=''  # Bind to all interfaces
		s.bind((host,arg.port))
	except socket.error as msg:
		print("Error: unable to bind on port %d" % arg.port)
		print("Description: " + str(msg))
		sys.exit()

	# Listening
	try:
		backlog=10	# Number of incoming connections that can wait
				# to be accept()'ed before being turned away
		s.listen(backlog)
	except socket.error as msg:
		print("Error: unable to listen()")
		print("Description: " + str(msg))
		sys.exit()    

	print("Listening socket bound to port %d" % arg.port)

	# Loop to accept multiple requests
	# Accept an incoming request
	while (1):
		try:
			(client_s, client_addr) = s.accept()
			# If successful, we now have TWO sockets
			#  (1) The original listening socket, still active
			#  (2) The new socket connected to the client
		except socket.error as msg:
			print("Error: unable to accept()")
			print("Description: " + str(msg))
			sys.exit()

		print("Accepted incoming connection from client")
		print("Client IP, Port = %s" % str(client_addr))
		#print("Client Socket = ", client_s)

		q.put(client_s)

	for one_process in all_processes:
		one_process.join()
	print("All processes have finished")

if __name__ == "__main__":
    sys.exit(main())
