from typing import List


PORT_COORDS = {
    "Singapore": (1.2640, 103.8190),
    "Colombo": (6.9271, 79.8612),
    "Mumbai": (19.0760, 72.8777),
    "Jebel Ali": (25.0112, 55.0715),
    "Rotterdam": (51.9244, 4.4777),
    "Hamburg": (53.5511, 9.9937),
    "Shanghai": (31.2304, 121.4737),
    "Hong Kong": (22.3193, 114.1694),
    "Los Angeles": (34.0522, -118.2437),
}


def get_best_route(origin: str, destination: str) -> List[List[float]]:
    if origin not in PORT_COORDS or destination not in PORT_COORDS:
        return []

    start = PORT_COORDS[origin]
    end = PORT_COORDS[destination]
    return [[start[0], start[1]], [end[0], end[1]]]