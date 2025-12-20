//
//  DataManager.swift
//  MBRewrite
//
//  Created by Charles Duyk on 12/19/25.
//

import Foundation
import SwiftUI
import Combine
import Security

class DataManager: ObservableObject {
    @Published var selectedPersonas: [Persona] = []
    @Published var customPersonas: [Persona] = []
    @Published var messageHistory: [MessageHistory] = []
    @Published var apiKey: String = ""
    
    private let selectedPersonasKey = "selectedPersonas"
    private let customPersonasKey = "customPersonas"
    private let messageHistoryKey = "messageHistory"
    private let apiKeyKey = "apiKey"
    
    init() {
        loadData()
    }
    
    func saveData() {
        // Save selected personas
        if let encoded = try? JSONEncoder().encode(selectedPersonas) {
            UserDefaults.standard.set(encoded, forKey: selectedPersonasKey)
        }
        
        // Save custom personas
        if let encoded = try? JSONEncoder().encode(customPersonas) {
            UserDefaults.standard.set(encoded, forKey: customPersonasKey)
        }
        
        // Save message history (limit to last 100)
        let limitedHistory = Array(messageHistory.prefix(100))
        if let encoded = try? JSONEncoder().encode(limitedHistory) {
            UserDefaults.standard.set(encoded, forKey: messageHistoryKey)
        }
        
        // Save API key to Keychain for security
        saveAPIKey(apiKey)
    }
    
    func loadData() {
        // Load selected personas
        if let data = UserDefaults.standard.data(forKey: selectedPersonasKey),
           let decoded = try? JSONDecoder().decode([Persona].self, from: data) {
            selectedPersonas = decoded
        }
        
        // Load custom personas
        if let data = UserDefaults.standard.data(forKey: customPersonasKey),
           let decoded = try? JSONDecoder().decode([Persona].self, from: data) {
            customPersonas = decoded
        }
        
        // Load message history
        if let data = UserDefaults.standard.data(forKey: messageHistoryKey),
           let decoded = try? JSONDecoder().decode([MessageHistory].self, from: data) {
            messageHistory = decoded
        }
        
        // Load API key from Keychain
        apiKey = loadAPIKey()
    }
    
    func addCustomPersona(_ persona: Persona) {
        customPersonas.append(persona)
        saveData()
    }
    
    func removeCustomPersona(_ persona: Persona) {
        customPersonas.removeAll { $0.id == persona.id }
        saveData()
    }
    
    func togglePersona(_ persona: Persona) {
        if selectedPersonas.contains(where: { $0.id == persona.id }) {
            selectedPersonas.removeAll { $0.id == persona.id }
        } else {
            selectedPersonas.append(persona)
        }
        saveData()
    }
    
    func isPersonaSelected(_ persona: Persona) -> Bool {
        selectedPersonas.contains(where: { $0.id == persona.id })
    }
    
    func addToHistory(_ history: MessageHistory) {
        messageHistory.insert(history, at: 0)
        saveData()
    }
    
    func clearHistory() {
        messageHistory.removeAll()
        saveData()
    }
    
    // Keychain operations for secure API key storage
    private func saveAPIKey(_ key: String) {
        let data = key.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: apiKeyKey,
            kSecValueData as String: data
        ]
        
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }
    
    private func loadAPIKey() -> String {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: apiKeyKey,
            kSecReturnData as String: true
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        if status == errSecSuccess,
           let data = result as? Data,
           let key = String(data: data, encoding: .utf8) {
            return key
        }
        
        return ""
    }
}

