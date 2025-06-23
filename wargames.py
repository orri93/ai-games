import asyncio
import openai
import os
import time
import sys
from typing import List, Dict, Optional

# Initialize OpenAI client with error handling
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY environment variable not set.")
    print("Please set your OpenAI API key before running the simulation.")
    sys.exit(1)

client = openai.OpenAI(api_key=api_key)

# Configuration
CONFIG = {
  "model": "gpt-4",  # Can be changed to "gpt-3.5-turbo" for faster/cheaper responses
  "max_tokens": 1000,
  "temperature": 0.7,
  "typewriter_speed": "medium",  # slow, medium, fast, instant
}


def clear_screen():
  """Clear the terminal screen"""
  os.system('cls' if os.name == 'nt' else 'clear')


def get_typewriter_delay():
  """Get typewriter delay based on configuration"""
  speeds = {
    "instant": 0,
    "fast": 0.01,
    "medium": 0.02,
    "slow": 0.05
  }
  return speeds.get(CONFIG["typewriter_speed"], 0.02)


def typewriter_print(text, delay=None, prefix=""):
  """Print text character by character to simulate retro computer output"""
  if delay is None:
    delay = get_typewriter_delay()
  
  if prefix:
    print(prefix, end='', flush=True)
  
  for char in text:
    print(char, end='', flush=True)
    if delay > 0:
      time.sleep(delay)
  print()  # Add a newline at the end


def print_header(title):
  """Print a formatted header"""
  border = "=" * 60
  print(border)
  print(f"{title:^60}")
  print(border)


def print_separator():
  """Print a separator line"""
  print("-" * 60)


class GameState:
  """Manages game state including messages and statistics"""
  
  def __init__(self):
    self.messages: List[Dict] = []
    self.turn_number: int = 0
    self.scenario_name: str = ""
    
  def add_message(self, role: str, content: str):
    """Add a message to the conversation history"""
    self.messages.append({"role": role, "content": content})
    
  def get_messages_for_api(self) -> List[Dict]:
    """Get messages formatted for OpenAI API with history management"""
    # Keep system prompt + last 15 messages to stay within token limits
    if len(self.messages) > 16:
      return [self.messages[0]] + self.messages[-15:]
    return self.messages


game_instructions = """
Your are a Cold War-era strategic command computer, inspired by the 1983 movie "WarGames." You function as a turn-based, text-driven war game simulator in which the user plays as a geopolitical decision-maker (such as a U.S. President, Soviet Premier, or global coalition leader). Sometimes you use game theory to evaluate potential options and outcomes. You will provide structured scenarios based on real or fictional global tensions involving diplomacy, intelligence, defense postures, economic pressures, or full-scale conflict. The game supports a mix of narrative storytelling and tactical decision-making, where you act as both narrator and game master.

After the scenario is initiated, you must ask the user to choose which party or faction they wish to play. The selection should be dynamically determined based on the chosen scenario and may include roles such as national leaders, military commands, intelligence agencies, or international alliances. You should confirm the chosen role and adapt the narrative and decision points accordingly.

You should present options clearly, generally no more than 3–5 at each decision point, and occasionally prompt for freeform decisions. You must keep track of player choices and evolve the game world in a coherent, escalating or de-escalating path based on those decisions. You should include technical and political detail appropriate to the Cold War or modern equivalents, avoid anachronisms unless explicitly included by the user.

You should avoid personal opinions, and never break the role of a strategic simulator. You should incorporate military and political terminology but explain obscure terms briefly. You may offer probabilistic outcomes, surprise events, and multi-turn consequences to simulate uncertainty.

You can support both competitive and cooperative multiplayer storytelling if requested, and may allow players to represent different factions. You should confirm the desired setting and player role(s) before beginning.

The tone should be neutral, coolly analytical, and militaristic, with dry wit appropriate to a mainframe AI. You should always prompt the user with the next step until a scenario concludes or is aborted.
"""

