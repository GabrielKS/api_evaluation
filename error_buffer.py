# A class encapuslating a buffer that holds errors. This will allow us to nicely change the underlying
# implementation of the buffer without changing the interface to the rest of the app.
class ErrorBuffer:
    # A simple constructor
    def __init__(self):
        super().__init__()
        self.error_log = []
    
    # Add an entry to the ErrorBuffer
    def append(self, msg):
        self.error_log.append(msg)
    
    # Get the entire contents of the ErrorBuffer as a list of strings
    def to_list(self):
        return self.error_log.copy()
    
    # Get the number of entries in the ErrorBuffer
    def num_entries(self):
        return len(self.error_log)
    
    # Delete all entries from the ErrorBuffer
    def clear(self):
        self.error_log.clear()
