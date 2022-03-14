package database

import (
	"fmt"

	"github.com/go-redis/redis/v8"
	"github.com/hmccarty/arc-assistant/internal/services/config"
)

func OpenClient(config *config.Config) *RedisClient {
	return &RedisClient{
		Client: redis.NewClient(&redis.Options{
			Addr:     "localhost:6379",
			Password: "", // no password set
			DB:       0,  // use default DB
		}),
	}
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
