package database

import (
	"fmt"

	"github.com/go-redis/redis/v8"
	"github.com/hmccarty/arc-assistant/internal/models"
)

func OpenRedisClient(config models.Config) (*DbClient, error) {
	return &RedisClient{
		Client: redis.NewClient(&redis.Options{
			Addr:     "localhost:6379",
			Password: "", // no password set
			DB:       0,  // use default DB
		}),
	}, nil
}

type RedisClient struct {
	Client *redis.Client
}

func (r *RedisClient) GetUserBalance(userID string) (float32, error) {
	key := fmt.Sprintf("user:%s:balance", userID)
	val, err := r.Client.Get(key).Result()
	if err != nil {
		return 0, err
	}
	return val, nil
}
