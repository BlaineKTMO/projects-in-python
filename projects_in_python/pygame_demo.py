import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import pygame
import sys

class RaceGameNode(Node):
    def __init__(self):
        super().__init__('race_game_node')
        self.subscription1 = self.create_subscription(
            Twist,
            'player1/cmd_vel',
            self.listener_callback1,
            10)
        self.subscription2 = self.create_subscription(
            Twist,
            'player2/cmd_vel',
            self.listener_callback2,
            10)
        self.player1_vel = [0, 0]
        self.player2_vel = [0, 0]

    def listener_callback1(self, msg):
        self.player1_vel[0] = msg.linear.x
        self.player1_vel[1] = msg.linear.y

    def listener_callback2(self, msg):
        self.player2_vel[0] = msg.linear.x
        self.player2_vel[1] = msg.linear.y

def main(args=None):
    rclpy.init(args=args)
    node = RaceGameNode()

    # Initialize Pygame
    pygame.init()

    # Set up display
    width, height = 800, 600
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Race Game")

    # Define colors
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    yellow = (255, 255, 0)
    grey = (128, 128, 128)

    # Player settings
    player_size = 50
    player1_x, player1_y = 100, height // 2
    player2_x, player2_y = 200, height // 2

    # Grid settings
    grid_size = 40  # Increase the grid size to make the resolution smaller
    grid_width = width // grid_size
    grid_height = height // grid_size
    grid = [[False for _ in range(grid_height)] for _ in range(grid_width)]
    drag_set = set()
    toggled_set = set()

    # Main game loop
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // grid_size
                grid_y = mouse_y // grid_size
                drag_set.add((grid_x, grid_y))
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left mouse button is pressed
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = mouse_x // grid_size
                    grid_y = mouse_y // grid_size
                    drag_set.add((grid_x, grid_y))
            elif event.type == pygame.MOUSEBUTTONUP:
                for cell in drag_set:
                    grid_x, grid_y = cell
                    grid[grid_x][grid_y] = not grid[grid_x][grid_y]  # Toggle the cell state
                drag_set.clear()

        # Update player positions
        new_player1_x = player1_x + node.player1_vel[0]
        new_player1_y = player1_y + node.player1_vel[1]
        new_player2_x = player2_x + node.player2_vel[0]
        new_player2_y = player2_y + node.player2_vel[1]

        # Check for collisions with filled grid cells
        player1_rect = pygame.Rect(new_player1_x, new_player1_y, player_size, player_size)
        player2_rect = pygame.Rect(new_player2_x, new_player2_y, player_size, player_size)
        collision = False
        for x in range(grid_width):
            for y in range(grid_height):
                if grid[x][y]:
                    cell_rect = pygame.Rect(x * grid_size, y * grid_size, grid_size, grid_size)
                    if player1_rect.colliderect(cell_rect) or player2_rect.colliderect(cell_rect):
                        collision = True
                        break
            if collision:
                break

        # Update player positions if no collision
        if not collision:
            player1_x = new_player1_x
            player1_y = new_player1_y
            player2_x = new_player2_x
            player2_y = new_player2_y

        # Fill the background
        window.fill(black)

        # Draw the grid
        for x in range(grid_width):
            for y in range(grid_height):
                rect = pygame.Rect(x * grid_size, y * grid_size, grid_size, grid_size)
                pygame.draw.rect(window, grey, rect, 1)  # Draw the border
                if grid[x][y] and (x, y) not in drag_set:
                    pygame.draw.rect(window, green, rect)  # Fill the cell
                elif (x, y) in drag_set and not grid[x][y]:
                    pygame.draw.rect(window, yellow, rect)  # Highlight the cell being dragged over

        # Draw the players
        pygame.draw.rect(window, red, (player1_x, player1_y, player_size, player_size))
        pygame.draw.rect(window, blue, (player2_x, player2_y, player_size, player_size))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

        # Allow ROS2 to process incoming messages
        rclpy.spin_once(node, timeout_sec=0.01)

    # Quit Pygame
    pygame.quit()
    rclpy.shutdown()
    sys.exit()

if __name__ == '__main__':
    main()