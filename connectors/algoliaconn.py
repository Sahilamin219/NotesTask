"""
Initialize Algolia search client and index.

- `ALGOLIA_APP_ID`: The Algolia Application ID.
- `ALGOLIA_API_KEY`: The Algolia API Key.
- `ALGOLIA_INDEX_NAME`: The name of the Algolia index for notes content.
- `algoclient`: The Algolia search client instance created with the provided application ID and API key.
- `algoindex`: The Algolia index instance initialized with the provided index name.

This code snippet sets up the Algolia search client and index to enable searching and indexing notes content.
"""


from algoliasearch.search_client import SearchClient

ALGOLIA_APP_ID = "ZWY5JIVM1P"
ALGOLIA_API_KEY = "0501a59caa5bd2c7b5f3a199ce71da5c"
ALGOLIA_INDEX_NAME = "notes_content"
algoclient = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
algoindex = algoclient.init_index(ALGOLIA_INDEX_NAME)