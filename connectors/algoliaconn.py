from algoliasearch.search_client import SearchClient

ALGOLIA_APP_ID = "ZWY5JIVM1P"
ALGOLIA_API_KEY = "0501a59caa5bd2c7b5f3a199ce71da5c"
ALGOLIA_INDEX_NAME = "notes_content"
algoclient = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
algoindex = algoclient.init_index(ALGOLIA_INDEX_NAME)