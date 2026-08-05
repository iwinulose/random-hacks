import Foundation
import MapKit
import CoreLocation

enum LocationMath {
    static func bearing(from origin: CLLocationCoordinate2D, to destination: CLLocationCoordinate2D) -> CLLocationDirection {
        let originLatitude = origin.latitude.radians
        let originLongitude = origin.longitude.radians
        let destinationLatitude = destination.latitude.radians
        let destinationLongitude = destination.longitude.radians

        let y = sin(destinationLongitude - originLongitude) * cos(destinationLatitude)
        let x = cos(originLatitude) * sin(destinationLatitude)
            - sin(originLatitude) * cos(destinationLatitude) * cos(destinationLongitude - originLongitude)

        let heading = atan2(y, x).degrees
        return normalizedDegrees(heading)
    }

    static func normalizedDegrees(_ degrees: CLLocationDirection) -> CLLocationDirection {
        var value = degrees.truncatingRemainder(dividingBy: 360)
        if value < 0 {
            value += 360
        }
        return value
    }

    static func shortestAngleDelta(from source: CLLocationDirection, to destination: CLLocationDirection) -> CLLocationDirection {
        let delta = normalizedDegrees(destination - source)
        if delta > 180 {
            return delta - 360
        }
        return delta
    }

    static func geodesicCoordinates(
        from origin: CLLocationCoordinate2D,
        to destination: CLLocationCoordinate2D,
        progress: Double = 1
    ) -> [CLLocationCoordinate2D] {
        let polyline = MKGeodesicPolyline(coordinates: [origin, destination], count: 2)
        let pointCount = polyline.pointCount
        guard pointCount > 1 else { return [origin, destination] }

        let allPoints = polyline.points()
        let coordinates = (0..<pointCount).map { allPoints[$0].coordinate }
        let cappedProgress = min(max(progress, 0), 1)
        let visibleCount = max(2, Int(Double(coordinates.count - 1) * cappedProgress) + 1)
        return Array(coordinates.prefix(visibleCount))
    }

    static func coordinateRegion(center: CLLocationCoordinate2D, distance: CLLocationDistance) -> MKCoordinateRegion {
        MKCoordinateRegion(
            center: center,
            latitudinalMeters: max(distance, 250),
            longitudinalMeters: max(distance, 250)
        )
    }

    static func mapRectIncluding(_ coordinates: [CLLocationCoordinate2D], paddingMeters: Double = 1000) -> MKMapRect {
        let points = coordinates.map(MKMapPoint.init)
        guard let firstPoint = points.first else { return .world }

        var rect = MKMapRect(origin: firstPoint, size: MKMapSize(width: 0, height: 0))
        for point in points.dropFirst() {
            rect = rect.union(MKMapRect(origin: point, size: MKMapSize(width: 0, height: 0)))
        }

        let padding = MKMapPointsPerMeterAtLatitude(coordinates.first?.latitude ?? 0) * paddingMeters
        return rect.insetBy(dx: -padding, dy: -padding)
    }
}

private extension CLLocationDegrees {
    var radians: Double { self * .pi / 180 }
    var degrees: Double { self * 180 / .pi }
}
