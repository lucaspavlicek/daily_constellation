import warnings

import matplotlib
matplotlib.use("Agg")

from starplot import ZenithPlot, Observer, styles, CollisionHandler, _
from starplot.models import Constellation
from starplot.styles import PolygonStyle
from shapely.geometry import MultiPolygon

from matplotlib.colors import LinearSegmentedColormap, to_hex

warnings.filterwarnings(
    "ignore",
    message=r".*ChainedAssignmentError.*",
    category=FutureWarning,
)


def highlight_constellation(p: ZenithPlot, iau_id: str, fill_color: str = "#31ce80", alpha: float = 0.1) -> ZenithPlot:
    """
    Highlight a constellation region on the plot.
    """
    constellation = Constellation.get(iau_id=iau_id)

    highlight_style = PolygonStyle(
        fill_color=fill_color,
        alpha=alpha,
        edge_width=0,
    )

    geometry = constellation.boundary

    if isinstance(geometry, MultiPolygon):

        for poly in geometry.geoms:
            p.polygon(geometry=poly, style=highlight_style)
            
    else:
        p.polygon(geometry=geometry, style=highlight_style)

    return p


def choose_colors(n: int) -> list[str]:
    """
    Returns a list of n visually smooth hex colors from Green to Red using Matplotlib.
    """
    if n < 2:
        raise ValueError("n must be at least 2.")
        
    cmap = LinearSegmentedColormap.from_list("red_to_green", ["#FF0000", "#FFFF00", "#00FF00"])
    
    colors = [to_hex(cmap(i / (n - 1))) for i in range(n)]
    return colors

def flip_observer(observer: Observer) -> Observer:
    """
    Takes a Starplot Observer and returns a new Observer on the exact
    opposite side of the Earth.
    """
    current_lat = observer.lat
    current_lon = observer.lon
    
    opposite_lat = -current_lat
    
    if current_lon < 0:
        opposite_lon = current_lon + 180
    else:
        opposite_lon = current_lon - 180
        
    return Observer(
        dt=observer.dt,
        lat=opposite_lat,
        lon=opposite_lon,
        elevation=observer.elevation
    )

def make_zenith_plot(observer: Observer, counter: dict, guess: str, plot_type: str = 'zenith_plot') -> ZenithPlot:
    """
    Create a zenith plot for the given observer and counter.
    """
    
    style = styles.PlotStyle()

    style.text_border_width = 0

    style.border_line_color = "black"

    style.horizon.line.color = "#04006B" if plot_type == 'zenith_plot' else "#391F00"
    style.horizon.label.font_color = "#707070"
    style.horizon.line.edge_color = "#707070"

    style.background_color = "#00000000"

    style.constellation_labels.font_color = "#FFFFFF"
    style.constellation_lines.color = "#707070"

    style.star.marker.color = "#707070"
    style.star.marker.edge_color = "#707070"

    style.constellation_labels.zorder = style.star.marker.zorder + 1
    
    obs = observer if plot_type == 'zenith_plot' else flip_observer(observer)

    p = ZenithPlot(
        observer=obs,
        style=style,
        resolution=512,
        autoscale=True,
        suppress_warnings=True,
        
    )
    p.horizon()

    colors = choose_colors(max(counter.values())+1)

    for abbr in counter.keys():

        if counter[abbr] > -1:
            color = colors[counter[abbr]]

        else:
            color = '#767676'

        if abbr == 'ser':
            highlight_constellation(p, iau_id='ser1', fill_color=color, alpha=0.25)
            highlight_constellation(p, iau_id='ser2', fill_color=color, alpha=0.25)
        else:
            highlight_constellation(p, iau_id=abbr, fill_color=color, alpha=0.25)

    p.constellations()
    p.constellation_borders()
    p.stars(where=[_.magnitude < 4.6], where_labels=[_.magnitude < -100.0])
  

    p.constellation_labels(
        collision_handler=CollisionHandler(
            attempts=4,
            plot_on_fail=True,
            allow_label_collisions=True, 
            allow_constellation_line_collisions=True
        )
    )

    for text in p.ax.texts:
        text.set_clip_path(p.ax.patch)
        text.set_clip_on(True)

    p.ax.text(
        0.02, 0.98, f"Turn: {max(counter.values())}\nGuess: {guess}",
        transform=p.ax.transAxes,
        ha="left", va="top",
        fontsize=8,
        fontfamily="DejaVu Sans",
        color="#707070"
    )

    p.ax.text(
        0.84, 0.98, f"Observer\nlat: {observer.lat:.2f}\nlon: {observer.lon:.2f}",
        transform=p.ax.transAxes,
        ha="left", va="top",
        fontsize=8,
        fontfamily="DejaVu Sans",
        color="#707070"
    )

    return p.fig