//
//  HistoryView.swift
//  MBRewrite
//
//  Created by Charles Duyk on 12/19/25.
//

import SwiftUI

struct HistoryView: View {
    @ObservedObject var dataManager: DataManager
    
    var body: some View {
        Group {
            if dataManager.messageHistory.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "clock.arrow.circlepath")
                        .font(.system(size: 50))
                        .foregroundColor(.gray)
                    Text("No history yet")
                        .font(.headline)
                        .foregroundColor(.secondary)
                    Text("Your rewritten messages will appear here")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                List {
                    ForEach(dataManager.messageHistory) { history in
                        Section {
                            VStack(alignment: .leading, spacing: 12) {
                                // Original message
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Original:")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Text(history.originalMessage)
                                        .font(.body)
                                }
                                .padding(.bottom, 8)
                                
                                Divider()
                                
                                // Results
                                ForEach(history.results) { result in
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text("[\(result.personaLabel)]")
                                            .font(.headline)
                                            .foregroundColor(.blue)
                                        Text(result.rewrittenMessage)
                                            .font(.body)
                                            .padding(.leading, 8)
                                    }
                                    .padding(.vertical, 4)
                                }
                                
                                // Timestamp
                                Text(history.timestamp, style: .relative)
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                                    .padding(.top, 4)
                            }
                            .padding(.vertical, 8)
                        }
                    }
                }
            }
        }
        .navigationTitle("History")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                if !dataManager.messageHistory.isEmpty {
                    Button("Clear") {
                        dataManager.clearHistory()
                    }
                    .foregroundColor(.red)
                }
            }
        }
    }
}

