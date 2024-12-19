import pubsub.pub
from panda3d.core import CollisionBox, CollisionNode
from pubsub import pub

class ViewObject:
    def __init__(self, game_object):
        self.game_object = game_object

        # TODO: we don't always need a cube model.  Check the
        # game object's kind property to what type of model to use
        self.cube = base.loader.loadModel("Models/cube")
        self.cube.reparentTo(base.render)
        self.cube.setPos(*game_object.position)

        # TODO: we don't always need a texture.  We need a
        # mechanism to see if we need a texture or color,
        # and what texture/color to use.
        self.cube_texture = base.loader.loadTexture("Textures/crate.png")
        self.cube.setTexture(self.cube_texture)

        self.cube.setTag('selectable', '')
        self.cube.setPythonTag("owner", self)

        bounds = self.cube.getTightBounds()
        # bounds is two vectors
        bounds = bounds[1]-bounds[0]
        # bounds is now the widths with bounds[0] the x width, bounds[1] the y depth, bounds[2] the z height
        size = game_object.size

        x_scale = size[0] / bounds[0]
        y_scale = size[1] / bounds[1]
        z_scale = size[2] / bounds[2]

        self.cube.setScale(x_scale, y_scale, z_scale)

        self.is_selected = False
        self.texture_on = True
        self.toggle_texture_pressed = False
        pub.subscribe(self.toggle_texture, 'input')

    def deleted(self):
        # Prevent circular references from keeping both the view object and the cube alive
        self.cube.setPythonTag("owner", None)

    def toggle_texture(self, events=None):
        if 'toggleTexture' in events:
            self.toggle_texture_pressed = True

    def selected(self):
        self.is_selected = True

    def tick(self):
        # TODO: this will only be needed for game objects that
        # aren't also physics objects.  physics objects will
        # have their position and rotation updated by the
        # engine automatically
        h = self.game_object.z_rotation
        p = self.game_object.x_rotation
        r = self.game_object.y_rotation
        self.cube.setHpr(h, p, r)
        self.cube.set_pos(*self.game_object.position)

        # This sort of interaction with the view itself is fine
        # for both physics and non-physics objects
        if self.toggle_texture_pressed and self.is_selected:
            if self.texture_on:
                self.texture_on = False
                self.cube.setTextureOff(1)
            else:
                self.texture_on = True
                self.cube.setTexture(self.cube_texture)

            self.toggle_texture_pressed = False

        self.is_selected = False
