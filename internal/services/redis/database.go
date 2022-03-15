package database

import (
	"fmt"

	"context"
	"strconv"

	"github.com/go-redis/redis/v8"
	m "github.com/hmccarty/arc-assistant/internal/models"
	c "github.com/hmccarty/arc-assistant/internal/services/config"
)

func OpenRedisClient(config *c.Config) (m.DbClient, error) {
	return &RedisClient{
		client: redis.NewClient(&redis.Options{
			Addr:     "localhost:6379",
			Password: "", // no password set
			DB:       0,  // use default DB
		}),
	}, nil
}

type RedisClient struct {
	client *redis.Client
}

func (r *RedisClient) GetUserBalance(userID string) (float64, error) {
	key := fmt.Sprintf("user:%s:balance", userID)
	ctx := context.Background()
	val, err := r.client.Get(ctx, key).Result()
	if err != nil {
		return 0, err
	}

	balance, err := strconv.ParseFloat(val, 64)
	return balance, nil
}

func (r *RedisClient) SetUserBalance(userID string, balance float64) error {
	key := fmt.Sprintf("user:%s:balance", userID)
	ctx := context.Background()
	return r.client.Set(ctx, key, balance, 0).Err()
}
