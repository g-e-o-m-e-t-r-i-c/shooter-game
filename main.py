import random
import math
import arcade

from typing import cast

STARTING_METEOR_COUNT = 3
SCALE = 0.5
OFFSCREEN_SPACE = 300
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Meteor Shooter"
LEFT_LIMIT = -OFFSCREEN_SPACE
RIGHT_LIMIT = SCREEN_WIDTH + OFFSCREEN_SPACE
BOTTOM_LIMIT = -OFFSCREEN_SPACE
TOP_LIMIT = SCREEN_HEIGHT + OFFSCREEN_SPACE

# list down all images and sounds used in the game
BULLET_IMAGE = "images/laser.png"

METEOR_BIG_IMAGE_LIST = ["images/meteorGrey_big1.png", "images/meteorGrey_big2.png", "images/meteorGrey_big3.png", "images/meteorGrey_big4.png"]

METEOR_MED_IMAGE_LIST = ["images/meteorGrey_med1.png", "images/meteorGrey_med2.png"]

METEOR_SMALL_IMAGE_LIST = ["images/meteorGrey_small1.png", "images/meteorGrey_small2.png"]

METEOR_TINY_IMAGE_LIST = ["images/meteorGrey_tiny1.png", "images/meteorGrey_tiny2.png"]

SHIP_IMAGE = "images/spaceship.png"
SHIPLIFE_IMAGE = "images/spaceship_life.png"

HIT_SOUND1 = "sounds/explosion1.wav"
HIT_SOUND2 = "sounds/explosion2.wav"
HIT_SOUND3 = "sounds/hit1.wav"
HIT_SOUND4 = "sounds/hit2.wav"
LASER_SOUND = "sounds/laser.wav"


class BulletSprite(arcade.Sprite):

    def update(self):
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))


class MeteorSprite(arcade.Sprite):

    def __init__(self, image_file_name, scale):
        super().__init__(image_file_name, scale=scale)
        self.size = 0

    def update(self):
        super().update()
        if self.center_x < LEFT_LIMIT:
            self.center_x = RIGHT_LIMIT
        if self.center_x > RIGHT_LIMIT:
            self.center_x = LEFT_LIMIT
        if self.center_y > TOP_LIMIT:
            self.center_y = BOTTOM_LIMIT
        if self.center_y < BOTTOM_LIMIT:
            self.center_y = TOP_LIMIT


class ShipSprite(arcade.Sprite):

    def __init__(self, filename, scale):

        super().__init__(filename, scale)

        # Info on where we are going.
        # Angle comes in automatically from the parent class.
        self.thrust = 0
        self.drag = 0.05
        self.speed = 0
        self.max_speed = 4
        self.respawning = 0

        # Mark that we are respawning.
        self.respawn()

    def respawn(self):
        # Called when the ship dies and we need to make a new ship.
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        self.angle = 0

    def update(self):
        # Update our position and other particulars.

        # step 1: continue respawning if it is respawning
        if self.respawning:
            self.respawning += 1
            # alpha: Transparency of sprite. 0 is invisible, 255 is opaque.
            """as alpha changes from 2, 3,...255, the spaceship changes from transparent,
            semi-transparent to opaque."""
            self.alpha = self.respawning
            if self.respawning == 255:
                self.respawning = 0

        # step 2: set speed
        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0

        if self.speed < 0:
            self.speed += self.drag
            if self.speed > 0:
                self.speed = 0

        self.speed += self.thrust
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed

        # step 3: set location
        self.change_x = -math.sin(math.radians(self.angle)) * self.speed
        self.change_y = math.cos(math.radians(self.angle)) * self.speed

        self.center_x += self.change_x
        self.center_y += self.change_y

        # step 4: If the ship goes off-screen, move it to the other side of the window
        if self.right < 0:
            self.left = SCREEN_WIDTH

        if self.left > SCREEN_WIDTH:
            self.right = 0

        if self.top < 0:
            self.bottom = SCREEN_HEIGHT

        if self.bottom > SCREEN_HEIGHT:
            self.top = 0

        # step 5
        super().update()


