import socket
import ollama

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect(("localhost", 12345))
print("Connected to server on port 12345...")

initial = input("Input: ")
# Send data to the server
client_socket.send(initial.encode('utf-8'))

client_socket.send("END".encode('utf-8'))

messages = [{'role' : 'user',
             'content' : initial}]

while True:
    data_str = ""
    

    print("\nServer:")
    # Receive data
    while "END" not in data_str:
        data = client_socket.recv(1024).decode('utf-8')
        data_str += data
        if("END" not in data_str):
            print(data, end='', flush=True)

    new_text = {'role' : 'user',
                'content' : data_str[:-3]}

    messages.append(new_text)

    # Generate response
    response = ollama.chat(model='phi3', messages=messages, stream=True)
    response_str = ""

    print("\nClient:")
    for chunk in response:
        # Send response
        client_socket.sendall(chunk['message']['content'].encode('utf-8'))
        response_str += chunk['message']['content']
        print(chunk['message']['content'], end='', flush=True)
    
    new_text = {'role' : 'assistant',
                'content' : response_str}

    messages.append(new_text)

    client_socket.send("END".encode('utf-8'))

    

