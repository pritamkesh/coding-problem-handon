#!/usr/bin/env python3
"""
Archiver for User Activity Pipeline (Local File Version)
Archives events from input files to organized storage
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import yaml

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class UserActivityArchiver:
    """Archives user activity events to local storage"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the archiver with configuration"""
        self.config = self._load_config(config_path)
        self.input_dir = Path("data/events")
        self.archive_dir = Path("data/archive")
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.batch = []
        self.last_batch_time = time.time()
        self.processed_files = set()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _get_archive_path(self, timestamp_ms: int) -> Path:
        """Generate archive path based on event timestamp"""
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        return (
            self.archive_dir / 
            f"event_date={dt.strftime('%Y-%m-%d')}" /
            f"hour={dt.strftime('%H')}" /
            f"events_{dt.strftime('%Y%m%d_%H%M%S')}_{int(time.time())}.json"
        )

    def _should_flush_batch(self) -> bool:
        """Check if the current batch should be flushed to archive"""
        batch_size_reached = len(self.batch) >= self.config["s3"]["batch_size"]
        time_limit_reached = (
            time.time() - self.last_batch_time
            > self.config["s3"]["max_batch_time_seconds"]
        )
        return batch_size_reached or (time_limit_reached and self.batch)

    def _flush_batch_to_archive(self):
        """Flush the current batch of events to archive"""
        if not self.batch:
            return

        try:
            # Use the timestamp of the first event for archive path
            first_event_ts = self.batch[0]["event_timestamp"]
            archive_path = self._get_archive_path(first_event_ts)
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            # Write events to archive
            with open(archive_path, 'w') as f:
                for event in self.batch:
                    json.dump(event, f)
                    f.write('\n')

            logger.info(
                f"Archived batch of {len(self.batch)} events to "
                f"{archive_path}"
            )

            # Clear the batch
            self.batch = []
            self.last_batch_time = time.time()

        except Exception as e:
            logger.error(f"Failed to flush batch to archive: {e}")
            raise

    def process_input_file(self, file_path: Path):
        """Process a single input file"""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    event = json.loads(line.strip())
                    self.batch.append(event)

                    if self._should_flush_batch():
                        self._flush_batch_to_archive()

            # Mark file as processed
            self.processed_files.add(file_path)
            
            # Optionally, delete processed file
            # file_path.unlink()

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise

    def archive_events(self):
        """Main loop to archive events"""
        try:
            logger.info("Starting to archive events...")
            while True:
                # Look for new files
                input_files = list(self.input_dir.glob("*.json"))
                new_files = [f for f in input_files if f not in self.processed_files]

                if new_files:
                    for file_path in new_files:
                        self.process_input_file(file_path)
                else:
                    # No new files, sleep before checking again
                    time.sleep(1)

                # Flush any remaining events if we've waited too long
                if self._should_flush_batch():
                    self._flush_batch_to_archive()

        except KeyboardInterrupt:
            logger.info("Archiving stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            # Ensure any remaining events are flushed
            if self.batch:
                self._flush_batch_to_archive()

def main():
    """Main function to run the archiver"""
    try:
        archiver = UserActivityArchiver()
        archiver.archive_events()
    except Exception as e:
        logger.error(f"Failed to run archiver: {e}")
        raise

if __name__ == "__main__":
    main() 