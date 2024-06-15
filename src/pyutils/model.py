from typing import TypedDict, Dict, List


class DataObject(TypedDict):
    id: str
    title: str
    description: str
    vector: List[float]

Data = Dict[str, DataObject]

class Body(TypedDict):
	userId: str
	itemId: str
	positive: bool