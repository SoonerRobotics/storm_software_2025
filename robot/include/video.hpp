#ifndef VIDEOSTREAM_HPP
#define VIDEOSTREAM_HPP

#include <boost/asio.hpp>
#include <opencv2/opencv.hpp>
#include <string>

#define VIDEO_PORT 5001
#define VIDEO_HOST "127.0.0.1"

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

#endif // VIDEOSTREAM_HPP

