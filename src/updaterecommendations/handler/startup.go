package handler

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/benosborntech/recgen/utils/constants"
	"github.com/benosborntech/recgen/utils/misc"
	"github.com/benosborntech/recgen/utils/model"
	"github.com/redis/go-redis/v9"
)

func Startup(ctx context.Context, data model.Data, rdb *redis.Client) error {
	for key, value := range data {
		serialized, err := json.Marshal(value.Vector)
		if err != nil {
			return fmt.Errorf("serialize failed: %v", err)
		}

		if _, err := rdb.HSet(ctx, misc.KeyConcat(constants.DB_PREFIX, key), "title", value.Title, "description", value.Description, "vector", serialized).Result(); err != nil {
			return fmt.Errorf("set vector error: %v", err)
		}
	}

	if _, err := rdb.Do(ctx, "FT.CREATE", constants.VectorIndexName,
		"ON", "HASH",
		"PREFIX", "1", misc.KeyConcat(constants.DB_PREFIX, ""),
		"SCHEMA",
		"title", "TEXT",
		"description", "TEXT",
		"vector", "VECTOR", "HNSW", "12", "TYPE", "FLOAT32", "DIM", "1536", "DISTANCE_METRIC", "COSINE").Result(); err != nil && err.Error() != "Index already exists" {

		return fmt.Errorf("create index error: %v", err)
	}

	return nil
}
