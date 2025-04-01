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
PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = 50
PLAYER_SHOT_SPEED = 300

LEVEL_TIME = 60

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
                texture=self.load_tilemap_textures[100],
                scale=SPRITE_SCALING, 
                center_x = layer_tile.center_x,
                center_y = layer_tile.center_y,
            )
            self.goal_sprite_list.append(new_goal_sprite)

    def get_tiles_from_screen_coordinate(self, screen_x, screen_y):
        """
        get all tiles with matching map coordinate
        """
        # the map coordinate corresponding to the screen coordinate
        map_coordinate = self.map.get_cartesian(screen_x, screen_y)

        # all tiles with same map coordinate
        tiles = []

        for layer_name, layer_tiles in self.map.sprite_lists.items():
            for tile in layer_tiles:
                # checks if screen and tile coordinate share same map (cartesian) coordinates
                if self.map.get_cartesian(tile.center_x, tile.center_y) == map_coordinate:
                    tiles.append(layer_name)
        return tiles

    def reset(self):
        """
        Level is reset
        """
        # Move player to start pos
        for layer_name, layer_sprites in self.map.sprite_lists.items():
            if layer_name == "start-pos":
                position = random.choice(
                    list(tile.position for tile in layer_sprites)
                )
                self.pe.set_position(
                    self.player,
                    position,
                )

        # Add cars (moving objects)
        for object in self.map.sprite_lists["moving-objects"]:
            # Add cars to physics engine. We may not want this
            self.pe.add_sprite(
                sprite=object,
                # Body type cannot be kinematic if we want handler to work
                # body_type=arcade.PymunkPhysicsEngine.KINEMATIC,
                collision_type="object",
                )
            
            self.pe.set_velocity(
                sprite=object,
                velocity=(
                    object.properties.get("x-speed", 0),
                    object.properties.get("y-speed", 0),
                )
            )

        # Reset timer
        self.timer = LEVEL_TIME


    def handler_player_object(self, player, object, _arbiter, _space, _data):
        #self.reset()
        print("player + object collision")

    def on_show_view(self):
        """
        This is run once when we switch to this view
        """

        self.pe = arcade.PymunkPhysicsEngine(
            gravity=(0, 0),
        )

        self.pe.add_collision_handler(
            "player",
            "object",
            post_handler = self.handler_player_object,
        )

        self.map = self.load_map()

        self.timer = 0


        # Set up the player info
        self.player_score = 0

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
            min_x_pos=0,
            max_x_pos=SCREEN_WIDTH,
            scale=SPRITE_SCALING,
        )
        
        self.player.texture = self.load_tilemap_textures[106]

        # Let physics engine control player sprite
        self.pe.add_sprite(
            self.player,
            # Body type cannot be kinematic, if we want our handler to work
            # body_type=arcade.PymunkPhysicsEngine.KINEMATIC,
            collision_type="player",
            )

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

        # Add goals
        self.goal_sprite_list = arcade.SpriteList(use_spatial_hash=False)
        self.add_goals()

        # Set player position, cars and timer
        self.reset()

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

        # Draw time on screen
        arcade.draw_text(
            f"TIME: {round(self.timer)}",
            10,
            SCREEN_HEIGHT-40,
            arcade.color.WHITE,
        )

        # draw lives on screen
        arcade.draw_text(
            f"LIVES: {self.player.lives}",
            10,
            SCREEN_HEIGHT - 60,
            arcade.color.WHITE,
        )

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        # Movement using joystick is not correct. Still here if we want to implement joystick later
        # Move player with joystick if present
        """
        if self.joystick:
            self.player.change_x = round(self.joystick.x) * PLAYER_SPEED_X
        """

        self.goal_sprite_list.update()

        # Update player sprite
        self.player.on_update(delta_time)

        # Physics engine takes a step
        self.pe.step()

        goal_hit_list = arcade.check_for_collision_with_list(self.player, self.goal_sprite_list)

        # Check if objects should wrap
        for o in self.map.sprite_lists["moving-objects"]:

            # Wrap on x-axis
            if o.center_x > SCREEN_WIDTH+TILE_SIZE/2:
                self.pe.set_position(
                    sprite=o,
                    position=(0-TILE_SIZE/2, o.center_y)
                )
            elif o.center_x < 0-TILE_SIZE/2:
                self.pe.set_position(
                    sprite=o,
                    position=(SCREEN_WIDTH+TILE_SIZE/2, o.center_y)
                )

            # Wrap on y-axis
            if o.center_y > SCREEN_HEIGHT+TILE_SIZE/2:
                self.pe.set_position(
                    sprite=o,
                    position=(o.center_x, 0-TILE_SIZE/2)
                )
            elif o.center_y < 0-TILE_SIZE/2:
                self.pe.set_position(
                    sprite=o,
                    position=(o.center_x, SCREEN_HEIGHT+TILE_SIZE/2)
                )

        for g in goal_hit_list:
            # Remove the goal
            g.remove_from_sprite_lists()

        # The game is over when the player touches all goals
        if not any(self.goal_sprite_list):
            self.game_over()

        # Check if player dies when touching "deadly" tile
        for deadly_tile in self.map.sprite_lists["deadly"]:
            if deadly_tile.collides_with_point(self.player.position):
                self.player.lives -= 1

                if self.player.lives < 1:
                    self.game_over()
                else:
                    self.reset()

        # Update the timer
        self.timer -= delta_time

        # check if time has run out
        if self.timer <= 0:
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
