import socket
import _thread as thread
import time
import queue
import os

#initialize method
def init():
    global host_ip, serverSocket, connectedClients, connectionSocket, address,serverSocket
    get_Host_name_IP()

    bindSocket()

    connectedClients=[]
    while True:
        connectionSocket, address=serverSocket.accept()
        #print(connectionSocket)
        connectedClients.append(connectionSocket)
        print (str(address)+ " has successfully connected")

        thread.start_new_thread(createConnectionThread,(connectionSocket,address))

    connectionSocket.close()
    serverSocket.close()

#gets hostname and hostip
def get_Host_name_IP():
    global host_name, host_ip
    try:
        host_name=socket.gethostname()
        host_ip=socket.gethostbyname(host_name)
        print("Hostname :  ",host_name) 
        print("IP : ",host_ip)
    except: 
        print("Unable to get Hostname and IP")

#binds serverSocker
def bindSocket():
    global serverSocket,serverPort
    serverSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverPort=12002
    print("Port: ",serverPort)
    serverSocket.bind((host_ip,serverPort))
    serverSocket.listen()
    print("Server is listening...")

#handles different messages format
def createConnectionThread(connection, address):
    global dictionary, connectedClients, q
    connection.send('======================================\n'.encode())
    connection.send('       Welcome, Valar Morghulis\n'.encode())
    connection.send('======================================'.encode())
    while True:
        try:
            message=connection.recv(2048).decode()
            if message:
                
                #for name mapping(~~~ = TAG)
                if message.startswith('~~~'):
                    testList=message.split('&')
                    dictionary[testList[1]]=testList[2]
                    #print(dictionary)

                #for file sending/receiving
                elif message.startswith('~FS'):
                    q.put(get_send_file(connection, address))
                    time.sleep(10)
                    while not q.empty():
                        q.get()

                #removing connection
                elif message=='\quit':
                    remove(connection,address)

                #change name
                elif message.startswith('newname'):
                    oname=dictionary[str(address)]
                    dictionary[str(address)]=message.split('-')[1]
                    sendMessage='<'+oname+'> has changed name to <'+dictionary[str(address)]+'>'
                    print(sendMessage)
                    forwardMessage(sendMessage, connection, address)

                #message receive
                else:
                    sendMessage='<'+ dictionary[str(address)]+'> ' + message
                    print(sendMessage)
                    forwardMessage(sendMessage, connection, address)                   

            else:
                remove(connection,address)
        except:
            continue

def get_send_file(connection, address):
    global connectedClients
    
    extension=connection.recv(1024).decode().split('&')
    file='server' + extension[1]
    print(file)
    print('Receiving File (Server)')
    byte='~FE'.encode()
    #client to server file writing
    with open(file,'wb') as fw:
        while True:
            data=connection.recv(1024)
            if data[-3:]==byte:
                fw.write(data[:-3])
                break
            else:                                
                fw.write(data)
        fw.close()
    print('Received File (Server)')
    
    forwardMessage('~FS'+extension[0], connection, address)
    #server to client sending
    with open(file,'rb') as fs:
        while True:
            data = fs.read(4096)
            forwardFile(data, connection, address)
            if not data:
                forwardMessage('~FE', connection, address)
                break
        fs.close()
        print('sent all')
        os.remove(file)

def remove(connection,address):
    if connection in connectedClients:
        connectedClients.remove(connection)
        leftMessage=dictionary[str(address)]+' has left the chat room'
        print(leftMessage)
        forwardMessage(leftMessage, connection,address)

def forwardFile(_bytes, conn, adr):
    for client in connectedClients:
        if client!=conn:
            try:
                client.send(_bytes)
            except:
                remove(conn, adr)

def forwardMessage(msg, conn, adr):
    for client in connectedClients:
        if client!=conn:
            try:
                client.send(msg.encode())
            except:
                remove(conn, adr)
            
#Global variables
q=queue.Queue()
host_ip, serverSocket,serverPort, connectedClients, connectionSocket, address, host_ip, dictionary= None, None, None, None, None, None, None, {}
init()

