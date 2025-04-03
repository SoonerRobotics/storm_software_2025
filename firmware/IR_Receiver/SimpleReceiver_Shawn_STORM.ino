#include <Arduino.h>
#define DECODE_NEC
#include <Wire.h>
#include <IRremote.hpp> 


void setup() {
    const int IR_RECEIVE_PIN1 = 15;
    Wire.setSDA(4);
    Wire.setSCL(5);
    Wire.begin(2);
    Wire.onRequest(requestInt);

    IrReceiver.begin(IR_RECEIVE_PIN1, ENABLE_LED_FEEDBACK);
}

int byteSending = 1;
int toTransfer = 5;
int Shift = toTransfer;
int mask = 0xFF;
unsigned char toSend = 0;


void loop() {
    if (IrReceiver.decode()) {
            IrReceiver.resume(); // Early enable receiving of the next IR frame
            Serial.println(IrReceiver.decodedIRData.command);
            toTransfer = IrReceiver.decodedIRData.command;
        }
}

void requestInt()
{
  if (byteSending == 1) //send packet 1
  {
    toSend = Shift & mask;
    Shift = Shift >> 8;
    Wire.write(toSend);
    byteSending = 2;
  }
  else if (byteSending == 2) //send packet 2
  {
    toSend = Shift & mask;
    Shift = Shift >> 8;
    Wire.write(toSend);
    byteSending = 3;
  }
  else if (byteSending == 3) //send packet 3
  {
    toSend = Shift & mask;
    Shift = Shift >> 8;
    Wire.write(toSend);
    byteSending = 4;
  }
  else if (byteSending == 4) //send packet 4
  {
    toSend = Shift & mask;
    Shift = Shift >> 8;
    Wire.write(toSend);
    byteSending = 1;
    //initialization for next turn
    Shift = toTransfer;
    mask = 0xFF;
    toSend = 0;
  }
}