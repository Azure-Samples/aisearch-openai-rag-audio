#!/bin/bash

# Define the .env file path
ENV_FILE_PATH="app/backend/.env"

# Clear the contents of the .env file
> $ENV_FILE_PATH

# Append new values to the .env file
echo "AZURE_OPENAI_ENDPOINT=$(azd env get-value AZURE_OPENAI_ENDPOINT)" >> $ENV_FILE_PATH
echo "AZURE_OPENAI_REALTIME_DEPLOYMENT=$(azd env get-value AZURE_OPENAI_REALTIME_DEPLOYMENT)" >> $ENV_FILE_PATH
echo "AZURE_SEARCH_ENDPOINT=$(azd env get-value AZURE_SEARCH_ENDPOINT)" >> $ENV_FILE_PATH
echo "AZURE_SEARCH_INDEX=$(azd env get-value AZURE_SEARCH_INDEX)" >> $ENV_FILE_PATH
echo "AZURE_TENANT_ID=$(azd env get-value AZURE_TENANT_ID)" >> $ENV_FILE_PATH