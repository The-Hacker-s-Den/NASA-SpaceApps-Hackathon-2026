"""
Prithvi Soil + Weather Model Architecture
==========================================
Extends PrithviWeatherNet to include soil moisture and soil health features.

New prediction targets added alongside weather:
  SOIL TARGETS:
    - volumetric_soil_water_-5cm:m3m3    Surface volumetric water content
    - volumetric_soil_water_-15cm:m3m3   Root zone volumetric water content
    - volumetric_soil_water_-50cm:m3m3   Deep soil volumetric water content
    - volumetric_soil_water_-150cm:m3m3  Very deep soil volumetric water
    - soil_moisture_index_-5cm:idx       Surface moisture index
    - soil_moisture_index_-15cm:idx      Root zone moisture index
    - soil_moisture_index_-50cm:idx      Deep moisture index
    - soil_moisture_index_-150cm:idx     Very deep moisture index
    - soil_moisture_deficit:mm           Soil moisture deficit
    - soil_frost:p                       Soil frost probability

  WEATHER TARGETS (retained from original model):
    - t_2m:C, precip_1h:mm, relative_humidity_2m:p,
      wind_speed_10m:ms, msl_pressure:hPa
"""

import sys
import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

# ── Prithvi integration ────────────────────────────────────────────────────────
PRITHVI_PATH = r"C:\Users\Hp\prithvi"
if os.path.exists(PRITHVI_PATH) and PRITHVI_PATH not in sys.path:
    sys.path.insert(0, PRITHVI_PATH)

try:
    from prithvi_mae import LocationEncoder, TemporalEncoder
    HAS_PRITHVI = True
    print("[Prithvi] LocationEncoder + TemporalEncoder loaded from prithvi_mae.py")
