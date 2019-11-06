from socket import *
import socket
import sys
import threading
import pickle
import re
import os
import time

ssocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port1 = 65402
ssocket.bind(('',port1))

csocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

RFCserver_name = socket.gethostbyname(socket.gethostname());
peer_active = False;
RS_cookie = None;
RS_port = 65423
RFCserver_port = port1
RS_name = socket.gethostbyname(socket.gethostname());
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((RS_name, RS_port));
choice = '';
activePeer_list = [];
RFC_index=[]
oldRFC_index=[]


def load_RFCindex_list():
	global RFC_index
	global oldRFC_index
	path ='RFC_files/'
	
	if not os.path.exists(path):
		os.makedirs(path);
	else:
		file_count = 0;
		for name in os.listdir(path):
			if os.path.isfile(os.path.join(path, name)):
				file_count += 1;
		if file_count != 0:
			for name in os.listdir(path):
				if os.path.isfile(os.path.join(path, name)):
					x = re.search(r'\d+', name);
					RFC_num = int(x.group());
					RFC_Titlename = name;
					RFC_hostname = socket.gethostbyname(socket.gethostname())
					RFC_TTL = 7200;
					RFC_detail = [RFC_num, RFC_Titlename, RFC_hostname, RFC_TTL];
					RFC_index.append(RFC_detail);
					oldRFC_index.append(RFC_detail);
	

def load_oldRFCindex_list():
	global RFC_index
	global oldRFC_index
	path ='RFC_files/'
	
	if not os.path.exists(path):
		os.makedirs(path);
	else:
		file_count = 0;
		for name in os.listdir(path):
			if os.path.isfile(os.path.join(path, name)):
				file_count += 1;
		if file_count != 0:
			for name in os.listdir(path):
				if os.path.isfile(os.path.join(path, name)):
					x = re.search(r'\d+', name);
					RFC_num = int(x.group());
					RFC_Titlename = name;
					RFC_hostname = socket.gethostbyname(socket.gethostname())
					RFC_TTL = 7200;
					RFC_detail = [RFC_num, RFC_Titlename, RFC_hostname, RFC_TTL];
					oldRFC_index.append(RFC_detail);
					
def serverside():
	global RFC_index;
	global ssocket;
	print "\nserver socket bound to", port1
	ssocket.listen(5)
	print "\nserver is listening...\n"
	#cone=0
	while True:
		csocket, addr = ssocket.accept()
		print "Got connection from: ", addr
		loopthread=threading.Thread(target=servingsubthread, args=(csocket, addr))
		loopthread.daemon=True
		loopthread.start()
		#servingsubthread(csocket,addr)
		#csocket.close()
		
def servingsubthread(csocket,addr):
	global RFC_index;
	global ssocket;
	#print "enteredsubthread"
	message=csocket.recv(23).decode('utf-8')
	print message
	if message.split(' ')[1]=="RFCqry":
		RFCquery_response(csocket,addr)
	elif message.split(' ')[1]=="GetRFC":
		#print message
		GetRFC_response(csocket,addr)
	
def RFCquery_response(csocket,addr):
	global RFC_index;
	global ssocket;
	msg = pickle.dumps(RFC_index)
	message="P2P-DI/1.0 100 RFCqry OK"
	csocket.send(message)
	csocket.send(msg)
	csocket.close()
	
def GetRFC_response(csocket,addr):
	print "EnterGetRFCresponse"
	global RFC_index;
	global ssocket;
	reqRFC=csocket.recv(1024).decode('utf-8')
	print reqRFC
	message= "P2P-DI/1.0 150 GetRFC OK"
	path = 'RFC_files/'
	for name in os.listdir(path):
		if name==reqRFC:
			csocket.send(message)
			with open(os.path.join(path, reqRFC), 'rb') as f:
				while True:
					line=f.read(2048)
					csocket.send(line.encode('utf-8'))
					if len(line)<2048:
						break
			break
	csocket.close()
	
############################################################################################
############################################################################################
############################################################################################	

