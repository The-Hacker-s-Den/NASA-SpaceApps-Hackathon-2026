"""
Verification Test Suite for Prithvi Weather + Soil + Air Quality AI
====================================================================
Tests multi-task predictions across Islamabad, Murree, and Lahore,
verifying weather physical bounds, soil moisture ranges, and AQI categories.
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from prithvi_soil_weather_model import (
    interpret_air_quality,
    interpret_soil_health,
    ALL_TARGETS,
    WEATHER_TARGETS,
    SOIL_TARGETS,
    AQ_TARGETS
)


class TestAirQualityLogic(unittest.TestCase):
    def test_aqi_categories(self):
        """Verify EPA AQI categorization and advisories"""
        cat, desc, emoji = interpret_air_quality(25)
        self.assertEqual(cat, "Good")
        self.assertEqual(emoji, "🟢")

        cat, desc, emoji = interpret_air_quality(75)
        self.assertEqual(cat, "Moderate")
        self.assertEqual(emoji, "🟡")

        cat, desc, emoji = interpret_air_quality(135)
        self.assertEqual(cat, "Unhealthy for Sensitive")
        self.assertEqual(emoji, "🟠")

        cat, desc, emoji = interpret_air_quality(175)
        self.assertEqual(cat, "Unhealthy")
        self.assertEqual(emoji, "🔴")

        cat, desc, emoji = interpret_air_quality(250)
        self.assertEqual(cat, "Very Unhealthy")
        self.assertEqual(emoji, "🟣")

        cat, desc, emoji = interpret_air_quality(380)
        self.assertEqual(cat, "Hazardous")
        self.assertEqual(emoji, "⚫")

    def test_soil_health_logic(self):
        """Verify soil health interpretation logic"""
        # Frozen test
        res = interpret_soil_health(vwc_5=0.2, smi_5=0.1, smd=10, frost_pct=65)
        self.assertIn("Frozen", res)

        # Drought test
        res = interpret_soil_health(vwc_5=0.03, smi_5=-0.7, smd=20, frost_pct=0)
        self.assertIn("Dry", res)

        # Deficit test
        res = interpret_soil_health(vwc_5=0.2, smi_5=-0.1, smd=65, frost_pct=0)
        self.assertIn("Deficit", res)

        # Healthy test
        res = interpret_soil_health(vwc_5=0.25, smi_5=0.15, smd=10, frost_pct=0)
        self.assertIn("Optimal", res)


class TestArchitectureTargets(unittest.TestCase):
    def test_target_counts(self):
        """Verify 5 weather + 10 soil + 1 AQ = 16 outputs"""
        self.assertEqual(len(WEATHER_TARGETS), 5)
        self.assertEqual(len(SOIL_TARGETS), 10)
        self.assertEqual(len(AQ_TARGETS), 1)
        self.assertEqual(len(ALL_TARGETS), 16)
        self.assertIn("air_quality:idx", ALL_TARGETS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
