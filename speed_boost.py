from game_object import GameObject
from panda3d.core import Vec3, TransformState, VBase3
from pubsub import pub

class SpeedBoost(GameObject):
    def __init__(self, position, kind, id, size, physics):
        super().__init__(position, kind, id, size, physics)
        self.is_collected = False

    def collision(self, other):
        if other.kind == "player" and not self.is_collected:
            self.is_collected = True
            pub.sendMessage("speed_boost_collected", power_up=self)
            print("Speed boost collected!")

    def tick(self, dt):
        if self.is_collected:
            pub.sendMessage("remove_object", game_object=self)