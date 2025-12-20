#!/usr/bin/env python3
"""
mb_rewrite.py - Rewrite messages for different personas using OpenAI

Takes a message and rewrites it for specified Myers-Briggs personality types
or custom personas. Supports interactive mode after initial run.
"""

import argparse
import sys
import os
from typing import List, Dict, Set
from openai import OpenAI
from dotenv import load_dotenv


# Myers-Briggs personality type descriptions
MB_DESCRIPTIONS = {
    "INTJ": "INTJ (The Architect): Strategic, independent, analytical, and decisive. Values competence and efficiency. Communicates directly and logically.",
    "INTP": "INTP (The Thinker): Innovative, logical, independent, and theoretical. Values knowledge and understanding. Communicates with precision and intellectual depth.",
    "ENTJ": "ENTJ (The Commander): Bold, strategic, decisive, and natural leader. Values achievement and efficiency. Communicates assertively and directly.",
    "ENTP": "ENTP (The Debater): Smart, curious, quick-thinking, and outspoken. Values innovation and intellectual challenge. Communicates enthusiastically and argumentatively.",
    "INFJ": "INFJ (The Advocate): Creative, insightful, principled, and passionate. Values authenticity and helping others. Communicates with empathy and depth.",
    "INFP": "INFP (The Mediator): Poetic, kind, altruistic, and open-minded. Values authenticity and personal growth. Communicates with warmth and creativity.",
    "ENFJ": "ENFJ (The Protagonist): Charismatic, inspiring, natural-born leaders. Values harmony and helping others. Communicates persuasively and empathetically.",
    "ENFP": "ENFP (The Campaigner): Enthusiastic, creative, sociable, and free-spirited. Values authenticity and possibilities. Communicates with energy and enthusiasm.",
    "ISTJ": "ISTJ (The Logistician): Practical, fact-minded, reliable, and responsible. Values tradition and order. Communicates clearly and factually.",
    "ISFJ": "ISFJ (The Protector): Warm-hearted, dedicated, and protective. Values security and helping others. Communicates with care and consideration.",
    "ESTJ": "ESTJ (The Executive): Organized, decisive, and natural-born leaders. Values tradition and order. Communicates directly and efficiently.",
    "ESFJ": "ESFJ (The Consul): Extraordinarily caring, social, and popular. Values harmony and cooperation. Communicates warmly and supportively.",
    "ISTP": "ISTP (The Virtuoso): Bold, practical experimenters, masters of tools. Values freedom and action. Communicates concisely and factually.",
    "ISFP": "ISFP (The Adventurer): Flexible, charming, and always ready to explore. Values beauty and personal values. Communicates gently and authentically.",
    "ESTP": "ESTP (The Entrepreneur): Smart, energetic, perceptive, and risk-takers. Values action and results. Communicates directly and dynamically.",
    "ESFP": "ESFP (The Entertainer): Spontaneous, enthusiastic, and people-oriented. Values fun and experiences. Communicates with energy and excitement.",
}


def get_client() -> OpenAI:
    """Initialize and return OpenAI client."""
    # Also try loading from current directory (for convenience)
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found.", file=sys.stderr)
        print("Please set it using one of the following methods:", file=sys.stderr)
        print("  1. Environment variable: export OPENAI_API_KEY='your-key-here'", file=sys.stderr)
        print(f"  2. .env file: Create a file named '.env' in {script_dir} with:", file=sys.stderr)
        print("     OPENAI_API_KEY=your-key-here", file=sys.stderr)
        sys.exit(1)
    return OpenAI(api_key=api_key)


def normalize_mb_type(mb_type: str) -> str:
    """Normalize Myers-Briggs type to uppercase."""
    return mb_type.upper()


def validate_mb_type(mb_type: str) -> bool:
    """Validate that the Myers-Briggs type is valid."""
    normalized = normalize_mb_type(mb_type)
    return normalized in MB_DESCRIPTIONS


def build_persona_description(mb_types: List[str], custom_personas: List[str]) -> List[Dict[str, str]]:
    """Build list of persona descriptions from MB types and custom personas."""
    personas = []
    
    for mb_type in mb_types:
        normalized = normalize_mb_type(mb_type)
        if not validate_mb_type(normalized):
            print(f"Warning: Invalid Myers-Briggs type '{mb_type}'. Skipping.", file=sys.stderr)
            continue
        personas.append({
            "label": normalized,
            "description": MB_DESCRIPTIONS[normalized]
        })
    
    for i, custom in enumerate(custom_personas, start=1):
        personas.append({
            "label": f"Custom {i}",
            "description": custom
        })
    
    return personas


