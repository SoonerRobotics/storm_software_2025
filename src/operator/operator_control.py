import pygame
import socket

# Initialize Pygame and joystick support
pygame.init()
pygame.joystick.init()

server_ip = "127.0.0.1"  # Change 
port = 8000

def run():
    # Create a socket to send data
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Attempt to connect instead of binding 
    try:
        server.connect((server_ip, port))
    except ConnectionRefusedError:
        print("Could not connect to server.")
        return

    # Initialize the joystick 
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print("Controller connected:", joystick.get_name())
    else:
        print("No controller detected.")
        return

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.JOYAXISMOTION:
                leftStickX = joystick.get_axis(3)
                rightStickY = joystick.get_axis(1)

                print(f"RS, axis3: {leftStickX:.2f}")
                print(f"LS, axis1: {rightStickY:.2f}")

                for i in range(joystick.get_numaxes()):
                    axis = joystick.get_axis(i)

            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"Button {event.button} pressed")

    pygame.quit()

if __name__ == "__main__":
    run()
