import redis

REDIS_HOST='localhost'
REDIS_PORT=6379

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT
)

r.set("anya", 23)

print(r.get("any"))
