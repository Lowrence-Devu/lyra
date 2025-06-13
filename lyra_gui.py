import tkinter as tk
from tkinter import scrolledtext
import threading

# Import your LYRA functions
from lyra import respond, speak, listen

class LyraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LYRA Assistant")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)

        self.entry = tk.Entry(root, font=("Arial", 14))
        self.entry.pack(padx=10, pady=(0,10), fill=tk.X)
        self.entry.bind("<Return>", self.send_command)

        self.voice_button = tk.Button(root, text="🎤 Voice", command=self.voice_command)
        self.voice_button.pack(pady=(0,10))

        self.add_message("LYRA", "Hello! How can I assist you today?")

    def add_message(self, sender, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def send_command(self, event=None):
        user_input = self.entry.get().strip()
        if user_input:
            self.add_message("You", user_input)
            self.entry.delete(0, tk.END)
            threading.Thread(target=self.process_command, args=(user_input,)).start()

    def process_command(self, command):
        # Use your existing respond() function
        respond(command)

    def voice_command(self):
        self.add_message("LYRA", "Listening...")
        threading.Thread(target=self.listen_and_respond).start()

    def listen_and_respond(self):
        command = listen()
        if command:
            self.add_message("You (voice)", command)
            respond(command)

if __name__ == "__main__":
    root = tk.Tk()
    app = LyraGUI(root)
    root.mainloop()