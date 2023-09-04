import langchain
import gradio as gr

llm = langchain.LLM(...) 

def chat(input):
    response = llm.generate_response(input)
    return response

app = gr.Interface(chat, "text", "text")