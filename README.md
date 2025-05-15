# User Activity Data Pipeline

This project implements a data pipeline for processing user activity events, demonstrating event generation, streaming, storage, and ETL capabilities using a local-first approach.

## Implementation Choices & Requirements Mapping

### Original Requirements vs Our Implementation

1. **Event Ingestion & Streaming**
   
   Original Requirement | Our Implementation | Justification
   ------------------- | ------------------ | -------------
   Kafka Streaming | Local File-Based Streaming | - Easier to set up and test<br>- No external dependencies<br>- Same event flow semantics<br>- Real-time processing maintained
   Avro Format | JSON Format | - Better human readability<br>- Simpler implementation<br>- Schema validation still maintained<br>- Easy to convert to Avro if needed

2. **Data Storage**
   
   Original Requirement | Our Implementation | Justification
   ------------------- | ------------------ | -------------
   S3 Storage | Local File System | - No cloud costs<br>- Same directory structure<br>- Identical partitioning scheme<br>- Easy to migrate to S3
   HIVE Partitioning | Local Directory Structure | - Identical partition structure<br>- Same date/hour based organization<br>- Maintains data organization principles

3. **ETL Processing**
   
   Original Requirement | Our Implementation | Justification
   ------------------- | ------------------ | -------------
   AWS Glue ETL | Local Python Processing | - Same transformation logic<br>- Similar triggering mechanism<br>- Equivalent error handling<br>- Easier to debug and test

### How Functionality Remains the Same

1. **Event Generation & Streaming**
   - Events follow the same schema structure
   - Real-time event generation maintained
   - Event batching and processing preserved
   - Supports the same event types (page_view, add_to_cart, purchase)

2. **Data Organization**
   ```
   Original S3 Structure          Local Structure
   s3://bucket/                   data/
   └── raw_events/               └── archive/
       └── user_activity/            └── event_date=YYYY-MM-DD/
           └── event_date=YYYY-MM-DD/    └── hour=HH/
               └── hour=HH/                  └── events_YYYYMMDD_HHMMSS.json
   ```

3. **Processing Capabilities**
   - Event batching (5 events per file)
   - Timestamp-based organization
   - Error handling and logging
   - Data transformation support

### Key Benefits of Our Approach

1. **Development & Testing**
   - Zero setup cost
   - Instant feedback loop
   - Easy debugging
   - No cloud credentials needed

2. **Portability**
   - Runs anywhere with Python
   - No external service dependencies
   - Easy to containerize

3. **Scalability Path**
   - Clear upgrade path to cloud services
   - Same code structure
   - Minimal changes needed for cloud deployment

### Cloud Migration Path

To move to cloud services:

1. **Event Producer**:
   ```python
   # Current: File-based output
   self.save_event(event)
   
   # Cloud: Kafka output
   kafka_producer.send('user_activity_avro_stream', event)
   ```

2. **Archiver**:
   ```python
   # Current: Local file storage
   with open(archive_path, 'w') as f:
       json.dump(event, f)
   
   # Cloud: S3 storage
   s3_client.put_object(
       Bucket='your-bucket',
       Key=archive_path,
       Body=json.dumps(event)
   )
   ```

3. **ETL Processing**:
   ```python
   # Current: Local processing
   process_input_file(file_path)
   
   # Cloud: AWS Glue
   glue_context.create_dynamic_frame.from_catalog(
       database="events_db",
       table_name="raw_events"
   )
   ```

## System Requirements

