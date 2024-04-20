import os
import random
import sys

import pygame


class Game:

    def __init__(self):
        self.screen = None
        self.clock = None
        self.animation_speed = 1.0  # Controls how fast the animation plays
        self.frame_index = 0
        self.screen_width, self.screen_height = 1024, 768

    def setup(self):
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.init()


# Enemy class
class Enemy:
    def __init__(self, x_pos, y_pos, size, speed, color=None, level=1):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.size = (size[0] + level, size[1] + level)
        self.speed = speed + level
        self.color = color or (255, 0, 0)
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])


def load_sprites(action, scale_factor=3, new_size=None, path="./assets"):
    images = []
    for file in sorted(os.listdir(path)):
        if file.startswith(action) and file.endswith(".png"):
            image_path = os.path.join(path, file)
            image = pygame.image.load(image_path)
            if scale_factor:
                # Scale by a factor
                new_width = int(image.get_width() * scale_factor)
                new_height = int(image.get_height() * scale_factor)
                image = pygame.transform.scale(image, (new_width, new_height))
            elif new_size:
                # Scale to a new size
                image = pygame.transform.scale(image, new_size)
            images.append(image)
    return images


sprites = {
    "attack": load_sprites("adventurer-attack1"),
    "idle": load_sprites("adventurer-idle-2"),
    "move_left": load_sprites("adventurer-run"),
    "move_right": load_sprites("adventurer-run"),
    "move_up": load_sprites("adventurer-jump"),
    "move_down": load_sprites("adventurer-fall"),
}


def update_animation(current_action, game):
    game.frame_index += game.animation_speed
    if game.frame_index >= len(sprites[current_action]):
        game.frame_index = 0

    player_image = sprites[current_action][int(game.frame_index)]
    return player_image


def create_enemy(game, level=1):
    enemy_size = (5, 5)
    red = (255, 0, 0)
    enemy_speed = 1  # Set a constant speed for all enemies
    x_pos = random.randint(0, game.screen_width - enemy_size[0])
    y_pos = random.randint(0, game.screen_height - enemy_size[1])
    _enemy = Enemy(x_pos, y_pos, enemy_size, enemy_speed, red, level=level)
    return _enemy


def main():
    # Initialize Pygame
    # Example of loading sprites for different actions

    game = Game()
    game.setup()

    # Set up the display

    # Colors
    white = (255, 255, 255)
    green = (0, 255, 0)

    # Player settings
    player_size = (20, 10)
    player_pos = [game.screen_width // 2, game.screen_height // 2]
    player_speed = 6

    # Enemy settings

    num_enemies = 5
    enemies = []
    # Create initial enemies
    for _ in range(num_enemies):
        enemies.append(create_enemy(game))
    # Main game loop
    running = True
    player_image = pygame.Surface(player_size)
    player_image.fill(green)
    enemy_level = 1
    while running:
        game.clock.tick(10)  # Limit the frame rate to 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_pos[0] -= player_speed
            current_action = "move_left"
        elif keys[pygame.K_RIGHT]:
            player_pos[0] += player_speed
            current_action = "move_right"
        elif keys[pygame.K_SPACE]:
            current_action = "attack"
        else:
            current_action = "idle"
        player_image = update_animation(
            current_action=current_action, game=game
        )  # Update the animation frame
        if current_action == "move_left":
            player_image = pygame.transform.flip(
                player_image, True, False
            )  # Flip the image

        game.screen.blit(player_image, player_pos)
        # Keep player within screen boundaries
        player_pos[0] = max(0, min(player_pos[0], game.screen_width - player_size[0]))
        player_pos[1] = max(0, min(player_pos[1], game.screen_height - player_size[1]))

        # Update enemies and check boundaries
        # Update enemies and check boundaries
        for enemy in enemies:
            # Calculate the direction vector from enemy to player
            direction_vector = [
                player_pos[0] - enemy.x_pos,
                player_pos[1] - enemy.y_pos,
            ]
            # Calculate the magnitude of the vector
            distance = (direction_vector[0] ** 2 + direction_vector[1] ** 2) ** 0.5

            # Normalize the direction vector
            if distance != 0:
                direction_vector[0] /= distance
                direction_vector[1] /= distance

            # Move enemy away from the player, opposite to the direction vector
            enemy.x_pos -= enemy.speed * direction_vector[0] * enemy.direction_x
            enemy.y_pos -= enemy.speed * direction_vector[1] * enemy.direction_y

            # Check horizontal boundaries and bounce if necessary
            if enemy.x_pos <= 0 or enemy.x_pos >= game.screen_width - enemy.size[0]:
                enemy.direction_x *= (
                    -1
                )  # Reverse direction when hitting a horizontal boundary
            # Check vertical boundaries and bounce if necessary
            if enemy.y_pos <= 0 or enemy.y_pos >= game.screen_height - enemy.size[1]:
                enemy.direction_y *= (
                    -1
                )  # Reverse direction when hitting a vertical boundary

        # Collision detection
        player_rect = pygame.Rect(
            player_pos[0], player_pos[1], player_size[0], player_size[1]
        )
        enemies_to_remove = []
        for enemy in enemies:
            enemy_rect = pygame.Rect(
                enemy.x_pos, enemy.y_pos, enemy.size[0], enemy.size[1]
            )
            if player_rect.colliderect(enemy_rect):
                enemies_to_remove.append(enemy)
                player_size = (player_size[0] + 1, player_size[1] + 1)
                player_image = pygame.Surface(player_size)
                player_image.fill(green)
                print("Enemy Collision")
                print(player_size)
                if player_size[0] > 200:
                    running = False

        for enemy in enemies_to_remove:
            enemies.remove(enemy)
            enemy_level += 1

            enemies.append(create_enemy(game, level=enemy_level))

        # Clear screen and redraw elements
        game.screen.fill(white)
        game.screen.blit(player_image, player_pos)
        for enemy in enemies:
            pygame.draw.rect(
                game.screen,
                enemy.color,
                (enemy.x_pos, enemy.y_pos, enemy.size[0], enemy.size[1]),
            )

        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