except Exception:
    HAS_PRITHVI = False

    def _sincos_embed(embed_dim: int, pos: torch.Tensor):
        omega = torch.arange(embed_dim // 2, dtype=torch.float32, device=pos.device)
        omega /= embed_dim / 2.0
        omega = 1.0 / 10000 ** omega
        pos = pos.reshape(-1)
        out = torch.einsum("m,d->md", pos, omega)
        return torch.cat([torch.sin(out), torch.cos(out)], dim=1)

    class TemporalEncoder(nn.Module):
        def __init__(self, embed_dim: int, trainable_scale: bool = False):
            super().__init__()
            self.embed_dim = embed_dim
            self.year_dim  = embed_dim // 2
            self.doy_dim   = embed_dim - self.year_dim
            if trainable_scale:
                self.scale = nn.Parameter(torch.full((1,), 0.1))
            else:
                self.register_buffer("scale", torch.ones(1))

        def forward(self, temporal_coords, tokens_per_frame=None):
            shape = temporal_coords.shape[:2] + (-1,)
            year  = _sincos_embed(self.year_dim, temporal_coords[:, :, 0].flatten()).reshape(shape)
            doy   = _sincos_embed(self.doy_dim,  temporal_coords[:, :, 1].flatten()).reshape(shape)
            return self.scale * torch.cat([year, doy], dim=-1)

    class LocationEncoder(nn.Module):
        def __init__(self, embed_dim: int, trainable_scale: bool = False):
            super().__init__()
            self.embed_dim = embed_dim
            self.lat_dim   = embed_dim // 2
            self.lon_dim   = embed_dim - self.lat_dim
            if trainable_scale:
                self.scale = nn.Parameter(torch.full((1,), 0.1))
            else:
                self.register_buffer("scale", torch.ones(1))

        def forward(self, location_coords):
            shape = location_coords.shape[:1] + (1, -1)
            lat = _sincos_embed(self.lat_dim, location_coords[:, 0].flatten()).reshape(shape)
            lon = _sincos_embed(self.lon_dim, location_coords[:, 1].flatten()).reshape(shape)
            return self.scale * torch.cat([lat, lon], dim=-1)


# ── Target definitions ─────────────────────────────────────────────────────────

WEATHER_TARGETS = [
    "t_2m:C",
    "precip_1h:mm",
    "relative_humidity_2m:p",
    "wind_speed_10m:ms",
    "msl_pressure:hPa",
]

SOIL_TARGETS = [
    "volumetric_soil_water_-5cm:m3m3",
    "volumetric_soil_water_-15cm:m3m3",
    "volumetric_soil_water_-50cm:m3m3",
    "volumetric_soil_water_-150cm:m3m3",
    "soil_moisture_index_-5cm:idx",
    "soil_moisture_index_-15cm:idx",
    "soil_moisture_index_-50cm:idx",
    "soil_moisture_index_-150cm:idx",
    "soil_moisture_deficit:mm",
    "soil_frost:p",
]

AQ_TARGETS = [
    "air_quality:idx",   # Meteomatics Air Quality Index (0–500 scale, US EPA standard)
]

ALL_TARGETS = WEATHER_TARGETS + SOIL_TARGETS + AQ_TARGETS   # 16 total outputs

# Human-readable labels for display
TARGET_DISPLAY = {
    "t_2m:C":                            "Temperature (°C)",
    "precip_1h:mm":                      "Precipitation (mm/h)",
    "relative_humidity_2m:p":            "Relative Humidity (%)",
    "wind_speed_10m:ms":                 "Wind Speed (m/s)",
    "msl_pressure:hPa":                  "Sea Level Pressure (hPa)",
    "volumetric_soil_water_-5cm:m3m3":   "Soil Water  –5 cm (m³/m³)",
    "volumetric_soil_water_-15cm:m3m3":  "Soil Water –15 cm (m³/m³)",
    "volumetric_soil_water_-50cm:m3m3":  "Soil Water –50 cm (m³/m³)",
    "volumetric_soil_water_-150cm:m3m3": "Soil Water –150 cm (m³/m³)",
    "soil_moisture_index_-5cm:idx":      "Moisture Index –5 cm",
    "soil_moisture_index_-15cm:idx":     "Moisture Index –15 cm",
    "soil_moisture_index_-50cm:idx":     "Moisture Index –50 cm",
    "soil_moisture_index_-150cm:idx":    "Moisture Index –150 cm",
    "soil_moisture_deficit:mm":          "Soil Moisture Deficit (mm)",
    "soil_frost:p":                      "Soil Frost Probability (%)",
    "air_quality:idx":                   "Air Quality Index (AQI)",
}

# Physical clamping bounds for inference
TARGET_BOUNDS = {
    "t_2m:C":                            (None, None),
    "precip_1h:mm":                      (0.0,  None),
    "relative_humidity_2m:p":            (0.0,  100.0),
    "wind_speed_10m:ms":                 (0.0,  None),
    "msl_pressure:hPa":                  (900.0, 1100.0),
    "volumetric_soil_water_-5cm:m3m3":   (0.0,  0.6),
    "volumetric_soil_water_-15cm:m3m3":  (0.0,  0.6),
    "volumetric_soil_water_-50cm:m3m3":  (0.0,  0.6),
    "volumetric_soil_water_-150cm:m3m3": (0.0,  0.6),
    "soil_moisture_index_-5cm:idx":      (-1.0, 1.0),
    "soil_moisture_index_-15cm:idx":     (-1.0, 1.0),
    "soil_moisture_index_-50cm:idx":     (-1.0, 1.0),
    "soil_moisture_index_-150cm:idx":    (-1.0, 1.0),
    "soil_moisture_deficit:mm":          (0.0,  None),
    "soil_frost:p":                      (0.0,  100.0),
    "air_quality:idx":                   (0.0,  500.0),  # US EPA AQI scale
}


# ── Feature extraction ─────────────────────────────────────────────────────────

def extract_spatiotemporal_features(lat_series, lon_series, datetime_series):
    """
    Builds the 14-dim spatio-temporal feature matrix used by both models.
    Features: lat, lon, year, day_of_year, hour,
              sin_hour, cos_hour, sin_doy, cos_doy,
              sin_month, cos_month, norm_lat, norm_lon, year_scaled
    """
    if not isinstance(datetime_series, pd.Series):
        datetime_series = pd.Series(datetime_series)
    datetimes = pd.to_datetime(datetime_series)

    lats = np.atleast_1d(np.asarray(lat_series, dtype=np.float32))
    lons = np.atleast_1d(np.asarray(lon_series, dtype=np.float32))

    years       = datetimes.dt.year.values.astype(np.float32)
    days_of_year = (datetimes.dt.dayofyear.values).astype(np.float32)
    hours       = (datetimes.dt.hour.values + datetimes.dt.minute.values / 60.0).astype(np.float32)
    months      = datetimes.dt.month.values.astype(np.float32)

    sin_hour  = np.sin(2.0 * np.pi * hours        / 24.0).astype(np.float32)
    cos_hour  = np.cos(2.0 * np.pi * hours        / 24.0).astype(np.float32)
    sin_doy   = np.sin(2.0 * np.pi * days_of_year / 365.25).astype(np.float32)
    cos_doy   = np.cos(2.0 * np.pi * days_of_year / 365.25).astype(np.float32)
    sin_month = np.sin(2.0 * np.pi * months       / 12.0).astype(np.float32)
    cos_month = np.cos(2.0 * np.pi * months       / 12.0).astype(np.float32)

    norm_lat    = (lats / 90.0).astype(np.float32)
    norm_lon    = (lons / 180.0).astype(np.float32)
    year_scaled = ((years - 2020.0) / 10.0).astype(np.float32)

    features = np.column_stack([
        lats, lons, years, days_of_year, hours,
        sin_hour, cos_hour, sin_doy, cos_doy,
        sin_month, cos_month, norm_lat, norm_lon, year_scaled,
    ])

    feature_names = [
        "lat", "lon", "year", "day_of_year", "hour",
        "sin_hour", "cos_hour", "sin_doy", "cos_doy",
        "sin_month", "cos_month", "norm_lat", "norm_lon", "year_scaled",
    ]
    return features, feature_names


# ── Neural network blocks ──────────────────────────────────────────────────────

class ResBlock(nn.Module):
    """Residual MLP block with LayerNorm + GELU"""
    def __init__(self, dim, dropout=0.05):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
        )
        self.act = nn.GELU()

    def forward(self, x):
        return self.act(x + self.net(x))


