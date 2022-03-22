from pygame.math import Vector2

class VEC(Vector2):
    def __add__(self, other: Vector2) -> Vector2:
        return VEC(super().__add__(other))

    def __sub__(self, other: Vector2) -> Vector2:
        return VEC(super().__sub__(other))

    def __mul__(self, other: float) -> Vector2:
        return VEC(super().__mul__(other))

    def __truediv__(self, other: float) -> Vector2:
        return VEC(super().__truediv__(other))

    def __floordiv__(self, other: float) -> Vector2:
        return VEC(super().__floordiv__(other))

    def normalize(self) -> Vector2:
        try:
            return super().normalize()
        except ValueError:
            return self