class ShooterGame(arcade.Window):

    def __init__(self):

        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.game_over = False

        # Sprite lists
        self.player_sprite_list = arcade.SpriteList()
        self.meteor_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        self.score = 0
        self.player_sprite = None
        self.lives = 3

        # Sounds - BUG HERE
        self.laser_sound = arcade.load_sound(LASER_SOUND)  # arcade module unable to load sounds
        self.hit_sound1 = arcade.load_sound(HIT_SOUND1)
        self.hit_sound2 = arcade.load_sound(HIT_SOUND2)
        self.hit_sound3 = arcade.load_sound(HIT_SOUND3)
        self.hit_sound4 = arcade.load_sound(HIT_SOUND4)

    def start_new_game(self):

        self.game_over = False

        # Sprite lists
        # why I create so many lists?
        self.player_sprite_list = arcade.SpriteList()
        self.meteor_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = ShipSprite(SHIP_IMAGE, SCALE)
        self.player_sprite_list.append(self.player_sprite)
        self.lives = 3

        # Set up the little icons that represent the player lives.
        cur_pos = 10
        for i in range(self.lives):
            life = arcade.Sprite(SHIPLIFE_IMAGE, SCALE)
            life.center_x = cur_pos + life.width
            life.center_y = life.height
            cur_pos += life.width
            self.ship_life_list.append(life)

        image_list = METEOR_BIG_IMAGE_LIST

        for i in range(STARTING_METEOR_COUNT):
            image_no = random.randrange(4)
            enemy_sprite = MeteorSprite(image_list[image_no], SCALE)

            enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)
            enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)

            # generates a random float uniformly in the semi-open range[0.0, 1.0)
            enemy_sprite.change_x = random.random() * 2 - 1  # [-1,1)
            enemy_sprite.change_y = random.random() * 2 - 1  # [-1,1)

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.meteor_list.append(enemy_sprite)

    def on_key_press(self, symbol, modifiers):

        # Shoot if the player hit the space bar and we aren't respawning.
        if not self.player_sprite.respawning and symbol == arcade.key.SPACE:
            bullet_sprite = BulletSprite(BULLET_IMAGE, SCALE)

            bullet_speed = 13
            bullet_sprite.change_y = math.cos(math.radians(self.player_sprite.angle)) * bullet_speed
            bullet_sprite.change_x = -math.sin(math.radians(self.player_sprite.angle)) * bullet_speed

            bullet_sprite.center_x = self.player_sprite.center_x
            bullet_sprite.center_y = self.player_sprite.center_y
            bullet_sprite.update()

            self.bullet_list.append(bullet_sprite)

            arcade.play_sound(self.laser_sound)

        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = 3
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = -3
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = 0.15
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = -0.2

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = 0
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = 0

    def split_meteor(self, meteor: MeteorSprite):

        x = meteor.center_x
        y = meteor.center_y
        self.score += 1

        if meteor.size == 4:
            for i in range(3):
                # randomly pick a image from METEOR_MED_IMAGE_LIST
                image_list = METEOR_MED_IMAGE_LIST
                image_no = random.randrange(2)
                enemy_sprite = MeteorSprite(image_list[image_no], SCALE * 1.5)
                enemy_sprite.size = 3
                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 2.5 - 1.25
                enemy_sprite.change_y = random.random() * 2.5 - 1.25
                enemy_sprite.change_angle = (random.random() - 0.5) * 2

                self.meteor_list.append(enemy_sprite)
                self.hit_sound1.play()

        elif meteor.size == 3:
            for i in range(3):
                image_list = METEOR_SMALL_IMAGE_LIST
                image_no = random.randrange(2)
                enemy_sprite = MeteorSprite(image_list[image_no], SCALE * 1.5)
                enemy_sprite.size = 2
                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                # smaller meteor moves and rotates faster
                enemy_sprite.change_x = random.random() * 3 - 1.5
                enemy_sprite.change_y = random.random() * 3 - 1.5
                enemy_sprite.change_angle = (random.random() - 0.5) * 2

                self.meteor_list.append(enemy_sprite)
                self.hit_sound2.play()

        elif meteor.size == 2:
            for i in range(3):
                image_list = METEOR_TINY_IMAGE_LIST
                image_no = random.randrange(2)
                enemy_sprite = MeteorSprite(image_list[image_no], SCALE * 1.5)
                enemy_sprite.size = 1
                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3.5 - 1.75
                enemy_sprite.change_y = random.random() * 3.5 - 1.75
                enemy_sprite.change_angle = (random.random() - 0.5) * 2

                self.meteor_list.append(enemy_sprite)
                self.hit_sound3.play()

        elif meteor.size == 1:
            self.hit_sound4.play()

    def on_update(self, x):
        if not self.game_over:
            self.meteor_list.update()
            self.bullet_list.update()
            self.player_sprite_list.update()

            for bullet in self.bullet_list:
                meteors = arcade.check_for_collision_with_list(bullet, self.meteor_list)

                for meteor in meteors:
                    self.split_meteor(cast(MeteorSprite, meteor))
                    # expected MeteorSprite, got Sprite instead
                    meteor.remove_from_sprite_lists()
                    bullet.remove_from_sprite_lists()

                # Remove bullet if it goes off-screen
                size = max(bullet.width, bullet.height)
                if bullet.center_x < 0 - size:
                    bullet.remove_from_sprite_lists()
                if bullet.center_x > SCREEN_WIDTH + size:
                    bullet.remove_from_sprite_lists()
                if bullet.center_y < 0 - size:
                    bullet.remove_from_sprite_lists()
                if bullet.center_y > SCREEN_HEIGHT + size:
                    bullet.remove_from_sprite_lists()

            if not self.player_sprite.respawning:
                meteors = arcade.check_for_collision_with_list(self.player_sprite, self.meteor_list)
                if len(meteors) > 0:
                    if self.lives > 0:
                        self.lives -= 1
                        self.player_sprite.respawn()
                        self.split_meteor(cast(MeteorSprite, meteors[0]))
                        meteors[0].remove_from_sprite_lists()
                        self.ship_life_list.pop().remove_from_sprite_lists()
                        print("Crash!")
                    else:
                        self.game_over = True
                        print("--- GAME OVER ---")

    def on_draw(self):
        # Render the screen.

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.meteor_list.draw()
        self.ship_life_list.draw()
        self.bullet_list.draw()
        self.player_sprite_list.draw()

        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 70, arcade.color.WHITE, 13)

        output = f"Meteor Count: {len(self.meteor_list)}"
        arcade.draw_text(output, 10, 50, arcade.color.WHITE, 13)

        # No need to call arcade.finish_render() as arcade will call it implicitly when on_draw() ends.


def main():
    window = ShooterGame()
    window.start_new_game()
    arcade.run()


if __name__ == "__main__":
    main()
