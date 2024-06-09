package handler

import (
	"fmt"
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
const maxRecommendations = 10

func UpdateRecommendations(cfg *config.Config, body model.Body, rdb *redis.Client, lockClient *redislock.Client) error {
	for {
		lock, err := lockClient.Obtain(cfg.Context, body.UserId, duration, &redislock.Options{})
		if err == redislock.ErrNotObtained {
			continue
		} else if err != nil {
			return fmt.Errorf("lock error: %v", err)
		}
		defer lock.Release(cfg.Context)

		if body.Positive {
			// First we will look the element up by its value using some kind of database search to find the corresponding vector
			vectorJson, err := rdb.HGet(cfg.Context, constants.DBName, body.ItemId).Result()
			if err != nil {
				return fmt.Errorf("get item error: %v", err)
			}

			// Then we search for a list of new vectors, rank them, then attempt to add them to our list
			cursor := 0
			condition := true

			var count int64

			for condition {
				res, err := rdb.Do(cfg.Context, "FT.SEARCH", constants.VectorIndexName, "*=>[KNN 10 @embedding $vec AS score]",
					"SORTBY", "score", "DESC", "LIMIT", cursor, pageSize, "PARAMS", "2", "vec", vectorJson).Result()
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
					exists, err := rdb.BFExists(cfg.Context, body.UserId, body.ItemId).Result()
					if err != nil {
						return fmt.Errorf("bloom filter exists failed: %v", err)
					} else if exists {
						continue
					}

					if _, err := rdb.ZAdd(cfg.Context, body.UserId, redis.Z{Score: result.Score, Member: body.ItemId}).Result(); err != nil {
						return fmt.Errorf("add item to set failed: %v", err)
					}
				}

				count, err = rdb.ZCount(cfg.Context, body.UserId, "0", "1").Result()
				if err != nil {
					return fmt.Errorf("set count failed: %v", err)
				}

				condition = count < maxRecommendations && len(results) == int(count)
				cursor += pageSize
			}

			// Remove extra items from the set
			toRemove := count - maxRecommendations

			if toRemove > 0 {
				if _, err := rdb.ZPopMin(cfg.Context, body.UserId, toRemove).Result(); err != nil {
					return fmt.Errorf("pop items failed: %v", err)
				}
			}
		} else {
			if _, err := rdb.Do(cfg.Context, "BF.INSERT", append([]interface{}{body.UserId, "CAPACITY", 1000, "ERROR", 0.01, "ITEMS"}, misc.StringToISlice([]string{body.ItemId})...)).Result(); err != nil {
				return fmt.Errorf("bloom filter insert error: %v", err)
			}

			if _, err := rdb.ZRem(cfg.Context, body.UserId, body.ItemId).Result(); err != nil {
				return fmt.Errorf("sorted set remove error: %v", err)
			}
		}

		return nil
	}
}
