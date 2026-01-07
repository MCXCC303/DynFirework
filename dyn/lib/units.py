import math
from dataclasses import dataclass

from PyQt5.QtGui import QColor


class MinecraftVelocity:
    def __init__(self, vx: float, vy: float, vz: float):
        self._vx = vx
        self._vy = vy  # 纵向速度
        self._vz = vz
        pass

    """
    速度固定为只读，通过爆炸系数（原speed/radius_speed参数）决定初速度矢量
    """

    @property
    def vx(self):
        return self._vx

    @property
    def vy(self):
        return self._vy

    @property
    def vz(self):
        return self._vz

    @property
    def vector(self):
        # TODO
        return

    @vector.setter
    def vector(self, value):
        pass


@dataclass
class Position:
    x: float
    y: float
    z: float
    label: str
    main_color: tuple


class MinecraftPosition:
    def __init__(
            self,
            x: float,
            y: float,
            z: float,
            label: str,
            main_color: QColor,
    ):
        self._x = round(x, 2)
        self._y = round(y, 2)  # 纵轴
        self._z = round(z, 2)
        self._label = label
        self._main_color = main_color

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value: float):
        self._x = round(float(value), 2)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value: float):
        self._y = round(float(value), 2)

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value: float):
        self._z = round(float(value), 2)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value: str):
        self._label = value

    @property
    def spherical(self):
        """
        (x, y, z) -> (r, theta, phi) full spherical
        """
        r = math.sqrt(self._x ** 2 + self._y ** 2 + self._z ** 2)
        theta = math.acos(self._y / r)
        phi = math.atan2(self._z, self._x)
        if phi < 0:
            phi += 2 * math.pi
        return r, theta, phi

    @property
    def y_flatten_polar(self):
        """
        (x, y, z) -> (r, theta) with specified y
        """
        r = math.sqrt(self._x ** 2 + self._z ** 2)
        theta = math.atan2(self._z, self._x)
        return self._y, r, theta

    @property
    def pix_color(self):
        return self._main_color

    @property
    def position_text(self):
        return f"({self.x}, {self.y}, {self.z})"

    @property
    def export_obj(self):
        return Position(self.x, self.y, self.z, self.label, self.pix_color.getRgb())


@dataclass
class MinecraftTick:
    tick: int = None
    time: int = None

    # _frame_per_sec: int = None

    def __post_init__(self):
        if self.tick and not self.time:
            return
        if not self.tick:
            try:
                self.tick = self.time * 20
                return
            except:
                raise ValueError("At least 1 time unit provide needed.")
        if self.tick and self.time and self.to_time == self.time:
            return
        else:
            raise ValueError(
                f"tick-time validation not passed: {self.time}s to {self.tick}t."
            )

    def __repr__(self):
        return f"{self.tick}t"

    def __str__(self):
        return self.__repr__()

    def __add__(self, other):
        if isinstance(other, MinecraftTick):
            return MinecraftTick(other.tick + self.tick)
        elif isinstance(other, (int, float)):
            return MinecraftTick(int(other * 20) + self.tick)
        else:
            raise TypeError(
                f"MinecraftTick object could not calculate with {other.__class__.__name__} type."
            )

    @property
    def to_time(self):
        return self.tick / 20
