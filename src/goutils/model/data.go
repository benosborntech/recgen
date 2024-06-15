package model

type DataObject struct {
	Title       string    `json:"title"`
	Description string    `json:"description"`
	Vector      []float32 `json:"vector"`
}

type Data = map[string]DataObject
