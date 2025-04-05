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

	SerialUDP serial_udp = SerialUDP(io_service, "/dev/ttyUSB0", "0.0.0.0", 5001);
	VideoStream video_stream = VideoStream(io_service, "192.168.1.69", 5000);

	boost::thread serial_udp_thread([&]() {
		serial_udp.start();
	});

	boost::thread video_stream_thread([&]() {
		video_stream.start();
	});	

	serial_udp_thread.join();
	video_stream_thread.join();
	
  }
  catch (const std::exception& e) {
	std::cerr << "Error: " << e.what() << std::endl;
  }

  return 0;

}
