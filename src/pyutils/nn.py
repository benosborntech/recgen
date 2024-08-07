import torch
import torch.nn as nn
from torch.utils.data import Dataset
from src.pyutils.model import Body, Data


class RecommendationModel(nn.Module):
    def __init__(self, embedding_dim: int):
        super(RecommendationModel, self).__init__()
        self.embedding_dim = embedding_dim
        self.user_embeddings = nn.ParameterDict()
        self.fc = nn.Linear(self.embedding_dim * 2, 1)

    def forward(self, user_id: list[str], item_emb: torch.Tensor) -> torch.Tensor:
        user_embs = []
        for id in user_id:
            if not self.user_exists(id):
                raise Exception(f"user '{id}' does not exist")

            user_embs.append(self.user_embeddings[id])

        combined_emb = torch.cat((torch.stack(user_embs), item_emb), dim=1)
        output = torch.sigmoid(self.fc(combined_emb))

        return output

    def user_exists(self, user_id: str) -> bool:
        return user_id in self.user_embeddings

    def add_user(self, user_id: str) -> None:
        if self.user_exists(user_id):
            raise Exception(f"user '{user_id}' already exists")

        self.user_embeddings[user_id] = nn.Parameter(torch.randn(self.embedding_dim))

    def load_state_dict(self, state_dict, strict=True):
        for key in state_dict.keys():
            if key.startswith("user_embeddings."):
                user_id = key.split(".")[1]
                if not self.user_exists(user_id):
                    self.user_embeddings[user_id] = nn.Parameter(torch.randn(self.embedding_dim))
        
        super().load_state_dict(state_dict, strict)

class RecommendationDataset(Dataset):
    def __init__(self, data: list[Body], embedding_dim: int, item_data: Data):
        self.data = data
        self.embedding_dim = embedding_dim
        self.item_data = item_data
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx: int):
        item = self.data[idx]

        user_id = item["userId"]
        item_emb = torch.tensor(self.item_data[item["itemId"]]["vector"])
        label = torch.tensor([1.0]) if item["positive"] else torch.tensor([0.0])

        return user_id, item_emb, label