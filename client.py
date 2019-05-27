import argparse
import socket
import threading
import time
import os
from pathlib import Path

#initialize method
def init():
    global clientName, clientPort, serverIP, serverPort
    
    parser=argparse.ArgumentParser()
    parser.add_argument("-n")
    parser.add_argument("-p")
    parser.add_argument("-s")
    args=parser.parse_args()

    clientName=args.n
    serverPort=args.p
    serverIP=args.s
    #serverPort=12000
    print(clientName, serverPort, serverIP)

    get_Host_name_IP()
    bindSocket()

#gets hostname and hostip
def get_Host_name_IP():
    global host_ip
    try:
        host_name=socket.gethostname()
        host_ip=socket.gethostbyname(host_name)
        print(host_ip)
    except: 
        print("Unable to get Hostname and IP")   

#binds clientSocket
def bindSocket():
    global clientSocket, serverPort, serverIP
    clientSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverIP, int(serverPort)))

#receive messages
def receive_messages():    
    global clientSocket, _quit, clientName, time_sleep, sleep, blocklist
   
    while True:
        if not _quit:
            try:
                receivedMessage=clientSocket.recv(4096).decode()
                if not sleep:
                    senderIndex=receivedMessage.find('>')
                    sender=receivedMessage[1:senderIndex]
                    if sender not in blocklist:
                        if receivedMessage.startswith('~FS'):
                            get_file(receivedMessage)
                        else:
                            print(receivedMessage)
            except:
                exit()
        else:
            break

#for receiving file
def get_file(receivedMessage):
    global clientSocket, clientName
    
    file2=os.getcwd()+'/'+clientName+'/client'+str(time.time())+receivedMessage[3:]
    os.makedirs(os.path.dirname(file2),exist_ok=True)                            
    print(file2)
    print('Receiving File')
    byte='~FE'.encode()
    with open(file2,'wb') as fw:
        while True:
            data=clientSocket.recv(1024)
            #print(data)
            if data[-3:]==byte:
                fw.write(data[:-3])
                break
            else:
                fw.write(data)
            
        fw.close()
    print('Received File')

#for handling different messages
def send_messages():
    global clientSocket, _quit, clientName, time_sleep, sleep, blocklist
    
    clientDetails=""
    clientDetailsIndex=str(clientSocket).find('laddr=')
    for c in str(clientSocket)[clientDetailsIndex+6:]:
        clientDetails+=c
        clientDetailsIndex+=1
        if c==')':
            break

    clientSocket.send(('~~~&'+clientDetails+'&'+clientName).encode())   #for name mapping in server
   
    while not _quit:
        message=input()

        #quit
        if message=="\quit":
            _quit=True
            clientSocket.send(message.encode())
            clientSocket.close()

        #send file
        elif message=='\sendfile':
            clientSocket.send('~FS'.encode())
            file=input('Enter file path (with extension): ')
            while not os.path.isfile(file):
                file=input('Enter correct file path (with extension): ')
            clientSocket.send((Path(file).suffix+'&'+clientName).encode())
            
            with open(file,'rb') as fs:
                while True:
                    data = fs.read(1024)
                    if not data:
                        clientSocket.send('~FE'.encode())
                        break
                    else:
                        clientSocket.send(data)
                fs.close()
                print('sent all')
        
        #sleep
        elif message.startswith('\sleep'):
            m=message.split('\\')
            sleep=True
            time_sleep=int(m[2])
            print('Sleeping for '+str(time_sleep)+' seconds')
            
            time.sleep(time_sleep)
            sleep=False

        #change name 
        elif message.startswith('\\name'):
            m=message.split('\\')
            try:
                os.rename(clientName,m[2])
            except:
                pass
            clientName=m[2]
            name='newname'+'-'+m[2]            
            print(name)
            clientSocket.send(name.encode())

        #block
        elif message.startswith('\\block'):
            m=message.split('\\')
            if m[2] not in blocklist:
                blocklist.append(m[2])
                print('Blocklist:', blocklist)
            else:
                print(m[2] +' is already blocked')

        #unblock
        elif message.startswith('\\unblock'):
            m=message.split('\\')
            if m[2] in blocklist:
                blocklist.remove(m[2])
                print('Blocklist:',blocklist)
            else:
                print(m[2]+' not in blocklist')

        #send message
        else:
            clientSocket.send(message.encode())
            print("<You> "+message)            

    


#Global Variables
clientName, clientPort, serverIP, serverPort, host_ip, clientSocket= None, None, None, None, None, None
_quit=False
time_sleep=None
sleep=False
blocklist=[]
init()
t1=threading.Thread(target=receive_messages)
t1.start()
send_messages()
    
    
