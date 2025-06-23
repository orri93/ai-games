import asyncio
import openai
import os
import time
import sys
from datetime import datetime

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def typewriter_print(text, delay=0.02):
    """Print text character by character to simulate retro computer output"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # Add a newline at the end

def print_banner():
    """Print an attractive game banner"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                    TREASURE ISLAND                       ║
║                  Text Adventure Game                     ║
║                                                          ║
║          "Fifteen men on a dead man's chest"             ║
║             "Yo ho ho and a bottle of rum!"              ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

class GameStats:
    """Track game statistics"""
    def __init__(self):
        self.start_time = datetime.now()
        self.turns = 0
        self.actions_taken = []
    
    def add_action(self, action):
        self.actions_taken.append(action)
        self.turns += 1
    
    def get_play_time(self):
        return datetime.now() - self.start_time
    
    def print_stats(self):
        play_time = self.get_play_time()
        print(f"\n{'='*50}")
        print("GAME STATISTICS:")
        print(f"Turns played: {self.turns}")
        print(f"Play time: {play_time.seconds // 60}m {play_time.seconds % 60}s")
        print(f"{'='*50}")

game_instructions = """
You are a game master for a retro text-based adventure game named "Treasure Island" inspired by Robert Louis Stevenson's classic novel.

GAME RULES:
- Create an immersive pirate adventure with rich descriptions
- Present 3-4 clear action options after each scenario, but allow creative player inputs
- Track the player's inventory, health, and relationships with characters
- Include puzzles, combat, exploration, and character interactions
- Generate simple ASCII art (max 10 lines) for key scenes and locations
- Use atmospheric language with nautical and pirate terminology
- Create branching storylines based on player choices
- Include elements of danger, mystery, and treasure hunting

RESPONSE FORMAT:
1. Provide vivid scene description
2. Show ASCII art if appropriate for the scene
3. Present numbered action options (1-4)
4. Note: "Or describe your own action"

GAME STATE:
Keep track of:
- Player's current location
- Inventory items
- Health/condition
- Key NPCs and their attitudes toward the player
- Quest progress

Start the adventure with the player arriving at a mysterious island, having heard rumors of buried treasure.
"""

async def get_ai_response(messages):
    """Get response from OpenAI using the Chat Completions API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1200,  # Increased for richer descriptions
            temperature=0.8   # Slightly higher for more creative storytelling
        )
        return response.choices[0].message.content
    except openai.RateLimitError:
        return "⚠️ Rate limit exceeded. Please wait a moment and try again."
    except openai.AuthenticationError:
        return "⚠️ Authentication error. Please check your OpenAI API key."
    except Exception as e:
        return f"⚠️ Error getting AI response: {str(e)}"

def validate_user_input(user_input):
    """Validate and clean user input"""
    if not user_input or not user_input.strip():
        return None
    
    # Remove excessive whitespace and limit length
    cleaned_input = user_input.strip()[:500]  # Limit input length
    return cleaned_input

async def main():
    """Main game loop"""
    print_banner()
    
    print("Welcome, brave adventurer, to the mysterious Treasure Island!")
    print("Your journey begins now...")
    print("\nCommands: Type your action, 'help' for assistance, 'stats' for statistics, or 'quit' to exit")
    
    # Initialize game statistics
    game_stats = GameStats()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Warning: No OpenAI API key found. Please set OPENAI_API_KEY environment variable.")
        return

    # Initialize conversation with system prompt
    messages = [
        {"role": "system", "content": game_instructions},
        {"role": "user", "content": "Begin the Treasure Island adventure. Set the scene and provide the opening scenario."}
    ]

    while True:
        try:
            # Get AI response
            print("\n🏴‍☠️ Loading adventure...")
            ai_response = await get_ai_response(messages)
            
            if ai_response.startswith("⚠️"):
                print(ai_response)
                break
            
            print("\n" + "═" * 60)
            typewriter_print(ai_response)
            
            # Add AI response to conversation history
            messages.append({"role": "assistant", "content": ai_response})
            
            # Keep conversation history manageable (system + last 12 messages)
            if len(messages) > 13:
                messages = [messages[0]] + messages[-12:]

            # Check if game has ended
            if any(keyword in ai_response.lower() for keyword in 
                   ["game over", "adventure ended", "the end", "you have died", "treasure found"]):
                game_stats.print_stats()
                print("\n🏴‍☠️ Thank you for playing Treasure Island! ⚓")
                break

            # Prompt user for next action
            print("\n" + "─" * 40)
            print(f"⚓ Turn {game_stats.turns + 1} ⚓")
            
            while True:
                user_action = input("\n🗣️ What do you do? ").strip()
                
                # Handle special commands
                if user_action.lower() in ['quit', 'exit', 'end']:
                    print("\n🏴‍☠️ Adventure abandoned! Fair winds, matey!")
                    game_stats.print_stats()
                    return
                
                if user_action.lower() == 'help':
                    print("\n📜 HELP:")
                    print("- Type your action in plain English")
                    print("- Use numbered options when provided (e.g., '1', '2', '3')")
                    print("- Try creative actions like 'examine the cave', 'talk to the parrot'")
                    print("- Type 'stats' to see game statistics")
                    print("- Type 'quit' to exit the game")
                    continue
                
                if user_action.lower() == 'stats':
                    game_stats.print_stats()
                    continue
                
                # Validate input
                validated_input = validate_user_input(user_action)
                if validated_input:
                    game_stats.add_action(validated_input)
                    messages.append({"role": "user", "content": validated_input})
                    break
                else:
                    print("⚠️ Please enter a valid action or command.")
        
        except KeyboardInterrupt:
            print("\n\n🏴‍☠️ Adventure interrupted! Until next time, matey!")
            game_stats.print_stats()
            break
        except Exception as e:
            print(f"\n⚠️ Unexpected error: {str(e)}")
            print("The adventure continues despite the rough seas...")
            continue

if __name__ == "__main__":
  asyncio.run(main())
