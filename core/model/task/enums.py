from enum import Enum


class StatusEnum(str, Enum):
    CANCELLED = "Cancelled"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    NOT_DEFINED = "NotDefined"


class TaskTypeEnum(str, Enum):
    MOV_MARSH = "MovMarsh"


class SubtaskTypeEnum(str, Enum):
    MST_IN = "Mst_In"
    MST_OUT = "Mst_Out"
    SET_UNLOADING = "SetUnLoading"
    SET_LOADING = "SetLoading"


class MarshTemperatureProperty(int, Enum):
    HOT = 1
    COLD = 2
    UNDEFINED = 0