def display_persona_menu(selected_mb_types: Set[str], custom_personas: List[str]):
    """Display the current selection of personas."""
    print("\n" + "="*70)
    print("Current Persona Selection:")
    print("="*70)
    
    if selected_mb_types:
        print("\nMyers-Briggs Types:")
        for mb_type in sorted(selected_mb_types):
            print(f"  • {mb_type} - {MB_DESCRIPTIONS[mb_type].split(':')[1].strip()}")
    else:
        print("\nMyers-Briggs Types: (none selected)")
    
    if custom_personas:
        print("\nCustom Personas:")
        for i, custom in enumerate(custom_personas, start=1):
            print(f"  • Custom {i}: {custom}")
    else:
        print("\nCustom Personas: (none selected)")
    
    print("="*70)


def display_mb_types_menu():
    """Display all available Myers-Briggs types in a menu format."""
    print("\n" + "="*70)
    print("Available Myers-Briggs Personality Types:")
    print("="*70)
    
    mb_list = sorted(MB_DESCRIPTIONS.keys())
    for i, mb_type in enumerate(mb_list, start=1):
        desc = MB_DESCRIPTIONS[mb_type].split(':')[1].strip()
        print(f"{i:2d}. {mb_type:4s} - {desc}")
    
    print("="*70)


def interactive_persona_selection() -> List[Dict[str, str]]:
    """Interactive menu for selecting personas."""
    selected_mb_types: Set[str] = set()
    custom_personas: List[str] = []
    
    while True:
        display_persona_menu(selected_mb_types, custom_personas)
        
        print("\nOptions:")
        print("  1. Add Myers-Briggs type")
        print("  2. Remove Myers-Briggs type")
        print("  3. Add custom persona")
        print("  4. Remove custom persona")
        print("  5. View all MBTI types")
        print("  6. Done (proceed with current selection)")
        print("  7. Exit")
        
        try:
            choice = input("\nSelect an option (1-7): ").strip()
            
            if choice == "1":
                display_mb_types_menu()
                mb_input = input("\nEnter MBTI type (or number from list): ").strip().upper()
                
                # Check if it's a number
                try:
                    mb_num = int(mb_input)
                    mb_list = sorted(MB_DESCRIPTIONS.keys())
                    if 1 <= mb_num <= len(mb_list):
                        mb_type = mb_list[mb_num - 1]
                        if mb_type in selected_mb_types:
                            print(f"{mb_type} is already selected.")
                        else:
                            selected_mb_types.add(mb_type)
                            print(f"Added {mb_type}.")
                    else:
                        print("Invalid number.")
                except ValueError:
                    # Not a number, treat as MBTI type
                    normalized = normalize_mb_type(mb_input)
                    if validate_mb_type(normalized):
                        if normalized in selected_mb_types:
                            print(f"{normalized} is already selected.")
                        else:
                            selected_mb_types.add(normalized)
                            print(f"Added {normalized}.")
                    else:
                        print(f"Invalid MBTI type: {mb_input}")
            
            elif choice == "2":
                if not selected_mb_types:
                    print("No MBTI types selected.")
                    continue
                
                print("\nSelected MBTI types:")
                mb_list = sorted(selected_mb_types)
                for i, mb_type in enumerate(mb_list, start=1):
                    print(f"  {i}. {mb_type}")
                
                mb_input = input("\nEnter MBTI type to remove: ").strip().upper()
                normalized = normalize_mb_type(mb_input)
                if normalized in selected_mb_types:
                    selected_mb_types.remove(normalized)
                    print(f"Removed {normalized}.")
                else:
                    print(f"{normalized} is not in the selection.")
            
            elif choice == "3":
                custom = input("Enter custom persona description: ").strip()
                if custom:
                    custom_personas.append(custom)
                    print(f"Added custom persona: {custom}")
                else:
                    print("Empty description not allowed.")
            
            elif choice == "4":
                if not custom_personas:
                    print("No custom personas selected.")
                    continue
                
                print("\nCustom personas:")
                for i, custom in enumerate(custom_personas, start=1):
                    print(f"  {i}. {custom}")
                
                try:
                    idx_input = input("\nEnter number to remove: ").strip()
                    idx = int(idx_input)
                    if 1 <= idx <= len(custom_personas):
                        removed = custom_personas.pop(idx - 1)
                        print(f"Removed: {removed}")
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Please enter a valid number.")
            
            elif choice == "5":
                display_mb_types_menu()
                input("\nPress Enter to continue...")
            
            elif choice == "6":
                if not selected_mb_types and not custom_personas:
                    print("\nError: At least one persona must be selected.")
                    input("Press Enter to continue...")
                    continue
                break
            
            elif choice == "7":
                print("\nExiting.")
                sys.exit(0)
            
            else:
                print("Invalid option. Please select 1-7.")
        
        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting.")
            sys.exit(0)
    
    # Build final persona list
    return build_persona_description(list(selected_mb_types), custom_personas)