def clientside():
	global csocket;
	global RFC_index;
	global RS_cookie;
	global peer_active;
	time.sleep(0.5)
	while True:
		inp=raw_input("Do you want to enter the P2P system?(y/n): ")
		if inp=="y":
			break
			
	peer_active = True;
	try:
		RS_cookie = pickle.load(open('RScookie.pkl', 'rb'));
	except IOError:
		pass;
	global activePeer_list;
	global clientSocket;
	#clientSocket.connect((RS_name, RS_port));
	#load_RFCindex_list();
	#print(len(RFC_index));
	if RS_cookie == None:
		message = "POST Register P2P-DI/1.0\r\nHost: {0}\r\nPort: {1}".format(RFCserver_name, RFCserver_port);
		clientSocket.send(message.encode('utf-8'));
		resp = clientSocket.recv(1024).decode('utf-8');
		for line in resp.split('\r\n'):
			if re.search(r'^Cookie: ', line):
				cookie = int(line.split(': ')[1]);
				print(cookie);
				pickle.dump(cookie, open('RScookie.pkl', 'wb'));
				RS_cookie = pickle.load(open('RScookie.pkl', 'rb'));
		clientSocket.close();
		""""RFC_server_thread = threading.Thread(target=RFCserver_handler);
		RFC_server_thread.daemon = True;
		RFC_server_thread.start();"""
		RS_keepalive_thread = threading.Thread(target=KeepAliveHandler);
		RS_keepalive_thread.daemon = True;
		RS_keepalive_thread.start();
	else:
		"""RFC_server_thread = threading.Thread(target=RFCserver_handler);
		RFC_server_thread.daemon = True;
		RFC_server_thread.start();"""
		RS_keepalive_thread = threading.Thread(target=KeepAliveHandler);
		RS_keepalive_thread.daemon = True;
		RS_keepalive_thread.start();
	
	
	
	
	while True:
		print('Welcome!!!\nPlease enter your choice among the following\n');
		print('1. Download a specific RFC file\n2. Leave the server\n3. Display RFC index\n4.Download any one RFC from the other peer\n');
		choice = input();
		if choice == 1:
			message = "GET PQuery P2P-DI/1.0\r\nRSCookie: {0}".format(RS_cookie);
			clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			clientSocket.connect((RS_name, RS_port));
			clientSocket.send(message.encode('utf-8'));
			resp1 = clientSocket.recv(1024).decode('utf-8');
			print(resp1);
			if resp1.split('\r\n')[0].split(' ')[2] == "NoActivePeerFound":
				print("No active peers available");
				clientSocket.close();
			else:
				resp2 = clientSocket.recv(1024);
				activePeer_list = pickle.loads(resp2);
				print(resp1+'\n');
				print(activePeer_list);
				clientSocket.close();
				
				reqRFC = raw_input("Enter the required RFC (for eg: rfc4234.txt) : ")
				#activePeer_list=[[socket.gethostbyname(socket.gethostname()),65403]]
				hostname=0
				query=0
				for peer in activePeer_list:
					recvdRFCindex= RFCqry(peer)
					#print "\nreceicd: ", recvdRFCindex
					merge_RFCindex(recvdRFCindex)
					#print "\nmerged: ", RFC_index
					hostname = searchRFCindex(reqRFC)
					print hostname
					if hostname!=0:
						print "host is present"
						GetRFC(hostname,reqRFC,activePeer_list)
						load_oldRFCindex_list()
						#print oldRFC_index, "%%%%%%%%%"
						query=1
					elif hostname==0:
						print "\n\nEntered RFC not in the RFC Index. Please Enter a different RFC value \n\n"
					if query!=0:
						print "\nSucess!!!! RFC downloaded."
						break

             		
		elif choice==2:
			print "\nEntered choice 2\n"
			message = "PUT Leave P2P-DI/1.0\r\nRSCookie: {0}".format(RS_cookie);
			#lock = threading.Lock();
			#lock.acquire();
			peer_active = False;
			#lock.release();
			clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			clientSocket.connect((RS_name, RS_port));
			clientSocket.send(message.encode('utf-8'));
			resp = clientSocket.recv(1024).decode('utf-8');
			print(resp);
			clientSocket.close();
			break;
		
		elif choice==3:
			for rec in RFC_index:
				print "\n", rec, "\n"
				
		elif choice==4:
			message = "GET PQuery P2P-DI/1.0\r\nRSCookie: {0}".format(RS_cookie);
			clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			clientSocket.connect((RS_name, RS_port));
			clientSocket.send(message.encode('utf-8'));
			resp1 = clientSocket.recv(1024).decode('utf-8');
			print(resp1);
			if resp1.split('\r\n')[0].split(' ')[2] == "NoActivePeerFound":
				print("No active peers available");
				clientSocket.close();
			else:
				resp2 = clientSocket.recv(1024);
				activePeer_list = pickle.loads(resp2);
				print(resp1+'\n');
				print(activePeer_list);
				clientSocket.close();
				
				#reqRFC = raw_input("Enter the required RFC (for eg: rfc4234.txt) : ")
				#activePeer_list=[[socket.gethostbyname(socket.gethostname()),65403]]
				hostname=0
				query=0
				for peer in activePeer_list:
					recvdRFCindex= RFCqry(peer)
					#print "\nreceicd: ", recvdRFCindex
					reqRFC=recvdRFCindex[0][1]
					merge_RFCindex(recvdRFCindex)
					#print "\nmerged: ", RFC_index
					hostname = searchRFCindex(reqRFC)
					print hostname
					if hostname!=0:
						print "host is present"
						GetRFC(hostname,reqRFC,activePeer_list)
						load_oldRFCindex_list()
						print oldRFC_index, "%%%%%%%%%"
						query=1
					if query!=0:
						print "\nSucess!!!! RFC", reqRFC, "downloaded.\n\n"
						break
			
				
	print("exiting...");
	sys.exit();		
	
	
	
			
