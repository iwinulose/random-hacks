//
//  MainView.swift
//  MBRewrite
//
//  Created by Charles Duyk on 12/19/25.
//

import SwiftUI

struct MainView: View {
    @StateObject private var dataManager = DataManager()
    @State private var showingSettings = false
    
    var body: some View {
        TabView {
            NavigationView {
                MessageInputView(dataManager: dataManager)
                    .navigationTitle("MB Rewrite")
                    .toolbar {
                        ToolbarItem(placement: .navigationBarTrailing) {
                            Button(action: {
                                showingSettings = true
                            }) {
                                Image(systemName: "gearshape.fill")
                            }
                        }
                    }
            }
            .tabItem {
                Label("Rewrite", systemImage: "pencil.and.outline")
            }
            
            NavigationView {
                HistoryView(dataManager: dataManager)
            }
            .tabItem {
                Label("History", systemImage: "clock")
            }
        }
        .sheet(isPresented: $showingSettings) {
            SettingsView(dataManager: dataManager)
        }
    }
}

