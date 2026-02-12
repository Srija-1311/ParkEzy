from shapely.geometry import Point, Polygon

def predict_occupancy(slots, car_centers):
    predictions = []

    for slot in slots:
        poly = Polygon(slot["polygon"])
        occupied = any(poly.contains(Point(cx, cy)) for cx, cy in car_centers)
        predictions.append(occupied)

    return predictions
