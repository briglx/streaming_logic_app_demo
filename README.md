# Streaming Logic App Demo



This project demonstrates how to query streaming data using several Azure technologies:

- Azure Logic Apps
- Azure Eventhubs
- Kafka Connect
- Service Now Integration

Workflow:

- Generator App sents message to Eventhubs
- Logic App will push messages to Service Now

![Architecture Overview](docs/architecture_overview.png "Architecture Overview")


# Setup

This setup will deploy the core infrastructure needed to run the the solution:

- Core infrastructure
- Generator App
- Core Infrastructure
- Configure the global variables

## Core infrastructure

### Global

```bash
RG_NAME=logic_demo
RG_REGION=westus
STORAGE_ACCOUNT_NAME=logic_demo

#Event Hubs
EH_NAMESPACE=logic_app_demo_ehn
EH_NAME=logic_app_demo_eh

# Logic App variables
LOGIC_APP_NAME = TicketApp

# Existing Resources
ACR_REGISTRY_NAME = <existing-registry-name>
SERVICE_PRINCIPAL_ID = <existing-service-principal-id>
SERVICE_PRINCIPAL_PASSWORD = <existing-service-principal-password>
```

### Resource Group

Create a resource group for this project

az group create --name $RG_NAME --location $RG_REGION