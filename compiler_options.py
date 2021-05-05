import enum


class LayoutType(enum.Enum):
    SimplePreDistilledStates = "Simple"


class SchedulingMode(enum.Enum):
    Sequential = "Sequential"
    Parallel = "Parallel"


class CompilerOptions:
    def __init__(self,
        layout_type : LayoutType = LayoutType.SimplePreDistilledStates,
        scheduling_mode: SchedulingMode = SchedulingMode.Sequential,
        apply_stabilizer_commuting_transform : bool = True):

        self.layout_type : LayoutType = layout_type
        self.scheduling_mode : SchedulingMode = scheduling_mode
        self.apply_stabilizer_commuting_transform : bool = apply_stabilizer_commuting_transform



