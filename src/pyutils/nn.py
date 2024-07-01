import json
import torch
import torch.nn as nn
import torch.nn.functional as F


class RecommendationModel(nn.Module):
    def __init__(self, embedding_dim: int):
        super(RecommendationModel, self).__init__()
        self.embedding_dim = embedding_dim
        self.user_embeddings = {}
        self.fc = nn.Linear(self.embedding_dim * 2, 1)

    def forward(self, user_id: str, item_emb: torch.Tensor) -> torch.Tensor:
        assert self.user_exists(user_id), "user does not exist"

        user_emb = self.user_embeddings[user_id]
        combined_emb = torch.cat((user_emb, item_emb), dim=1)
        output = torch.sigmoid(self.fc(combined_emb))

        return output

    def user_exists(self, user_id: str) -> bool:
        return user_id in self.user_embeddings

    def add_user(self, user_id: str) -> None:
        assert not self.user_exists(user_id), "user already exists"

        self.user_embeddings[user_id] = nn.Parameter(torch.randn(self.embedding_dim))

    def save(self) -> str:
        user_embeddings = {}
        for key in self.user_embeddings.keys():
            user_embeddings[key] = self.user_embeddings[key].tolist()

        state = {
            "model_dict": self.state_dict(),
            "user_dict": user_embeddings
        }

        return json.dumps(state)

    def load(self, state: str):
        obj = json.loads(state)

        self.load_state_dict(obj["model_dict"])
        
        user_embeddings = {}
        for key in obj["user_dict"].keys():
            user_embeddings[key] = torch.Tensor(obj["user_dict"])

        self.user_embeddings = user_embeddings