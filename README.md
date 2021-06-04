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
EH_NAMESPACE=LogicAppDemoEhn
EH_NAME=logic_app_demo_eh

# Logic App variables
LOGIC_APP_NAME=TicketApp

# Kafka
KAFKA_VM_NAME=kafka-vm
KAFKA_TOPIC=logic_app_demo
```

### Resource Group

Create a resource group for this project

```bash
az group create --name $RG_NAME --location $RG_REGION
```

### Evenhubs

```bash
# Create an Event Hubs namespace. Specify a name for the Event Hubs namespace.
az eventhubs namespace create --name $EH_NAMESPACE --resource-group $RG_NAME -l $RG_REGION

# Create an event hub. Specify a name for the event hub.
az eventhubs eventhub create --name $EH_NAME --resource-group $RG_NAME --namespace-name $EH_NAMESPACE

#Create Read Policy and Connection string**
#TBD

```

### Logic App

**Create Logic App**
Make a copy of `logic_app\definition-example.json` and rename to `logic_app\definition.json`. Edit the file with the necessary values.

- The `<subscription_id>` is the target subscription id.

Deploy the Logic App

```bash
az logic workflow create --definition /path_to_project/logic_app/definition.json
--location $RG_REGION
--name $LOGIC_APP_NAME
--resource-group $RG_NAME
```

### Kafka

Deploy the bitnami image of kafka. 

```bash

az deployment group create --name "{$KAFKA_VM_NAME}deployment" --resource-group $RG_NAME --template-file kafka/template.json --parameters kafka/parameters.json

# ssh onto machine
ssh kafka_user@<public_ip_of_kafka_deployment>

# create a new topic
/opt/bitnami/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic $KAFKA_TOPIC

# Start a new producer and generate a message in the topic
export KAFKA_OPTS="-Djava.security.auth.login.config=/opt/bitnami/kafka/conf/kafka_jaas.conf"
/opt/bitnami/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --producer.config /opt/bitnami/kafka/conf/producer.properties --topic $KAFKA_TOPIC

this is my first message
this is my second message

```

 Press `CTRL-D` to send the message.

 Collect and display the messages

 ```bash

 /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic $KAFKA_TOPIC --consumer.config /opt/bitnami/kafka/conf/consumer.properties --from-beginning

 ```


## Generator
The generator is a python application that runs in a docker container. The container expects the following environment variables stored in a `local.env` file.

Run generator in docker

```bash
# Build and run image localy
> docker build --pull --rm -f "dockerfile" -t streaminglogicappdemo:latest "."
> docker run --rm -it --env-file local.env streaminglogicappdemo:latest

#Run app
> python main.py
```



# Development

The development environment is to manages two types of environments:

- Python Generator Code
- Azure Resources

## Python Generator code

Setup your dev environment by creating a virtual environment

```bash
# virtualenv \path\to\.venv -p path\to\specific_version_python.exe
python -m venv .venv.
.venv\scripts\activate

deactivate
```

## Style Guidelines

This project enforces quite strict [PEP8](https://www.python.org/dev/peps/pep-0008/) and [PEP257 (Docstring Conventions)](https://www.python.org/dev/peps/pep-0257/) compliance on all code submitted.

We use [Black](https://github.com/psf/black) for uncompromised code formatting.

Summary of the most relevant points:

- Comments should be full sentences and end with a period.
- [Imports](https://www.python.org/dev/peps/pep-0008/#imports) should be ordered.
- Constants and the content of lists and dictionaries should be in alphabetical order.
- It is advisable to adjust IDE or editor settings to match those requirements.


### Use new style string formatting

Prefer [f-strings](https://docs.python.org/3/reference/lexical_analysis.html#f-strings) over ``%`` or ``str.format``.

```python

    #New
    f"{some_value} {some_other_value}"
    # Old, wrong
    "{} {}".format("New", "style")
    "%s %s" % ("Old", "style")

```

One exception is for logging which uses the percentage formatting. This is to avoid formatting the log message when it is suppressed.

```python

    _LOGGER.info("Can't connect to the webservice %s at %s", string1, string2)

```

### Testing
You'll need to install the test dependencies into your Python environment:

```bash

    pip3 install -r requirements_dev.txt

```

Now that you have all test dependencies installed, you can run linting and tests on the project:

```bash

    isort .
    codespell  --skip=".venv"
    black generator
    flake8 generator
    pylint generator
    pydocstyle generator

```