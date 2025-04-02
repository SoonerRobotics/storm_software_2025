char buff[9];
float left_motor_speed;
float right_motor_speed;
float back_arm_angle;
float front_arm_angle;
float intake_speed;
uint8_t actuator_control;
uint8_t control_state;

void setup() {
    Serial.begin(115200);
    while (!Serial);
    Serial2.begin(115200);
    Serial.println("Ready to receive serial messages...");
}

void loop() {
  if (Serial2.available() >= 9) {

    Serial2.readBytes(buff, 9);
    memcpy(&control_state, &buff[0], sizeof(char));

    switch (control_state) {
      case 1:
        memcpy(&right_motor_speed, &buff[1], sizeof(float));
        memcpy(&left_motor_speed, &buff[5], sizeof(float));
        Serial.println("Received motor command: " + String(left_motor_speed) + ", " + String(right_motor_speed));
        break;
      case 2:
        memcpy(&back_arm_angle, &buff[1], sizeof(float));
        memcpy(&front_arm_angle, &buff[5], sizeof(float));
        Serial.println("Received arm command: " + String(back_arm_angle) + ", " + String(front_arm_angle));
        break;
      case 3:
        memcpy(&intake_speed, &buff[1], sizeof(float));
        Serial.println("Received intake command: " + String(intake_speed));
        break;
      case 4:
        memcpy(&actuator_control, &buff[1], sizeof(float));
        if (actuator_control == 1) {
          Serial.println("Received actuator command: On.");
        }
        else {
          Serial.println("Received actuator command: Off.");
        }
      default:
        Serial.println("Unknown command.");
    }
  }
}