# ── Main model ─────────────────────────────────────────────────────────────────

class PrithviSoilWeatherNet(nn.Module):
    """
    Multi-task Prithvi-Informed Neural Network predicting 16 targets:
      5 weather variables + 10 soil variables + 1 air quality index

    Input  : 14-dim spatio-temporal feature vector
    Output : 16-dim prediction (weather + soil + air quality)
    """

    def __init__(self, embed_dim: int = 64, hidden_dim: int = 384, num_blocks: int = 4):
        super().__init__()
        self.embed_dim  = embed_dim
        self.hidden_dim = hidden_dim

        # Prithvi spatial-temporal encoders
        self.location_encoder = LocationEncoder(embed_dim=embed_dim)
        self.temporal_encoder = TemporalEncoder(embed_dim=embed_dim)

        # 9 cyclic / normalized features (indices 5-13 from feature vector)
        cyclic_dim      = 9
        total_input_dim = embed_dim + embed_dim + cyclic_dim  # 64+64+9 = 137

        self.input_proj = nn.Sequential(
            nn.Linear(total_input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.05),
        )

        # Shared trunk
        self.shared_blocks = nn.ModuleList(
            [ResBlock(hidden_dim) for _ in range(num_blocks)]
        )

        # Task-specific branches (deeper for soil — richer patterns needed)
        self.weather_branch = nn.Sequential(ResBlock(hidden_dim))
        self.soil_branch    = nn.Sequential(ResBlock(hidden_dim), ResBlock(hidden_dim))
        self.aq_branch      = nn.Sequential(ResBlock(hidden_dim))

        # ── Weather heads ──────────────────────────────────────────────────────
        self.head_temperature  = nn.Linear(hidden_dim, 1)   # °C,  unconstrained
        self.head_precipitation= nn.Linear(hidden_dim, 1)   # mm,  ≥0 via softplus
        self.head_humidity     = nn.Linear(hidden_dim, 1)   # %,   sigmoid→[0,100]
        self.head_wind         = nn.Linear(hidden_dim, 1)   # m/s, ≥0 via softplus
        self.head_pressure     = nn.Linear(hidden_dim, 1)   # hPa, ~1013 anchored

        # ── Soil heads ────────────────────────────────────────────────────────
        # Volumetric water content (4 depths) → sigmoid → [0, 0.6]
        self.head_vwc_5   = nn.Linear(hidden_dim, 1)
        self.head_vwc_15  = nn.Linear(hidden_dim, 1)
        self.head_vwc_50  = nn.Linear(hidden_dim, 1)
        self.head_vwc_150 = nn.Linear(hidden_dim, 1)
        # Moisture index (4 depths) → tanh → [-1, 1]
        self.head_smi_5   = nn.Linear(hidden_dim, 1)
        self.head_smi_15  = nn.Linear(hidden_dim, 1)
        self.head_smi_50  = nn.Linear(hidden_dim, 1)
        self.head_smi_150 = nn.Linear(hidden_dim, 1)
        # Moisture deficit → softplus → ≥0 mm
        self.head_smd     = nn.Linear(hidden_dim, 1)
        # Soil frost probability → sigmoid → [0, 100] %
        self.head_frost   = nn.Linear(hidden_dim, 1)

        # ── Air Quality head ──────────────────────────────────────────────────
        # AQI (US EPA 0–500 scale) → softplus anchored at ~50 baseline
        self.head_aqi     = nn.Linear(hidden_dim, 1)

    def forward(self, raw_features: torch.Tensor):
        """
        raw_features : (B, 14) from extract_spatiotemporal_features()
        returns      : (B, 16) — [weather×5, soil×10, aq×1]
        """
        loc_coords  = raw_features[:, 0:2]               # lat, lon
        time_coords = raw_features[:, 2:4].unsqueeze(1)  # year, doy
        cyclic      = raw_features[:, 5:14]               # 9 cyclic features

        loc_emb  = self.location_encoder(loc_coords).squeeze(1)   # (B, embed_dim)
        time_emb = self.temporal_encoder(time_coords).squeeze(1)  # (B, embed_dim)

        x = torch.cat([loc_emb, time_emb, cyclic], dim=-1)        # (B, 137)
        x = self.input_proj(x)                                     # (B, hidden_dim)

        for block in self.shared_blocks:
            x = block(x)

        wx = self.weather_branch(x)   # weather task representation
        sx = self.soil_branch(x)      # soil task representation
        ax = self.aq_branch(x)        # air quality task representation

        # ── Weather outputs ────────────────────────────────────────────────────
        temp    = self.head_temperature(wx)                        # °C
        precip  = F.softplus(self.head_precipitation(wx))         # ≥ 0 mm
        humid   = torch.sigmoid(self.head_humidity(wx)) * 100.0   # [0,100]%
        wind    = F.softplus(self.head_wind(wx))                   # ≥ 0 m/s
        press   = 1013.25 + self.head_pressure(wx) * 15.0         # ~hPa

        # ── Soil outputs ───────────────────────────────────────────────────────
        vwc_5   = torch.sigmoid(self.head_vwc_5(sx))   * 0.6     # [0, 0.6] m³/m³
        vwc_15  = torch.sigmoid(self.head_vwc_15(sx))  * 0.6
        vwc_50  = torch.sigmoid(self.head_vwc_50(sx))  * 0.6
        vwc_150 = torch.sigmoid(self.head_vwc_150(sx)) * 0.6
        smi_5   = torch.tanh(self.head_smi_5(sx))                 # [-1, 1]
        smi_15  = torch.tanh(self.head_smi_15(sx))
        smi_50  = torch.tanh(self.head_smi_50(sx))
        smi_150 = torch.tanh(self.head_smi_150(sx))
        smd     = F.softplus(self.head_smd(sx))                   # ≥ 0 mm
        frost   = torch.sigmoid(self.head_frost(sx))  * 100.0     # [0, 100] %

        # ── Air Quality output ─────────────────────────────────────────────────
        # Anchored at a baseline of 50 (Moderate), clipped to [0, 500] AQI
        aqi     = 50.0 + self.head_aqi(ax) * 80.0                 # real-valued AQI

        out = torch.cat([
            temp, precip, humid, wind, press,          # weather (5)
            vwc_5, vwc_15, vwc_50, vwc_150,            # VWC     (4)
            smi_5, smi_15, smi_50, smi_150,            # SMI     (4)
            smd, frost,                                 # misc    (2)
            aqi,                                        # AQ      (1)
        ], dim=-1)                                      # total: 16
        return out


