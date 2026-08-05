import SwiftUI
import CoreLocation

struct CompassScreen: View {
    @EnvironmentObject private var appState: AppState

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                if let selectedTarget = appState.selectedTarget {
                    Text(selectedTarget.name)
                        .font(.title3.bold())
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)

                    CompassDial(
                        heading: appState.currentHeading,
                        targetBearing: appState.targetBearing
                    )
                    .frame(width: 280, height: 280)
                    .padding(.top, 8)

                    VStack(spacing: 12) {
                        HStack {
                            CompassMetric(title: "Target", value: formattedDegrees(appState.targetBearing))
                            CompassMetric(title: "Current Heading", value: formattedDegrees(appState.currentHeading))
                        }

                        CompassMetric(title: "Distance", value: formattedDistance(appState.targetDistance))
                    }
                    .padding(.horizontal)

                    statusMessage

                    Button("Choose Different Target") {
                        appState.openTargetChooserForNewSearch()
                    }
                    .buttonStyle(.borderedProminent)
                } else {
                    Spacer()
                    Image(systemName: "location.north.line.circle")
                        .font(.system(size: 60))
                        .foregroundStyle(.secondary)

                    Text("No Active Target")
                        .font(.title2.bold())

                    Text("Choose a destination on the map to see its bearing and distance here.")
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 24)

                    Button("Choose Target") {
                        appState.openTargetChooser()
                    }
                    .buttonStyle(.borderedProminent)
                    Spacer()
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Compass")
        }
    }

    @ViewBuilder
    private var statusMessage: some View {
        if !appState.headingAvailable {
            Text("Heading is unavailable on this device or in the current environment.")
                .font(.footnote)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 24)
        } else if appState.isTargetVeryClose {
            Text("You are effectively at the target.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        } else if appState.isLocationAccuracyLow {
            Text("Current GPS accuracy is low, so the bearing may drift.")
                .font(.footnote)
                .foregroundStyle(.orange)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 24)
        }
    }

    private func formattedDegrees(_ degrees: CLLocationDirection?) -> String {
        guard let degrees else { return "--" }
        return "\(Int(degrees.rounded()))°"
    }

    private func formattedDistance(_ distance: CLLocationDistance?) -> String {
        guard let distance else { return "--" }
        let formatter = MeasurementFormatter()
        formatter.unitOptions = .naturalScale
        formatter.unitStyle = .medium
        return formatter.string(from: Measurement(value: distance, unit: UnitLength.meters))
    }
}

private struct CompassDial: View {
    let heading: CLLocationDirection?
    let targetBearing: CLLocationDirection?

    var body: some View {
        ZStack {
            ZStack {
                Circle()
                    .fill(.background)
                    .overlay(
                        Circle()
                            .stroke(Color.secondary.opacity(0.2), lineWidth: 2)
                    )

                ForEach(0..<72, id: \.self) { index in
                    Rectangle()
                        .fill(index.isMultiple(of: 6) ? Color.primary : Color.secondary.opacity(0.5))
                        .frame(width: 2, height: index.isMultiple(of: 6) ? 16 : 8)
                        .offset(y: -126)
                        .rotationEffect(.degrees(Double(index) * 5))
                }

                GoalTrack()
                    .stroke(
                        Color.orange,
                        style: StrokeStyle(lineWidth: 6, lineCap: .round, lineJoin: .round)
                    )
                    .frame(width: 76, height: 120)
                    .offset(y: -72)
            }
            .rotationEffect(.degrees(dialRotation))
            .animation(.easeInOut(duration: 0.2), value: heading)
            .animation(.easeInOut(duration: 0.2), value: targetBearing)

            Image(systemName: "arrowtriangle.up.fill")
                .font(.system(size: 44))
                .foregroundStyle(.orange)
                .offset(y: -64)

            VStack(spacing: 10) {
                HStack(spacing: 10) {
                    turnDirectionArrow
                        .opacity(showsLeftTurnArrow ? 1 : 0)

                    Text(turnDegreesText)
                        .font(.title.monospacedDigit().bold())
                        .foregroundStyle(.primary)

                    turnDirectionArrow
                        .opacity(showsRightTurnArrow ? 1 : 0)
                }

                Text(turnInstruction)
                    .font(.title3.bold())
                    .foregroundStyle(.primary)
                    .multilineTextAlignment(.center)
            }
        }
        .padding(16)
        .background(
            Circle()
                .fill(
                    LinearGradient(
                        colors: [Color(.secondarySystemBackground), Color(.systemBackground)],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .shadow(color: .black.opacity(0.08), radius: 16, y: 8)
        )
    }

    private var turnDelta: CLLocationDirection? {
        guard let heading, let targetBearing else { return nil }
        return LocationMath.shortestAngleDelta(from: heading, to: targetBearing)
    }

    private var dialRotation: CLLocationDirection {
        guard let turnDelta else { return 0 }
        return turnDelta
    }

    private var turnInstruction: String {
        guard let turnDelta else { return "Finding direction" }

        let magnitude = abs(turnDelta)
        switch magnitude {
        case 0..<8:
            return "Straight ahead"
        case 8..<25:
            return turnDelta > 0 ? "Slightly right" : "Slightly left"
        case 25..<60:
            return turnDelta > 0 ? "Turn right" : "Turn left"
        case 60..<135:
            return turnDelta > 0 ? "Turn more right" : "Turn more left"
        default:
            return turnDelta > 0 ? "Turn around right" : "Turn around left"
        }
    }

    private var turnDirectionSymbol: String {
        guard let turnDelta else { return "location.slash" }

        let magnitude = abs(turnDelta)
        if magnitude < 8 {
            return "arrow.up"
        }

        if magnitude < 25 {
            return turnDelta > 0 ? "arrow.up.right" : "arrow.up.left"
        }

        return turnDelta > 0 ? "arrow.right" : "arrow.left"
    }

    private var showsLeftTurnArrow: Bool {
        guard let turnDelta else { return false }
        return turnDelta < -8
    }

    private var showsRightTurnArrow: Bool {
        guard let turnDelta else { return false }
        return turnDelta > 8
    }

    @ViewBuilder
    private var turnDirectionArrow: some View {
        Image(systemName: turnDirectionSymbol)
            .font(.title2.weight(.bold))
            .foregroundStyle(.primary)
            .frame(width: 24)
    }

    private var turnDegreesText: String {
        guard let turnDelta else { return "--°" }
        return "\(Int(abs(turnDelta).rounded()))°"
    }
}

private struct GoalTrack: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        let centerX = rect.midX
        path.move(to: CGPoint(x: centerX, y: rect.minY))
        path.addLine(to: CGPoint(x: centerX, y: rect.maxY - 18))
        return path
    }
}

private struct CompassMetric: View {
    let title: String
    let value: String

    var body: some View {
        VStack(spacing: 6) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(value)
                .font(.title3.monospacedDigit().bold())
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

#Preview {
    CompassScreen()
        .environmentObject(AppState())
}
