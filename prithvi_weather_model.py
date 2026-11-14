"""
Prithvi-Informed Spatio-Temporal Weather Forecasting Model
==========================================================
Integrates NASA-IBM Prithvi Geospatial Foundation Model representations
(Location & Temporal Sinusoidal Harmonic Encodings) with deep multi-task
residual networks and gradient boosted ensembles for future weather prediction.
"""

import sys
import os
import math
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

# Try importing LocationEncoder and TemporalEncoder directly from Prithvi
PRITHVI_PATH = r"C:\Users\Hp\prithvi"
if os.path.exists(PRITHVI_PATH) and PRITHVI_PATH not in sys.path:
    sys.path.append(PRITHVI_PATH)

try:
    from prithvi_mae import LocationEncoder, TemporalEncoder
    HAS_PRITHVI = True
except Exception:
    HAS_PRITHVI = False

    # Standalone implementation conforming to Prithvi architecture
    def _get_1d_sincos_embed_from_grid_torch(embed_dim: int, pos: torch.Tensor):
        omega = torch.arange(embed_dim // 2, dtype=torch.float32, device=pos.device)
        omega /= embed_dim / 2.0
        omega = 1.0 / 10000**omega
        pos = pos.reshape(-1)
        out = torch.einsum("m,d->md", pos, omega)
        return torch.cat([torch.sin(out), torch.cos(out)], dim=1)

    class TemporalEncoder(nn.Module):
        def __init__(self, embed_dim: int, trainable_scale: bool = False):
            super().__init__()
            self.embed_dim = embed_dim
            self.year_embed_dim = embed_dim // 2
            self.julian_day_embed_dim = embed_dim - self.year_embed_dim
            if trainable_scale:
                self.scale = nn.Parameter(torch.full((1,), 0.1))
            else:
                self.register_buffer('scale', torch.ones(1))

        def forward(self, temporal_coords: torch.Tensor, tokens_per_frame: int = None):
            shape = temporal_coords.shape[:2] + (-1,)
            year = _get_1d_sincos_embed_from_grid_torch(
                self.year_embed_dim, temporal_coords[:, :, 0].flatten()).reshape(shape)
            julian_day = _get_1d_sincos_embed_from_grid_torch(
                self.julian_day_embed_dim, temporal_coords[:, :, 1].flatten()).reshape(shape)
            embedding = self.scale * torch.cat([year, julian_day], dim=-1)
            return embedding

    class LocationEncoder(nn.Module):
        def __init__(self, embed_dim: int, trainable_scale: bool = False):
            super().__init__()
            self.embed_dim = embed_dim
            self.lat_embed_dim = embed_dim // 2
            self.lon_embed_dim = embed_dim - self.lat_embed_dim
            if trainable_scale:
                self.scale = nn.Parameter(torch.full((1,), 0.1))
            else:
                self.register_buffer('scale', torch.ones(1))

        def forward(self, location_coords: torch.Tensor):
            shape = location_coords.shape[:1] + (1, -1)
            lat = _get_1d_sincos_embed_from_grid_torch(
                self.lat_embed_dim, location_coords[:, 0].flatten()).reshape(shape)
            lon = _get_1d_sincos_embed_from_grid_torch(
                self.lon_embed_dim, location_coords[:, 1].flatten()).reshape(shape)
            embedding = self.scale * torch.cat([lat, lon], dim=-1)
            return embedding


# Target Weather Parameters
WEATHER_TARGETS = [
    "t_2m:C",                   # 2-meter air temperature (°C)
    "precip_1h:mm",             # 1-hour precipitation (mm)
    "relative_humidity_2m:p",   # 2-meter relative humidity (%)
    "wind_speed_10m:ms",        # 10-meter wind speed (m/s)
    "msl_pressure:hPa"          # Mean sea level pressure (hPa)
]


def extract_spatiotemporal_features(lat_series, lon_series, datetime_series):
    """
    Transforms location coordinates and future datetimes into rich feature matrix:
    - Prithvi raw coordinates
    - Prithvi temporal coordinates (Year, Day of Year)
    - Cyclic diurnal features (sin/cos hour)
    - Cyclic seasonal features (sin/cos day of year, sin/cos month)
    - Year progress
    """
    if not isinstance(datetime_series, pd.Series):
        datetime_series = pd.Series(datetime_series)
    datetimes = pd.to_datetime(datetime_series)
    
    lats = np.atleast_1d(np.asarray(lat_series, dtype=np.float32))
    lons = np.atleast_1d(np.asarray(lon_series, dtype=np.float32))
    
    years = datetimes.dt.year.values.astype(np.float32)
    try:
        days_of_year = datetimes.dt.day_of_year.values.astype(np.float32)
    except AttributeError:
        days_of_year = datetimes.dt.dayofyear.values.astype(np.float32)
    hours = datetimes.dt.hour.values.astype(np.float32) + datetimes.dt.minute.values.astype(np.float32) / 60.0
    months = datetimes.dt.month.values.astype(np.float32)
    
    # Cyclic representations
    sin_hour = np.sin(2.0 * np.pi * hours / 24.0).astype(np.float32)
    cos_hour = np.cos(2.0 * np.pi * hours / 24.0).astype(np.float32)
    
    sin_doy = np.sin(2.0 * np.pi * days_of_year / 365.25).astype(np.float32)
    cos_doy = np.cos(2.0 * np.pi * days_of_year / 365.25).astype(np.float32)
    
    sin_month = np.sin(2.0 * np.pi * months / 12.0).astype(np.float32)
    cos_month = np.cos(2.0 * np.pi * months / 12.0).astype(np.float32)
    
    # Normalized raw values
    norm_lat = (lats / 90.0).astype(np.float32)
    norm_lon = (lons / 180.0).astype(np.float32)
    year_scaled = ((years - 2020.0) / 10.0).astype(np.float32)

    features = np.column_stack([
        lats,           # 0
        lons,           # 1
        years,          # 2
        days_of_year,   # 3
        hours,          # 4
        sin_hour,       # 5
        cos_hour,       # 6
        sin_doy,        # 7
        cos_doy,        # 8
        sin_month,      # 9
        cos_month,      # 10
        norm_lat,       # 11
        norm_lon,       # 12
        year_scaled     # 13
    ])
    
    feature_names = [
        "lat", "lon", "year", "day_of_year", "hour",
        "sin_hour", "cos_hour", "sin_doy", "cos_doy",
        "sin_month", "cos_month", "norm_lat", "norm_lon", "year_scaled"
    ]
    return features, feature_names


class ResBlock(nn.Module):
    """Residual MLP block with LayerNorm and GELU activations"""
    def __init__(self, dim, dropout=0.05):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim, dim),
            nn.LayerNorm(dim)
        )
        self.act = nn.GELU()

    def forward(self, x):
        return self.act(x + self.net(x))


