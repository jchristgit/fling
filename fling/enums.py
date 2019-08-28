import enum


class BuildState(enum.Enum):
    SUCCESS = 'success'
    FAILED = 'failed'
    ERROR = 'error'
