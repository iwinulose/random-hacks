import Foundation
import MapKit
import CoreLocation
import Combine

@MainActor
final class DestinationSearchService: NSObject, ObservableObject {
    @Published var query = ""
    @Published private(set) var completions: [MKLocalSearchCompletion] = []
    @Published private(set) var searchErrorMessage: String?

    private let completer = MKLocalSearchCompleter()

    override init() {
        super.init()
        completer.delegate = self
        completer.resultTypes = [.address, .pointOfInterest, .query]
    }

    var coordinateCandidate: TargetLocation? {
        Self.parseCoordinate(query)
    }

    func updateRegion(using location: CLLocation?) {
        guard let location else { return }
        completer.region = LocationMath.coordinateRegion(center: location.coordinate, distance: 100_000)
    }

    func updateQuery(_ query: String) {
        self.query = query
        searchErrorMessage = nil

        if query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || coordinateCandidate != nil {
            completions = []
            completer.queryFragment = ""
            return
        }

        completer.queryFragment = query
    }

    func chooseCompletion(_ completion: MKLocalSearchCompletion) async -> TargetLocation? {
        let request = MKLocalSearch.Request(completion: completion)
        request.resultTypes = .pointOfInterest.union(.address)

        return await performSearch(request: request)
    }

    func searchFirstResult() async -> TargetLocation? {
        if let coordinateCandidate {
            return coordinateCandidate
        }

        let trimmedQuery = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedQuery.isEmpty else {
            searchErrorMessage = "Enter a place or coordinates."
            return nil
        }

        let request = MKLocalSearch.Request()
        request.naturalLanguageQuery = trimmedQuery
        request.resultTypes = .pointOfInterest.union(.address)
        return await performSearch(request: request)
    }

    private func performSearch(request: MKLocalSearch.Request) async -> TargetLocation? {
        do {
            let response = try await MKLocalSearch(request: request).start()
            guard let item = response.mapItems.first else {
                searchErrorMessage = "No results found."
                return nil
            }

            let target = TargetLocation(mapItem: item)
            commitSelection(named: target.name)
            return target
        } catch {
            searchErrorMessage = "Search failed. Try a different query."
            return nil
        }
    }

    func commitSelection(named query: String) {
        self.query = query
        searchErrorMessage = nil
        completions = []
        completer.queryFragment = ""
    }

    static func parseCoordinate(_ rawText: String) -> TargetLocation? {
        let components = rawText
            .split(separator: ",", omittingEmptySubsequences: true)
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }

        guard components.count == 2,
              let latitude = Double(components[0]),
              let longitude = Double(components[1]),
              (-90...90).contains(latitude),
              (-180...180).contains(longitude) else {
            return nil
        }

        let coordinate = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
        return TargetLocation(
            name: String(format: "Lat %.4f, Lon %.4f", latitude, longitude),
            subtitle: "Manual coordinates",
            coordinate: coordinate
        )
    }
}

extension DestinationSearchService: MKLocalSearchCompleterDelegate {
    func completerDidUpdateResults(_ completer: MKLocalSearchCompleter) {
        guard completer.queryFragment == query else { return }
        completions = completer.results
    }

    func completer(_ completer: MKLocalSearchCompleter, didFailWithError error: Error) {
        completions = []
        searchErrorMessage = "Search suggestions are unavailable right now."
    }
}
