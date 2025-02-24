#include <ctime>
#include <thread>
#include <bits/stdc++.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h>

using namespace std;

void messages() {
 
}

void serial() {

}

void network(int sock) {

}

int main() {

  int sock;
  struct sockaddr_in servaddr, cliaddr;

  if ((sock=socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
		perror("Socket creation failed.");
		exit(EXIT_FAILURE);
	}
	memset(&servaddr, 0, sizeof(servaddr));
	memset(&cliaddr, 0, sizeof(cliaddr));

	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = INADDR_ANY;
	servaddr.sin_port = htons(8080); 

	if (bind(sock, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
		perror("Bind failed.");
		exit(EXIT_FAILURE);
	}

	socklen_t len;
	int n;
	len = sizeof(cliaddr);

  std::thread network_thread(network, sock);
  std::thread serial_thread();
  std::thread messages_thread();
  
  network_thread.join();
  serial_thread.join();
  messages_thread.join();

  return 0;

}
