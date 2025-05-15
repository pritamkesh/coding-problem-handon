#!/usr/bin/env python3
"""
Event Producer for User Activity Pipeline (Local File Version)
Generates mock user activity events and writes to local files
"""

import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import yaml
from faker import Faker

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class UserActivityProducer:
    """Produces mock user activity events to local files"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the producer with configuration"""
        self.config = self._load_config(config_path)
        self.fake = Faker()
        self.output_dir = Path("data/events")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def generate_event(self) -> Dict:
        """Generate a single mock user activity event"""
        event_type = random.choice(self.config["event_producer"]["event_types"])
        event = {
            "user_id": f"{self.config['event_producer']['user_id_prefix']}{self.fake.uuid4()}",
            "event_timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
            "event_type": event_type,
            "session_id": self.fake.uuid4(),
            "event_properties": {}
        }

        # Add product_id and price for purchase and add_to_cart events
        if event_type in ["purchase", "add_to_cart"]:
            event["product_id"] = f"{self.config['event_producer']['product_id_prefix']}{self.fake.uuid4()}"
            event["event_properties"]["price"] = str(round(random.uniform(10.0, 1000.0), 2))

        return event

    def save_event(self, event: Dict):
        """Save event to a local file"""
        timestamp = datetime.fromtimestamp(event["event_timestamp"] / 1000)
        filename = self.output_dir / f"events_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'a') as f:
                json.dump(event, f)
                f.write('\n')
            logger.info(f"Event saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save event: {e}")
            raise

    def produce_events(self, total_events: Optional[int] = None):
        """Produce events to local files"""
        if total_events is None:
            total_events = self.config["event_producer"]["total_events"]

        try:
            for i in range(total_events):
                event = self.generate_event()
                self.save_event(event)

                # Sleep to control event generation rate
                time.sleep(1 / self.config["event_producer"]["events_per_second"])

                if (i + 1) % 10 == 0:
                    logger.info(f"Produced {i + 1} events")

        except Exception as e:
            logger.error(f"Error producing events: {e}")
            raise

def main():
    """Main function to run the producer"""
    try:
        producer = UserActivityProducer()
        logger.info("Starting event production...")
        producer.produce_events()
        logger.info("Event production completed successfully")
    except Exception as e:
        logger.error(f"Failed to run event producer: {e}")
        raise

if __name__ == "__main__":
    main() 