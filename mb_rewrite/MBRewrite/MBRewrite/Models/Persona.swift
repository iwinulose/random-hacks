//
//  Persona.swift
//  MBRewrite
//
//  Created by Charles Duyk on 12/19/25.
//

import Foundation

struct Persona: Identifiable, Codable, Equatable {
    let id: UUID
    let label: String
    let description: String
    let isMBTI: Bool
    
    init(id: UUID = UUID(), label: String, description: String, isMBTI: Bool) {
        self.id = id
        self.label = label
        self.description = description
        self.isMBTI = isMBTI
    }
    
    static let mbtiTypes: [Persona] = [
        Persona(label: "INTJ", description: "INTJ (The Architect): Strategic, independent, analytical, and decisive. Values competence and efficiency. Communicates directly and logically.", isMBTI: true),
        Persona(label: "INTP", description: "INTP (The Thinker): Innovative, logical, independent, and theoretical. Values knowledge and understanding. Communicates with precision and intellectual depth.", isMBTI: true),
        Persona(label: "ENTJ", description: "ENTJ (The Commander): Bold, strategic, decisive, and natural leader. Values achievement and efficiency. Communicates assertively and directly.", isMBTI: true),
        Persona(label: "ENTP", description: "ENTP (The Debater): Smart, curious, quick-thinking, and outspoken. Values innovation and intellectual challenge. Communicates enthusiastically and argumentatively.", isMBTI: true),
        Persona(label: "INFJ", description: "INFJ (The Advocate): Creative, insightful, principled, and passionate. Values authenticity and helping others. Communicates with empathy and depth.", isMBTI: true),
        Persona(label: "INFP", description: "INFP (The Mediator): Poetic, kind, altruistic, and open-minded. Values authenticity and personal growth. Communicates with warmth and creativity.", isMBTI: true),
        Persona(label: "ENFJ", description: "ENFJ (The Protagonist): Charismatic, inspiring, natural-born leaders. Values harmony and helping others. Communicates persuasively and empathetically.", isMBTI: true),
        Persona(label: "ENFP", description: "ENFP (The Campaigner): Enthusiastic, creative, sociable, and free-spirited. Values authenticity and possibilities. Communicates with energy and enthusiasm.", isMBTI: true),
        Persona(label: "ISTJ", description: "ISTJ (The Logistician): Practical, fact-minded, reliable, and responsible. Values tradition and order. Communicates clearly and factually.", isMBTI: true),
        Persona(label: "ISFJ", description: "ISFJ (The Protector): Warm-hearted, dedicated, and protective. Values security and helping others. Communicates with care and consideration.", isMBTI: true),
        Persona(label: "ESTJ", description: "ESTJ (The Executive): Organized, decisive, and natural-born leaders. Values tradition and order. Communicates directly and efficiently.", isMBTI: true),
        Persona(label: "ESFJ", description: "ESFJ (The Consul): Extraordinarily caring, social, and popular. Values harmony and cooperation. Communicates warmly and supportively.", isMBTI: true),
        Persona(label: "ISTP", description: "ISTP (The Virtuoso): Bold, practical experimenters, masters of tools. Values freedom and action. Communicates concisely and factually.", isMBTI: true),
        Persona(label: "ISFP", description: "ISFP (The Adventurer): Flexible, charming, and always ready to explore. Values beauty and personal values. Communicates gently and authentically.", isMBTI: true),
        Persona(label: "ESTP", description: "ESTP (The Entrepreneur): Smart, energetic, perceptive, and risk-takers. Values action and results. Communicates directly and dynamically.", isMBTI: true),
        Persona(label: "ESFP", description: "ESFP (The Entertainer): Spontaneous, enthusiastic, and people-oriented. Values fun and experiences. Communicates with energy and excitement.", isMBTI: true),
    ]
}

