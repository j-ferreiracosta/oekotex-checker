from openai import OpenAI

# Create an Ollama client instance pointing to your local Ollama instance.
client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)

def fetch_model_choices():
    """
    Query the local Ollama instance for available models.
    Returns a list of model IDs.
    """
    try:
        models = client.models.list()  # Expected to return an object with a "data" attribute.
        choices = [m.id for m in models.data]
        if not choices:
            choices = ["deepseek-r1:8b", "llama3.2:latest"]
        return choices
    except Exception as e:
        print("Error fetching models:", e)
        return ["llama3.2:latest"]

def process_chat(user_input, chat_history, chat_model, chat_temperature, chat_max_tokens, chat_top_k_tokens, system_role):
    """
    Assemble the conversation messages, call the local Ollama instance via the Ollama client,
    and append the assistant's reply to the chat history.
    The chat history is expected to be a list of dictionaries, each with 'role' and 'content' keys.
    """
    if user_input.strip() == "":
        return "", chat_history, chat_history

    # Build the list of messages for the API call.
    chat_messages = []
    # Include the system role message if provided.
    if system_role.strip() != "":
        chat_messages.append({"role": "system", "content": system_role})
    # Append previous conversation from chat_history.
    chat_messages.extend(chat_history)
    # Append the new user message.
    chat_messages.append({"role": "user", "content": user_input})

    # Call the API.
    response = client.chat.completions.create(
        model=chat_model,
        messages=chat_messages,
        temperature=chat_temperature,
        max_tokens=chat_max_tokens
    )
    try:
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Error: {e}"
    
    # Update chat_history with the new exchange.
    # Append the user message and the assistant's reply as separate dictionary entries.
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": reply})

    # Return an empty string for the input box and the updated chat history.
    return "", chat_history, chat_history
