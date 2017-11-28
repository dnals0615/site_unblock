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
                data = self.dest.recv(8192) #4096
                if len(data) == 0:
                    raise Exception("endpoint closed")
                string = data.decode("utf-8")
                print("받은 문자열 : ",string)
                print("HTTP갯수 : ",string.count('HTTP'))
                if string.count("HTTP/1.1 404 Not Found") >= 1:
                    print("여기까지는 성공!!!!!!!!!!!이건 안보낸다!!!!!!")
                else :
                    index = string.find("HTTP/1.1")
                    if index >=0:
                        print("이거는 보내야한다!!!!!!")
                        #string = string[string.find("HTTP/1.1")+8 : ]
                        #index = string.find("HTTP/1.1")
                        #string = string[index : ]
                        #string = string[index:]
                        string = string.encode("utf-8")
                        self.source.request.sendall(string)
                #string = string.encode("utf-8")
                #self.source.request.sendall(string)#request
                print ("Received from dest: " + str(len(data)))
                
        except Exception as e:
            print ("EXCEPTION reading from forwarding socket")
            print (e)

        #self.source.stop_forwarding()
        #print ("...ending forwarder.")
        
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
                print("string : ",string)#string
                index = string.find("Host: ")
                index = index + 6
                print("index : ",index)#
                print("host[0] : ", string[index])#
                string2 = string[index:]
                print("string2 : ", string2)#
                index2 = string2.find("\r\n")
                print("index2 : ", index2)#
                host = string[index:(index+index2)]
                print("host :",host)
                #host = host.encode("utf-8")
                
                if index != -1:
                    f = Forwarder(self)
                    f.dest.connect((host,80))    
                    f.start()
                    string =  'GET / HTTP/1.1\r\nHost: test.gilgil.net\r\n\r\n' + string
                    string = string.encode("utf-8")
                    f.dest.sendall(string)
                print ("Received from source: " + str(len(data)))
                
                
        except Exception as e:
            print ("EXCEPTION reading from main socket")
            print (e)

        #f.stop_forwarding()
        #print ("...finishing handling connection")


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
