import enum


class BuildState(enum.Enum):
    ERROR = 'error'
    FAILED = 'failed'
    PENDING = 'pending'
    SUCCESS = 'success'
    WARNING = 'warning'