def rewrite_message(client: OpenAI, message: str, persona: Dict[str, str]) -> str:
    """Rewrite a message for a specific persona using OpenAI."""
    prompt = f"""Rewrite the following message as if you were {persona['description']}.

The rewritten message should reflect how this persona would naturally communicate, maintaining the core meaning but adapting the tone, style, and approach to match their personality.

Original message:
{message}

Rewritten message:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that rewrites messages to match different communication styles and personalities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: Failed to rewrite message - {str(e)}"


def format_output(personas: List[Dict[str, str]], message: str, rewritten_messages: List[str]):
    """Format the output for easy copying and pasting."""
    print("\n" + "="*70)
    print(f"Original message: {message}")
    print("="*70 + "\n")
    
    for persona, rewritten in zip(personas, rewritten_messages):
        print(f"[{persona['label']}]")
        print("-" * 70)
        print(rewritten)
        print()


def process_message(client: OpenAI, message: str, personas: List[Dict[str, str]]):
    """Process a single message for all personas."""
    if not message.strip():
        return
    
    rewritten_messages = []
    for persona in personas:
        rewritten = rewrite_message(client, message, persona)
        rewritten_messages.append(rewritten)
    
    format_output(personas, message, rewritten_messages)


def interactive_mode(client: OpenAI, personas: List[Dict[str, str]]):
    """Enter interactive mode to process multiple messages."""
    print("\n" + "="*70)
    print("Interactive mode. Enter messages to rewrite (Ctrl+D or Ctrl+C to exit).")
    print("="*70 + "\n")
    
    try:
        while True:
            try:
                message = input("Message: ").strip()
                if message:
                    process_message(client, message, personas)
            except EOFError:
                print("\nExiting interactive mode.")
                break
            except KeyboardInterrupt:
                print("\n\nExiting interactive mode.")
                break
    except KeyboardInterrupt:
        print("\n\nExiting interactive mode.")


def main():
    parser = argparse.ArgumentParser(
        description="Rewrite messages for different personas using OpenAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -m INTJ -m ENFP "Hello, how are you?"
  %(prog)s -m intj -p "a person who loves cats" "Check out this new feature"
  %(prog)s -m INTJ -m ENFP -p "a professional developer" "Let's schedule a meeting"
  %(prog)s
  %(prog)s "Hello, how are you?"

If no personas are specified via command line, an interactive menu will be shown
to select personas before processing messages.
        """
    )
    
    parser.add_argument(
        "-m", "--meyers-briggs",
        dest="mb_types",
        action="append",
        default=[],
        help="Myers-Briggs personality type (can be specified multiple times)"
    )
    
    parser.add_argument(
        "-p", "--personas",
        dest="custom_personas",
        action="append",
        default=[],
        help="Custom persona description (can be specified multiple times)"
    )
    
    parser.add_argument(
        "message",
        nargs="?",
        help="Initial message to rewrite (optional if entering interactive mode)"
    )
    
    args = parser.parse_args()
    
    # Initialize OpenAI client
    client = get_client()
    
    # If personas are specified via command line, use them
    # Otherwise, show interactive menu
    if args.mb_types or args.custom_personas:
        # Build persona descriptions from command line args
        personas = build_persona_description(args.mb_types, args.custom_personas)
        
        if not personas:
            print("Error: No valid personas specified.", file=sys.stderr)
            sys.exit(1)
    else:
        # Show interactive persona selection menu
        print("="*70)
        print("Welcome to MB Rewrite!")
        print("="*70)
        print("\nNo personas specified. Please select personas to use:")
        personas = interactive_persona_selection()
        print("\n" + "="*70)
        print("Persona selection complete!")
        print("="*70)
    
    # Process initial message if provided
    if args.message:
        process_message(client, args.message, personas)
    
    # Enter interactive mode
    interactive_mode(client, personas)


if __name__ == "__main__":
    main()