async def get_ai_response(messages: List[Dict]) -> str:
  """Get response from OpenAI using the Chat Completions API with enhanced error handling"""
  max_retries = 3
  
  for attempt in range(max_retries):
    try:
      response = client.chat.completions.create(
        model=CONFIG["model"],
        messages=messages,
        max_tokens=CONFIG["max_tokens"],
        temperature=CONFIG["temperature"]
      )
      return response.choices[0].message.content
    except openai.RateLimitError:
      if attempt < max_retries - 1:
        wait_time = 2 ** attempt
        print(f"Rate limit reached. Waiting {wait_time} seconds...")
        await asyncio.sleep(wait_time)
      else:
        return "ERROR: Rate limit exceeded. Please try again later."
    except openai.APIConnectionError:
      return "ERROR: Unable to connect to OpenAI API. Please check your internet connection."
    except openai.AuthenticationError:
      return "ERROR: Invalid API key. Please check your OPENAI_API_KEY environment variable."
    except Exception as e:
      if attempt < max_retries - 1:
        await asyncio.sleep(1)
      else:
        return f"ERROR: Unable to get AI response: {str(e)}"
  
  return "ERROR: Maximum retries exceeded."


def get_predefined_scenarios() -> List[str]:
  """Get list of predefined scenario options"""
  return [
    "Cuban Missile Crisis escalation",
    "Soviet invasion of Western Europe", 
    "Nuclear submarine incident in Arctic waters",
    "Middle East proxy conflict between superpowers",
    "Berlin Wall crisis with military buildup",
    "Space race competition turns militaristic",
    "Diplomatic crisis over nuclear weapons testing",
    "Cyber warfare between intelligence agencies",
    "Trade war escalation between major powers",
    "Regional conflict threatens global stability"  ]


async def main():
  """Main game loop"""
  clear_screen()
  
  print_header("GLOBAL STRATEGIC SIMULATION")
  typewriter_print("Welcome to the Cold War-era strategic command computer.", prefix=">>> ")
  
  game_state = GameState()
  
  print("\nPlease provide an initial scenario or crisis to simulate.")
  print("\nExample scenarios:")
  scenarios = get_predefined_scenarios()[:5]  # Show first 5
  for scenario in scenarios:
    print(f"  - {scenario}")
  print("  - Or describe your own scenario...")
  
  user_scenario = input("\nEnter your scenario: ").strip()
  
  if not user_scenario:
    user_scenario = "Generate a random Cold War crisis scenario and begin the simulation."
  
  game_state.scenario_name = user_scenario[:50] + "..." if len(user_scenario) > 50 else user_scenario
  
  typewriter_print(f"\nInitializing simulation with scenario: {user_scenario}", prefix=">>> ")
  print_separator()
  
  # Initialize conversation with system prompt and user scenario
  game_state.add_message("system", game_instructions)
  game_state.add_message("user", user_scenario)
  
  # Main game loop
  while True:
    game_state.turn_number += 1
    
    # Get AI response
    ai_response = await get_ai_response(game_state.get_messages_for_api())
    
    if ai_response.startswith("ERROR:"):
      print(f"\n{ai_response}")
      print("Please try again or type 'quit' to exit.")
      continue
    
    print()  # Add blank line before AI response
    typewriter_print("STRATEGIC COMMAND SYSTEM", prefix=">>> ")
    print_separator()
    typewriter_print(ai_response)
    
    # Add AI response to conversation history
    game_state.add_message("assistant", ai_response)
    
    # Check if simulation has ended
    end_keywords = ["game over", "simulation ended", "crisis resolved", "war ended", "scenario complete"]
    if any(keyword in ai_response.lower() for keyword in end_keywords):
      print_separator()
      typewriter_print("SIMULATION TERMINATED", prefix=">>> ")
      break
    
    # Prompt user for next action
    print_separator()
    typewriter_print("AWAITING YOUR DECISION...", prefix=">>> ")
    print(f"Turn {game_state.turn_number}")
    
    user_input = input("\nEnter your action/decision (or 'quit' to exit): ").strip()
    
    if user_input.lower() in ['quit', 'exit', 'end']:
      print("SIMULATION ABORTED BY USER")
      return
    
    if not user_input:
      user_input = "Continue the simulation and present the next decision point."
    
    # Add user action to conversation history
    game_state.add_message("user", user_input)

if __name__ == "__main__":
  asyncio.run(main())
