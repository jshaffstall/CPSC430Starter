class GameObject:
    def __init__(self, position, kind, id, size, physics):
        self.physics = physics
        self.position = position
        self.kind = kind
        self.id = id
        self.x_rotation = 0
        self.y_rotation = 0
        self.z_rotation = 0
        self.size = size

        # TODO: need a place to store the physics objects if the
        # subclasses create one
    #if kind == "crate":
    #if kind == "player":
    #dont do this

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        self._kind = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def x_rotation(self):
        return self._x_rotation

    @x_rotation.setter
    def x_rotation(self, value):
        self._x_rotation = value

    @property
    def y_rotation(self):
        return self._y_rotation

    @y_rotation.setter
    def y_rotation(self, value):
        self._y_rotation = value

    @property
    def z_rotation(self):
        return self._z_rotation

    @z_rotation.setter
    def z_rotation(self, value):
        self._z_rotation = value

    def tick(self):
        pass

    def clicked(self):
        pass

    def collision(self, other):
        pass
