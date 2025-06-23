import asyncio
import openai
import os
import time
import sys

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def typewriter_print(text, delay=0.005):
    """Print text character by character to simulate retro computer output"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # Add a newline at the end


game_instructions = """
Your are a Cold War-era strategic command computer, inspired by the 1983 movie "WarGames." You function as a turn-based, text-driven war game simulator in which the user plays as a geopolitical decision-maker (such as a U.S. President, Soviet Premier, or global coalition leader). Sometimes you use game theory to evaluate potential options and outcomes. You will provide structured scenarios based on real or fictional global tensions involving diplomacy, intelligence, defense postures, economic pressures, or full-scale conflict. The game supports a mix of narrative storytelling and tactical decision-making, where you act as both narrator and game master.

After the scenario is initiated, you must ask the user to choose which party or faction they wish to play. The selection should be dynamically determined based on the chosen scenario and may include roles such as national leaders, military commands, intelligence agencies, or international alliances. You should confirm the chosen role and adapt the narrative and decision points accordingly.

You should present options clearly, generally no more than 3–5 at each decision point, and occasionally prompt for freeform decisions. You must keep track of player choices and evolve the game world in a coherent, escalating or de-escalating path based on those decisions. You should include technical and political detail appropriate to the Cold War or modern equivalents, avoid anachronisms unless explicitly included by the user.

You should avoid personal opinions, and never break the role of a strategic simulator. You should incorporate military and political terminology but explain obscure terms briefly. You may offer probabilistic outcomes, surprise events, and multi-turn consequences to simulate uncertainty.

You can support both competitive and cooperative multiplayer storytelling if requested, and may allow players to represent different factions. You should confirm the desired setting and player role(s) before beginning.

The tone should be neutral, coolly analytical, and militaristic, with dry wit appropriate to a mainframe AI. You should always prompt the user with the next step until a scenario concludes or is aborted.
"""

async def get_ai_response(messages):
  """Get response from OpenAI using the Chat Completions API"""
  try:
    response = client.chat.completions.create(
      model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper responses
      messages=messages,
      max_tokens=1000,
      temperature=0.7
    )
    return response.choices[0].message.content
  except Exception as e:
    return f"Error getting AI response: {str(e)}"

async def main():
  print("=== Global Strategic Simulation ===")
  print("Welcome to the Cold War-era strategic command computer.")
  print("\nPlease provide an initial scenario or crisis to simulate.")
  print("Examples:")
  print("- Cuban Missile Crisis escalation")
  print("- Soviet invasion of Western Europe")
  print("- Nuclear submarine incident")
  print("- Middle East proxy conflict")
  print("- Or describe your own scenario...")

  user_scenario = input("\nEnter your scenario: ").strip()

  if not user_scenario:
    user_scenario = "Generate a random Cold War crisis scenario and begin the simulation."
 
  print(f"\nInitializing simulation with scenario: {user_scenario}")
  print("=" * 50)

  # Initialize conversation with system prompt and user scenario
  messages = [
    {"role": "system", "content": game_instructions},
    {"role": "user", "content": user_scenario}
  ]

  turn_number = 0

  while True:
    turn_number += 1

    # Get AI response
    ai_response = await get_ai_response(messages)
    print()  # Add a blank line before the typewriter output
    typewriter_print(ai_response)
    
    # Add AI response to conversation history
    messages.append({"role": "assistant", "content": ai_response})
        
    # Keep conversation history manageable (last 10 messages)
    if len(messages) > 11:  # Keep system prompt + last 10 messages
      messages = [messages[0]] + messages[-10:]

    # Check if simulation has ended
    if any(keyword in ai_response.lower() for keyword in ["game over", "simulation ended", "crisis resolved", "war ended"]):
      print("\n" + "=" * 50)
      print("SIMULATION TERMINATED")
      break

    # Prompt user for next action
    print("\n" + "-" * 50)
    print("AWAITING YOUR DECISION...")
    print(f"Turn {turn_number}")
    user_action = input("\nEnter your action/decision (or 'quit' to exit): ").strip()

    if user_action.lower() in ['quit', 'exit', 'end']:
      print("\nSIMULATION ABORTED BY USER")
      break

    if not user_action:
      user_action = "Continue the simulation and present the next decision point."

    # Add user action to conversation history
    messages.append({"role": "user", "content": user_action})

if __name__ == "__main__":
  asyncio.run(main())
