//
//  PointMeTests.swift
//  PointMeTests
//
//  Created by Charles Duyk on 4/1/26.
//

import Testing
import CoreLocation
@testable import PointMe

struct PointMeTests {
    @MainActor @Test func bearingCalculationMatchesExpectedDirection() async throws {
        let start = CLLocationCoordinate2D(latitude: 28.572872, longitude: -80.64898)
        let destination = CLLocationCoordinate2D(latitude: 40.689247, longitude: -74.044502)

        let bearing = LocationMath.bearing(from: start, to: destination)
        #expect(bearing > 30)
        #expect(bearing < 40)
    }

    @MainActor @Test func coordinateParsingRejectsInvalidInput() async throws {
        #expect(DestinationSearchService.parseCoordinate("not,a,coordinate") == nil)
        #expect(DestinationSearchService.parseCoordinate("91, 10") == nil)
    }

    @MainActor @Test func coordinateParsingAcceptsLatitudeLongitude() async throws {
        let target = DestinationSearchService.parseCoordinate("28.5729, -80.6490")
        #expect(target != nil)
        #expect(target?.coordinate.latitude == 28.5729)
        #expect(target?.coordinate.longitude == -80.6490)
    }
}
