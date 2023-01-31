import socket
import re as regex
import urllib.parse

user = "USER %s\r\n" % "uduevbod"
pwd = "PASS %s\r\n" % "eDWI6JoLwnrNqjfV8yAs"
pasv = "PASV\r\n"

modes = {
    'binaryMode': "TYPE I\r\n",
    'streamMode': "MODE S\r\n",
    'struMode': 'STRU F\r\n',
}

socket.setdefaulttimeout(10)
control_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 21
host = 'ftp.3700.network'
server = (host, port)
BUFFER_SIZE = 4096

############ LOGGING IN ##################################
control_connection.connect(server)
res = control_connection.recv(BUFFER_SIZE)
print('RES:', res)
control_connection.sendall(user.encode())
control_connection.recv(BUFFER_SIZE)
control_connection.sendall(pwd.encode())

answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')
print(answer)

if "230" in answer:
    print("Connected")
elif "530" in answer:
    data_channel.close()
    quit()
##########################################################

regexAddress = ''
regexPort = 0

def enterPasvMode():
    ############## PASV ########################
    # control_connection.recv(BUFFER_SIZE)
    control_connection.sendall(pasv.encode())
    answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')

    regexPASV = regex.findall("[^\d](\d+)", answer)
    regexAddress = '.'.join(regexPASV[:4])
    regexPort = (int(regexPASV[4]) << 8) + int(regexPASV[5])


    print('PASV Mode', (regexAddress, regexPort))
    ############################################

enterPasvMode()

# control_connection.recv(BUFFER_SIZE)
control_connection.sendall(modes["struMode"].encode())
answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')
print('STRU activated:', answer)

print('Connecting to data channel...')
data_channel.connect((regexAddress, regexPort))
print('Connected to data channel')

"""
data_channel.recv(BUFFER_SIZE)
data_channel.sendall(modes["struMode"].encode())
answer = data_channel.recv(BUFFER_SIZE).decode('utf-8')
print(answer)
"""

############ LIST DIR ##############################
listDir = "LIST ftp://%s:%s@ftp.3700.network/my_stuff\r\n" % (user, pwd)
control_connection.sendall(listDir.encode())
answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')
data_channel.close()
print(answer)
####################################################

"""
welcome = data_channel.recv(BUFFER_SIZE)
print('Listing...', welcome)
data_channel.sendall(listDir.encode())
answer = data_channel.recv(BUFFER_SIZE).decode('utf-8')
print(answer)
"""

enterPasvMode()
data_channel.connect((regexAddress, regexPort))
############ MAKE DIR ##############################
mkDIR = "MKD ftp://%s:%s@ftp.3700.network/my_stuff\r\n" % (user, pwd)
control_connection.sendall(mkDIR.encode())
answer = control_connection.recv(BUFFER_SIZE).decode('utf-8')
print(answer)
####################################################

data_channel.close()
control_connection.close()
quit()
