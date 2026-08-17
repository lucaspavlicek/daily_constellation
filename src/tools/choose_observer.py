import math
import random
import numpy as np
import datetime
from starplot.models import Constellation
from shapely.geometry import Polygon, MultiPolygon
from starplot import Observer
import shapely

import numpy as np

def haversine(ra1, dec1, ra2, dec2):
    """
    Calculates the great-circle distance between two points on the celestial sphere. Works in radians
    """    
    a = math.sin((dec2 - dec1) / 2)**2 + math.cos(dec1) * math.cos(dec2) * math.sin((ra2 - ra1) / 2)**2
    return 2 * math.asin(math.sqrt(a))

def azi_alt_to_ra_dec(sid: float, lat: float, azi: float, alt: float):
    """
    Transforms Alt/Az to RA/Dec.
    """
    sin_dec = math.sin(alt) * math.sin(lat) + math.cos(alt) * math.cos(lat) * math.cos(azi)

    dec = math.asin(max(-1.0, min(1.0, sin_dec)))

    y = -math.sin(azi) * math.cos(alt) / math.cos(dec)
    x = (math.sin(alt) - math.sin(dec) * math.sin(lat)) / (math.cos(dec) * math.cos(lat))
    ha = math.atan2(y, x)
    
    ra = (sid - ha) % (2 * math.pi)
    
    return ra, dec

def ra_dec_to_azi_alt(sid, lat, ra, dec):
    """
    Transforms RA/Dec to Alt/Azi.
    """
    ha = sid - ra
    
    sin_alt = (math.sin(dec) * math.sin(lat) + 
               math.cos(dec) * math.cos(lat) * math.cos(ha))
    
    alt = math.asin(max(-1.0, min(1.0, sin_alt)))
    
    y = -math.sin(ha) * math.cos(dec)
    x = math.sin(dec) * math.cos(lat) - math.cos(dec) * math.sin(lat) * math.cos(ha)

    azi = math.atan2(y, x) % (2 * math.pi)
        
    return azi, alt

def generate_point(rng: random.Random, max_alt: float = math.pi/2):

    u1 = rng.random()
    u2 = rng.random()*math.sin(max_alt)

    azi = 2*math.pi*u1 
    alt = math.asin(u2)

    return azi, alt


def constellation_centroid(abbr: str):
    if abbr == 'ser':
        geom1 = Constellation.get(iau_id='ser1').boundary
        geom2 = Constellation.get(iau_id='ser2').boundary

        geometry = shapely.ops.unary_union([geom1, geom2])

        del geom1, geom2
    else:
        geometry = Constellation.get(iau_id=abbr).boundary

    if isinstance(geometry, (Polygon, MultiPolygon)):

        pts = shapely.get_coordinates(geometry)

        ras = np.deg2rad(pts[:, 0])
        decs = np.deg2rad(pts[:, 1])

        x = np.cos(decs) * np.cos(ras)
        y = np.cos(decs) * np.sin(ras)
        z = np.sin(decs)

        c_x = np.mean(x)
        c_y = np.mean(y)
        c_z = np.mean(z)

        r = math.sqrt(c_x**2 + c_y**2)
        c_ra = math.atan2(c_y, c_x) % (2*np.pi)
        c_dec = math.atan2(c_z, r)

        return c_ra, c_dec

    else:
        raise ValueError('geometry is not a Polygon or MultiPolygon')
    
def choose_observer_zenith(con1, con2, rng):

    ra1, dec1 = constellation_centroid(con1)
    ra2, dec2 = constellation_centroid(con2)

    azi2, alt2 = ra_dec_to_azi_alt(ra1, dec1, ra2, dec2)

    max_alt = min(math.pi - haversine(ra1, dec1, ra2, dec2), math.pi/2)

    for _ in range(1_000_000):
        azi, alt = generate_point(rng, max_alt=max_alt)

        if haversine(azi, alt, azi2, alt2)*2 < math.pi:
            return azi_alt_to_ra_dec(ra1, dec1, azi, alt)
        
    raise ValueError('Somehow we failed to find a suitable observer zenith. This was never supposed to happen.')
    
def create_observer(ra: float, dec: float):
    """
    Calculates the (Latitude, Longitude) in degrees where the given 
    RA and Dec are perfectly positioned at the zenith right now.
    """

    lat = math.degrees(dec)

    now = datetime.datetime.now(datetime.timezone.utc)
    
    # The J2000 timestamp is 946728000
    seconds_since_j2000 = now.timestamp() - 946728000.0
    days_since_j2000 = seconds_since_j2000 / 86400.0
    
    # standard IAU 1982 linear expansion formula tracking Earth's rotation which I copied
    gmst_hours = (6.697374558 + 0.06570982441908 * days_since_j2000 + 1.00273790935 * (now.hour + now.minute/60.0 + now.second/3600.0)) % 24
    gmst = gmst_hours * 15.0

    lon = math.degrees(ra) - gmst
    
    lon = (lon + 180) % (360) - 180

    observer = Observer(
        datetime=now,
        lat=lat,
        lon=lon,
    )

    return observer