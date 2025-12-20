//
//  PersonaManagementView.swift
//  MBRewrite
//
//  Created by Charles Duyk on 12/19/25.
//

import SwiftUI

struct PersonaManagementView: View {
    @ObservedObject var dataManager: DataManager
    @State private var showingAddCustom = false
    @State private var newCustomLabel = ""
    @State private var newCustomDescription = ""
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            List {
                Section(header: Text("Myers-Briggs Types")) {
                    ForEach(Persona.mbtiTypes) { persona in
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(persona.label)
                                    .font(.headline)
                                Text(persona.description)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                    .lineLimit(2)
                            }
                            
                            Spacer()
                            
                            if dataManager.isPersonaSelected(persona) {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.blue)
                            }
                        }
                        .contentShape(Rectangle())
                        .onTapGesture {
                            dataManager.togglePersona(persona)
                        }
                    }
                }
                
                Section(header: Text("Custom Personas")) {
                    ForEach(dataManager.customPersonas) { persona in
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(persona.label)
                                    .font(.headline)
                                Text(persona.description)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                    .lineLimit(2)
                            }
                            
                            Spacer()
                            
                            if dataManager.isPersonaSelected(persona) {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.blue)
                            }
                        }
                        .contentShape(Rectangle())
                        .onTapGesture {
                            dataManager.togglePersona(persona)
                        }
                    }
                    .onDelete { indexSet in
                        for index in indexSet {
                            dataManager.removeCustomPersona(dataManager.customPersonas[index])
                        }
                    }
                    
                    Button(action: {
                        showingAddCustom = true
                    }) {
                        HStack {
                            Image(systemName: "plus.circle.fill")
                            Text("Add Custom Persona")
                        }
                        .foregroundColor(.blue)
                    }
                }
            }
            .navigationTitle("Manage Personas")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .sheet(isPresented: $showingAddCustom) {
                AddCustomPersonaView(dataManager: dataManager)
            }
        }
    }
}

struct AddCustomPersonaView: View {
    @ObservedObject var dataManager: DataManager
    @State private var label = ""
    @State private var description = ""
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Persona Details")) {
                    TextField("Label (e.g., 'Cat Lover')", text: $label)
                    TextField("Description", text: $description, axis: .vertical)
                        .lineLimit(3...6)
                }
            }
            .navigationTitle("Add Custom Persona")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        let persona = Persona(
                            label: label,
                            description: description,
                            isMBTI: false
                        )
                        dataManager.addCustomPersona(persona)
                        dismiss()
                    }
                    .disabled(label.isEmpty || description.isEmpty)
                }
            }
        }
    }
}

