from socket import *
import threading
import random
from datetime import *
import re
import time
import pickle

peer_List = {};

server_port = 65423;

cookie_range = list(range(7000, 9000));

def peerClientHandler(peer_Socket, addr):
	response_msg = peer_Socket.recv(1024);
	protocol_msg = response_msg.decode('utf-8');
	print(protocol_msg);
	print("request received");
	if protocol_msg.split('\r\n')[0].split(' ')[1] == "Register":
		peerList_ADD(peer_Socket, protocol_msg);
		print("added to peer list");
	elif protocol_msg.split('\r\n')[0].split(' ')[1] == "PQuery":
		peerList_SHOW(peer_Socket, protocol_msg);
		print("active peer list shared");
	elif protocol_msg.split('\r\n')[0].split(' ')[1] == "KeepAlive":
		peer_KeepAlive(peer_Socket, protocol_msg);
		print("updated peer TTL value");
	elif protocol_msg.split('\r\n')[0].split(' ')[1] == "Leave":
		peer_Leave(peer_Socket, protocol_msg);
	peer_Socket.close();


def peerList_ADD(peer_Socket, peer_msg):
    global peer_List;
    cookie = random.choice(cookie_range);
    cookie_range.remove(cookie);
    for line in peer_msg.split('\r\n'):
        if re.search(r'^Host: ', line):
            peer_hostname = line.split(': ')[1];
        elif re.search(r'^Port: ', line):
            peer_port = int(line.split(': ')[1]);
    reg_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S");
    # reg_time = datetime.now();
    active_count = 1;
    active = True;
    peer_TTL = 7200;
    peer = [];
    peer.extend([peer_hostname, int(peer_port), active, active_count, peer_TTL, reg_time]);
    peer_List[cookie] = peer;
    peer_Socket.send("P2P-DI/1.0 200 RegOK\r\nCookie: {0}".format(cookie).encode('utf-8'));
    peer_TTL_thread = threading.Thread(target=peer_TTL_counter, args=[cookie]);
    peer_TTL_thread.start();
    # for i in range(10):
    print(peer_List);
    #     time.sleep(1);


def peerList_SHOW(peer_Socket, peer_msg):
	global peer_List;
	print peer_List;
	for line in peer_msg.split('\r\n'):
		print(line);
		if re.search(r'^RSCookie: ', line):
			peer_cookie = int(line.split(': ')[1]);
			active_peerList = [];
			for cookie in peer_List:
				if (peer_List[cookie][2] is True) and (cookie != peer_cookie):
					peerDetails = [peer_List[cookie][0], peer_List[cookie][1]];
					active_peerList.append(peerDetails);
	if len(active_peerList) == 0:
		peer_Socket.send("P2P-DI/1.0 404 NoActivePeerFound\r\nRSCookie: {0}".format(peer_cookie).encode('utf-8'));
	else:
		peer_Socket.send("P2P-DI/1.0 300 PeerQueryOK\r\nRSCookie: {0}".format(peer_cookie).encode('utf-8'));
		msg = pickle.dumps(active_peerList);
		peer_Socket.send(msg);


def peer_TTL_counter(cookie):
    global peer_List;
    while peer_List[cookie][4] > 0:
        peer_List[cookie][4] -= 1;
        time.sleep(1);
    if peer_List[cookie][4] == 0:
        peer_List[cookie][2] = False;


def peer_KeepAlive(peer_Socket, peer_msg):
	global peer_List;
	for line in peer_msg.split('\r\n'):
		if re.search(r'^RSCookie: ', line):
			peer_cookie = int(line.split(': ')[1]);
	if not peer_List[peer_cookie][2]:
		peer_update_record(peer_cookie);
	print(peer_List[peer_cookie]);
	peer_List[peer_cookie][4] = 7200;
	print(peer_List[peer_cookie]);
	peer_Socket.send("P2P-DI/1.0 400 KeepAliveOK\r\nCookie: {0}".format(peer_cookie).encode('utf-8'));

def peer_update_record(peer_cookie):
    global peer_List;
    peer_List[peer_cookie][2] = True;
    reg_time = datetime.strptime(peer_List[peer_cookie][5], "%d/%m/%Y %H:%M:%S").date();
    if (reg_time - date.today()).days < 30:
        peer_List[peer_cookie][3] += 1;
    else:
        peer_List[peer_cookie][3] = 1;
    peer_List[peer_cookie][5] = datetime.now().strftime("%d/%m/%Y %H:%M:%S");


def peer_Leave(peer_Socket, peer_msg):
    global peer_List;
    for line in peer_msg.split('\r\n'):
        if re.search(r'^RSCookie: ', line):
            peer_cookie = int(line.split(': ')[1]);
    print(peer_List[peer_cookie]);
    peer_List[peer_cookie][2] = False;
    print(peer_List[peer_cookie]);
    peer_Socket.send("P2P-DI/1.0 550 LeaveOK\r\nCookie: {0}".format(peer_cookie).encode('utf-8'));


def main():
    server_socket = socket(AF_INET, SOCK_STREAM);
    try:
        server_socket.bind(('', server_port));
    except error:
        print('Bind was unsuccessful.');
    print('The server is ready to receive');
    try:
        while True:
            server_socket.listen(6);
            peer_Socket, addr = server_socket.accept();
            RS_server_thread = threading.Thread(target=peerClientHandler, args=(peer_Socket, addr));
            RS_server_thread.start();
        # server_socket.close();
    except KeyboardInterrupt:
        print('Socket connection was unsuccessful.');
        server_socket.close();
    print(peer_List);


if __name__ == '__main__':
    main();
















# class peerList_node:
#     def __init__(self, peer_host, cookie, active, peer_port, active_no, reg_time):
#         self.peer_host = peer_host;
#         self.cookie = cookie;
#         self.active = active;
#         self.peer_port = peer_port;
#         self.active_no = active_no;
#         self.reg_time = reg_time;

# class peerList:
#     def __init__(self):
#         self.head = None;
#         self.tail = None;
#         return;

# print(sentence.decode('utf-8'));
# capitalizedSentence = sentence.upper();
# connectionSocket.send(capitalizedSentence);
# print("Server has sent the sentence to the client");
# connectionSocket.close();