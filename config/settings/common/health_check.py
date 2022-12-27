# Settings for custom health checks
#
# Defines rules for each health checks
# (module, timeout for cache, API keys and others)
# ``backend`` is reference of custom health check
# in `config` defines api keys for API
#  `timeout` define time for cache (in seconds)
# Example:
#     'geocoding_health_check': {
#             'backend': 'libs.health.backends.google_maps.'
#                        'GoogleMapsGeocodingCheckBackend',
#             'timeout': 3600,
#             'config': {
#                 'API_KEY': 'GOOGLE_API_KEY',
#             },

HEALTH_CHECK_SETTINGS = {

    }

HEALTH_CHECKS_APPS = (
    'libs.health',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.celery',
    'health_check.contrib.psutil',
    'health_check.contrib.s3boto3_storage',
)