def merge_RFCindex(arg):
	global csocket;
	global RFC_index;
	check=0
	for rfc in arg:
		for rec in RFC_index:
			if rfc[1]==rec[1]:
				check=1
		if check==0:		
			RFC_index.append(rfc)
		
			
def TTLfun():
	while True:
		global RFC_index
		global oldRFC_index
		for rfc in RFC_index:
			if rfc in oldRFC_index:
				rfc[3]=7200
			if rfc not in oldRFC_index:
				rfc[3]-=1
		time.sleep(1)
			
def RFCqry(peer):
	global csocket;
	global RFC_index;
	csocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	csocket.connect((peer[0],peer[1]))
	csocket.send("GET RFCqry P2P-DI/1.0\r\n".encode('utf-8'))
	message=csocket.recv(1024)
	print "\n", message
	temp=csocket.recv(10000)
	#print "\ntemp typw: ", type(temp)
	#print "\ntempl is: ", temp, "\ntempl ends here"
	recvdRFCindex = pickle.loads(temp)
	#print "\nreceived RFC_index : ", recvdRFCindex
	#print "\nexisting RFC_index: ", RFC_index
	csocket.close()
	return recvdRFCindex

def searchRFCindex(reqRFC):
	global csocket;
	global RFC_index;
	hostname=0
	for RFC_detail in RFC_index:
		if RFC_detail[1]==reqRFC:
			print "RFC found in RFC_index and available from ", RFC_detail[2]
			hostname=RFC_detail[2]
			break
	return hostname

def GetRFC(hostname,reqRFC,activePeer_list):
	gsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	global RFC_index;
	for peer in activePeer_list:
		print peer
		if peer[0]==hostname:
			print "serveport: ", peer[1]
			#connectport=peer[1]
			break
	gsocket.connect((peer[0],peer[1]))
	print "connected to RFC serving peer", peer[0]
	gsocket.send("GET GetRFC P2P-DI/1.0\r\n".encode('utf-8'))
	gsocket.send(reqRFC.encode('utf-8'))
	print gsocket.recv(1024)
	
	while True:
		file=gsocket.recv(2048).decode('utf-8')
		#print file, "\n"
		if file=="Not Available":
			print "Peer does not have the required RFC"
		else:
			path = 'RFC_files/'
			with open(os.path.join(path, reqRFC), "ab") as f:
				f.write(file)
		if len(file)<2048:
			break
	gsocket.close()
	
def KeepAliveHandler():
    print("Entering keep alive:...");
    global RS_cookie;
    global peer_active;
    while True:
        if not peer_active:
            break;
        RSclientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        RSclientSocket.connect((RS_name, RS_port));
        RSclientSocket.send("POST KeepAlive P2P-DI/1.0\r\nRSCookie: {0}".format(RS_cookie).encode('utf-8'));
        resp = RSclientSocket.recv(1024);
        print(resp.decode('utf-8'));
        RSclientSocket.close();
        time.sleep(200);

###############################################################################	

def main():
	global RFC_index
	load_RFCindex_list()
		
	serverthread=threading.Thread(target=serverside)
	serverthread.daemon=True
	serverthread.start()
	clientthread=threading.Thread(target=clientside)
	clientthread.daemon=True
	clientthread.start()	
	TTLthread=threading.Thread(target=TTLfun)
	TTLthread.daemon=True
	TTLthread.start()
	while True:
		qwe=1
	#clientside()
		
if __name__ == '__main__':
    main();