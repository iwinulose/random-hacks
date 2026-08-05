import SwiftUI
import MapKit
import CoreLocation

struct MapScreen: View {
    @EnvironmentObject private var appState: AppState
    @StateObject private var searchService = DestinationSearchService()
    @FocusState private var isSearchFieldFocused: Bool
    @State private var searchText = ""
    @State private var searchSelection: TextSelection?
    @State private var isRouteVisible = false
    @State private var cameraPosition: MapCameraPosition = .automatic
    @State private var displayedRouteCoordinates: [CLLocationCoordinate2D] = []
    @State private var pointMeTask: Task<Void, Never>?

    var body: some View {
        ZStack(alignment: .top) {
            mapView
            searchOverlay
            bottomOverlay
        }
        .toolbar {
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()
                Button("Done") {
                    dismissSearchFocus()
                }
            }
        }
        .onAppear {
            searchText = searchService.query
            searchService.updateRegion(using: appState.currentLocation)
            if appState.currentLocation != nil {
                recenterOnUser(animated: false, followsHeading: appState.followModeEnabled)
            }
            handlePendingMapSearchRequest()
        }
        .onChange(of: appState.currentLocation?.coordinate.latitude) { _, _ in
            handleLocationChange()
        }
        .onChange(of: appState.currentLocation?.coordinate.longitude) { _, _ in
            handleLocationChange()
        }
        .onChange(of: appState.currentHeading) { _, _ in
            if appState.followModeEnabled {
                recenterOnUser(animated: true, followsHeading: true)
            }
        }
        .onChange(of: appState.selectedTarget) { _, newValue in
            if let newValue {
                pointMeTask?.cancel()
                isRouteVisible = false
                displayedRouteCoordinates = []
                focus(on: newValue.coordinate)
            } else {
                pointMeTask?.cancel()
                isRouteVisible = false
                displayedRouteCoordinates = []
            }
        }
        .onChange(of: appState.pendingMapSearchRequest) { _, _ in
            handlePendingMapSearchRequest()
        }
        .onChange(of: appState.shouldFocusMapSearchField) { _, shouldFocus in
            if shouldFocus {
                handlePendingMapSearchRequest()
            }
        }
        .onChange(of: appState.selectedTab) { _, newValue in
            if newValue == .map {
                handlePendingMapSearchRequest()
            }
        }
        .onDisappear {
            pointMeTask?.cancel()
        }
    }

    private var mapView: some View {
        Map(position: $cameraPosition, interactionModes: .all) {
            if let currentLocation = appState.currentLocation {
                Annotation("You", coordinate: currentLocation.coordinate, anchor: .center) {
                    UserHeadingMarker(heading: appState.currentHeading)
                }
            }

            if let selectedTarget = appState.selectedTarget {
                Annotation(selectedTarget.name, coordinate: selectedTarget.coordinate, anchor: .bottom) {
                    TargetMarkerAnnotation(
                        title: selectedTarget.name,
                        isPointMeEnabled: appState.currentLocation != nil,
                        pointMeAction: runPointMeFlow
                    )
                }
            }

            if displayedRouteCoordinates.count >= 2 {
                MapPolyline(coordinates: displayedRouteCoordinates)
                    .stroke(.tint, style: StrokeStyle(lineWidth: 5, lineCap: .round, lineJoin: .round))
            }
        }
        .mapStyle(.standard(elevation: .realistic))
        .mapControls {
            MapScaleView()
            MapCompass()
        }
        .ignoresSafeArea(edges: .top)
        .simultaneousGesture(
            TapGesture().onEnded {
                dismissSearchFocus()
            }
        )
    }

    private var searchOverlay: some View {
        VStack(spacing: 10) {
            HStack(spacing: 12) {
                Image(systemName: "magnifyingglass")
                    .foregroundStyle(.secondary)

                TextField("Search place or lat, lon", text: $searchText, selection: $searchSelection)
                    .textInputAutocapitalization(.words)
                    .autocorrectionDisabled()
                    .submitLabel(.search)
                    .focused($isSearchFieldFocused)
                    .onSubmit {
                        runPrimarySearch()
                    }
                    .onChange(of: searchText) { _, newValue in
                        searchService.updateQuery(newValue)
                    }

                if !searchText.isEmpty {
                    Button {
                        searchText = ""
                        searchService.updateQuery("")
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 12)
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 18, style: .continuous))

            if shouldShowSearchResults, let coordinateCandidate = searchService.coordinateCandidate {
                SearchResultRow(
                    title: coordinateCandidate.name,
                    subtitle: coordinateCandidate.subtitle ?? "Coordinates"
                ) {
                    selectTarget(coordinateCandidate)
                }
            }

            ForEach(visibleCompletions, id: \.self) { completion in
                SearchResultRow(
                    title: completion.title,
                    subtitle: completion.subtitle
                ) {
                    dismissSearchFocus()
                    Task {
                        if let target = await searchService.chooseCompletion(completion) {
                            selectTarget(target)
                        }
                    }
                }
            }

            if let searchErrorMessage = searchService.searchErrorMessage {
                Text(searchErrorMessage)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(.ultraThinMaterial, in: Capsule())
            }
        }
        .padding(.horizontal)
        .padding(.top, 8)
    }

    private var shouldShowSearchResults: Bool {
        isSearchFieldFocused
    }

    private var visibleCompletions: [MKLocalSearchCompletion] {
        guard shouldShowSearchResults else { return [] }
        return Array(searchService.completions.prefix(5))
    }

    private var bottomOverlay: some View {
        VStack {
            Spacer()

            VStack(alignment: .leading, spacing: 12) {
                if let selectedTarget = appState.selectedTarget {
                    Text(selectedTarget.name)
                        .font(.headline)

                    if let subtitle = selectedTarget.subtitle, !subtitle.isEmpty {
                        Text(subtitle)
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }

                    HStack {
                        StatBadge(title: "Bearing", value: formattedDegrees(appState.targetBearing))
                        StatBadge(title: "Distance", value: formattedDistance(appState.targetDistance))
                    }
                } else {
                    Text("Choose a destination on the map to begin.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                if appState.isLocationAccuracyLow {
                    Text("Location accuracy is currently low.")
                        .font(.footnote)
                        .foregroundStyle(.orange)
                }

                if appState.isTargetVeryClose {
                    Text("You are already at or very near this destination.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                HStack(spacing: 10) {
                    Button("Recenter") {
                        recenterOnUser(animated: true, followsHeading: appState.followModeEnabled)
                    }
                    .buttonStyle(.bordered)
                    .disabled(appState.currentLocation == nil)

                    Button(appState.followModeEnabled ? "Following" : "Follow Me") {
                        appState.followModeEnabled.toggle()
                        recenterOnUser(animated: true, followsHeading: appState.followModeEnabled)
                    }
                    .buttonStyle(.bordered)
                    .disabled(appState.currentLocation == nil)
                }

                if appState.selectedTarget != nil {
                    Button("Clear Target", role: .destructive) {
                        pointMeTask?.cancel()
                        isRouteVisible = false
                        displayedRouteCoordinates = []
                        appState.clearTarget()
                    }
                    .buttonStyle(.borderless)
                }
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
            .padding()
        }
    }

    private func runPrimarySearch() {
        searchService.updateQuery(searchText)
        dismissSearchFocus()
        Task {
            if let target = await searchService.searchFirstResult() {
                selectTarget(target)
            }
        }
    }

    private func selectTarget(_ target: TargetLocation) {
        searchText = target.name
        searchSelection = nil
        searchService.commitSelection(named: target.name)
        dismissSearchFocus()
        pointMeTask?.cancel()
        isRouteVisible = false
        displayedRouteCoordinates = []
        appState.selectTarget(target)
        focus(on: target.coordinate)
    }

    private func dismissSearchFocus() {
        isSearchFieldFocused = false
        searchSelection = nil
        appState.consumeMapSearchFocusRequest()
    }

    private func handlePendingMapSearchRequest() {
        guard appState.selectedTab == .map,
              appState.shouldFocusMapSearchField,
              let request = appState.pendingMapSearchRequest else { return }

        Task { @MainActor in
            await Task.yield()
            isSearchFieldFocused = true
            if request.selectsExistingQuery, !searchText.isEmpty {
                searchSelection = TextSelection(range: searchText.startIndex..<searchText.endIndex)
            }
            appState.consumePendingMapSearchRequest()
        }
    }

    private func handleLocationChange() {
        searchService.updateRegion(using: appState.currentLocation)
        if isRouteVisible {
            updateRouteIfPossible()
        }

        if appState.followModeEnabled {
            recenterOnUser(animated: true, followsHeading: true)
        }
    }

    private func updateRouteIfPossible() {
        guard let userCoordinate = appState.currentLocation?.coordinate,
              let targetCoordinate = appState.selectedTarget?.coordinate else {
            displayedRouteCoordinates = []
            return
        }

        displayedRouteCoordinates = LocationMath.geodesicCoordinates(from: userCoordinate, to: targetCoordinate)
    }

    private func runPointMeFlow() {
        guard let userCoordinate = appState.currentLocation?.coordinate,
              let targetCoordinate = appState.selectedTarget?.coordinate else { return }

        pointMeTask?.cancel()
        isRouteVisible = true
        displayedRouteCoordinates = []

        let fitRect = LocationMath.mapRectIncluding([userCoordinate, targetCoordinate], paddingMeters: 1_200)
        let distance = appState.targetDistance ?? 1_000
        let userCamera = MapCamera(
            centerCoordinate: userCoordinate,
            distance: min(max(distance * 1.2, 500), 150_000),
            heading: appState.followModeEnabled ? (appState.currentHeading ?? 0) : 0,
            pitch: 45
        )

        pointMeTask = Task { @MainActor in
            withAnimation(.easeInOut(duration: 0.8)) {
                cameraPosition = .rect(fitRect)
            }

            try? await Task.sleep(for: .milliseconds(800))

            for step in 1...30 {
                if Task.isCancelled {
                    return
                }
                let progress = Double(step) / 30
                displayedRouteCoordinates = LocationMath.geodesicCoordinates(
                    from: userCoordinate,
                    to: targetCoordinate,
                    progress: progress
                )
                try? await Task.sleep(for: .milliseconds(24))
            }

            try? await Task.sleep(for: .milliseconds(250))

            withAnimation(.easeInOut(duration: 1.0)) {
                cameraPosition = .camera(userCamera)
            }
        }
    }

    private func recenterOnUser(animated: Bool, followsHeading: Bool) {
        guard let currentLocation = appState.currentLocation else { return }

        let camera = MapCamera(
            centerCoordinate: currentLocation.coordinate,
            distance: 1_000,
            heading: followsHeading ? (appState.currentHeading ?? 0) : 0,
            pitch: followsHeading ? 50 : 0
        )

        if animated {
            withAnimation(.easeInOut(duration: 0.45)) {
                cameraPosition = .camera(camera)
            }
        } else {
            cameraPosition = .camera(camera)
        }
    }

    private func focus(on coordinate: CLLocationCoordinate2D) {
        let region = LocationMath.coordinateRegion(center: coordinate, distance: 1_500)
        withAnimation(.easeInOut(duration: 0.45)) {
            cameraPosition = .region(region)
        }
    }

    private func formattedDistance(_ distance: CLLocationDistance?) -> String {
        guard let distance else { return "--" }
        let formatter = MeasurementFormatter()
        formatter.unitOptions = .naturalScale
        formatter.unitStyle = .short
        return formatter.string(from: Measurement(value: distance, unit: UnitLength.meters))
    }

    private func formattedDegrees(_ degrees: CLLocationDirection?) -> String {
        guard let degrees else { return "--" }
        return "\(Int(degrees.rounded()))°"
    }
}

private struct SearchResultRow: View {
    let title: String
    let subtitle: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 3) {
                Text(title)
                    .font(.headline)
                    .foregroundStyle(.primary)
                Text(subtitle)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(12)
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .buttonStyle(.plain)
    }
}

private struct TargetMarkerAnnotation: View {
    let title: String
    let isPointMeEnabled: Bool
    let pointMeAction: () -> Void

    var body: some View {
        VStack(spacing: 8) {
            Button("Point Me", action: pointMeAction)
                .buttonStyle(.borderedProminent)
                .controlSize(.small)
                .disabled(!isPointMeEnabled)

            VStack(spacing: 4) {
                Text(title)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.primary)
                    .lineLimit(1)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(.thinMaterial, in: Capsule())

                Image(systemName: "mappin.circle.fill")
                    .font(.system(size: 34))
                    .foregroundStyle(.red)
                    .background(
                        Circle()
                            .fill(.white)
                            .frame(width: 20, height: 20)
                    )
            }
        }
    }
}

private struct StatBadge: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(value)
                .font(.subheadline.bold())
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color.secondary.opacity(0.12), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}

private struct UserHeadingMarker: View {
    let heading: CLLocationDirection?

    var body: some View {
        ZStack {
            Circle()
                .fill(.blue)
                .frame(width: 22, height: 22)
                .overlay(
                    Circle()
                        .stroke(.white, lineWidth: 3)
                )

            if let heading {
                Image(systemName: "location.north.fill")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundStyle(.white, .blue)
                    .offset(y: -22)
                    .rotationEffect(.degrees(heading))
            }
        }
    }
}

#Preview {
    MapScreen()
        .environmentObject(AppState())
}
