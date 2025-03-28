from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from panda3d.bullet import BulletDebugNode
from panda3d.core import CollisionTraverser, WindowProperties, Quat, Vec3, Point3, TextNode
from direct.showbase.InputStateGlobal import inputState
from pubsub import pub
import sys

from kcc import PandaBulletCharacterController
from world_view import WorldView
from game_world import GameWorld

controls = {
    'escape': 'toggleMouseMove',
    't': 'teleport',
    'mouse1': 'toggleTexture',
    'space': 'kick',
}

held_keys = {
    'w': 'moveForward',
    's': 'moveBackward',
    'a': 'moveLeft',
    'd': 'moveRight',
}

class Main(ShowBase):
    def go(self):
        self.cTrav = CollisionTraverser()

        self.game_world.load_world()
        self.player = PandaBulletCharacterController(self.game_world.physics_world, self.render, self.player)

        self.taskMgr.add(self.tick)
        self.score_text = self.make_text("Score: 0", (0.9, 0.95), TextNode.ARight)
        self.time_text = self.make_text("Time: 60", (-0.9, 0.95), TextNode.ALeft)

        self.input_events = {}
        for key in controls:
            self.accept(key, self.input_event, [controls[key]])

        for key in held_keys:
            inputState.watchWithModifiers(held_keys[key], key)

        self.SpeedRot = 0.05
        self.CursorOffOn = 'Off'
        self.props = WindowProperties()
        self.props.setCursorHidden(True)
        self.win.requestProperties(self.props)

        self.camera_pitch = 0

        pub.subscribe(self.handle_input, 'input')
        pub.subscribe(self.handle_game_event, "game_event")
        pub.subscribe(self.update_score, "property")
        self.run()

    def make_text(self, text, pos, align):
        text_node = TextNode('text')
        text_node.setText(text)
        text_node.setAlign(align)
        text_np = self.aspect2d.attachNewNode(text_node)
        text_np.setScale(0.07)
        text_np.setPos(pos[0], 0, pos[1])
        return text_np

    def handle_game_event(self, event):
        if event == "end":
            final_score = self.game_world.get_property("score")
            self.make_text(f"Game Over! Final Score: {final_score}", (0, 0), TextNode.ACenter)

    def handle_input(self, events=None):
        # Simple place to put debug outputs so they only happen on a click
        if 'toggleTexture' in events:
            print(f"Player position: {self.player.getPos()}")
            print(f"Forward position: {self.forward(self.player.getHpr(), self.player.getPos(), 5)}")


    def update_score(self, key, value):
        if key == "score":
            self.score_text.node().setText(f"Score: {value}")

    def input_event(self, event):
        self.input_events[event] = True

    def forward(self, hpr, pos, distance):
        h, p, r = hpr
        x, y, z = pos
        q = Quat()
        q.setHpr((h, p, r))
        forward = q.getForward()
        return x + forward[0]*distance, y + forward[1]*distance, z + forward[2]*distance

    def tick(self, task):
        if 'toggleMouseMove' in self.input_events:
            if self.CursorOffOn == 'Off':
                self.CursorOffOn = 'On'
                self.props.setCursorHidden(False)
            else:
                self.CursorOffOn = 'Off'
                self.props.setCursorHidden(True)

            self.win.requestProperties(self.props)

        pub.sendMessage('input', events=self.input_events)
        self.move_player(self.input_events)

        if not self.game_world.get_property("game_over"):
            self.time_text.node().setText(f"Time: {int(self.game_world.get_property('time_remaining'))}")

        if self.CursorOffOn == 'Off':
            md = self.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            if self.win.movePointer(0, base.win.getXSize() // 2, self.win.getYSize() // 2):
                z_rotation = self.camera.getH() - (x - self.win.getXSize() / 2) * self.SpeedRot
                x_rotation = self.camera.getP() - (y - self.win.getYSize() / 2) * self.SpeedRot
                if (x_rotation <= -90.1):
                    x_rotation = -90
                if (x_rotation >= 90.1):
                    x_rotation = 90

                self.player.setH(z_rotation)
                self.camera_pitch = x_rotation

        h = self.player.getH()
        p = self.camera_pitch
        r = self.player.getR()
        self.camera.setHpr(h, p, r)

        # This seems to work to prevent seeing into objects the player collides with.
        # It moves the camera a bit back from the center of the player object.
        q = Quat()
        q.setHpr((h, p, r))
        x, y, z = self.player.getPos()
        z_adjust = self.player.game_object.size[0]
        self.camera.set_pos(x, y, z + z_adjust)

        dt = globalClock.getDt()
        self.player.update(dt)
        self.game_world.tick(dt)
        self.world_view.tick()

        if self.game_world.get_property("quit"):
            sys.exit()

        self.input_events.clear()
        return Task.cont

    def move_player(self, events=None):
        speed = Vec3(0, 0, 0)
        delta = 5.0
        if inputState.isSet('moveForward'): speed.setY(delta)
        if inputState.isSet('moveBackward'): speed.setY(-delta)
        if inputState.isSet('moveLeft'): speed.setX(-delta)
        if inputState.isSet('moveRight'): speed.setX(delta)
        self.player.setLinearMovement(speed)

        if 'kick' in events:
            ball = next((obj for obj in self.game_world.game_objects.values() if obj.kind == "ball"), None)
            if ball:
                player_pos = self.player.getPos()
                ball_pos = ball.position
                dist = (player_pos - ball_pos).length()
                if dist < 2: #distance from player to kick
                    #calculate direction based on player's heading value
                    q = Quat()
                    q.setHpr((self.player.getH(), 0, 0))
                    direction = q.getForward()
                    ball.physics.applyCentralImpulse(direction * 20)

    def new_player_object(self, game_object):
        if game_object.kind == 'player':
            self.player = game_object

    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()
        self.render.setShaderAuto()

        self.instances = []
        self.player = None
        pub.subscribe(self.new_player_object, 'create')

        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(False)
        debugNode.showNormals(False)
        debugNP = render.attachNewNode(debugNode)
        debugNP.show()

        # create model and view
        self.game_world = GameWorld(debugNode)
        self.world_view = WorldView(self.game_world)


if __name__ == '__main__':
    main = Main()
    main.go()