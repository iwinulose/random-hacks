//
//  MessageHistory.swift
//  MBRewrite
//
//  Created by Charles Duyk on 12/19/25.
//

import Foundation

struct MessageHistory: Identifiable, Codable {
    let id: UUID
    let originalMessage: String
    let timestamp: Date
    let results: [PersonaResult]
    
    init(id: UUID = UUID(), originalMessage: String, timestamp: Date = Date(), results: [PersonaResult]) {
        self.id = id
        self.originalMessage = originalMessage
        self.timestamp = timestamp
        self.results = results
    }
}

struct PersonaResult: Identifiable, Codable {
    let id: UUID
    let personaLabel: String
    let rewrittenMessage: String
    
    init(id: UUID = UUID(), personaLabel: String, rewrittenMessage: String) {
        self.id = id
        self.personaLabel = personaLabel
        self.rewrittenMessage = rewrittenMessage
    }
}

