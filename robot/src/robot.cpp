#include <boost/asio.hpp>
#include <boost/thread.hpp>
#include <iostream>
#include <stdexcept>
#include "video.hpp"
#include "messages.hpp"
#include "messages.pb.h"

using namespace std;

int main() {

  try {
	boost::asio::io_service io_service;

	std::cout << "Starting robot..." << std::endl;

	SerialUDP serial_udp = SerialUDP(io_service, "/dev/ttyS1", "127.0.0.1", 5001);
	// VideoStream video_stream = VideoStream(io_service, "127.0.0.1", 5001);

	serial_udp.start();

	/*
	boost::thread video_stream_thread([&]() {
		video_stream.start();
	});
	*/

	// video_stream_thread.join();
	
  }
  catch (const std::exception& e) {
	std::cerr << "Error: " << e.what() << std::endl;
  }

  return 0;

}
