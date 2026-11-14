"""
Verification Test Suite for Prithvi Weather Prediction AI
=========================================================
Tests future predictions across different locations and timestamps,
verifying that predictions meet physical sanity bounds and format contracts.
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from predict_weather import predict_weather, load_models


class TestWeatherPrediction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n[*] Loading models for verification tests...")
        load_models()
        print("[+] Models loaded successfully.")

    def test_islamabad_future_prediction(self):
        """Test predicting weather for Islamabad 1 week in the future"""
        future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d 12:00:00")
        res = predict_weather(lat=33.6844, lon=73.0479, target_time=future_time)

        self.assertIn("forecast", res)
        self.assertIn("condition", res)
        fc = res["forecast"]

        # Physical sanity checks
        self.assertGreaterEqual(fc["temperature_c"], -15.0)
        self.assertLessEqual(fc["temperature_c"], 55.0)
        self.assertGreaterEqual(fc["precipitation_mm"], 0.0)
        self.assertGreaterEqual(fc["relative_humidity_pct"], 0.0)
        self.assertLessEqual(fc["relative_humidity_pct"], 100.0)
        self.assertGreaterEqual(fc["wind_speed_ms"], 0.0)
        self.assertGreaterEqual(fc["pressure_hpa"], 950.0)
        self.assertLessEqual(fc["pressure_hpa"], 1050.0)

    def test_spatial_consistency(self):
        """Murree (high altitude) should be cooler than Lahore (Punjab plains) on the same day"""
        target_time = "2027-01-15 12:00:00"
        murree = predict_weather(lat=33.9070, lon=73.3943, target_time=target_time)
        lahore = predict_weather(lat=31.5204, lon=74.3587, target_time=target_time)

        print(f"\n[Spatial Test] Murree Temp: {murree['forecast']['temperature_c']}°C | Lahore Temp: {lahore['forecast']['temperature_c']}°C")
        self.assertLess(murree["forecast"]["temperature_c"], lahore["forecast"]["temperature_c"])

    def test_seasonal_consistency(self):
        """Summer (June) should be hotter than Winter (January) in Islamabad"""
        summer = predict_weather(lat=33.6844, lon=73.0479, target_time="2027-06-15 14:00:00")
        winter = predict_weather(lat=33.6844, lon=73.0479, target_time="2027-01-15 14:00:00")

        print(f"[Seasonal Test] Summer Islamabad: {summer['forecast']['temperature_c']}°C | Winter Islamabad: {winter['forecast']['temperature_c']}°C")
        self.assertGreater(summer["forecast"]["temperature_c"], winter["forecast"]["temperature_c"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
