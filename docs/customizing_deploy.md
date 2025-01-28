# Customizing the VoiceRAG deployment

This guide shows you how to customize the [VoiceRAG](../README.md#deploying-the-app) deployment to specify different options.
If your goal is to reuse existing services (OpenAI or Search), see the [existing services guide](./existing_services.md) instead.

## Customizing the real-time voice choice

Run this command to set the voice choice for the real-time deployment:

```bash
azd env set AZURE_OPENAI_REALTIME_VOICE_CHOICE <echo, alloy, or shimmer>
```

The default voice choice is `alloy`, but 2 other voices are available.

Once you have set the voice choice, run `azd up` to apply the changes to the deployed app.
If you've already run `azd up` and want to first preview the voice with the development server, then update your local `.env` file by running `./scripts/write_env.sh` or `pwsh ./scripts/write_env.ps1`, and then restart the development server.

## Customizing the Azure OpenAI deployment

To use a different version for the real-time deployment, run this command:

```bash
azd env set AZURE_OPENAI_REALTIME_DEPLOYMENT_VERSION 2024-12-17
```

To specify a different capacity (the default is 1), run this command:

```bash
azd env set AZURE_OPENAI_REALTIME_DEPLOYMENT_CAPACITY 2
```

You will need to run `azd up` to apply the changes to the Azure OpenAI resource.
