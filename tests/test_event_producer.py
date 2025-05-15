"""
Unit tests for the event producer
"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

import yaml
from kafka import KafkaProducer

from src.event_producer import UserActivityProducer

class TestUserActivityProducer(unittest.TestCase):
    """Test cases for UserActivityProducer"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config
        self.mock_config = {
            "kafka": {
                "bootstrap_servers": "localhost:9092",
                "topic": "test_topic"
            },
            "event_producer": {
                "events_per_second": 1,
                "total_events": 5,
                "event_types": ["page_view", "add_to_cart", "purchase"],
                "user_id_prefix": "TEST_USER",
                "product_id_prefix": "TEST_PROD"
            }
        }

        # Mock the config loading
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = yaml.dump(self.mock_config)
            self.producer = UserActivityProducer()
            self.producer.producer = MagicMock(spec=KafkaProducer)

    def test_generate_event(self):
        """Test event generation"""
        event = self.producer.generate_event()

        # Check required fields
        self.assertIn("user_id", event)
        self.assertIn("event_timestamp", event)
        self.assertIn("event_type", event)
        self.assertIn("session_id", event)
        self.assertIn("event_properties", event)

        # Check field types
        self.assertIsInstance(event["user_id"], str)
        self.assertIsInstance(event["event_timestamp"], int)
        self.assertIsInstance(event["event_type"], str)
        self.assertIsInstance(event["session_id"], str)
        self.assertIsInstance(event["event_properties"], dict)

        # Check event type is valid
        self.assertIn(event["event_type"], self.mock_config["event_producer"]["event_types"])

    def test_purchase_event_properties(self):
        """Test purchase event has required properties"""
        # Force event type to be purchase
        with patch('random.choice', return_value="purchase"):
            event = self.producer.generate_event()
            
            self.assertEqual(event["event_type"], "purchase")
            self.assertIn("product_id", event)
            self.assertIn("price", event["event_properties"])
            
            # Check price is a valid float string
            price = float(event["event_properties"]["price"])
            self.assertGreaterEqual(price, 10.0)
            self.assertLessEqual(price, 1000.0)

    def test_produce_events(self):
        """Test event production to Kafka"""
        test_events = 3
        self.producer.produce_events(test_events)

        # Check if correct number of events were produced
        self.assertEqual(
            self.producer.producer.send.call_count,
            test_events
        )

        # Check if events were sent to correct topic
        calls = self.producer.producer.send.call_args_list
        for call in calls:
            args, kwargs = call
            self.assertEqual(args[0], self.mock_config["kafka"]["topic"])
            self.assertIsInstance(kwargs["value"], dict)

    def test_error_handling(self):
        """Test error handling during event production"""
        # Mock Kafka producer to raise an exception
        self.producer.producer.send.side_effect = Exception("Kafka error")

        with self.assertRaises(Exception):
            self.producer.produce_events(1)

if __name__ == '__main__':
    unittest.main() 