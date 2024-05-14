import socket
import ollama
import gradio as gr

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to a specific address and port
server_socket.bind(("localhost", 12345))

# Listen for incoming connections
server_socket.listen(1)
print("Server started. Listening on port 12345...")

messages = []

# Create the Gradio interface
with gr.Blocks() as demo:
    
    chatbot = gr.Chatbot(height=800, elem_id="chatbotbox", show_share_button=True, show_copy_button=True)
    
    chat_history_state = gr.State([])  # State to hold the chat history

    def startbot(chat_history) :
        # Accept an incoming connection
        client_socket, address = server_socket.accept()
        print("Connection accepted from", address)

        # Receive data from the client
        while True:
            try:
                chat_history.append(("", ""))

                data_str = ""
                # Print to terminal (Optional)
                #print("\nClient:")
                # Receive data
                while "END" not in data_str:
                    data = client_socket.recv(1024).decode('utf-8')
                    data_str += data
                    if("END" not in data_str):
                        # Print to terminal (Optional)
                        #print(data, end='', flush=True)
                        chat_history[len(chat_history)-1] = (data_str, "")
                        yield chat_history


                new_text = {'role' : 'user',
                            'content' : data_str[:-3]}

                messages.append(new_text)

                # Generate response
                response = ollama.chat(model='phi3', messages=messages, stream=True)
                response_str = ""

                # Print to terminal (Optional)
                #print("\nServer:")

                # Send data
                for chunk in response:
                    client_socket.sendall(chunk['message']['content'].encode('utf-8'))
                    response_str += chunk['message']['content']
                    # Print to terminal (Optional)
                    #print(chunk['message']['content'], end='', flush=True)
                    chat_history[len(chat_history)-1] = (chat_history[len(chat_history)-1][0], response_str)
                    yield chat_history

                new_text = {'role' : 'assistant',
                            'content' : response_str}

                messages.append(new_text)

                client_socket.sendall("END".encode('utf-8'))

            except socket.error as e:
                print("Error receiving data:", e)
                break
            
        # Close the connection
        client_socket.close()

    demo.load(startbot, chat_history_state, chatbot)

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