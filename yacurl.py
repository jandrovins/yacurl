#!/bin/env python
import socket
import logging
import argparse
import cmd
from urllib.parse import urlparse
import pathlib
from bs4 import BeautifulSoup

class yacurl():
    def __init__(self,parsed_url ,port=80 ):
        self.port = port
        self.parsed_url = parsed_url
        self.path = parsed_url.path
        self.query = parsed_url.query
        self.hostname = parsed_url.hostname
        self.host = socket.gethostbyname(self.hostname)
        self.create_socket()
        self.socket_file = self.sock.makefile("rb")
        self.message = None
        self.header = None
        self.payload = None
        self.read_header = False
        self.read_payload = False
        self.sent_message = False
        logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s", 
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )

        logging.info(f"STARTED CLIENT USING {self.hostname}:{self.port}")
    def reset_socket(self):
        self.sock.close()
        self.create_socket()
        self.read_header = False
        self.read_payload = False
    def create_socket(self):
        logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.sock.connect((self.host, self.port))
        logging.info(f'-- Created socket - connected to {self.host}:{self.port}')
        print(f'-- Created socket - connected to {self.host}:{self.port}')
        return self.sock
    def gen_request(self):
        message  = f'GET {self.path} HTTP/1.1\r\n'.encode()
        message += f'User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)\r\n'.encode()
        message += f'Host: {self.hostname}:{self.port}\r\n'.encode()
        message += b'Connection: close\r\n'
        message += b'\r\n'
        self.message = message
        return message
    def send_request(self):
        logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )
        message = self.gen_request()
        logging.info(f'-- Sending message: {message.decode()}')
        logging.info(f'##########################################################################')
        self.sock.sendall(message)
        self.sent_message = True
        return message
    def process_header(self):
        logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )
        header = []
        while True:
            line = self.socket_file.readline()
            logging.info(f'-- Read Header: {line.decode("iso-8859-1")}')
            header.append(line)
            if line in (b'\r\n', b'\n', b''):
                break
        header = b''.join(header).decode('iso-8859-1')
        self.header = header
        logging.info(f'-- Read all Header: '+ header.replace("\r\n", " || " ))
        logging.info(f'##########################################################################')
        self.read_header = True
        return header
    def process_payload(self):
        logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )
        payload = b''
        while True:
            buf = self.socket_file.read(1024)
            if not buf:
                break
            payload += buf
        self.payload_bytes = payload
        self.payload = payload.decode('ISO-8859-1')
        logging.info(f'-- Read Payload: {self.payload}')
        logging.info(f'##########################################################################')
        self.read_payload = True
        return payload
    def save_payload_to_file(self):
        logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )
        header_lines = self.header.split('\r\n')
        file_type = None
        for l in header_lines:
            if 'content-type'.lower() in l.lower():
                file_type = l.split(";")[0].split(":")[1].split("/")[1].strip()
        if file_type == None:
            return
        with pathlib.Path("./" + self.hostname + "." + file_type) as f:
            f.write_bytes(self.payload_bytes)
    def list_static_resources(self):
        soup = BeautifulSoup(self.payload, 'html.parser')
        img_tags = soup.find_all('img')
        self.urls = [img['src'] for img in img_tags]
        for link in soup.find_all('a'):
            self.urls.append(link.get('href'))
        return self.urls
    def download_static_resources(self):
        self.list_static_resources()
        for u in self.urls:
            parsed_url = urlparse(u)
            port = 80
            c = yacurl(parsed_url, port)
            c.send_request()
            client.process_header()
            client.process_payload()
            client.save_payload_to_file()
            print(f"Tried to download {u} #############")
            del c
            


            


class YacurlShell(cmd.Cmd):
    intro = "Welcome to yacurl! \n Type ? or help to see commands. \n Type help COMMAND_NAME to see further information about the command. \n Type bye to leave."
    prompt = "yacurl cli-> "
    file = None
    def do_PRINT_REQUEST(self, arg):
        'Prints request sent to server'
        if self.client.message == None:
            print("Message not yet sent: ")
        else:
            print("Message sent: ")
        print(self.client.gen_request().decode())
    def do_SEND_REQUEST(self, arg):
        'Prints and sends request to server'
        self.client.send_request()
    def do_PROCESS_RESPONSE(self, arg):
        'Recieves response from server'
        if not self.client.sent_message:
            print("Either you have already processed a response or you need to send the request to the server before you try to process the server response.")
        else:
            self.client.process_header()
            self.client.process_payload()
            self.client.sent_message = False
    def do_PRINT_HEADER(self, arg):
        'Recieves and prints the header'
        if not self.client.read_header:
            print("Header has not been processed. Use the command to process it.")
        else:
            print(f"########### HEADER #############\n{self.client.header}\n################################")
        print(f'##########################################################################')
    def do_PRINT_PAYLOAD(self, arg):
        'Recieves and prints the payload'
        if not self.client.read_payload:
            print("payload has not been processed. Use the command to process it.")
        else:
            print(f"########### PAYLOAD ############\n{self.client.payload}\n################################")
        print(f'##########################################################################')
    def do_PRINT_FULL_RESPONSE(self, arg):
        'Prints header and payload response'
        print(f'##########################################################################')
        if not self.client.read_header:
            print("Header has not been processed. Use the command to process it.")
        else:
            print(f"########### HEADER #############\n{self.client.header}\n################################")
        if not self.client.read_payload:
            print("Payload has not been processed. Use the command to process it.")
        else:
            print(f"########### PAYLOAD ############\n{self.client.payload}\n################################")
        print(f'##########################################################################')
    def do_LIST_STATIC_CONTENT(self, arg):
        'Lists static content in the HTML of the URL provided'
        if not self.client.read_header or not self.client.read_payload:
            print("Header or payload has not been processed. Use the command to process them.")
        else:
            print(f"########### STATIC CONTENT #############\n{self.client.list_static_resources()}\n################################")
    def do_DOWNLOAD_STATIC_CONTENT(self, arg):
        'Downloads static content from the static content found on the HTML of the URL provided'
        if not self.client.read_header or not self.client.read_payload:
            print("Header or payload has not been processed. Use the command to process them.")
        else:
            self.client.download_static_resources()
        



if __name__ == "__main__":
    # Parameters management
    parser = argparse.ArgumentParser(description="Get web page")
    parser.add_argument("--port", type=int, metavar="PORT", default = 80, help="Port on which the client will open sockets. Default is 80")
    parser.add_argument("--url", type=str, default="https://en.wikipedia.org/wiki/Vincent", help="URL to be retrieved. Default is en.wikipedia.org/wiki/Vincent")

    args = parser.parse_args()
    parsed_url = urlparse(args.url)
    port = args.port
    client = yacurl(parsed_url, port)

    shell = YacurlShell()
    shell.client = client
    try:
        shell.cmdloop()
    except Exception as e:
        print(f"Sorry, we were not expecting that. {e}")

    client.sock.close()
