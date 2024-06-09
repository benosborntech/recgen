package handler

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/benosborntech/recgen/utils/config"
	"github.com/benosborntech/recgen/utils/constants"
	"github.com/benosborntech/recgen/utils/misc"
	"github.com/benosborntech/recgen/utils/model"
	"github.com/bsm/redislock"
	"github.com/redis/go-redis/v9"
)

const duration = 30 * time.Second
const pageSize = 20

func UpdateRecommendations(cfg *config.Config, body model.Body, rdb *redis.Client, lockClient *redislock.Client) error {
	for {
		lock, err := lockClient.Obtain(cfg.Context, misc.KeyConcat(constants.LOCK_PREFIX, body.UserId), duration, &redislock.Options{})
		if err == redislock.ErrNotObtained {
			continue
		} else if err != nil {
			return fmt.Errorf("lock error: %v", err)
		}
		defer lock.Release(cfg.Context)

		if body.Positive {
			// First we will look the element up by its value using some kind of database search to find the corresponding vector
			vectorRaw, err := rdb.HGet(cfg.Context, misc.KeyConcat(constants.DB_PREFIX, body.ItemId), "vector").Result()
			if err != nil {
				return fmt.Errorf("get item error: %v", err)
			}
			var vectorArr []string
			if err := json.Unmarshal([]byte(vectorRaw), &vectorArr); err != nil {
				return fmt.Errorf("parse vector error: %v", err)
			}
			vector := strings.Join(vectorArr, " ")

			// Then we search for a list of new vectors, rank them, then attempt to add them to our list
			cursor := 0
			condition := true

			var count int64

			for condition {
				res, err := rdb.Do(cfg.Context, "FT.SEARCH", constants.VectorIndexName, "*=>[KNN 10 @embedding $vec AS score]",
					"SORTBY", "score", "DESC", "LIMIT", cursor, pageSize, "PARAMS", "2", "vec", vector).Result()
				if err != nil {
					return fmt.Errorf("vector search error: %v", err)
				}

				results := []model.SearchResult{}
				for _, item := range res.([]interface{}) {
					results = append(results, model.SearchResult{
						ItemId: item.(map[string]interface{})["itemId"].(string),
						Score:  item.(map[string]interface{})["score"].(float64),
					})
				}

				for _, result := range results {
					exists, err := rdb.BFExists(cfg.Context, misc.KeyConcat(constants.BF_PREFIX, body.UserId), body.ItemId).Result()
					if err != nil {
						return fmt.Errorf("bloom filter exists failed: %v", err)
					} else if exists {
						continue
					}

					if _, err := rdb.ZAdd(cfg.Context, misc.KeyConcat(constants.SET_PREFIX, body.UserId), redis.Z{Score: result.Score, Member: body.ItemId}).Result(); err != nil {
						return fmt.Errorf("add item to set failed: %v", err)
					}
				}

				count, err = rdb.ZCount(cfg.Context, misc.KeyConcat(constants.SET_PREFIX, body.UserId), "0", "1").Result()
				if err != nil {
					return fmt.Errorf("set count failed: %v", err)
				}

				condition = count < constants.MaxRecommendations && len(results) == int(count)
				cursor += pageSize
			}

			// Remove extra items from the set
			toRemove := count - constants.MaxRecommendations

			if toRemove > 0 {
				if _, err := rdb.ZPopMin(cfg.Context, misc.KeyConcat(constants.SET_PREFIX, body.UserId), toRemove).Result(); err != nil {
					return fmt.Errorf("pop items failed: %v", err)
				}
			}
		} else {
			if _, err := rdb.BFAdd(cfg.Context, misc.KeyConcat(constants.BF_PREFIX, body.UserId), body.ItemId).Result(); err != nil {
				return fmt.Errorf("bloom filter add error: %v", err)
			}

			if _, err := rdb.ZRem(cfg.Context, misc.KeyConcat(constants.SET_PREFIX, body.UserId), body.ItemId).Result(); err != nil {
				return fmt.Errorf("sorted set remove error: %v", err)
			}
		}

		return nil
	}
}