class PrithviWeatherNet(nn.Module):
    """
    Spatio-Temporal Deep Neural Network for Weather Prediction.
    Directly incorporates Prithvi's LocationEncoder and TemporalEncoder.
    """
    def __init__(self, embed_dim: int = 64, hidden_dim: int = 256, num_blocks: int = 3):
        super().__init__()
        self.embed_dim = embed_dim
        
        # NASA-IBM Prithvi Encoders
        self.location_encoder = LocationEncoder(embed_dim=embed_dim)
        self.temporal_encoder = TemporalEncoder(embed_dim=embed_dim)
        
        # Additional cyclic features: sin/cos hour, doy, month, norm coords, year_scaled (9 features)
        cyclic_dim = 9
        total_input_dim = embed_dim + embed_dim + cyclic_dim  # 64 + 64 + 9 = 137
        
        self.input_proj = nn.Sequential(
            nn.Linear(total_input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.05)
        )
        
        self.blocks = nn.ModuleList([ResBlock(hidden_dim) for _ in range(num_blocks)])
        
        # Multi-task heads for physically grounded weather variables
        self.head_temperature = nn.Linear(hidden_dim, 1)      # (°C)
        self.head_precipitation = nn.Linear(hidden_dim, 1)    # (mm) >= 0
        self.head_humidity = nn.Linear(hidden_dim, 1)         # (%) in [0, 100]
        self.head_wind_speed = nn.Linear(hidden_dim, 1)       # (m/s) >= 0
        self.head_pressure = nn.Linear(hidden_dim, 1)         # (hPa) ~1013

    def forward(self, raw_features: torch.Tensor):
        """
        raw_features shape: (Batch, 14) as constructed by extract_spatiotemporal_features
        """
        # Extract location coords: lat, lon -> shape (B, 2)
        loc_coords = raw_features[:, 0:2]
        # Extract temporal coords: year, day_of_year -> shape (B, 1, 2)
        time_coords = raw_features[:, 2:4].unsqueeze(1)
        
        # Prithvi embeddings
        loc_emb = self.location_encoder(loc_coords).squeeze(1)     # (B, embed_dim)
        time_emb = self.temporal_encoder(time_coords).squeeze(1)   # (B, embed_dim)
        
        # Cyclic and normalized features: indices 5 to 13 (9 dims)
        cyclic_feats = raw_features[:, 5:14]                       # (B, 9)
        
        # Concatenate full representation
        x = torch.cat([loc_emb, time_emb, cyclic_feats], dim=-1)
        x = self.input_proj(x)
        
        for block in self.blocks:
            x = block(x)
            
        # Apply physical domain constraints
        temp = self.head_temperature(x)
        precip = F.softplus(self.head_precipitation(x))            # strictly >= 0 mm
        humidity = torch.sigmoid(self.head_humidity(x)) * 100.0     # strictly in [0, 100]%
        wind = F.softplus(self.head_wind_speed(x))                 # strictly >= 0 m/s
        pressure = 1013.25 + self.head_pressure(x) * 15.0          # calibrated around sea level hPa
        
        out = torch.cat([temp, precip, humidity, wind, pressure], dim=-1)
        return out
