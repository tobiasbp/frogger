"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/assets/space-shooter-redux

"""
import random

import arcade

# Import sprites from local file my_sprites.py
from my_sprites import Player, PlayerShot

# Set the scaling of all sprites in the game
SPRITE_SCALING = 2

TILE_SIZE = 16 * SPRITE_SCALING
MAP_WIDTH = 15
MAP_HEIGHT = 18

# Set the size of the screen
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE

# Variables controlling the player
PLAYER_LIVES = 3
PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = 50
PLAYER_SHOT_SPEED = 300


FIRE_KEY = arcade.key.SPACE


class GameView(arcade.View):
    """
    The view with the game itself
    """

    def load_map(self):
        m = arcade.tilemap.TileMap(
            map_file = "images/tiny-battle/sampleMap.tmx",
            scaling=SPRITE_SCALING,
        )

        return m

    def add_goals(self):
        """
        Add goal posts on the spots that the tile map specifies
        """
        for layer_tile in self.map.sprite_lists["goal"]:
            # /4 tile offset considering neither tile nor goal sprite has position in the center
            new_goal_sprite = arcade.Sprite(
                texture=self.load_tilemap_textures[190],
                scale=SPRITE_SCALING, 
                center_x = layer_tile.center_x,
                center_y = layer_tile.center_y,
            )
            self.goal_sprite_list.append(new_goal_sprite)


    def on_show_view(self):
        """
        This is run once when we switch to this view
        """

        self.pe = arcade.PymunkPhysicsEngine(
            gravity=(0, 0),
        )

        self.map = self.load_map()

        # player spawns at random position from the start position layer
        for layer_name, layer_sprites in self.map.sprite_lists.items():
            if layer_name == "start-pos":
                self.player_start_pos = random.choice(
                    list(tile.position for tile in layer_sprites)
                )

        # Set up the player info
        self.player_score = 0
        self.player_lives = PLAYER_LIVES

        self.texture_pack_name = "images/tiny-battle/tilemap.png"

        self.load_tilemap_textures = arcade.load_spritesheet(
            file_name=self.texture_pack_name,
            sprite_width=16,
            sprite_height=16,
            columns=18,
            count=11 * 18,
            margin=1
        )

        # Create a Player object
        self.player = Player(
            center_x=self.player_start_pos[0],
            center_y=self.player_start_pos[1],
            min_x_pos=0,
            max_x_pos=SCREEN_WIDTH,
            scale=SPRITE_SCALING,
        )
        self.player.texture = self.load_tilemap_textures[106]

        # Let physics engine control player sprite
        self.pe.add_sprite(self.player)

        # Track the current state of what keys are pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Get list of joysticks
        joysticks = arcade.get_joysticks()

        if joysticks:
            print("Found {} joystick(s)".format(len(joysticks)))

            # Use 1st joystick found
            self.joystick = joysticks[0]

            # Communicate with joystick
            self.joystick.open()

            # Map joysticks functions to local functions
            self.joystick.on_joybutton_press = self.on_joybutton_press
            self.joystick.on_joybutton_release = self.on_joybutton_release
            self.joystick.on_joyaxis_motion = self.on_joyaxis_motion
            self.joystick.on_joyhat_motion = self.on_joyhat_motion

        else:
            print("No joysticks found")
            self.joystick = None

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        self.goal_sprite_list = arcade.SpriteList(use_spatial_hash=False)

        self.add_goals()

    def on_draw(self):
        """
        Render the screen.
        """

        # Clear screen so we can draw new stuff
        self.clear()

        for key, sprite_list in self.map.sprite_lists.items():
            sprite_list.draw()

        # Draw the player sprite
        self.player.draw()

        # Draw Goal
        self.goal_sprite_list.draw()

        # Draw players score on screen
        arcade.draw_text(
            f"SCORE: {self.player_score}",  # Text to show
            10,  # X position
            SCREEN_HEIGHT - 20,  # Y positon
            arcade.color.WHITE,  # Color of text
        )

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        # Calculate player speed based on the keys pressed
        self.player.change_x = 0

        
        self.goal_sprite_list.update()

        #goal_hit_list = arcade.check_for_collision_with_list(self.player, self.goal_sprite_list)

        #for g in goal_hit_list:
            # Remove the goal
        #    g.remove_from_sprite_lists()

        # Move player with joystick if present
        if self.joystick:
            self.player.change_x = round(self.joystick.x) * PLAYER_SPEED_X

        # Update player sprite
        self.player.on_update(delta_time)

        # Physics engine takes a step
        self.pe.step()

        # The game is over when the player touches all goals
        if not any(self.goal_sprite_list):
            self.game_over()

    def game_over(self):
        """
        Call this when the game is over
        """

        # Create a game over view
        game_over_view = GameOverView(score=self.player_score)

        # Change to game over view
        self.window.show_view(game_over_view)

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """

        # The new player position
        new_pp = self.player.position

        # End the game if the escape key is pressed
        if key == arcade.key.ESCAPE:
            self.game_over()

        # Track state of arrow keys
        if key == arcade.key.UP:
            self.up_pressed = True
            new_pp = (new_pp[0], new_pp[1] + TILE_SIZE)
            print(new_pp)
        elif key == arcade.key.DOWN:
            self.down_pressed = True
            new_pp = (new_pp[0], new_pp[1] - TILE_SIZE)
        elif key == arcade.key.LEFT:
            self.left_pressed = True
            new_pp = (new_pp[0] - TILE_SIZE, new_pp[1])
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
            new_pp = (new_pp[0] + TILE_SIZE, new_pp[1])

        self.pe.set_position(
            sprite=self.player,
            position=new_pp,
        )

        if key == FIRE_KEY:
            pass

    def on_key_release(self, key, modifiers):
        """
        Called whenever a key is released.
        """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_joybutton_press(self, joystick, button_no):
        print("Button pressed:", button_no)
        # Press the fire key
        self.on_key_press(FIRE_KEY, [])

    def on_joybutton_release(self, joystick, button_no):
        print("Button released:", button_no)

    def on_joyaxis_motion(self, joystick, axis, value):
        print("Joystick axis {}, value {}".format(axis, value))

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print("Joystick hat ({}, {})".format(hat_x, hat_y))


