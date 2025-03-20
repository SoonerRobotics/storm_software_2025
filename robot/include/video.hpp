#ifndef VIDEO_HPP
#define VIDEO_HPP

#include <boost/asio.hpp>
#include <opencv2/opencv.hpp>
#include <string>

class VideoStream {
public:
    VideoStream(boost::asio::io_service& io_service, const std::string& host, unsigned short port);
    void start();

private:
    boost::asio::io_service& io_service;
    boost::asio::ip::udp::socket socket;
    boost::asio::ip::udp::endpoint udp_endpoint;

    VideoStream(const VideoStream&) = delete;
    VideoStream& operator=(const VideoStream&) = delete;
};

#endif // VIDEO_HPP

