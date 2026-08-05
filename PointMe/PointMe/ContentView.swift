import SwiftUI
import CoreLocation

struct ContentView: View {
    @EnvironmentObject private var appState: AppState
    @AppStorage("hasShownPermissionPrimer") private var hasShownPermissionPrimer = false
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        Group {
            if shouldShowPermissionPrimer {
                PermissionPrimerView {
                    hasShownPermissionPrimer = true
                    appState.requestWhenInUseAuthorization()
                }
            } else if appState.isPermissionBlocked {
                LocationBlockedView(
                    isLocationServicesEnabled: appState.isLocationServicesEnabled,
                    openSettings: appState.openSettings
                )
            } else {
                MainTabView()
            }
        }
        .onAppear {
            appState.refreshAuthorizationState()
        }
        .onChange(of: scenePhase) { _, newPhase in
            if newPhase == .active {
                appState.refreshAuthorizationState()
            }
        }
    }

    private var shouldShowPermissionPrimer: Bool {
        !hasShownPermissionPrimer && appState.authorizationStatus == .notDetermined
    }
}

private struct MainTabView: View {
    @EnvironmentObject private var appState: AppState

    var body: some View {
        TabView(selection: $appState.selectedTab) {
            MapScreen()
                .tabItem {
                    Label("Map", systemImage: "map")
                }
                .tag(AppTab.map)

            CompassScreen()
                .tabItem {
                    Label("Compass", systemImage: "location.north.line")
                }
                .tag(AppTab.compass)
        }
    }
}

private struct PermissionPrimerView: View {
    let continueAction: () -> Void

    var body: some View {
        VStack(spacing: 20) {
            Spacer()

            Image(systemName: "location.viewfinder")
                .font(.system(size: 64))
                .foregroundStyle(.tint)

            Text("Point Me")
                .font(.largeTitle.bold())

            Text("Point Me requires location access to guide you toward a destination.")
                .font(.body)
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 24)

            Button("Continue", action: continueAction)
                .buttonStyle(.borderedProminent)
                .controlSize(.large)

            Spacer()
        }
        .padding()
    }
}

private struct LocationBlockedView: View {
    let isLocationServicesEnabled: Bool
    let openSettings: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Spacer()

            Image(systemName: "location.slash.circle")
                .font(.system(size: 60))
                .foregroundStyle(.orange)

            Text("Location Access Required")
                .font(.title2.bold())

            Text(message)
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 24)

            Button("Open Settings", action: openSettings)
                .buttonStyle(.borderedProminent)

            Spacer()
        }
        .padding()
    }

    private var message: String {
        if isLocationServicesEnabled {
            return "Location access is required to use the app. Enable While Using the App access in Settings."
        }

        return "Location access is required to use the app. Turn on Location Services for this device, then return here."
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
}
