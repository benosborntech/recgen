package handler

import (
	"context"
	"fmt"
	"strings"

	"github.com/benosborntech/recgen/goutils/constants"
	"github.com/benosborntech/recgen/goutils/misc"
	"github.com/benosborntech/recgen/goutils/model"
	"github.com/redis/go-redis/v9"
)

func Startup(ctx context.Context, data model.Data, rdb *redis.Client) error {
	for key, value := range data {
		vectorString := []string{}
		for _, elem := range value.Vector {
			vectorString = append(vectorString, fmt.Sprint(elem))
		}
		vector := strings.Join(vectorString, " ")

		if _, err := rdb.HSet(ctx, misc.KeyConcat(constants.DB_PREFIX, key), "title", value.Title, "description", value.Description, "vector", vector).Result(); err != nil {
			return fmt.Errorf("set vector error: %v", err)
		}
	}

	if _, err := rdb.Do(ctx, "FT.CREATE", constants.VectorIndexName,
		"ON", "HASH",
		"PREFIX", "1", misc.KeyConcat(constants.DB_PREFIX, ""),
		"SCHEMA",
		"title", "TEXT",
		"description", "TEXT",
		"vector", "VECTOR", "HNSW", "6", "TYPE", "FLOAT32", "DIM", "1536", "DISTANCE_METRIC", "COSINE").Result(); err != nil && err.Error() != "Index already exists" {

		return fmt.Errorf("create index error: %v", err)
	}

	return nil
}
