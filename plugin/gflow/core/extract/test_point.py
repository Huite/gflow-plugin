from gflow.core.extract.extraction_base import Extraction
from gflow.core.memory_layer import PointMemoryLayer


class TestPointExtraction(Extraction):
    name = "gflow Test Point"
    attributes = (
        "x",
        "y",
        "z",
        "porosity",
        "conductivity",
        "base_elevation",
        "net_recharge",
        "leakage_bottom",
        "head",
        "lower_head",
        "resistance",
        "vx",
        "vy",
        "vz",
        "label",
    )

    @classmethod
    def layer_class(cls):
        return PointMemoryLayer