class IntroView(arcade.View):
    """
    View to show instructions
    """

    def on_show_view(self):
        """
        This is run once when we switch to this view
        """

        # Set the background color
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """
        Draw this view
        """
        self.clear()

        # Draw some text
        arcade.draw_text(
            "Instructions Screen",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
        )

        # Draw more text
        arcade.draw_text(
            "Press any key to start the game",
            self.window.width / 2,
            self.window.height / 2 - 75,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
        )

    def on_key_press(self, key: int, modifiers: int):
        """
        Start the game when any key is pressed
        """
        game_view = GameView()
        self.window.show_view(game_view)


class GameOverView(arcade.View):
    """
    View to show when the game is over
    """

    def __init__(self, score, window=None):
        """
        Create a Gaome Over view. Pass the final score to display.
        """
        self.score = score

        super().__init__(window)

    def setup_old(self, score: int):
        """
        Call this from the game so we can show the score.
        """
        self.score = score

    def on_show_view(self):
        """
        This is run once when we switch to this view
        """

        # Set the background color
        arcade.set_background_color(arcade.csscolor.DARK_GOLDENROD)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """
        Draw this view
        """

        self.clear()

        # Draw some text
        arcade.draw_text(
            "Game over!",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
        )

        # Draw player's score
        arcade.draw_text(
            f"Your score: {self.score}",
            self.window.width / 2,
            self.window.height / 2 - 75,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
        )

    def on_key_press(self, key: int, modifiers: int):
        """
        Return to intro screen when any key is pressed
        """
        intro_view = IntroView()
        self.window.show_view(intro_view)


def main():
    """
    Main method
    """
    # Create a window to hold views
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Game starts in the intro view
    start_view = IntroView()

    window.show_view(start_view)

    arcade.run()


if __name__ == "__main__":
    main()
