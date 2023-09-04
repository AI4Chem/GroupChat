
Here is an English version of the README for this virtual chatbot project:

# GroupChat

GroupChat is a research project to simulate team collaboration and social behaviors in an enterprise through multi-agent conversation.

## Project Structure

- agents/: Implementation of various agent classes like EmployeeAgent, CustomerAgent, etc
- assets/: Asset and transaction system
- memory/: Private memories for individual agents
- messages/: Message type definitions
- topics/: Various discussion topic classes
- hub/: Message router
- app.py: Main application logic
- base.py: Serialization base class
- main.py: Program entry point
- utils.py: Utility functions

## How It Works

1. The main program initializes the system
2. Root user and root discussion group are created
3. Root user adds employee agents
4. Employees interact with each other and customers
5. Agents have private memories for learning and recall

## Key Features

- Natural language interaction between multiple agents
- Communication in different discussion groups (Topics)
- Personality shaping based on memory for agents
- Asset transactions and collaborative tasks
- User roles and access control for topics

## Dependencies

- Python 3.6+
- Gradio
- LangChain

We welcome any suggestions to improve this virtual agent community for multi-agent collaboration and social research!
