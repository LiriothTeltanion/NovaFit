#!/usr/bin/env python3
"""Test script for weather functionality"""

import sys
import os

# Add current directory to path to import novafit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from novafit import get_weather

def test_weather():
    """Test the weather function with different cities."""
    cities = ["beersheba", "tel aviv", "jerusalem"]
    
    print("=== Testing Weather Function ===")
    
    for city in cities:
        print(f"\nTesting weather for: {city}")
        result = get_weather(city)
        print(f"Result: {result}")
        
        if result["status"] == "success":
            print(f"✅ SUCCESS: {city} - {result['temp']}°C, {result['humidity']}% humidity")
        else:
            print(f"❌ FAILED: {city} - {result['source']}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_weather()