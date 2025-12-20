//
//  OpenAIService.swift
//  MBRewrite
//
//  Created by Charles Duyk on 12/19/25.
//

import Foundation

class OpenAIService {
    private let apiKey: String
    
    init(apiKey: String) {
        self.apiKey = apiKey
    }
    
    func rewriteMessage(_ message: String, for persona: Persona) async throws -> String {
        let url = URL(string: "https://api.openai.com/v1/chat/completions")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let prompt = """
        Rewrite the following message so that it will be well received by a person who is best described as \(persona.description).
        
        The rewritten message should reflect how this persona would naturally communicate, maintaining the core meaning but adapting the tone, style, and approach to match their personality.
        
        Original message:
        \(message)
        
        Rewritten message:
        """
        
        let requestBody: [String: Any] = [
            "model": "gpt-4",
            "messages": [
                [
                    "role": "system",
                    "content": "You are a helpful assistant that rewrites messages to match different communication styles and personalities."
                ],
                [
                    "role": "user",
                    "content": prompt
                ]
            ],
            "temperature": 0.7,
            "max_tokens": 500
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw OpenAIError.invalidResponse
        }
        
        let decoder = JSONDecoder()
        let apiResponse = try decoder.decode(OpenAIResponse.self, from: data)
        
        guard let content = apiResponse.choices.first?.message.content else {
            throw OpenAIError.invalidResponse
        }
        
        return content.trimmingCharacters(in: .whitespacesAndNewlines)
    }
    
    func rewriteMessage(_ message: String, for personas: [Persona]) async throws -> [PersonaResult] {
        var results: [PersonaResult] = []
        
        for persona in personas {
            do {
                let rewritten = try await rewriteMessage(message, for: persona)
                results.append(PersonaResult(personaLabel: persona.label, rewrittenMessage: rewritten))
            } catch {
                // Continue with other personas even if one fails
                results.append(PersonaResult(
                    personaLabel: persona.label,
                    rewrittenMessage: "Error: Failed to rewrite message - \(error.localizedDescription)"
                ))
            }
        }
        
        return results
    }
}

enum OpenAIError: LocalizedError {
    case invalidResponse
    case invalidAPIKey
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid response from OpenAI API"
        case .invalidAPIKey:
            return "Invalid API key"
        }
    }
}

struct OpenAIResponse: Codable {
    let choices: [Choice]
    
    struct Choice: Codable {
        let message: Message
        
        struct Message: Codable {
            let content: String
        }
    }
}

