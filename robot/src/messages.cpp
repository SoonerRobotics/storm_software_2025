#include "messages.hpp"
#include "messages.pb.h"
#include <boost/bind.hpp>
#include <boost/asio.hpp>
#include <iostream>
#include <google/protobuf/message.h>

SerialUDP::SerialUDP(boost::asio::io_service& io_service, const std::string& port, const std::string& udp_host, unsigned short udp_port)
    : io_service(io_service),
      serial_port(io_service, port),
      udp_socket(io_service, boost::asio::ip::udp::endpoint(boost::asio::ip::udp::v4(), udp_port)),
      udp_endpoint(boost::asio::ip::address::from_string(udp_host), udp_port),
      stop_threads(false) {

    serial_port.set_option(boost::asio::serial_port_base::baud_rate(115200));
    serial_port.set_option(boost::asio::serial_port_base::character_size(8));
    serial_port.set_option(boost::asio::serial_port_base::stop_bits(boost::asio::serial_port_base::stop_bits::one));
    serial_port.set_option(boost::asio::serial_port_base::parity(boost::asio::serial_port_base::parity::none));
    
}

void SerialUDP::start() {
    readSerial();
    readUDP();
    io_service.run();
}

void SerialUDP::readSerial() {
    boost::asio::async_read(serial_port, serial_buffer, boost::asio::transfer_at_least(1),
        boost::bind(&SerialUDP::handleSerialRead, this, boost::asio::placeholders::error, boost::asio::placeholders::bytes_transferred));
}

void SerialUDP::readUDP() {
    udp_socket.async_receive_from(boost::asio::buffer(udp_buffer), udp_endpoint,
        boost::bind(&SerialUDP::handleUDPRead, this, boost::asio::placeholders::error, boost::asio::placeholders::bytes_transferred));
}


void SerialUDP::handleSerialRead(const boost::system::error_code& error, size_t bytes_transferred) {
    if (!error) {
        std::istream is(&serial_buffer);
        std::string message;
        std::getline(is, message);
        sendUDP(message); 
    } 
    else {
        std::cerr << "Error reading from serial port: " << error.message() << std::endl;
    }
    readSerial();
}

void SerialUDP::handleUDPRead(const boost::system::error_code& error, size_t bytes_transferred) {
    if (!error) {
        std::string udp_data(udp_buffer.data(), bytes_transferred);

        myproto::Wrapper wrapper;

        if (wrapper.ParseFromString(udp_data)) {
            // std::cout << "Received message of type: " << wrapper.type() << std::endl;

            switch (wrapper.type()) {
                case myproto::MOTOR_COMMAND: {
                    std::vector<uint8_t> packet;
                    packet.push_back(1);
                    uint8_t buffer[sizeof(float)];
                    float right_motor_speed = wrapper.motor_command().right_motor_speed();
                    std::memcpy(buffer, &right_motor_speed, sizeof(float));
                    packet.insert(packet.end(), buffer, buffer + sizeof(float));
                    float left_motor_speed = wrapper.motor_command().left_motor_speed();
                    std::memcpy(buffer, &left_motor_speed, sizeof(float));
                    packet.insert(packet.end(), buffer, buffer + sizeof(float));
                    sendSerial(std::string(packet.begin(), packet.end()));
                    break;
                }
                case myproto::ARM_COMMAND: {
                    std::vector<uint8_t> packet;
                    packet.push_back(2);
                    uint8_t buffer[sizeof(float)];
                    float back_servo_angle = wrapper.arm_command().x_dir();
                    std::memcpy(buffer, &back_servo_angle, sizeof(float));
                    packet.insert(packet.end(), buffer, buffer + sizeof(float));
                    float front_servo_angle = wrapper.arm_command().y_dir();
                    std::memcpy(buffer, &front_servo_angle, sizeof(float));
                    packet.insert(packet.end(), buffer, buffer + sizeof(float));
                    sendSerial(std::string(packet.begin(), packet.end()));
                    break;
                }
                case myproto::INTAKE_COMMAND: {
                    std::vector<uint8_t> packet;
                    packet.push_back(3);
                    uint8_t buffer[sizeof(float)];
                    float intake_speed = wrapper.intake_command().speed();
                    std::memcpy(buffer, &intake_speed, sizeof(float));
                    packet.insert(packet.end(), buffer, buffer + sizeof(float));
                    float pad = 0.0;
                    std::memcpy(buffer, &pad, sizeof(float));
                    packet.insert(packet.end(), buffer, buffer + sizeof(float));
                    sendSerial(std::string(packet.begin(), packet.end()));
                    break;
                }
                case myproto::ACTUATOR_COMMAND: {
                    std::vector<uint8_t> packet;
                    packet.push_back(4);
                    uint8_t buffer[sizeof(float)];
                    float actuator = static_cast<float>(wrapper.actuator_command().id());
                    std::memcpy(buffer, &actuator, sizeof(float));
                    packet.insert(packet.end(), buffer, buffer + sizeof(float));
                    float pad = 0.0;
                    std::memcpy(buffer, &pad, sizeof(float));
                    packet.insert(packet.end(), buffer, buffer + sizeof(float));
                    sendSerial(std::string(packet.begin(), packet.end()));
                    break;
                }
                default:
                    std::cerr << "Error: Unknown message type" << std::endl;
                    break;
            }
        } 
        else {
            std::cerr << "Error: Couldn't parse Wrapper message from UDP" << std::endl;
        }
    } 
    else {
        std::cerr << "Error reading from UDP: " << error.message() << std::endl;
    }

    readUDP();
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
        // std::cout << "Data successfully sent over serial. Bytes transferred: " << bytes_transferred << std::endl;
    }
    else {
        std::cerr << "Error writing to serial port: " << error.message() << std::endl;
    }
}

void SerialUDP::handleUDPWrite(const boost::system::error_code& error, size_t bytes_transferred) {
    if (!error) {
        // std::cout << "Data successfully sent over UDP. Bytes transferred: " << bytes_transferred << std::endl;
    } 
    else {
        std::cerr << "Error sending data over UDP: " << error.message() << std::endl;
    }
}