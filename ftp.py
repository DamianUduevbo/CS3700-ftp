import socket
import re as regex
import urllib.parse
import argparse

'''
parser = argparse.ArgumentParser()
parser.add_argument('operation')
parser.add_argument('param1')
parser.add_argument('param2')
args = parser.parse_args()
'''

socket.setdefaulttimeout(10)
control_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

modes = {
    'binaryMode': "TYPE I\r\n",
    'streamMode': "MODE S\r\n",
    'struMode': 'STRU F\r\n',
}

pasv = "PASV\r\n"
port = 21
host = 'ftp.3700.network'
server = (host, port)
BUFFER_SIZE = 4096

fs = open("toServer.txt", "rb")
a = fs.read()
print(a)

class FTPProject:
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password

        self.user = "USER %s\r\n" % username
        self.pwd = "PASS %s\r\n" % password
        self.regexPASV = ''
        self.regexAddress = ''
        self.regexPort = ''

        
        # self.file = fs.read(1024)

        print(self.user, self.pwd)
    
    def login(self):
        control_connection.connect(server)
        res = control_connection.recv(BUFFER_SIZE)
        print('RES:', res)
        control_connection.sendall(self.user.encode())
        control_connection.recv(BUFFER_SIZE)
        control_connection.sendall(self.pwd.encode())

        answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')
        print(answer)

        if "230" in answer:
            print("Connected")
        elif "530" in answer:
            data_channel.close()
            quit()

    def togglePassiveMode(self):
        control_connection.sendall(pasv.encode())
        answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')

        print('REGEX ANSWER:', answer)
        self.regexPASV = regex.findall("[^\d](\d+)", answer)
        self.regexAddress = '.'.join(self.regexPASV[:4])
        self.regexPort = (int(self.regexPASV[4]) << 8) + int(self.regexPASV[5])
        print('PASV Mode', (self.regexAddress, self.regexPort))
    
    def dataMode(self, mode):
        control_connection.sendall(modes[mode].encode())
        answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')
        print('%s activated:' % mode, answer)

    # COMMANDS

    # works
    def listDir(self, path_dir='/'):
        listDir = "LIST %s\r\n" % path_dir # % (self.username, self.password)
        control_connection.sendall(listDir.encode())
        answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')

        data_channel.sendall(listDir.encode())
        res = data_channel.recv(BUFFER_SIZE).decode()
        print(res)

        data_channel.close()
        print(answer)
    
    # works
    def deleteFile(self, file_path):
        dele = "DELE %s\r\n" % file_path # % (self.username, self.password)
        
        try:
            control_connection.sendall(dele.encode())
            answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')
        except:
            print(f'Unable to delete file at {file_path}')

        data_channel.close()
        print(answer)

    # works
    def deleteDir(self, directory_path):
        mkDIR = "RMD %s\r\n" % directory_path # % (self.username, self.password)

        try:
            control_connection.sendall(mkDIR.encode())
            answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')
        except:
            print(f'Unable to delete directory at {directory_path}')

        data_channel.close()
        print(answer)

    # works
    def makeDir(self, path_dir='/my_stuff/homeworks-v5'):
        mkDIR = "MKD %s\r\n" % (path_dir)

        try:
            control_connection.sendall(mkDIR.encode())
            answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')
        except:
            print(f'Unable to create directory at {path_dir}')
        
        data_channel.close()
        print(answer)

    """
    # works - not needed
    def makeFile(self, file_path: str):
        mkDIR = "STOR %s\r\n" % (file_path)
        control_connection.sendall(mkDIR.encode())
        answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')
        data_channel.close()
        print(answer)

        if '553' in answer:
            print('Could not create directory created')
    """

    # works
    def uploadFile(self, server_filepath = None, local_filepath = None):
        control_connection.send(("STOR %s\r\n" % server_filepath).encode())

        try:
            file = open(local_filepath, "rb")
            data = file.read()
            data_channel.sendall(data)
            file.close()
        except:
            print(f'Error writing to {local_filepath}')
        
        data_channel.close()

    # works
    def downloadFile(self, server_path : str, local_path : str):
        download = "RETR %s\r\n" % server_path # % (self.username, self.password)
        control_connection.sendall(download.encode())
        answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')

        if '550' in answer:
            print('File not found on server')
            data_channel.close()
            control_connection.close()
            quit()
        
        try:
            data_channel.sendall(download.encode())
            res = data_channel.recv(BUFFER_SIZE)
            print('RES:', res)
            file = open(local_path, "wb")
            file.write(res)
            file.close()
        except:
            print(f'Error writing to {local_path}')
        
        data_channel.close()
        

######### DO THIS FOR EVERY RUN VVV #####################
ftp3700 = FTPProject("uduevbod", "eDWI6JoLwnrNqjfV8yAs")
ftp3700.login()
ftp3700.togglePassiveMode()
ftp3700.dataMode('struMode')
ftp3700.dataMode('streamMode')

print('Connecting to data channel...')
data_channel.connect((ftp3700.regexAddress, ftp3700.regexPort))
print('Connected to data channel')
#########################################################

'''

# ls, mkdir, rm, rmdir, cp, and mv
operation = args.operation

if operation == 'ls':
    ftp3700.listDir()
elif operation == 'mkdir':
    ftp3700.makeDir()
elif operation == 'rm':
    ftp3700.deleteFile()
elif operation == 'rmdir':
    ftp3700.deleteDir()
elif operation == 'cp':
    'Copy from dest1 tp dest2'
elif operation == 'mv':
    ftp3700.makeDir()
    'Moves dile from dest1 to dest2'
    'copy paste to dest2'
    'delete from dest'
else:
    print('Error invalid operation')

'''

ftp3700.uploadFile('/toServer2.txt', 'fakeFile.txt')
data_channel.close()

