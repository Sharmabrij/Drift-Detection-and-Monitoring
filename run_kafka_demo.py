#!/usr/bin/env python3
"""
Kafka Drift Monitoring Demo

This script demonstrates the complete Kafka integration for real-time drift detection.
It sets up a producer to send data and a consumer to detect drift in real-time.
"""

import time
import threading
import logging
from datetime import datetime
import pandas as pd
import numpy as np

# Import Kafka components
from src.kafka import DriftDataProducer, DriftDataConsumer
from src.kafka.config import get_kafka_config, get_drift_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KafkaDriftDemo:
    """Demo class for Kafka drift monitoring"""
    
    def __init__(self):
        self.config = get_kafka_config()
        self.drift_config = get_drift_config()
        self.producer = None
        self.consumer = None
        self.running = False
        
    def setup(self):
        """Setup Kafka producer and consumer"""
        logger.info("🚀 Setting up Kafka drift monitoring demo...")
        
        try:
            # Initialize producer
            self.producer = DriftDataProducer(
                bootstrap_servers=self.config['bootstrap_servers'],
                topic=self.config['topic']
            )
            
            # Initialize consumer
            self.consumer = DriftDataConsumer(
                bootstrap_servers=self.config['bootstrap_servers'],
                topic=self.config['topic'],
                group_id=self.config['group_id'],
                window_size=self.drift_config['window_size'],
                check_interval=self.drift_config['check_interval']
            )
            
            logger.info("✅ Kafka components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Kafka components: {e}")
            return False
    
    def start_consumer(self):
        """Start the consumer in a background thread"""
        if self.consumer:
            self.consumer.start_background_consuming()
            logger.info("🚀 Consumer started in background")
    
    def send_normal_data(self, n_samples=100):
        """Send normal (non-drifted) data"""
        if self.producer:
            logger.info(f"📊 Sending {n_samples} normal data points...")
            sent, total = self.producer.generate_and_send_synthetic_data(
                n_samples=n_samples, 
                drift=False
            )
            logger.info(f"✅ Sent {sent}/{total} normal messages")
            return sent, total
        return 0, 0
    
    def send_drifted_data(self, n_samples=100):
        """Send drifted data"""
        if self.producer:
            logger.info(f"⚠️ Sending {n_samples} drifted data points...")
            sent, total = self.producer.generate_and_send_synthetic_data(
                n_samples=n_samples, 
                drift=True
            )
            logger.info(f"✅ Sent {sent}/{total} drifted messages")
            return sent, total
        return 0, 0
    
    def send_mixed_data(self, n_samples=200):
        """Send a mix of normal and drifted data"""
        logger.info(f"📊 Sending {n_samples} mixed data points...")
        
        # Send normal data first
        normal_sent, normal_total = self.send_normal_data(n_samples // 2)
        
        # Wait a bit
        time.sleep(2)
        
        # Send drifted data
        drifted_sent, drifted_total = self.send_drifted_data(n_samples // 2)
        
        total_sent = normal_sent + drifted_sent
        total_attempted = normal_total + drifted_total
        
        logger.info(f"📦 Total sent: {total_sent}/{total_attempted} messages")
        return total_sent, total_attempted
    
    def get_consumer_status(self):
        """Get current consumer status"""
        if self.consumer:
            return self.consumer.get_status()
        return {}
    
    def run_demo_scenario(self, scenario="mixed"):
        """Run a complete demo scenario"""
        logger.info(f"🎯 Running demo scenario: {scenario}")
        
        if not self.setup():
            logger.error("❌ Demo setup failed")
            return False
        
        try:
            # Start consumer
            self.start_consumer()
            time.sleep(2)  # Let consumer start
            
            # Run scenario
            if scenario == "normal":
                self.send_normal_data(200)
            elif scenario == "drifted":
                self.send_drifted_data(200)
            elif scenario == "mixed":
                self.send_mixed_data(300)
            else:
                logger.warning(f"⚠️ Unknown scenario: {scenario}")
                return False
            
            # Monitor for a while
            logger.info("📊 Monitoring drift detection for 30 seconds...")
            for i in range(30):
                status = self.get_consumer_status()
                logger.info(f"📈 Status update {i+1}/30: {status}")
                time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo scenario failed: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup Kafka connections"""
        logger.info("🧹 Cleaning up Kafka connections...")
        
        if self.producer:
            self.producer.close()
        
        if self.consumer:
            self.consumer.stop_consuming()
        
        logger.info("✅ Cleanup completed")

def interactive_demo():
    """Interactive demo with user input"""
    demo = KafkaDriftDemo()
    
    print("\n" + "="*60)
    print("📊 KAFKA DRIFT MONITORING DEMO")
    print("="*60)
    
    print("\nAvailable scenarios:")
    print("1. Normal data only")
    print("2. Drifted data only") 
    print("3. Mixed data (normal + drifted)")
    print("4. Interactive mode")
    print("5. Exit")
    
    while True:
        choice = input("\nSelect scenario (1-5): ").strip()
        
        if choice == "1":
            demo.run_demo_scenario("normal")
        elif choice == "2":
            demo.run_demo_scenario("drifted")
        elif choice == "3":
            demo.run_demo_scenario("mixed")
        elif choice == "4":
            interactive_mode(demo)
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-5.")

def interactive_mode(demo):
    """Interactive mode for manual control"""
    print("\n🎮 Interactive Mode")
    print("Commands: send_normal, send_drifted, status, quit")
    
    if not demo.setup():
        print("❌ Failed to setup demo")
        return
    
    demo.start_consumer()
    
    try:
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == "send_normal":
                n = int(input("Number of samples: "))
                demo.send_normal_data(n)
            
            elif command == "send_drifted":
                n = int(input("Number of samples: "))
                demo.send_drifted_data(n)
            
            elif command == "status":
                status = demo.get_consumer_status()
                print(f"📊 Consumer Status: {status}")
            
            elif command == "quit":
                break
            
            else:
                print("❌ Unknown command")
    
    finally:
        demo.cleanup()

def quick_demo():
    """Quick demo with predefined scenario"""
    demo = KafkaDriftDemo()
    
    print("🚀 Running quick demo...")
    success = demo.run_demo_scenario("mixed")
    
    if success:
        print("✅ Demo completed successfully!")
    else:
        print("❌ Demo failed!")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kafka Drift Monitoring Demo")
    parser.add_argument("--mode", choices=["interactive", "quick"], 
                       default="quick", help="Demo mode")
    parser.add_argument("--scenario", choices=["normal", "drifted", "mixed"],
                       default="mixed", help="Demo scenario")
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        interactive_demo()
    else:
        demo = KafkaDriftDemo()
        demo.run_demo_scenario(args.scenario)

if __name__ == "__main__":
    main() 