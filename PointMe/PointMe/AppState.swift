import SwiftUI
import MapKit
import CoreLocation
import UIKit
import Combine

enum AppTab: Hashable {
    case map
    case compass
}

struct MapSearchRequest: Equatable {
    let id = UUID()
    let selectsExistingQuery: Bool
}

struct TargetLocation: Identifiable, Equatable {
    let id = UUID()
    let name: String
    let subtitle: String?
    let coordinate: CLLocationCoordinate2D

    init(name: String, subtitle: String? = nil, coordinate: CLLocationCoordinate2D) {
        self.name = name
        self.subtitle = subtitle
        self.coordinate = coordinate
    }

    init(mapItem: MKMapItem) {
        self.name = mapItem.name ?? "Selected Destination"
        self.subtitle = nil
        self.coordinate = mapItem.location.coordinate
    }

    static func == (lhs: TargetLocation, rhs: TargetLocation) -> Bool {
        lhs.name == rhs.name
            && lhs.subtitle == rhs.subtitle
            && lhs.coordinate.latitude == rhs.coordinate.latitude
            && lhs.coordinate.longitude == rhs.coordinate.longitude
    }
}

@MainActor
final class AppState: NSObject, ObservableObject {
    @Published private(set) var authorizationStatus: CLAuthorizationStatus = .notDetermined
    @Published private(set) var isLocationServicesEnabled = true
    @Published private(set) var currentLocation: CLLocation?
    @Published private(set) var currentHeading: CLLocationDirection?
    @Published private(set) var headingAvailable = CLLocationManager.headingAvailable()
    @Published var selectedTarget: TargetLocation?
    @Published var followModeEnabled = false
    @Published var selectedTab: AppTab = .map
    @Published var pendingMapSearchRequest: MapSearchRequest?
    @Published var shouldFocusMapSearchField = false

    private let locationManager = CLLocationManager()

    override init() {
        super.init()
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.distanceFilter = 5
        locationManager.headingFilter = 3
        locationManager.activityType = .otherNavigation
        refreshAuthorizationState()
        refreshLocationServicesAvailability()
    }

    var isAuthorized: Bool {
        authorizationStatus == .authorizedWhenInUse || authorizationStatus == .authorizedAlways
    }

    var isPermissionBlocked: Bool {
        !isAuthorized && authorizationStatus != .notDetermined
    }

    var targetBearing: CLLocationDirection? {
        guard let location = currentLocation, let selectedTarget else { return nil }
        return LocationMath.bearing(from: location.coordinate, to: selectedTarget.coordinate)
    }

    var targetDistance: CLLocationDistance? {
        guard let location = currentLocation, let selectedTarget else { return nil }
        return location.distance(from: CLLocation(latitude: selectedTarget.coordinate.latitude, longitude: selectedTarget.coordinate.longitude))
    }

    var isLocationAccuracyLow: Bool {
        guard let currentLocation else { return false }
        return currentLocation.horizontalAccuracy < 0 || currentLocation.horizontalAccuracy > 100
    }

    var isTargetVeryClose: Bool {
        guard let targetDistance else { return false }
        return targetDistance < 5
    }

    func refreshAuthorizationState() {
        authorizationStatus = locationManager.authorizationStatus
        headingAvailable = CLLocationManager.headingAvailable()
        refreshLocationServicesAvailability()

        if isAuthorized {
            startUpdates()
        } else {
            stopUpdates()
        }
    }

    func requestWhenInUseAuthorization() {
        if authorizationStatus == .notDetermined {
            locationManager.requestWhenInUseAuthorization()
        } else if isAuthorized {
            startUpdates()
        }

        refreshLocationServicesAvailability()
    }

    func selectTarget(_ target: TargetLocation) {
        selectedTarget = target
    }

    func clearTarget() {
        selectedTarget = nil
    }

    func openTargetChooser() {
        pendingMapSearchRequest = MapSearchRequest(selectsExistingQuery: false)
        shouldFocusMapSearchField = true
        selectedTab = .map
    }

    func openTargetChooserForNewSearch() {
        pendingMapSearchRequest = MapSearchRequest(selectsExistingQuery: true)
        shouldFocusMapSearchField = true
        selectedTab = .map
    }

    func consumePendingMapSearchRequest() {
        pendingMapSearchRequest = nil
    }

    func consumeMapSearchFocusRequest() {
        shouldFocusMapSearchField = false
    }

    func openSettings() {
        guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
        UIApplication.shared.open(url)
    }

    private func startUpdates() {
        locationManager.startUpdatingLocation()

        if headingAvailable {
            locationManager.startUpdatingHeading()
        }
    }

    private func stopUpdates() {
        locationManager.stopUpdatingLocation()
        locationManager.stopUpdatingHeading()
    }

    private func updateHeading(with newHeading: CLLocationDirection) {
        guard newHeading >= 0 else { return }

        if let currentHeading {
            let delta = LocationMath.shortestAngleDelta(from: currentHeading, to: newHeading)
            self.currentHeading = LocationMath.normalizedDegrees(currentHeading + delta * 0.18)
        } else {
            currentHeading = newHeading
        }
    }

    private func refreshLocationServicesAvailability() {
        Task.detached(priority: .utility) { [weak self] in
            let isEnabled = CLLocationManager.locationServicesEnabled()
            await MainActor.run { [weak self] in
                self?.isLocationServicesEnabled = isEnabled
            }
        }
    }
}

extension AppState: CLLocationManagerDelegate {
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        refreshAuthorizationState()
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        currentLocation = location
    }

    func locationManager(_ manager: CLLocationManager, didUpdateHeading newHeading: CLHeading) {
        let heading = newHeading.trueHeading >= 0 ? newHeading.trueHeading : newHeading.magneticHeading
        updateHeading(with: heading)
    }

    func locationManagerShouldDisplayHeadingCalibration(_ manager: CLLocationManager) -> Bool {
        false
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        refreshLocationServicesAvailability()
    }
}
