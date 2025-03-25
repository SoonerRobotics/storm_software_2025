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

	// SerialUDP serial_udp = SerialUDP(io_service, "/dev/ttyACM0", "127.0.0.1", 5000);
	VideoStream video_stream = VideoStream(io_service, "127.0.0.1", 5001);

	/*
	boost::thread serial_udp_thread([&]() {
		serial_udp.start();
	});
	*/

	boost::thread video_stream_thread([&]() {
		video_stream.start();
	});

	io_service.run();

	// serial_udp_thread.join();
	video_stream_thread.join();
	
  }
  catch (const std::exception& e) {
	std::cerr << "Error: " << e.what() << std::endl;
  }

  return 0;

}
