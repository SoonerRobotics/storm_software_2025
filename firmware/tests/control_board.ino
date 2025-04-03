#include <Servo.h>
#include <Wire.h>

#define I2C_SDA 0
#define I2C_SCL 1
#define LED_B 3
#define LED_A 4
#define SERVO_ONE 6
#define LED_C 7
#define SERVO_TWO 10
#define SERVO_THREE 12
#define R_ENCA 13
#define R_ENCB 14
#define L_ENCA 15
#define L_ENCB 16
#define I_ENCA 17
#define LEFT_MOTOR 18
#define I_ENCB 19
#define RIGHT_MOTOR 20
#define INTAKE_MOTOR 21
#define ACTUATOR_THREE 26
#define ACTUATOR_ONE 27
#define ACTUATOR_TWO 28

Servo right_motor_;
Servo left_motor_;
Servo intake_motor_;
Servo back_servo_;
Servo front_servo_;

float back_servo_pos = 1389;
float front_servo_pos = 1389;

const float kp = 0.3;
const float ki = 0.1;
float integral = 0.0;
float right_current_speed;
float left_current_speed;
float right_motor_set;
float left_motor_set;
unsigned long previous_time;
unsigned long last_motor_message;

const float pulses_per_rotation = 1425.1;
const float circumference = 0.30159;
const float dt = 0.05;

bool debug = true;

void encoderISR() {

}

void setArm(float back_servo, float front_servo) {
  if (back_servo > 0.0) {
    back_servo_pos += 22;
    back_servo_pos = constrain(back_servo_pos, 1000, 1600);
  }
  else if (back_servo < 0.0){
    back_servo_pos -= 22;
    back_servo_pos = constrain(back_servo_pos, 1000, 1600);
  }
  else {
    // Do Nothing
  }
  if (front_servo > 0.0) {
    front_servo_pos += 22;
    front_servo_pos = constrain(front_servo_pos, 1000, 1600);
  }
  else if (front_servo < 0.0) {
    front_servo_pos -= 22;
    front_servo_pos = constrain(front_servo_pos, 1000, 1600);
  }
  else {
    // Do Nothing
  }

  if (debug) Serial.println("Back servo moving to: " + String(back_servo_pos));
  if (debug) Serial.println("Front servo moving to: " + String(front_servo_pos));
  back_servo_.writeMicroseconds(back_servo_pos);
  front_servo_.writeMicroseconds(front_servo_pos);

}

void setIntakeMotor(float speed) {
  intake_motor_.writeMicroseconds(map(speed, -1, 1, 500, 2500));
}

void setDrivetrainMotors(float left_speed, float right_speed) {
  right_motor_.writeMicroseconds(map(right_speed, -1, 1, 500, 2500));
  left_motor_.writeMicroseconds(map(left_speed, 1, -1, 500, 2500));
}

void setup() {

    Serial.begin(115200);
    // while (!Serial);
    Serial2.begin(115200);


    pinMode(RIGHT_MOTOR, OUTPUT);
    pinMode(R_ENCA, INPUT);
    pinMode(LEFT_MOTOR, OUTPUT);
    pinMode(L_ENCA, INPUT);
    pinMode(INTAKE_MOTOR, OUTPUT);
    pinMode(SERVO_THREE, OUTPUT);
    pinMode(SERVO_TWO, OUTPUT);
    pinMode(ACTUATOR_ONE, OUTPUT);

    right_motor_.attach(RIGHT_MOTOR);
    left_motor_.attach(LEFT_MOTOR);
    intake_motor_.attach(INTAKE_MOTOR);
    back_servo_.attach(SERVO_THREE);
    front_servo_.attach(SERVO_TWO);

    back_servo_.writeMicroseconds(back_servo_pos);
    front_servo_.writeMicroseconds(front_servo_pos);

    // attachInterrupt(digitalPinToInterrupt(R_ENA), encoderISR, CHANGE);
    // attachInterrupt(digitalPinToInterrupt(L_ENCA), encoderISR, CHANGE);
}

void loop() {

  char buff[9];
  float left_motor_speed;
  float right_motor_speed;
  float back_arm;
  float front_arm;
  float intake_speed;
  uint8_t actuator_control;
  uint8_t control_state;
  bool motor_set = false;
  
  unsigned long current_time = millis();
  float delta_time = (current_time - previous_time) / 1000.0;

  if (Serial2.available() >= 9) {

    Serial2.readBytes(buff, 9);
    memcpy(&control_state, &buff[0], sizeof(char));

    switch (control_state) {
      case 1:
        memcpy(&right_motor_speed, &buff[1], sizeof(float));
        memcpy(&left_motor_speed, &buff[5], sizeof(float));
        if (debug) Serial.println("Received motor command: " + String(left_motor_speed) + ", " + String(right_motor_speed));
        setDrivetrainMotors(left_motor_speed, right_motor_speed);
        last_motor_message = millis();
        break;
      case 2:
        memcpy(&back_arm, &buff[1], sizeof(float));
        memcpy(&front_arm, &buff[5], sizeof(float));
        if (debug) Serial.println("Received arm command: " + String(back_arm) + ", " + String(front_arm));
        if (delta_time >= dt) {
          setArm(back_arm, front_arm);
          previous_time = current_time;
        }
        break;
      case 3:
        memcpy(&intake_speed, &buff[1], sizeof(float));
        if (debug) Serial.println("Received intake command: " + String(intake_speed));
        setIntakeMotor(intake_speed);
        break;
      case 4:
        memcpy(&actuator_control, &buff[1], sizeof(float));
        if (debug) Serial.println("Received actuator command.");
      default:
        Serial.println("Unknown command.");
    }
  }
  
}
