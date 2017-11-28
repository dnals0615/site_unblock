import socket
import socketserver
import threading
from time import sleep

class Forwarder(threading.Thread):
    def __init__(self, source):
        threading.Thread.__init__(self)
        self.source = source
        self.dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def run(self):
        print ("starting forwarder... ")
        
        try:
            while True:
                data = self.dest.recv(4096)
                if len(data) == 0:
                    raise Exception("endpoint closed")
                string = data.decode("utf-8")
                if string.count("HTTP/1.1") > 1:
                    string = string[string.find("HTTP/1.1")+8 : ]
                    index = string.find("HTTP/1.1")
                    string = string[index : ]
                    self.source.sendall(string)
                print ("Received from dest: " + str(len(data)))
                
        except Exception as e:
            print ("EXCEPTION reading from forwarding socket")
            print (e)

        self.source.stop_forwarding()
        print ("...ending forwarder.")
        
    def stop_forwarding(self):
        print ("...closing forwarding socket")
        self.dest.close()

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print ("Starting to handle connection...")

        try:
            while True:
                data = self.request.recv(4096)
                if len(data) == 0:
                    raise Exception("endpoint closed")
                string = data.decode("utf-8")
                index = string.find("Host: ")
                index = index + 6
                string2 = string[index:len(string)]
                index2 = string2.find("\r\n")
                if index != -1:
                    f = Forwarder(self)
                    f.dest.connect(string[index:index2])    
                    f.start()
                    string = string + 'GET / HTTP/1.1\r\nHost: test.gilgil.net\r\n\r\n'
                    string = string.encode("utf-8")
                    f.sendall(string)
                print ("Received from source: " + str(len(data)))
                
                
        except Exception as e:
            print ("EXCEPTION reading from main socket")
            print (e)

        f.stop_forwarding()
        print ("...finishing handling connection")


    def stop_forwarding(self):
        print ("...closing main socket")
        self.request.close()



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    server_thread = threading.Thread(target=server.serve_forever)
    
    server_thread.daemon = True
    server_thread.start()
    print ("Server loop running on port ", port)
    try:
        while True:
            sleep(1)
    except:
        pass
    print ("...server stopping.")
    server.shutdown()
