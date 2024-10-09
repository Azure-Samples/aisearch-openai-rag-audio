# Define the .env file path
$envFilePath = "app\backend\.env"

# Clear the contents of the .env file
Set-Content -Path $envFilePath -Value ""

# Append new values to the .env file
$azureOpenAiEndpoint = azd env get-value AZURE_OPENAI_ENDPOINT
$azureOpenAiRealtimeDeployment = azd env get-value AZURE_OPENAI_REALTIME_DEPLOYMENT
$azureSearchEndpoint = azd env get-value AZURE_SEARCH_ENDPOINT
$azureSearchIndex = azd env get-value AZURE_SEARCH_INDEX
$azureTenantId = azd env get-value AZURE_TENANT_ID

Add-Content -Path $envFilePath -Value "AZURE_OPENAI_ENDPOINT=$azureOpenAiEndpoint"
Add-Content -Path $envFilePath -Value "AZURE_OPENAI_REALTIME_DEPLOYMENT=$azureOpenAiRealtimeDeployment"
Add-Content -Path $envFilePath -Value "AZURE_SEARCH_ENDPOINT=$azureSearchEndpoint"
Add-Content -Path $envFilePath -Value "AZURE_SEARCH_INDEX=$azureSearchIndex"
Add-Content -Path $envFilePath -Value "AZURE_TENANT_ID=$azureTenantId"