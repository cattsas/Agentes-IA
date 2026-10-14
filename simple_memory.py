from collections import deque

class SimpleMemory:
   
    def __init__(self, max_messages:int=10):
        self.history = deque(maxlen=max_messages)  # Use deque to maintain a fixed-size history



    def add(self, role:str, text:str):
        self.history.append({"role": role, "content": text})

    def get_memory(self):
        return list(self.history)