"""
Verification Test Suite for NASA Challenge Considerations & Innovations
========================================================================
Validates:
  1. Crop rotation strategy simulation for Barani and Irrigated tracts
  2. Climate sensitivity "what-if" modeling (temperature & precipitation anomalies)
  3. Scientific glossary completeness (ET, NDVI, soil moisture anomalies, water balance, satellite vs ground)
  4. Web Dashboard HTTP API endpoints (/api/rotations, /api/climate-sensitivity, /api/glossary)
  5. UI component presence in HTML dashboard
"""

import sys
import os
import unittest
import json
from urllib.request import urlopen, Request
from http.server import HTTPServer
import threading
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from nasa_challenge_evaluator import (
    simulate_crop_rotations,
    simulate_climate_sensitivity,
    SCIENTIFIC_GLOSSARY,
    ROTATION_SCENARIOS
)
from prithvi_weather_gui import DashboardRequestHandler, HTML_DASHBOARD


class TestNASAChallengeFeatures(unittest.TestCase):

    def test_glossary_completeness(self):
        """Verifies that all required NASA scientific concepts are documented."""
        required_keys = ["evapotranspiration", "soil_moisture_anomaly", "ndvi_vegetation_index", "water_balance", "satellite_vs_ground"]
        for key in required_keys:
            self.assertIn(key, SCIENTIFIC_GLOSSARY)
            item = SCIENTIFIC_GLOSSARY[key]
            self.assertIn("term", item)
            self.assertIn("formula", item)
            self.assertIn("definition", item)
            self.assertIn("field_impact", item)
            self.assertIn("nasa_mission", item)

    def test_barani_crop_rotations(self):
        """Tests that Barani rainfed tracts favor water resilience over intensive monoculture."""
        res = simulate_crop_rotations("Chakwal", is_barani=True, vwc_root=0.20, flood_score=15.0, farmer_priority="water")
        self.assertEqual(res["location"], "Chakwal")
        self.assertTrue(res["is_barani"])
        self.assertIn("Water-Conserving", res["recommended_rotation"])
        top_scenario = res["scenarios"][0]
        self.assertGreater(top_scenario["dynamic_score"], 80)
        self.assertGreaterEqual(len(top_scenario["cycle"]), 3)
        self.assertIn("benefits", top_scenario)
        self.assertGreater(top_scenario["benefits"]["water_savings_pct"], 20)

    def test_irrigated_crop_rotations(self):
        """Tests that Irrigated plains support economic intensive rotation when farmer requests income."""
        res = simulate_crop_rotations("Multan", is_barani=False, vwc_root=0.30, flood_score=20.0, farmer_priority="income")
        self.assertEqual(res["location"], "Multan")
        self.assertFalse(res["is_barani"])
        self.assertIn("Maximum Income", res["recommended_rotation"])
        top_scenario = res["scenarios"][0]
        self.assertGreater(top_scenario["dynamic_score"], 80)

    def test_climate_sensitivity_heatwave(self):
        """Tests field physiological response under +3°C heatwave scenario."""
        res = simulate_climate_sensitivity(
            base_temp=30.0,
            base_precip=5.0,
            base_vwc=0.25,
            base_flood=20.0,
            temp_delta=3.5,
            precip_mult=0.8
        )
        self.assertEqual(res["projected_temp_c"], 33.5)
        self.assertGreater(res["et_demand_shift_pct"], 15.0)  # High evaporative surge
        self.assertLess(res["projected_soil_moisture_m3m3"], 0.25)
        self.assertIn("Heatwave", res["thermal_diagnosis"])

    def test_climate_sensitivity_monsoon_deluge(self):
        """Tests field flood vulnerability under 180% monsoon surge."""
        res = simulate_climate_sensitivity(
            base_temp=26.0,
            base_precip=20.0,
            base_vwc=0.32,
            base_flood=35.0,
            temp_delta=0.0,
            precip_mult=1.8
        )
        self.assertEqual(res["projected_precip_mm"], 36.0)
        self.assertGreater(res["projected_flood_risk_score"], 50.0)
        self.assertIn("Inundation Risk", res["hydrological_diagnosis"])

    def test_html_dashboard_elements(self):
        """Verifies that all GUI components are embedded in the HTML dashboard template."""
        self.assertIn("Crop Rotation Simulator", HTML_DASHBOARD)
        self.assertIn("Interactive Map Widget", HTML_DASHBOARD)
        self.assertIn("NASA Scientific Intelligence Glossary", HTML_DASHBOARD)
        self.assertIn("climate-temp-slider", HTML_DASHBOARD)
        self.assertIn("climate-precip-slider", HTML_DASHBOARD)
        self.assertIn("glossary-modal", HTML_DASHBOARD)
        self.assertIn("Hourly Forecast", HTML_DASHBOARD)
        self.assertIn("UV Index Widget", HTML_DASHBOARD)
        self.assertIn("Sunrise/Sunset Widget", HTML_DASHBOARD)

    def test_gui_http_endpoints(self):
        """Tests that the HTTP server correctly responds to the new JSON API endpoints."""
        port = 5892
        server = HTTPServer(("127.0.0.1", port), DashboardRequestHandler)
        t = threading.Thread(target=server.serve_forever)
        t.daemon = True
        t.start()
        time.sleep(0.5)

        base_url = f"http://127.0.0.1:{port}"

        try:
            # 1. /api/rotations
            req = Request(f"{base_url}/api/rotations?station=chakwal&priority=water&vwc=0.22&flood=18.0")
            with urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertIn("recommended_rotation", data)
                self.assertIn("scenarios", data)
                self.assertEqual(len(data["scenarios"]), 4)

            # 2. /api/climate-sensitivity
            req = Request(f"{base_url}/api/climate-sensitivity?temp=24.0&precip=5.0&vwc=0.25&flood=15.0&temp_delta=2.0&precip_mult=1.2")
            with urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data["projected_temp_c"], 26.0)
                self.assertIn("et_demand_shift_pct", data)
                self.assertIn("thermal_diagnosis", data)

            # 3. /api/glossary
            req = Request(f"{base_url}/api/glossary")
            with urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertIn("evapotranspiration", data)
                self.assertIn("ndvi_vegetation_index", data)

        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
