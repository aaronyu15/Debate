import socket
import ollama
import gradio as gr

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect(("localhost", 12345))
print("Connected to server on port 12345...")


# Create the Gradio interface
with gr.Blocks() as demo:
    
    chatbot = gr.Chatbot(height=800, elem_id="chatbotbox", show_share_button=True, show_copy_button=True)

    prompt = gr.Textbox(label="Initial prompt:")
    
    chat_history_state = gr.State([])  # State to hold the chat history


    def startbot(initial, chat_history):
        #initial = input("Input: ")
        chat_history.append((initial, ""))

        # Send data to the server
        client_socket.send(initial.encode('utf-8'))

        client_socket.send("END".encode('utf-8'))

        messages = [{'role' : 'user',
                     'content' : initial}]

        while True:

            data_str = ""
            # Print to terminal (Optional)
            #print("\nServer:")

            # Receive data
            while "END" not in data_str:
                data = client_socket.recv(1024).decode('utf-8')
                data_str += data
                if("END" not in data_str):
                    # Print to terminal (Optional)
                    #print(data, end='', flush=True)
                    chat_history[len(chat_history)-1] = (chat_history[len(chat_history)-1][0], data_str)
                    yield chat_history

            new_text = {'role' : 'user',
                        'content' : data_str[:-3]}

            messages.append(new_text)

            # Generate response
            response = ollama.chat(model='phi3', messages=messages, stream=True)
            response_str = ""

            chat_history.append(("", ""))
            # Print to terminal (optional)
            #print("\nClient:")
            for chunk in response:
                # Send response
                client_socket.sendall(chunk['message']['content'].encode('utf-8'))
                response_str += chunk['message']['content']
                # Print to terminal (optional)
                #print(chunk['message']['content'], end='', flush=True)

                chat_history[len(chat_history)-1] = (response_str, "")
                yield chat_history

            new_text = {'role' : 'assistant',
                        'content' : response_str}

            messages.append(new_text)

            client_socket.send("END".encode('utf-8'))
            

    
    prompt.submit(startbot, [prompt, chat_history_state], chatbot)

    # Custom CSS for enabling scrolling in the Textbox component
    custom_css = """
    <style>
        #chatbotbox > div:first-child {
            inset : initial
        }
    </style>
    """
    # Add custom CSS 
    gr.HTML(custom_css)

# Launch the Gradio interface
demo.launch()