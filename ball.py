from panda3d.core import Vec3, TransformState, VBase3
from game_object import GameObject
from pubsub import pub

class Ball(GameObject):
    def __init__(self, position, kind, id, size, physics):
        super().__init__(position, kind, id, size, physics)
        self.kick_force = 10.0
        self.is_kicked = False

    def collision(self, other):
        pass
    #temp moving to troubleshoot
    #kicking anytime the player touches the ball

    def kick(self, direction):
        impulse = direction * self.kick_force
        self.physics.applyCentralImpulse(impulse)
        self.is_kicked = True
        print(f"Ball kicked")

    def tick(self, dt):
        if self.is_kicked:
            self.is_kicked = False

    def reset(self):
        self.physics.setTransform(TransformState.makePos(VBase3(0, 0, 0.5)))
        self.physics.setLinearVelocity(Vec3(0, 0, 0))
        self.is_kicked = False