#include <Wire.h>

void setup()
{
  Serial.begin(115200);  
  Wire.setSDA(4);
  Wire.setSCL(5);
  Wire.begin(); // join i2c bus (optional)

}
int output = 0;

void loop()
{
  Wire.requestFrom(2, 1);   // the first byte
  while(Wire.available())
  { 
    unsigned char received = Wire.read();
    output = received;
  }
  
  for (int i = 0 ; i < 3 ; i++) // next 3 bytes
  {
     Wire.requestFrom(2, 1);   
     while(Wire.available())
     { 
        unsigned char received = Wire.read();
        output |= (received << 8);
     }
  }
  Serial.print(output);
  Serial.println("");

  delay(100);
}