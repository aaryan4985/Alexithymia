class Memory:
    def __init__(self, max_interactions=5):
        self.max_interactions = max_interactions
        self.history = []

    def add_interaction(self, query, response):
        self.history.append({"query": query, "response": response})
        if len(self.history) > self.max_interactions:
            self.history.pop(0)

    def get_history_string(self):
        if not self.history:
            return ""
        
        history_str = "Conversation History:\n"
        for interaction in self.history:
            history_str += f"User: {interaction['query']}\n"
            history_str += f"Alexi: {interaction['response']}\n\n"
        return history_str
