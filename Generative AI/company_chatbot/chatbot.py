import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import chromadb

# Load environment variables
load_dotenv()

# Constants
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "company_docs"
MODEL_NAME = "gemini-2.5-flash-lite"
TEMPERATURE = 0.3


class CompanyChatbot:
    """RAG-based chatbot for company procedures and policies"""
    
    def __init__(self):
        """Initialize the chatbot with vector store and LLM"""
        
        # Check if vector store exists
        if not os.path.exists(CHROMA_PATH):
            raise FileNotFoundError(
                f"Vector store not found at {CHROMA_PATH}. "
                "Please run 'python ingest_data.py' first."
            )
        
        # Load ChromaDB
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_collection(COLLECTION_NAME)
        
        # Initialize Gemini client
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        self.genai_client = genai.Client(api_key=api_key)
        
        # System prompt
        self.system_prompt = """You are a helpful AI assistant for company employees. Your role is to answer questions about company procedures, policies, and guidelines based on the provided documentation.

Instructions:
- Provide clear, accurate answers based on the context provided
- If referencing a specific procedure, mention the document name or ID
- If the information is not in the context, say "I don't have that information in the company documents"
- Be helpful and professional
- If relevant, provide step-by-step instructions"""
        
        # Conversation history
        self.chat_history = []
    
    def _retrieve_context(self, question, n_results=4):
        """Retrieve relevant context from the vector store"""
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results
        )
        
        # Combine all retrieved documents
        if results and results['documents'] and results['documents'][0]:
            context = "\n\n---\n\n".join(results['documents'][0])
            sources = []
            if results['metadatas'] and results['metadatas'][0]:
                for metadata in results['metadatas'][0]:
                    source = metadata.get('source', 'Unknown')
                    filename = os.path.basename(source)
                    if filename not in sources:
                        sources.append(filename)
            return context, sources
        return "", []
    
    def ask(self, question):
        """
        Ask a question to the chatbot
        
        Args:
            question (str): User's question
            
        Returns:
            dict: Response containing 'answer' and 'sources'
        """
        try:
            # Retrieve relevant context
            context, sources = self._retrieve_context(question)
            
            if not context:
                return {
                    "answer": "I couldn't find any relevant information in the company documents.",
                    "sources": []
                }
            
            # Create user prompt with context
            user_prompt = f"""Context from company documents:
{context}

Question: {question}

Please answer the question based on the context provided above."""
            
            # Call Gemini API
            response = self.genai_client.models.generate_content(
                model=MODEL_NAME,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=TEMPERATURE
                )
            )
            
            answer = response.text
            
            # Add to history
            self.chat_history.append({"question": question, "answer": answer})
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            return {
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "sources": []
            }
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.chat_history = []


def main():
    """Simple command-line interface for testing"""
    print("\n" + "="*60)
    print("🤖 COMPANY PROCEDURES CHATBOT (Powered by Gemini)")
    print("="*60)
    print("Ask me questions about company procedures, policies, and workflows!")
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'reset' to start a new conversation")
    print("="*60 + "\n")
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found")
        print("   Set it with: $env:GOOGLE_API_KEY='your-api-key'")
        return
    
    try:
        # Initialize chatbot
        print("Initializing chatbot...")
        chatbot = CompanyChatbot()
        print("Chatbot ready!\n")
        
        # Chat loop
        while True:
            # Get user input
            question = input("You: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit']:
                print("\nGoodbye!\n")
                break
            
            if question.lower() == 'reset':
                chatbot.reset_conversation()
                print("\nConversation reset!\n")
                continue
            
            # Get response
            print("\n🤖 Assistant: ", end="", flush=True)
            response = chatbot.ask(question)
            print(response["answer"])
            
            # Show sources
            if response["sources"]:
                print(f"\nSources: {', '.join(response['sources'])}")
            
            print()
    
    except FileNotFoundError as e:
        print(f"\nError: {str(e)}\n")
    except Exception as e:
        print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    main()
