//
//  MessageInputView.swift
//  MBRewrite
//
//  Created by Charles Duyk on 12/19/25.
//

import SwiftUI

struct MessageInputView: View {
    @ObservedObject var dataManager: DataManager
    @State private var messageText = ""
    @State private var isProcessing = false
    @State private var results: [PersonaResult] = []
    @State private var showingError = false
    @State private var errorMessage = ""
    
    var body: some View {
        VStack(spacing: 0) {
            // Input area
            VStack(alignment: .leading, spacing: 12) {
                Text("Enter your message:")
                    .font(.headline)
                
                TextEditor(text: $messageText)
                    .frame(minHeight: 100)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                    )
                
                Button(action: {
                    Task {
                        await rewriteMessage()
                    }
                }) {
                    HStack {
                        if isProcessing {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Image(systemName: "arrow.right.circle.fill")
                        }
                        Text(isProcessing ? "Processing..." : "Rewrite")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        dataManager.selectedPersonas.isEmpty || messageText.isEmpty || isProcessing
                        ? Color.gray
                        : Color.blue
                    )
                    .foregroundColor(.white)
                    .cornerRadius(10)
                }
                .disabled(dataManager.selectedPersonas.isEmpty || messageText.isEmpty || isProcessing)
                
                if dataManager.selectedPersonas.isEmpty {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.orange)
                        Text("Please select at least one persona in Settings")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding()
            .background(Color(.systemBackground))
            
            Divider()
            
            // Results area
            if !results.isEmpty {
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Results:")
                            .font(.headline)
                            .padding(.horizontal)
                            .padding(.top)
                        
                        ForEach(results) { result in
                            VStack(alignment: .leading, spacing: 8) {
                                Text("[\(result.personaLabel)]")
                                    .font(.headline)
                                    .foregroundColor(.blue)
                                
                                Text(result.rewrittenMessage)
                                    .padding()
                                    .background(Color(.systemGray6))
                                    .cornerRadius(8)
                            }
                            .padding(.horizontal)
                        }
                    }
                    .padding(.bottom)
                }
            } else if isProcessing {
                VStack(spacing: 16) {
                    ProgressView()
                    Text("Rewriting messages...")
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .alert("Error", isPresented: $showingError) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(errorMessage)
        }
    }
    
    private func rewriteMessage() async {
        guard !dataManager.apiKey.isEmpty else {
            errorMessage = "Please set your OpenAI API key in Settings"
            showingError = true
            return
        }
        
        guard !dataManager.selectedPersonas.isEmpty else {
            errorMessage = "Please select at least one persona in Settings"
            showingError = true
            return
        }
        
        isProcessing = true
        results = []
        
        do {
            let service = OpenAIService(apiKey: dataManager.apiKey)
            let personaResults = try await service.rewriteMessage(
                messageText,
                for: dataManager.selectedPersonas
            )
            
            results = personaResults
            
            // Save to history
            let history = MessageHistory(
                originalMessage: messageText,
                results: personaResults
            )
            dataManager.addToHistory(history)
            
        } catch {
            errorMessage = "Failed to rewrite message: \(error.localizedDescription)"
            showingError = true
        }
        
        isProcessing = false
    }
}

