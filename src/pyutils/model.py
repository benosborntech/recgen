from typing import TypedDict, Dict, List
import numpy as np


class DataObject(TypedDict):
    id: str
    title: str
    description: str
    vector: np.array

Data = Dict[str, DataObject]

class Body(TypedDict):
	userId: str
	itemId: str
	positive: bool