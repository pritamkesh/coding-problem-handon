# User Activity Data Pipeline

This project implements a data pipeline for processing user activity events, including event generation, Kafka streaming, S3 archival, and AWS Glue ETL processing.

## Architecture Overview

The pipeline consists of three main components:

1. **Event Producer** (`event_producer.py`): 
   - Generates mock user activity events
   - Serializes events using Avro schema
   - Publishes events to Kafka topic

2. **Data Archiver** (`archiver.py`):
   - Consumes events from Kafka
   - Batches events (5 events per file)
   - Archives to S3 in HIVE partitioning format

3. **AWS Glue ETL** (`glue_etl/user_activity_etl.py`):
   - Processes raw Avro files from S3
   - Performs transformations
   - Writes processed data in Parquet format

## Prerequisites

1. Python 3.8+
2. Apache Kafka
3. AWS Account (or moto for S3 mocking)
4. Docker (optional, for local Kafka setup)

## Detailed Setup Instructions

### Option 1: Docker Setup (Recommended)

1. **Install Docker and Docker Compose**
   - Install Docker from [Docker's official website](https://docs.docker.com/get-docker/)
   - Docker Compose is included with Docker Desktop for Windows/Mac

2. **Start the Infrastructure**
```bash
# Clone the repository
git clone <repository-url>
cd user-activity-pipeline

# Start all services (Kafka, Zookeeper, LocalStack)
docker-compose up -d

# Verify services are running
docker ps
```

3. **Set up Python Environment**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

4. **Create Kafka Topic**
```bash
# Create the topic (using Kafka container)
docker exec -it kafka kafka-topics.sh \
    --create \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor 1
```

5. **Run the Pipeline**
```bash
# Start the event producer
python src/event_producer.py

# In a new terminal, start the archiver
python src/archiver.py
```

### Option 2: Local Setup (Without Docker)

1. **Install Apache Kafka**
   - Download Kafka from [Apache Kafka website](https://kafka.apache.org/downloads)
   - Extract the archive: `tar -xzf kafka_2.13-3.5.0.tgz`
   - Move to a suitable location: `mv kafka_2.13-3.5.0 /usr/local/kafka`

2. **Start Kafka Services**
```bash
# Start Zookeeper (in one terminal)
cd /usr/local/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka Server (in another terminal)
cd /usr/local/kafka
bin/kafka-server-start.sh config/server.properties
```

3. **Set up Python Environment**
```bash
# Clone the repository
git clone <repository-url>
cd user-activity-pipeline

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

4. **Create Kafka Topic**
```bash
# Create the topic
cd /usr/local/kafka
bin/kafka-topics.sh --create \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor 1
```

5. **Configure LocalStack for S3 (Optional)**
   - If you don't have an AWS account, install LocalStack:
     ```bash
     pip install localstack
     localstack start -d
     ```
   - Set environment variables:
     ```bash
     export AWS_ACCESS_KEY_ID=test
     export AWS_SECRET_ACCESS_KEY=test
     export AWS_DEFAULT_REGION=us-east-1
     ```

6. **Run the Pipeline**
```bash
# Start the event producer
python src/event_producer.py

# In a new terminal, start the archiver
python src/archiver.py
```

### Verification Steps (Both Setups)

1. **Check Kafka Topic**
```bash
# For Docker setup
docker exec -it kafka kafka-console-consumer.sh \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --from-beginning

# For local setup
cd /usr/local/kafka
bin/kafka-console-consumer.sh \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --from-beginning
```

2. **Monitor S3 Storage**
   - For LocalStack: Check `http://localhost:4566/health`
   - For AWS: Check your S3 bucket in AWS Console

3. **View Logs**
   - Check terminal output for both producer and archiver
   - For Docker setup: `docker logs kafka`
   - For local setup: Check Kafka logs in `/usr/local/kafka/logs`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd user-activity-pipeline
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Kafka:
```bash
# Using Docker
docker-compose up -d
```

5. Configure AWS credentials (if not using moto):
```bash
aws configure
```

## Configuration

The project uses a YAML configuration file (`config/config.yaml`) for managing:
- Kafka connection settings
- S3 bucket configuration
- Batch sizes and intervals
- AWS credentials (if not using environment variables)

## Usage

1. Start the event producer:
```bash
python src/event_producer.py
```

2. Start the archiver:
```bash
python src/archiver.py
```

3. For AWS Glue ETL:
   - Deploy the Glue job using AWS Console or AWS CLI
   - Configure job triggers based on S3 events

## Project Structure

```
.
├── README.md
├── requirements.txt
├── src/
│   ├── event_producer.py    # Event generation and Kafka production
│   ├── archiver.py         # Kafka consumption and S3 archival
│   └── glue_etl/
│       └── user_activity_etl.py  # AWS Glue ETL job
├── schemas/
│   └── user_activity.avsc  # Avro schema definition
├── config/
│   └── config.yaml        # Configuration settings
└── tests/
    └── test_event_producer.py  # Unit tests
```

## Design Choices

1. **Event Generation**:
   - Mock events cover diverse scenarios (page_view, add_to_cart, purchase)
   - Realistic timestamp generation within recent timeframe
   - Random but plausible user and session IDs

2. **S3 Archival Strategy**:
   - Batch size: 5 events per file for optimal performance
   - HIVE partitioning: `event_date=YYYY-MM-DD/hour=HH`
   - Unique filenames using UUID4

3. **ETL Processing**:
   - Incremental processing using job bookmarks
   - Error handling with DLQ implementation
   - Schema evolution support through schema registry

## Error Handling

1. **Event Producer**:
   - Kafka connection retries
   - Avro serialization validation
   - Dead letter queue for failed events

2. **Archiver**:
   - S3 upload retries
   - Batch failure recovery
   - Corrupt event handling

3. **Glue ETL**:
   - Schema validation
   - Data type conversion error handling
   - Failed record tracking

## Monitoring and Logging

- Kafka lag monitoring
- S3 batch upload metrics
- AWS CloudWatch integration
- Custom logging for debugging

## Testing

Run unit tests:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 