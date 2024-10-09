
# Manual setup guide

You'll need instances of the following Azure services. You can re-use service instances you have already or create new ones.

1. [Azure OpenAI](https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesOpenAI), with 2 model deployments, one of the **gpt-4o-realtime-preview** model, and one for embeddings (e.g.text-embedding-3-large, text-embedding-3-small, or text-embedding-ada-002)
1. [Azure AI Search](https://ms.portal.azure.com/#create/Microsoft.Search), any tier Basic or above will work, ideally with [Semantic Search enabled](https://learn.microsoft.com/azure/search/semantic-how-to-enable-disable)
1. [Azure Blob Storage](https://ms.portal.azure.com/#create/Microsoft.StorageAccount-ARM), with a container that has the content that represents your knowledge base (we include some sample data in this repo if you want an easy starting point)

## Creating an index

RAG applications use a retrieval system to get the right grounding data for LLMs. We use Azure AI Search as our retrieval system, so we need to get our knowledge base (e.g. documents or any other content you want the app to be able to talk about) into an Azure AI Search index.

### Using an already existing Azure AI Search index

You can use an existing index directly. If you created that index using the "Import and vectorize data" option in the portal, no further changes are needed. Otherwise, you'll need to update the field names in the [code](https://github.com/Azure-Samples/aisearch-openai-rag-audio/blob/main/app/backend/ragtools.py) to match your text/vector fields.

### Creating a new index with sample data or your own

Follow these steps to create a new index. We'll create a setup where once created, you can add, delete, or update your documents in blob storage and the index will automatically follow the changes.

1. Upload your documents to an Azure Blob Storage container. An easy way to do this is using the Azure Portal: navigate to the container and use the upload option to move your content (e.g. PDFs, Office docs, etc.)
1. In the Azure Portal, go to your Azure AI Search service and select "Import and vectorize data", choose Blob Storage, then point at your container and follow the rest of the steps on the screen.
1. Once the indexing process completes, you'll have a search index ready for vector and hybrid search.

For more details on ingesting data in Azure AI Search using "Import and vectorize data", here's a [quickstart](https://learn.microsoft.com/en-us/azure/search/search-get-started-portal-import-vectors).
