package model

type Body struct {
	UserId   string `json:"userId"`
	ItemId   string `json:"itemId"`
	Positive bool   `json:"positive"`
}

type SearchResult struct {
	ItemId string  `json:"itemId"`
	Score  float64 `json:"score"`
}
