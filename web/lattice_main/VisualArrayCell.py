class VisualArrayCell:
    def __init__(self, patch_type, edges): # patch_type: patches.PatchType, edges : dict[patches.Orientation, patches.EdgeType]
        self.edges = edges
        self.patch_type = patch_type
        self.text = None
        self.activity: Optional[QubitActivity] = None