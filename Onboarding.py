import tkinter as tk
from tkinter import messagebox
import webbrowser
import sqlite3

class PersistentVault:
    def __init__(self, root):
        self.root = root
        self.root.title("SkyPix: Authority Vault Setup")
        self.root.geometry("450x300")
        
        # KEY SETTING: This keeps the window on top of all others
        self.root.attributes("-topmost", True)

        self.keys_to_get = [
            ('NASA_API', 'NASA (Instant)', 'https://api.nasa.gov/'),
            ('OPENWEATHER', 'OpenWeather (Instant-ish)', 'https://home.openweathermap.org/api_keys'),
            ('METEOBLUE', 'Meteoblue (Delayed)', 'https://www.meteoblue.com/en/products/astronomy-api')
        ]
        self.current_index = 0

        # UI Elements
        self.label = tk.Label(root, text="Step 1: Acquire your Keys", font=("Arial", 12, "bold"), pady=10)
        self.label.pack()

        self.instruction = tk.Label(root, text="", wraplength=400, justify="center")
        self.instruction.pack(pady=5)

        self.entry = tk.Entry(root, width=40, show="*") # Masked for security
        self.entry.pack(pady=10)

        self.btn_action = tk.Button(root, text="Open Signup Page", command=self.open_url, width=20)
        self.btn_action.pack(pady=5)

        self.btn_save = tk.Button(root, text="Vault Key & Next", command=self.save_and_next, width=20, bg="#e1e1e1")
        self.btn_save.pack(pady=5)

        self.update_step()

    def update_step(self):
        if self.current_index < len(self.keys_to_get):
            k_id, provider, url = self.keys_to_get[self.current_index]
            self.label.config(text=f"Current Task: {provider}")
            self.instruction.config(text=f"Click the button below to get your key. \nThen paste it here and click 'Vault Key'.")
            self.entry.delete(0, tk.END)
        else:
            messagebox.showinfo("Done", "All keys processed! Vault is closed.")
            self.root.destroy()

    def open_url(self):
        url = self.keys_to_get[self.current_index][2]
        webbrowser.open(url)

    def save_and_next(self):
        key_val = self.entry.get().strip()
        k_id = self.keys_to_get[self.current_index][0]
        
        if key_val:
            with sqlite3.connect("skypix_config.db") as conn:
                conn.execute("UPDATE keys_vault SET key_value = ?, status = 'ACTIVE' WHERE key_name = ?", (key_val, k_id))
            print(f"✓ {k_id} Vaulted.")
        
        self.current_index += 1
        self.update_step()

# Initialize and Run
if __name__ == "__main__":
    # First, ensure DB exists (Reuse your previous init logic)
    root = tk.Tk()
    app = PersistentVault(root)
    root.mainloop()