from panda3d.core import Quat, lookAt, Vec3
from game_object import GameObject
from pubsub import pub

class Player(GameObject):
    def __init__(self, position, kind, id, size, physics):
        super().__init__(position, kind, id, size, physics)
        self.base_speed = 0.1
        self.speed = self.base_speed
        self.boost_active = False
        self.boost_timer = 0.0
        self.boost_duration = 7.0  # 7 seconds
        pub.subscribe(self.input_event, 'input')
        pub.subscribe(self.handle_speed_boost, 'speed_boost_collected')

    def handle_speed_boost(self, power_up):
        self.boost_active = True
        self.boost_timer = self.boost_duration
        self.speed = self.base_speed * 2  #double players speed
        print("Speed boost activated!")

    def tick(self, dt):
        if self.boost_active:
            self.boost_timer -= dt
            if self.boost_timer <= 0:
                self.boost_active = False
                self.speed = self.base_speed
                print("Speed boost ended!")

    def input_event(self, events=None):
        pass

    def collision(self, other):
        pass

    # Override these and don't defer to the physics object
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value