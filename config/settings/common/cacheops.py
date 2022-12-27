# Caching with cacheops
CACHEOPS_REDIS = {
    'host': 'redis',     # redis-server is on same machine
    'port': 6379,        # default redis port
    'db': 1,             # SELECT non-default redis database
                         # using separate redis db or redis instance
                         # is highly recommended
    'socket_timeout': 3  # connection timeout in seconds, optional
}

CACHEOPS = {
    # Automatically cache any User.objects.get() calls for 15 minutes
    # This includes request.user or post.author access,
    # where Post.author is a foreign key to auth.User
    'auth.user': {'ops': 'get', 'timeout': 60*15},

    # Automatically cache all gets and queryset fetches
    # to other django.contrib.auth models for an hour
    'auth.*': {'ops': ('fetch', 'get'), 'timeout': 60*60},

    # Cache gets, fetches, counts and exists to Permission
    # 'all' is just an alias for ('get', 'fetch', 'count', 'exists')
    'auth.permission': {'ops': 'all', 'timeout': 60*60},
}
