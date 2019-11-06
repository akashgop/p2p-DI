# p2p-DI
Peer-to-Peer (P2P) file transfer using a Distributed Index (DI)


Points to note:
The code is written in python 2.7. Kindly use an interpreter or a compiler for python 2.7.
The Registration servers IP address is added in the peer’s code as the gethostbyname(gethostname) (This gives the IP address of the machine that is running the code). If the registration server is running in a different system, please change the value of “RFCserver_name” in the peer’s code.
The peer’s hostname is also valued as gethostbyname(gethostname). Ideally, the peer code takes its IP address from the host machine automatically.
PS: The code works best if the server and the peers run in the same system.
Please make sure the two peer’s code run in different folders to make sure they have separate RFC file directories.
Kindly run the Registration server code initially. Then run the peer’s codes.
Every time a peer registers for the first time, its cookie information is stored in a pickle file. The cookies are uniquely selected by the RS from the range of values from 7000-9000
In case the Registration server is closed. Please delete the cookie file in each peer’s directory (folder where the code is running from) and restart the peers.
Once you run the peer’s code, the system asks you if you want to enter the P2P system. Once this is answered as ‘Yes’, the peer registers with the RS server.
Following this, the peer allows the user to choose from one of the four options:
1. Download a specific RFC file: The user enters a specific RFC that he wants to download from the other peer. This entered RFC is downloaded if available in the RFC index, else it gives a message that it is not available. (Please enter the filename in the format “rfc7854.txt”)
2. Leave the server: This sends leave message to the Registration server and is marked as inactive.
3. Display RFC index: This displays the RFC index of the peer with the TTL field. (The TTL field is decremented for the records in the received RFC index)
4. Download any one RFC file: Downloads a random file from the other peer.
The request and response messages can be viewed when operations are done. Intermediate messages will also be printed on screen to keep track of the operations.
