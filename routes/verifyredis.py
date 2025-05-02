import redis

try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
    print("Connected to Redis!")
except redis.ConnectionError as e:
    print(f"Redis connection error: {e}")
