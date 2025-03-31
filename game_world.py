from panda3d.bullet import BulletWorld, BulletBoxShape, BulletRigidBodyNode, BulletCapsuleShape, ZUp, BulletSphereShape
from panda3d.core import Vec3, TransformState, VBase3, Point3, LColor
from pubsub import pub
from game_object import GameObject
from player import Player
from teleporter import Teleporter


class GameWorld:
    def __init__(self, debugNode):
        self.properties = {
            "score": 0,
            "time_remaining": 60.0,
            "game_over": False,
            "quit": False
        }
        self.game_objects = {}
        self.next_id = 0
        self.physics_world = BulletWorld()
        self.physics_world.setGravity(Vec3(0, 0, -9.81))
        self.physics_world.setDebugNode(debugNode)

        self.kind_to_shape = {
            "crate": self.create_box,
            "floor": self.create_box,
            "ball": self.create_sphere,
            "goal": self.create_box,
            "wall": self.create_box,
            "red box": self.create_box,
            "teleporter": self.create_box,
        }

    def create_capsule(self, position, size, kind, mass):
        radius = size[0]
        height = size[1]
        shape = BulletCapsuleShape(radius, height, ZUp)
        # node = BulletCharacterControllerNode(shape, radius, kind)
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        node.setRestitution(0.0)
        # node.setKinematic(True)

        node.setTransform(TransformState.makePos(VBase3(position[0], position[1], position[2])))

        # self.physics_world.attachCharacter(node)
        self.physics_world.attachRigidBody(node)

        return node

    def create_box(self, position, size, kind, mass):
        # The box shape needs half the size in each dimension
        shape = BulletBoxShape(Vec3(size[0] / 2, size[1] / 2, size[2] / 2))
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        node.setTransform(TransformState.makePos(VBase3(position[0], position[1], position[2])))
        node.setRestitution(0.0)
        if kind == "goal":
            node.setPythonTag("color", LColor(1, 1, 1, 1))
        self.physics_world.attachRigidBody(node)
        return node

    def create_sphere(self, position, size, kind, mass):
        radius = size[0] / 2
        shape = BulletSphereShape(radius)
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        node.setTransform(TransformState.makePos(VBase3(position[0], position[1], position[2])))
        node.setRestitution(0.5)
        self.physics_world.attachRigidBody(node)

        return node

    def create_physics_object(self, position, kind, size, mass):
        if kind in self.kind_to_shape:
            return self.kind_to_shape[kind](position, size, kind, mass)

        return None

    def create_object(self, position, kind, size, mass, subclass, z_rotation=0):
        physics = self.create_physics_object(position, kind, size, mass)
        obj = subclass(position, kind, self.next_id, size, physics)
        obj.z_rotation = z_rotation # set for goal rotation issue
        if physics:
            transform = TransformState.makePosHpr(VBase3(position[0], position[1], position[2]), VBase3(z_rotation, 0, 0))
            physics.setTransform(transform)
        self.next_id += 1
        self.game_objects[obj.id] = obj

        pub.sendMessage('create', game_object=obj)
        return obj

    def check_goal(self, ball):
        goal = next((obj for obj in self.game_objects.values() if obj.kind == "goal"), None)
        if not goal or not ball:
            return False
        ball_pos = ball.position
        goal_pos = goal.position
        goal_size = goal.size
        if (abs(ball_pos[0] - goal_pos[0]) < goal_size[0] / 2 + 0.5 and
            abs(ball_pos[1] - goal_pos[1]) < goal_size[1] / 2 + 0.5 and
            ball_pos[2] < goal_size[2]):
            return True
        return False

    def reset_ball(self, ball):
        ball.physics.setTransform(TransformState.makePos(VBase3(0, 0, 0.5)))
        ball.physics.setLinearVelocity(Vec3(0, 0, 0))

    def tick(self, dt):
        for id in self.game_objects:
            self.game_objects[id].tick(dt)

        for id in self.game_objects:
            if self.game_objects[id].is_collision_source:
                contacts = self.get_all_contacts(self.game_objects[id])

                for contact in contacts:
                    if contact.getNode1() and contact.getNode1().getPythonTag("owner"):
                        # Notify both objects about the collision
                        contact.getNode1().getPythonTag("owner").collision(self.game_objects[id])
                        self.game_objects[id].collision(contact.getNode1().getPythonTag("owner"))

        self.physics_world.doPhysics(dt)

        if not self.properties["game_over"]:
            self.properties["time_remaining"] -= dt
            ball = next((obj for obj in self.game_objects.values() if obj.kind == "ball"), None)
            if ball and self.check_goal(ball):
                self.properties["score"] += 1
                pub.sendMessage('property', key="score", value=self.properties["score"])
                self.reset_ball(ball)
            if self.properties["time_remaining"] <= 0:
                self.properties["game_over"] = True
                pub.sendMessage("game_event", event="end")

    def load_world(self):
        #floor
        self.create_object([0, 0, -5], "floor", (40, 40, 2), 0, GameObject)

        #player starting position
        self.create_object([0, -5, 10], "player", (1, 0.5, 0.25, 0.5), 10, Player)
        #soccer ball starting position
        self.create_object([0, 0, 0.5], "ball", (0.5, 0.5, 0.5), 1, GameObject)
        #soccer goal
        self.create_object([0, 10, -4.5], "goal", (3, 1, 2), 0, GameObject, z_rotation=180)
        # four walls enclosing field
        self.create_object([0, 20.5, -2.5], "wall", (40, 1, 5), 0, GameObject)
        self.create_object([0, -20.5, -2.5], "wall", (40, 1, 5), 0, GameObject)
        self.create_object([20.5, 0, -2.5], "wall", (1, 40, 5), 0, GameObject)
        self.create_object([-20.5, 0, -2.5], "wall", (1, 40, 5), 0, GameObject)
        #jay additions 3/31
        self.create_object([3, 0, 0], "crate", (5, 2, 1), 10, GameObject)
        self.create_object([-3, 0, -4], "teleporter", (1, 1, 1), 0, Teleporter)
        player = self.create_object([0, -20, 0], "player", (1, 0.5, 0.25, 0.5), 10, Player)
        player.is_collision_source = True
        self.create_object([0, 0, -5], "crate", (1000, 1000, 0.5), 0, GameObject)

    def get_property(self, key):
        return self.properties.get(key)

    def set_property(self, key, value):
        self.properties[key] = value

        pub.sendMessage('property', key=key, value=value)

    def get_nearest(self, from_pt, to_pt):
        # This shows the technique of near object detection using the physics engine.
        fx, fy, fz = from_pt
        tx, ty, tz = to_pt
        result = self.physics_world.rayTestClosest(Point3(fx, fy, fz), Point3(tx, ty, tz))
        return result

    # TODO: use this to demonstrate a teleporting trap
    def get_all_contacts(self, game_object):
        if game_object.physics:
            return self.physics_world.contactTest(game_object.physics).getContacts()

        return []
