using './main.bicep'

// AZD environment variables
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'voicerag')
param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP', '')
param location = readEnvironmentVariable('AZURE_LOCATION', 'eastus2')
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')

// Azure Open AI
param openAiResourceLocation = readEnvironmentVariable('AZURE_OPENAI_LOCATION', 'eastus2')
param openAiServiceName = readEnvironmentVariable('AZURE_OPENAI_SERVICE', '')
param openAiResourceGroupName = readEnvironmentVariable('AZURE_OPENAI_RESOURCE_GROUP', '')
param realtimeDeploymentCapacity = int(readEnvironmentVariable('AZURE_OPENAI_REALTIME_DEPLOYMENT_CAPACITY', '1'))
param embeddingDeploymentCapacity = int(readEnvironmentVariable('AZURE_OPENAI_EMB_DEPLOYMENT_CAPACITY', '30'))

// Azure AI Search
param searchIndexName = readEnvironmentVariable('AZURE_SEARCH_INDEX', 'voicerag-intvect')
param searchServiceName = readEnvironmentVariable('AZURE_SEARCH_SERVICE', '')
param searchServiceResourceGroupName = readEnvironmentVariable('AZURE_SEARCH_SERVICE_RESOURCE_GROUP', '')
param searchServiceLocation = readEnvironmentVariable('AZURE_SEARCH_SERVICE_LOCATION', '')
param searchServiceSkuName = readEnvironmentVariable('AZURE_SEARCH_SERVICE_SKU', 'standard')
param searchServiceSemanticRankerLevel = readEnvironmentVariable('AZURE_SEARCH_SEMANTIC_RANKER', 'free')

// Azure Storage
param storageAccountName = readEnvironmentVariable('AZURE_STORAGE_ACCOUNT', '')
param storageResourceGroupName = readEnvironmentVariable('AZURE_STORAGE_RESOURCE_GROUP', '')
param storageSkuName = readEnvironmentVariable('AZURE_STORAGE_SKU', 'Standard_LRS')

// Azure Container Apps
param backendServiceName = readEnvironmentVariable('AZURE_CONTAINER_APP_NAME', '')
param webAppExists = bool(readEnvironmentVariable('SERVICE_WEB_RESOURCE_EXISTS', 'false'))
param azureContainerAppsWorkloadProfile = readEnvironmentVariable('AZURE_CONTAINER_APPS_WORKLOAD_PROFILE', 'Consumption')

// Azure Log Analytics
param logAnalyticsName = readEnvironmentVariable('AZURE_LOG_ANALYTICS', '')

// CI/CD
param runningOnGh = readEnvironmentVariable('GITHUB_ACTIONS', '')
param runningOnAdo = readEnvironmentVariable('TF_BUILD', '')

