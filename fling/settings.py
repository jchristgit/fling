import enum


class Trust(enum.Enum):
    EVERYONE = 'everyone'
    MAINTAINERS = 'maintainers'

    def __str__(self):
        return self.value
