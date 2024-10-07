import logging
import os

from azure.core.exceptions import ResourceExistsError
from azure.identity import AzureDeveloperCliCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    AzureOpenAIEmbeddingSkill,
    AzureOpenAIParameters,
    AzureOpenAIVectorizer,
    FieldMapping,
    HnswAlgorithmConfiguration,
    HnswParameters,
    IndexProjectionMode,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataSourceType,
    SearchIndexerIndexProjections,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    SearchIndexerSkillset,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    SplitSkill,
    VectorSearch,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)
from azure.storage.blob import BlobServiceClient
from rich.logging import RichHandler

from load_azd_env import load_azd_env

logging.basicConfig(level=logging.WARNING, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])
logger = logging.getLogger("voicerag")
logger.setLevel(logging.INFO)

NAME = "voicerag-intvect" # Used to name index, indexer, data source and skillset

load_azd_env()

AZURE_OPENAI_EMBEDDING_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
AZURE_OPENAI_EMBEDDING_MODEL = os.environ["AZURE_OPENAI_EMBEDDING_MODEL"]
EMBEDDINGS_DIMENSIONS = 3072
AZURE_SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
AZURE_STORAGE_ENDPOINT = os.environ["AZURE_STORAGE_ENDPOINT"]
AZURE_STORAGE_CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
AZURE_STORAGE_CONTAINER = os.environ["AZURE_STORAGE_CONTAINER"]

azure_credential = AzureDeveloperCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"], process_timeout=60)
index_client = SearchIndexClient(AZURE_SEARCH_ENDPOINT, azure_credential)
indexer_client = SearchIndexerClient(AZURE_SEARCH_ENDPOINT, azure_credential)

data_source_connections = indexer_client.get_data_source_connections()
if NAME in [ds.name for ds in data_source_connections]:
    logger.info(f"Data source connection {NAME} already exists, not re-creating")
else:
    logger.info(f"Creating data source connection: {NAME}")
    indexer_client.create_data_source_connection(
        data_source_connection=SearchIndexerDataSourceConnection(
            name=NAME, 
            type=SearchIndexerDataSourceType.AZURE_BLOB,
            connection_string=AZURE_STORAGE_CONNECTION_STRING,
            container=SearchIndexerDataContainer(name=AZURE_STORAGE_CONTAINER)))

index_names = [index.name for index in index_client.list_indexes()]
if NAME in index_names:
    logger.info(f"Index {NAME} already exists, not re-creating")
else:
    logger.info(f"Creating index: {NAME}")
    index_client.create_index(
        SearchIndex(
            name=NAME,
            fields=[
                SearchableField(name="chunk_id", key=True, analyzer_name="keyword", sortable=True),
                SimpleField(name="parent_id", type=SearchFieldDataType.String, filterable=True),
                SearchableField(name="title", filterable=True),
                SearchableField(name="chunk"),
                SearchField(
                    name="text_vector", 
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    vector_search_dimensions=EMBEDDINGS_DIMENSIONS,
                    vector_search_profile_name="vp",
                    stored=True,
                    hidden=False)
            ],
            vector_search=VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(name="algo", parameters=HnswParameters(metric=VectorSearchAlgorithmMetric.COSINE))
                ],
                vectorizers=[
                    AzureOpenAIVectorizer(
                        name="openai_vectorizer",
                        azure_open_ai_parameters=AzureOpenAIParameters(
                            resource_uri=AZURE_OPENAI_EMBEDDING_ENDPOINT,
                            deployment_id=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                            model_name=AZURE_OPENAI_EMBEDDING_MODEL
                        )
                    )
                ],
                profiles=[
                    VectorSearchProfile(name="vp", algorithm_configuration_name="algo", vectorizer="openai_vectorizer")
                ]
            ),
            semantic_search=SemanticSearch(
                configurations=[
                    SemanticConfiguration(
                        name="semsearch",
                        prioritized_fields=SemanticPrioritizedFields(title_field=SemanticField(field_name="title"), content_fields=[SemanticField(field_name="chunk")])
                    )
                ],
                default_configuration_name="semsearch"
            )
        )
    )

skillsets = indexer_client.get_skillsets()
if NAME in [skillset.name for skillset in skillsets]:
    logger.info(f"Skillset {NAME} already exists, not re-creating")
else:
    logger.info(f"Creating skillset: {NAME}")
    indexer_client.create_skillset(
        skillset=SearchIndexerSkillset(
            name=NAME,
            skills=[
                SplitSkill(
                    text_split_mode="pages",
                    context="/document",
                    maximum_page_length=2000,
                    page_overlap_length=500,
                    inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                    outputs=[OutputFieldMappingEntry(name="textItems", target_name="pages")]),
                AzureOpenAIEmbeddingSkill(
                    context="/document/pages/*",
                    resource_uri=AZURE_OPENAI_EMBEDDING_ENDPOINT,
                    api_key=None,
                    deployment_id=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                    model_name=AZURE_OPENAI_EMBEDDING_MODEL,
                    dimensions=EMBEDDINGS_DIMENSIONS,
                    inputs=[InputFieldMappingEntry(name="text", source="/document/pages/*")],
                    outputs=[OutputFieldMappingEntry(name="embedding", target_name="text_vector")])
            ],
            index_projection=SearchIndexerIndexProjections(
                selectors=[
                    SearchIndexerIndexProjectionSelector(
                        target_index_name=NAME,
                        parent_key_field_name="parent_id",
                        source_context="/document/pages/*",
                        mappings=[
                            InputFieldMappingEntry(name="chunk", source="/document/pages/*"),
                            InputFieldMappingEntry(name="text_vector", source="/document/pages/*/text_vector"),
                            InputFieldMappingEntry(name="title", source="/document/metadata_storage_name")
                        ]
                    )
                ],
                parameters=SearchIndexerIndexProjectionsParameters(
                    projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS
                )
            )))

indexers = indexer_client.get_indexers()
if NAME in [indexer.name for indexer in indexers]:
    logger.info(f"Indexer {NAME} already exists, not re-creating")
else:
    indexer_client.create_indexer(
        indexer=SearchIndexer(
            name=NAME,
            data_source_name=NAME,
            skillset_name=NAME,
            target_index_name=NAME,        
            field_mappings=[FieldMapping(source_field_name="metadata_storage_name", target_field_name="title")]
        )
    )

# Upload the documents in /data folder to the blob storage container
blob_client = BlobServiceClient(
    account_url=AZURE_STORAGE_ENDPOINT, credential=azure_credential,
    max_single_put_size=4 * 1024 * 1024
)
container_client = blob_client.get_container_client(AZURE_STORAGE_CONTAINER)
if not container_client.exists():
    container_client.create_container()
existing_blobs = [blob.name for blob in container_client.list_blobs()]

# Open each file in /data folder
for file in os.scandir("data"):
    with open(file.path, "rb") as opened_file:
        filename = os.path.basename(file.path)
        # Check if blob already exists
        if filename in existing_blobs:
            logger.info("Blob already exists, skipping file: %s", filename)
        else:
            logger.info("Uploading blob for file: %s", filename)
            blob_client = container_client.upload_blob(filename, opened_file, overwrite=True)

# Start the indexer
try:
    indexer_client.run_indexer(NAME)
    logger.info("Indexer started. Any unindexed blobs should be indexed in a few minutes, check the Portal for status.")
except ResourceExistsError:
    logger.info("Indexer already running, not starting again")