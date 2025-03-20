#include "video.hpp"
#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>

VideoStream::VideoStream(boost::asio::io_service& io_service, const std::string& host, unsigned short port)
    : io_service(io_service),
      socket(io_service, boost::asio::ip::udp::endpoint(boost::asio::ip::udp::v4(), 0)),
      udp_endpoint(boost::asio::ip::address::from_string(host), port) {}

void VideoStream::start() {

    cv::VideoCapture cap(0); 
    if (!cap.isOpened()) {
        std::cerr << "Error: Couldn't open video capture!" << std::endl;
        return;
    }

    while (true) {
        cv::Mat frame;
        cap >> frame; 
        if (frame.empty()) {
            std::cerr << "Error: Empty frame!" << std::endl;
            break;
        }

        std::vector<uchar> frame_data;
        cv::imencode(".jpg", frame, frame_data); 

        boost::asio::const_buffer buffer(frame_data.data(), frame_data.size());
        
        try {
            socket.send_to(buffer, udp_endpoint);
        }
        catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << std::endl;
        }

    }

    cap.release();
    
}


