import gradio as gr
from chatbot import CompanyChatbot

# Initialize chatbot
print("Initializing chatbot...")
try:
    chatbot = CompanyChatbot()
    print("Chatbot ready!")
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit(1)
except Exception as e:
    print(f"Error: {e}")
    exit(1)


def chat_function(message, history):
    """Process chat messages and return response"""
    response = chatbot.ask(message)
    answer = response["answer"]
    if response["sources"]:
        answer += "\n\n**Sources:** " + ", ".join(response["sources"])
    return answer


demo = gr.ChatInterface(
    fn=chat_function,
    title="Company Procedures Assistant",
    description="Ask about company procedures, policies, and workflows!",
    examples=[
        "How do I report a workplace incident?",
        "What is the document approval process?",
        "What are the password requirements?",
        "How do I submit travel expenses?",
    ]
)

if __name__ == "__main__":
    print("\nStarting web interface...")
    demo.launch(server_name="127.0.0.1", server_port=7860)
