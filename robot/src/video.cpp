#include "video.hpp"
#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>

VideoStream::VideoStream(boost::asio::io_service& io_service, const std::string& host, unsigned short port, int camera_index)
    : io_service(io_service),
      socket(io_service, boost::asio::ip::udp::endpoint(boost::asio::ip::udp::v4(), 0)),
      udp_endpoint(boost::asio::ip::address::from_string(host), port),
      camera_index(camera_index) {} 

void VideoStream::start() {

    cv::VideoCapture cap(camera_index);
    if (!cap.isOpened()) {
        std::cerr << "Error: Couldn't open video capture!" << std::endl;
        return;
    }
    
    double width = 320;
    double height = 240;
    cap.set(cv::CAP_PROP_FRAME_WIDTH, width);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, height);

    int frame_skip = 2;
    int frame_count = 0;

    while (true) {
        cv::Mat frame;
        cap >> frame; 
        if (frame.empty()) {
            std::cerr << "Error: Empty frame!" << std::endl;
            break;
        }

        frame_count++;
        if (frame_count % frame_skip != 0) {
            continue; 
        }

        std::vector<uchar> frame_data;
        std::vector<int> params = {cv::IMWRITE_JPEG_QUALITY, 40};
        cv::imencode(".jpg", frame, frame_data, params);
        frame_data.resize(frame_data.size(), 0);
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