def interpret_soil_health(vwc_5, smi_5, smd, frost_pct):
    """
    Returns a human-readable soil health label based on key soil indicators.
    """
    if frost_pct > 50:
        return "Frozen / Frost-locked"
    if smi_5 < -0.5 or vwc_5 < 0.05:
        return "Severely Dry / Drought Stress"
    if smd > 50:
        return "Moisture Deficit — Irrigation Needed"
    if smi_5 < 0.0:
        return "Slightly Dry — Monitor Moisture"
    if 0.0 <= smi_5 <= 0.3 and vwc_5 >= 0.15:
        return "Optimal Moisture — Healthy"
    if smi_5 > 0.5 or vwc_5 > 0.45:
        return "Saturated — Waterlogging Risk"
    return "Adequate Moisture"


# AQI category thresholds follow US EPA standard (used by Meteomatics air_quality:idx)
AQI_CATEGORIES = [
    (  0,  50, "Good",                    "Air quality is satisfactory — no health risk."),
    ( 51, 100, "Moderate",               "Acceptable; some pollutants may affect very sensitive people."),
    (101, 150, "Unhealthy for Sensitive", "Sensitive groups (asthma, heart disease) may experience effects."),
    (151, 200, "Unhealthy",              "Everyone may experience health effects; sensitive groups, serious effects."),
    (201, 300, "Very Unhealthy",         "Health alert: serious effects for everyone."),
    (301, 500, "Hazardous",             "Emergency conditions; entire population affected."),
]


def interpret_air_quality(aqi: float):
    """
    Returns (category_label, description, emoji) for a given AQI value.
    Follows the US EPA 6-category standard used by Meteomatics air_quality:idx.
    """
    aqi = max(0.0, min(500.0, float(aqi)))
    for lo, hi, label, desc in AQI_CATEGORIES:
        if lo <= aqi <= hi:
            emoji = {"Good": "🟢", "Moderate": "🟡",
                     "Unhealthy for Sensitive": "🟠", "Unhealthy": "🔴",
                     "Very Unhealthy": "🟣", "Hazardous": "⚫"}.get(label, "⚪")
            return label, desc, emoji
    return "Hazardous", AQI_CATEGORIES[-1][3], "⚫"
