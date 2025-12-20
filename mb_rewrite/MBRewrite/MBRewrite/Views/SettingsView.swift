//
//  SettingsView.swift
//  MBRewrite
//
//  Created by Charles Duyk on 12/19/25.
//

import SwiftUI

struct SettingsView: View {
    @ObservedObject var dataManager: DataManager
    @State private var apiKey: String = ""
    @State private var showingPersonaManagement = false
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("OpenAI API Key")) {
                    SecureField("Enter your OpenAI API key", text: $apiKey)
                        .onAppear {
                            apiKey = dataManager.apiKey
                        }
                    
                    Button("Save API Key") {
                        dataManager.apiKey = apiKey
                        dataManager.saveData()
                    }
                    .disabled(apiKey.isEmpty)
                    
                    if !dataManager.apiKey.isEmpty {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                            Text("API key is set")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                
                Section(header: Text("Selected Personas")) {
                    if dataManager.selectedPersonas.isEmpty {
                        Text("No personas selected")
                            .foregroundColor(.secondary)
                    } else {
                        ForEach(dataManager.selectedPersonas) { persona in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(persona.label)
                                    .font(.headline)
                                Text(persona.description)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                    .lineLimit(2)
                            }
                        }
                        .onDelete { indexSet in
                            for index in indexSet {
                                dataManager.togglePersona(dataManager.selectedPersonas[index])
                            }
                        }
                    }
                }
                
                Section(header: Text("Custom Personas")) {
                    if dataManager.customPersonas.isEmpty {
                        Text("No custom personas")
                            .foregroundColor(.secondary)
                    } else {
                        ForEach(dataManager.customPersonas) { persona in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(persona.label)
                                    .font(.headline)
                                Text(persona.description)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                    .lineLimit(2)
                            }
                        }
                        .onDelete { indexSet in
                            for index in indexSet {
                                dataManager.removeCustomPersona(dataManager.customPersonas[index])
                            }
                        }
                    }
                }
                
                Section {
                    Button("Manage Personas") {
                        showingPersonaManagement = true
                    }
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .sheet(isPresented: $showingPersonaManagement) {
                PersonaManagementView(dataManager: dataManager)
            }
        }
    }
}

