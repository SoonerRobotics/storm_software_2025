#include "messages.hpp"
#include <boost/bind.hpp>
#include <boost/asio.hpp>
#include <iostream>

SerialUDP::SerialUDP(boost::asio::io_service& io_service, const std::string& port, const std::string& udp_host, unsigned short udp_port)
    : io_service(io_service),
      serial_port(io_service, port),
      udp_socket(io_service, boost::asio::ip::udp::endpoint(boost::asio::ip::udp::v4(), udp_port)),
      udp_endpoint(boost::asio::ip::address::from_string(udp_host), udp_port) {

    serial_port.set_option(boost::asio::serial_port_base::baud_rate(9600));
    serial_port.set_option(boost::asio::serial_port_base::character_size(8));
    serial_port.set_option(boost::asio::serial_port_base::stop_bits(boost::asio::serial_port_base::stop_bits::one));
    serial_port.set_option(boost::asio::serial_port_base::parity(boost::asio::serial_port_base::parity::none));

    udp_socket.open(boost::asio::ip::udp::v4());
}

void SerialUDP::start() {
    serial_to_udp = boost::thread(&SerialUDP::readSerial, this);
    udp_to_serial = boost::thread(&SerialUDP::readUDP, this);
}

void SerialUDP::readSerial() {
    while (true) {
        boost::asio::async_read(serial_port, serial_buffer, boost::asio::transfer_at_least(1),
            boost::bind(&SerialUDP::handleSerialRead, this, boost::asio::placeholders::error, boost::asio::placeholders::bytes_transferred));
        io_service.run();
    }
}

void SerialUDP::readUDP() {
    while (true) {
        udp_socket.async_receive_from(boost::asio::buffer(udp_buffer), udp_endpoint,
            boost::bind(&SerialUDP::handleUDPRead, this, boost::asio::placeholders::error, boost::asio::placeholders::bytes_transferred));
        io_service.run();
    }
}

void SerialUDP::handleSerialRead(const boost::system::error_code& error, size_t bytes_transferred) {
    if (!error) {
        std::istream is(&serial_buffer);
        std::string message;
        std::getline(is, message);
        sendUDP(message); 
    } else {
        std::cerr << "Error reading from serial port: " << error.message() << std::endl;
    }
}

void SerialUDP::handleUDPRead(const boost::system::error_code& error, size_t bytes_transferred) {
    if (!error) {
        std::string udp_data(udp_buffer.data(), bytes_transferred);
        std::istringstream is(udp_data);
        std::string message;
        std::getline(is, message);
        sendSerial(message);
    } else {
        std::cerr << "Error reading from UDP socket: " << error.message() << std::endl;
    }
}

void SerialUDP::sendSerial(const std::string& message) {
    boost::asio::async_write(serial_port, boost::asio::buffer(message),
        boost::bind(&SerialUDP::handleSerialWrite, this, boost::asio::placeholders::error, boost::asio::placeholders::bytes_transferred));
}

void SerialUDP::sendUDP(const std::string& message) {
    udp_socket.async_send_to(boost::asio::buffer(message), udp_endpoint,
        boost::bind(&SerialUDP::handleUDPWrite, this, boost::asio::placeholders::error, boost::asio::placeholders::bytes_transferred));
}

void SerialUDP::handleSerialWrite(const boost::system::error_code& error, size_t bytes_transferred) {
    if (!error) {
        std::cout << "Data successfully sent over serial. Bytes transferred: " << bytes_transferred << std::endl;
    }
    else {
        std::cerr << "Error writing to serial port: " << error.message() << std::endl;
    }
}

void SerialUDP::handleUDPWrite(const boost::system::error_code& error, size_t bytes_transferred) {
    if (!error) {
        std::cout << "Data successfully sent over UDP. Bytes transferred: " << bytes_transferred << std::endl;
    } 
    else {
        std::cerr << "Error sending data over UDP: " << error.message() << std::endl;
    }
}