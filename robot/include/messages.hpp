#ifndef MESSAGES_HPP
#define MESSAGES_HPP

#include <boost/asio.hpp>
#include <boost/thread.hpp>
#include <boost/bind.hpp>
#include <string>
#include <google/protobuf/message.h>
#include "messages.pb.h"

class SerialUDP {
    public:
        SerialUDP(boost::asio::io_service& io_service, const std::string& port, const std::string& udp_host, unsigned short udp_port);
        void start();
        void stop();

    private:
        void readSerial();
        void readUDP();
        void sendSerial(const std::string& message);
        void sendUDP(const std::string& message);
        void handleSerialRead(const boost::system::error_code& erro, size_t bytes_transferred);
        void handleUDPRead(const boost::system::error_code& error, size_t bytes_transferred);
        void handleUDPWrite(const boost::system::error_code& error, size_t bytes_transferred);
        void handleSerialWrite(const boost::system::error_code& error, size_t bytes_transferred);

        boost::asio::io_service& io_service;
        boost::asio::serial_port serial_port;
        boost::asio::ip::udp::socket udp_socket;
        boost::asio::ip::udp::endpoint udp_endpoint;
        boost::asio::streambuf serial_buffer;
        std::array<char, 1024> udp_buffer;

        boost::thread serial_to_udp;
        boost::thread udp_to_serial;
        std::mutex mtx;
        std::atomic<bool> stop_threads;

        myproto::MotorCommand motor_command_;
        myproto::ArmCommand arm_command_;
        myproto::IntakeCommand intake_command_;
        myproto::ActuatorCommand actuator_command_;
    
};

#endif // MESSAGES_HPP

