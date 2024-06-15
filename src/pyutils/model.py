from typing import TypedDict, Dict, List

class DataObject(TypedDict):
    title: str
    description: str
    vector: List[float]

Data = Dict[str, DataObject]