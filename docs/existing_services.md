# Connecting VoiceRAG to existing services

VoiceRAG can be connected to existing Azure services, such as Azure OpenAI and Azure Search. This guide will show you how to reuse existing services in your Azure subscription.

* [Reuse existing OpenAI real-time deployment](#reuse-existing-openai-real-time-deployment)
* [Reuse existing index from azure-search-openai-demo](#reuse-existing-index-from-azure-search-openai-demo)

## Reuse existing OpenAI real-time deployment

Run these commands _before_ running `azd up`:

1. Run this command to ensure that the [infrastructure](../infra/main.bicep) does not make a brand new OpenAI service:

    ```bash
    azd env set AZURE_OPENAI_REUSE_EXISTING true
    ```

2. Run this command to ensure that the [infrastructure](../infra/main.bicep) assigns the proper RBAC roles for accessing the OpenAI resource:

    ```bash
    azd env set AZURE_OPENAI_RESOURCE_GROUP <YOUR_RESOURCE_GROUP>
    ```

3. Run this command to point the app code at your Azure OpenAI endpoint:

    ```bash
    azd env set AZURE_OPENAI_ENDPOINT https://<YOUR_OPENAI_SERVICE>.openai.azure.com
    ```

4. Run this command to point the app code at your Azure OpenAI real-time deployment. Note that the deployment name may be different from the model name:

    ```bash
    azd env set AZURE_OPENAI_REALTIME_DEPLOYMENT <YOUR_REALTIME_DEPLOYMENT_NAME>
    ```

## Reuse existing index from azure-search-openai-demo

If you are using the popular RAG solution [azure-search-openai-demo](https://www.github.com/Azure-samples/azure-search-openai-demo), you can connect VoiceRAG to the existing index by setting the following `azd` environment variables.
Run these commands _before_ running `azd up`.

1. Run this command to ensure that the [infrastructure](../infra/main.bicep) does not make a brand new Azure Search service:

    ```bash
    azd env set AZURE_SEARCH_REUSE_EXISTING true
    ```

2. Run this command to ensure that the [infrastructure](../infra/main.bicep) assigns the proper RBAC roles for accessing the Azure Search resource:

    ```bash
    azd env set AZURE_SEARCH_SERVICE_RESOURCE_GROUP <YOUR_RESOURCE_GROUP>
    ```

3. Run this command to point the app code at your Azure Search service:

    ```bash
    azd env set AZURE_SEARCH_ENDPOINT https://<YOUR_SEARCH_SERVICE>.search.windows.net
    ```

4. Run these commands to point the app code at the existing index and fields:

    ```bash
    azd env set AZURE_SEARCH_SEMANTIC_CONFIGURATION default
    azd env set AZURE_SEARCH_IDENTIFIER_FIELD id
    azd env set AZURE_SEARCH_CONTENT_FIELD content
    azd env set AZURE_SEARCH_TITLE_FIELD sourcepage
    azd env set AZURE_SEARCH_EMBEDDING_FIELD embedding
    azd env set AZURE_SEARCH_REUSE_EXISTING true
    azd env set AZURE_SEARCH_INDEX gptkbindex
    ```

5. (Optional) Run this command to disable vector search:

    ```bash
    azd env set AZURE_SEARCH_USE_VECTOR_QUERY false
    ```

    This variable is not needed if your search index has a built-in vectorizer,
    which was added to the `azure-search-openai-demo` index setup in the October 17, 2024 release.

### Development server

Alternatively, you can first test the solution locally with the `azure-search-openai-demo` index by creating a `.env` file in `app/backend` with contents like the following:

```bash
AZURE_TENANT_ID=<YOUR-TENANT-ID>
AZURE_OPENAI_ENDPOINT=https://<YOUR_OPENAI_ENDPOINT>.openai.azure.com
AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-realtime-preview
AZURE_OPENAI_REALTIME_VOICE_CHOICE=<choose one: echo, alloy, shimmer>
AZURE_SEARCH_ENDPOINT=https://<YOUR_SEARCH_SERVICE>.search.windows.net
AZURE_SEARCH_INDEX=gptkbindex
AZURE_SEARCH_SEMANTIC_CONFIGURATION=default
AZURE_SEARCH_IDENTIFIER_FIELD=id
AZURE_SEARCH_CONTENT_FIELD=content
AZURE_SEARCH_TITLE_FIELD=sourcepage
AZURE_SEARCH_EMBEDDING_FIELD=embedding
```

Then follow the steps in the project's [README](../README.md@#development-server) to run the app locally.
