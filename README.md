# HTTP-Server-and-Client
Bryan Ching
Written in Python 3

SERVER:
Summary: Originally designed as a simple server that supports single connections that loads a website. Afterwards, the code
was updated to support multiple connections through the use of processes. The code was benchmarked using a program called, Siege.

Server supports:
- TCP connections
- HTTP status codes (200, 404, and 501)
- String and command-line argument parsing
- Parallelism using multiprocesses
- Persistent connections
- Server response headers (date, server, content-length, content-type, expires)



CLIENT:
Summary: This client was programmed during a midterm exam to upload files to a class server. This code successfully 
uploads files to the class server.

Client supports:
- TCP connections
- String and command-line argument parsing
- Server response headers (date, server, content-length, content-type, expires)
