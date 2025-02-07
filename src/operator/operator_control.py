import pygame
import socket

#gets inputs from controller and sends them to pi?or  transfers to serial and sends to pi
pygame.init()
pygame.joystick.init()

server_ip = "127.0.0.1" #change later (?)
port = 8000

def run():
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) ##all we gonna do is send information
  server.bind(('', port))

  joysticks = []
  for event in pygame.event.get():
    if event.type == pygame.JOYDEVICEADDED:
      joy = pygame.joystick.Joystick(event.device_index)
      joysticks.append(joy)
 
  running = True;
  while running:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False
      
        if event.type == pygame.JOYAXISMOTION:#we only care about the rightstick from right to left, axis 3   
          leftStickX = joy.get_axis(3)
          print("RS, axis3: " + leftStickX)
          #flesh out

          rightStickY = joy.get_axis(1)#and up and down with leftstick for actual speed of the bot, axis 1
          print("LS, axis1: " + rightStickY)
          #flesh out 

          for i in range(joy.get_numaxes()):#smth to test what axes come through (if it works right)
                  axis = joy.get_axis(i)
                  print(axis + " ")
          #triggers count as axis, LT: axis 2, RT: axis 5
      
        elif event.type == pygame.JOYBUTTONDOWN: # for other robot functions idk 
          joy.getbutton()

  pygame.quit()
if __name__ == "__main__":
    run()
