from pubsub import pub
from panda3d.core import CollisionBox, CollisionNode

class ViewObject:
    def __init__(self, game_object):
        self.game_object = game_object

        if self.game_object.physics:
            self.node_path = base.render.attachNewNode(self.game_object.physics)
        else:
            self.node_path = base.render.attachNewNode(self.game_object.kind)

        #load specific models based on kind, coding practice will change, possibly use a dictionary.
        if self.game_object.kind == "ball":
            self.model = base.loader.loadModel("Models/soccerBall.egg")
        elif self.game_object.kind == "goal":
            self.model = base.loader.loadModel("Models/hockeyGoal.egg")
        elif self.game_object.kind == "crate":
            self.model = base.loader.loadModel("Models/cube")
        elif self.game_object.kind == "floor":
            self.model = base.loader.loadModel("Models/cube")
        elif self.game_object.kind == "wall":
            self.model = base.loader.loadModel("Models/cube")
        elif self.game_object.kind == "speed_boost":
            self.model = base.loader.loadModel("Models/cube") #find custom model for this
            self.model.setColor(1, 1, 0, 1)
        else:
            self.model = base.loader.loadModel("Models/cube")

        self.model.reparentTo(self.node_path)

       #will need updated to use a dictionary eventually. using temporarily with all of the pieces I will need
        if self.game_object.kind == "crate":
            self.cube_texture = base.loader.loadTexture("Textures/crate.png")
            self.model.setTexture(self.cube_texture)
        elif self.game_object.kind == "floor":
            self.floor_texture = base.loader.loadTexture("Textures/grass.png")
            self.model.setTexture(self.floor_texture)
        elif self.game_object.kind == "wall":
             self.wall_texture = base.loader.loadTexture("Textures/wall.png")
        elif self.game_object.kind == "speed_boost":
            pass

        bounds = self.model.getTightBounds()
        # bounds is two vectors
        bounds = bounds[1]-bounds[0]
        # bounds is now the widths with bounds[0] the x width, bounds[1] the y depth, bounds[2] the z height
        size = game_object.size

        x_scale = size[0] / bounds[0]
        y_scale = size[1] / bounds[1]
        z_scale = size[2] / bounds[2]
        self.model.setScale(x_scale, y_scale, z_scale)

        self.is_selected = False
        self.texture_on = True
        self.toggle_texture_pressed = False
        pub.subscribe(self.toggle_texture, 'input')

    def deleted(self):
        self.node_path.removeNode()

    def toggle_texture(self, events=None):
        if 'toggleTexture' in events:
            self.toggle_texture_pressed = True

    def tick(self):
        # This will only be needed for game objects that
        # aren't also physics objects.  physics objects will
        # have their position and rotation updated by the
        # engine automatically
        if not self.game_object.physics:
            h = self.game_object.z_rotation
            p = self.game_object.x_rotation
            r = self.game_object.y_rotation
            self.model.setHpr(h, p, r)
            self.model.set_pos(*self.game_object.position)

        # If the right control was pressed, and the game object
        # is currently selected, toggle the texture.
        if self.toggle_texture_pressed and self.game_object.is_selected:
            if self.texture_on:
                self.texture_on = False
                self.model.setTextureOff(1)
            else:
                self.texture_on = True
                self.model.setTexture(self.cube_texture)

        self.toggle_texture_pressed = False
        self.game_object.is_selected = False

