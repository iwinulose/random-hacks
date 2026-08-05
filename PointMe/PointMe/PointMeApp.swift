//
//  PointMeApp.swift
//  PointMe
//
//  Created by Charles Duyk on 4/1/26.
//

import SwiftUI

@main
struct PointMeApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}