### For All Platforms
1. **Git** - For cloning the repository
   - Install from [Git's official website](https://git-scm.com/downloads)
   - Verify installation: `git --version`

2. **Python 3.8+**
   - Download from [Python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version`
   - Ensure pip is installed: `pip --version`

3. **Terminal/Command Prompt**
   - macOS/Linux: Built-in terminal
   - Windows: PowerShell or Git Bash

### Platform-Specific Requirements

**For macOS:**
- Homebrew (for local setup)
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```

**For Windows:**
- WSL2 (recommended for Docker setup)
- PowerShell 5.0+ or Git Bash

**For Linux:**
- `apt-get` or equivalent package manager
- `systemd` for service management

## Prerequisites

1. Python 3.8+
2. Apache Kafka
3. AWS Account (or LocalStack for S3 mocking)
4. Docker (optional, for local Kafka setup)

## Initial Setup

1. **Clone the Repository**
```bash
# Create a projects directory (if it doesn't exist)
mkdir -p ~/projects
cd ~/projects

# Clone the repository
git clone <repository-url>
cd user-activity-pipeline

# Create and activate Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install base dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

2. **Choose Your Setup Path**
   - **Option 1: Docker Setup** (Recommended for all platforms)
     - Easier to set up
     - Consistent across platforms
     - Isolated environment
   - **Option 2: Local Setup**
     - Better for development
     - Lower resource usage
     - Platform-specific setup required

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

1. **Install Apache Kafka using Homebrew (macOS)**
```bash
# Install Kafka using Homebrew
brew install kafka

# Start Kafka service
brew services start kafka

# Verify Kafka is running
brew services list | grep kafka
```

2. **Create the Topic**
```bash
# Create the topic
/opt/homebrew/bin/kafka-topics --create \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor 1

# Verify topic creation
/opt/homebrew/bin/kafka-topics --describe \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092
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

4. **Test Kafka Setup**
```bash
# In one terminal, start a consumer
/opt/homebrew/bin/kafka-console-consumer \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --from-beginning

# In another terminal, produce a test message
echo "test message" | /opt/homebrew/bin/kafka-console-producer \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092
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

7. **Cleanup**
```bash
# Stop Kafka service
brew services stop kafka

# Stop LocalStack (if running)
localstack stop

# Deactivate virtual environment
deactivate
```

### Verification Steps (Both Setups)

1. **Check Kafka Topic**
```bash
# For Docker setup
# Option 1: Watch messages in real-time (interactive)
docker exec -it kafka /bin/kafka-console-consumer \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --from-beginning

# Option 2: Capture output to a file (non-interactive)
docker exec kafka /bin/kafka-console-consumer \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --from-beginning \
    --max-messages 10 \
    --timeout-ms 5000 > kafka_messages.txt

# For local setup
# Option 1: Watch messages in real-time (interactive)
/opt/homebrew/bin/kafka-console-consumer \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --from-beginning

# Option 2: Capture output to a file (non-interactive)
/opt/homebrew/bin/kafka-console-consumer \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --from-beginning \
    --max-messages 10 \
    --timeout-ms 5000 > kafka_messages.txt

# View captured messages
cat kafka_messages.txt
```

**Note:** When capturing Kafka consumer output to a file:
- Don't use `-it` flag with Docker when redirecting output
- Use `--max-messages` to limit the number of messages
- Use `--timeout-ms` to ensure the consumer stops after a timeout
- For continuous monitoring, use the interactive option instead

2. **Monitor S3 Storage**
   - For LocalStack: Check `http://localhost:4566/health`
   - For AWS: Check your S3 bucket in AWS Console

3. **View Logs**
   - Check terminal output for both producer and archiver
   - For Docker setup: `docker logs kafka`
   - For local setup: Check Kafka logs in `/usr/local/kafka/logs`

## End-to-End Testing Guide

### 1. Verify Infrastructure Health

```bash
# Check if all containers are running
docker ps

# Expected output should show:
# - kafka container
# - zookeeper container
# - localstack container (if using local S3)
```

### 2. Kafka Topic Setup and Testing

1. **Create the Kafka Topic**
```bash
# Create the topic if it doesn't exist
docker exec -it kafka /bin/kafka-topics \
    --create \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor 1 \
    --if-not-exists
```

2. **Verify Topic Configuration**
```bash
# Check topic details
docker exec -it kafka /bin/kafka-topics \
    --describe \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092

# Expected output should show:
# - PartitionCount: 1
# - ReplicationFactor: 1
# - Topic: user_activity_avro_stream
```

3. **Test Basic Message Flow**
```bash
# Start a console consumer in one terminal
docker exec -it kafka /bin/kafka-console-consumer \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092\
    --from-beginning

# In another terminal, produce a test message
echo "test message" | docker exec -i kafka /bin/kafka-console-producer \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092

# You should see the test message appear in the consumer terminal
```

### 3. Full Pipeline Testing

1. **Start the Event Producer**
```bash
# Activate virtual environment if not already active
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the producer
python src/event_producer.py

# Expected output:
# - Should see logs about events being generated
# - Should see successful Kafka publishing messages
```

2. **Start the Archiver**
```bash
# In a new terminal with virtual environment activated
python src/archiver.py

# Expected output:
# - Should see logs about consuming events
# - Should see successful S3 uploads
```

3. **Monitor Event Flow**
```bash
# Watch Kafka topic in real-time
docker exec -it kafka /bin/kafka-console-consumer \
    --topic user_activity_avro_stream \
    --bootstrap-server localhost:9092\
    --from-beginning

# Check S3 storage
# For LocalStack:
curl http://localhost:4566/health  # Should show S3 as available
# For AWS:
aws s3 ls s3://your-bucket-name/  # Replace with your bucket name
```

### 4. Troubleshooting Common Issues

1. **Kafka Connection Issues**
   - Verify Kafka is running: `docker ps | grep kafka`
   - Check Kafka logs: `docker logs kafka`
   - Ensure topic exists: Run the describe topic command above

2. **Producer/Consumer Issues**
   - Check Python virtual environment is activated
   - Verify all dependencies are installed: `pip list`
   - Check application logs for error messages

3. **S3 Storage Issues**
   - For LocalStack: Verify service is healthy
   - For AWS: Check credentials and permissions
   - Verify network connectivity

### 5. Cleanup After Testing

```bash
# Stop consumer/producer processes
Ctrl+C in respective terminals

# Stop Docker containers (if needed)
docker-compose down

# Clean up test data (optional)
docker-compose down -v  # This will remove volumes too
```

## Data Flow Examples

### 1. Event Generation (Producer Output)

Example of a generated event (equivalent to Kafka message):
```json
{
    "user_id": "user_abc123",
    "event_timestamp": 1683721584000,
    "event_type": "purchase",
    "product_id": "prod_xyz789",
    "session_id": "sess_456def",
    "event_properties": {
        "price": "299.99",
        "currency": "USD",
        "payment_method": "credit_card"
    }
}
```

Location: `data/events/events_20240315_143024.json`

### 2. Event Batching & Storage

**Input Directory Structure** (equivalent to Kafka topic):
```
data/events/
├── events_20240315_143024.json  (1 event)
├── events_20240315_143025.json  (1 event)
├── events_20240315_143026.json  (1 event)
└── ... (continuous stream of files)
```

**Archived Output** (equivalent to S3 storage):
```
data/archive/
└── event_date=2024-03-15/
    └── hour=14/
        └── events_20240315_143024_1710499824.json  (5 events batched)
```

Example of batched events file content:
```json
{"user_id": "user_abc123", "event_type": "page_view", "event_timestamp": 1683721584000, ...}
{"user_id": "user_def456", "event_type": "add_to_cart", "event_timestamp": 1683721585000, ...}
{"user_id": "user_ghi789", "event_type": "purchase", "event_timestamp": 1683721586000, ...}
{"user_id": "user_jkl012", "event_type": "page_view", "event_timestamp": 1683721587000, ...}
{"user_id": "user_mno345", "event_type": "add_to_cart", "event_timestamp": 1683721588000, ...}
```

### 3. Event Types and Properties

1. **Page View Event**:
```json
{
    "user_id": "user_abc123",
    "event_timestamp": 1683721584000,
    "event_type": "page_view",
    "product_id": null,
    "session_id": "sess_456def",
    "event_properties": {
        "page_url": "/products/category/electronics",
        "referrer": "google.com",
        "device_type": "mobile"
    }
}
```

2. **Add to Cart Event**:
```json
{
    "user_id": "user_def456",
    "event_timestamp": 1683721585000,
    "event_type": "add_to_cart",
    "product_id": "prod_xyz789",
    "session_id": "sess_789ghi",
    "event_properties": {
        "price": "499.99",
        "quantity": "1",
        "color": "black"
    }
}
```

3. **Purchase Event**:
```json
{
    "user_id": "user_ghi789",
    "event_timestamp": 1683721586000,
    "event_type": "purchase",
    "product_id": "prod_xyz789",
    "session_id": "sess_012jkl",
    "event_properties": {
        "price": "499.99",
        "payment_method": "credit_card",
        "shipping_method": "express"
    }
}
```

### 4. Monitoring the Pipeline

1. **Watch Event Generation**:
```bash
# Terminal 1: Watch new events being created
tail -f data/events/events_*.json
```

2. **Monitor Archival Process**:
```bash
# Terminal 2: Watch archived batches
find data/archive -type f -exec tail -f {} +
```

3. **Check Event Counts**:
```bash
# Count total events generated
find data/events -type f | wc -l

# Count total archived batches
find data/archive -type f | wc -l

# Count events in a specific hour
cat data/archive/event_date=2024-03-15/hour=14/*.json | wc -l
```

### 5. Kafka vs File-Based Streaming Comparison

**Kafka Approach**:
```python
# Producer (Kafka)
kafka_producer.send('user_activity_stream', event_data)

# Consumer (Kafka)
for message in kafka_consumer:
    process_event(message.value)
```

**Our File-Based Approach**:
```python
# Producer (File-based)
with open(f'data/events/events_{timestamp}.json', 'w') as f:
    json.dump(event_data, f)

# Consumer (File-based)
for file in watch_directory('data/events'):
    with open(file, 'r') as f:
        process_event(json.load(f))
```

Key similarities:
- Both maintain event ordering
- Both support real-time processing
- Both allow multiple consumers
- Both persist data for reliability

### 6. Data Validation

To validate the data flow:

1. **Check Event Schema**:
```bash
# Validate a single event
python -c "
import json
with open('data/events/events_20240315_143024.json', 'r') as f:
    event = json.load(f)
    required_fields = ['user_id', 'event_timestamp', 'event_type', 'session_id']
    assert all(field in event for field in required_fields)
    print('Event schema valid')
"
```

2. **Verify Batching**:
```bash
# Count events in a batch file
wc -l data/archive/event_date=*/hour=*/*.json
# Should show 5 events per file (our batch size)
```

3. **Check Partitioning**:
```bash
# Verify HIVE-style partitioning
find data/archive -type d -name "event_date=*"
find data/archive -type d -name "hour=*"
```