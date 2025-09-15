import asyncio
import websockets

async def run_websocket_client():
    # 1. get member_code for user
    member_code = input("Member code: ")
    if not member_code:
        print("Member ocde cannot be empty")
        return

    uri = f"ws://127.0.0.1:8000/ws/{member_code}"
    origin = "http://127.0.0.1:8000"
    
    try:
        async with websockets.connect(uri, origin=origin) as websocket:
            # the server will send a confirmation message first
            initial_response = await websocket.recv()
            print(f"Server: {initial_response}")

            # check if the connection was succesful
            if initial_response.startswith("Error"):
                return

            
            print("Connected to WebSocket server. Type a message and press Enter to send.")
            print("Type 'exit' to close the connection")

            while True:
                # get user input from the terminal
                message = await asyncio.to_thread(input, "> ")

                if message.lower() == 'exit':
                    break   

                # send the message to the server
                await websocket.send(message)
                response = await websocket.recv()
                print(f"Chatbot: {response}")

    except ConnectionRefusedError:
        print("Connection failed. Is the server running?")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(run_websocket_client())