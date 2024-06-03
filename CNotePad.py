import tkinter as tk
from tkinter import scrolledtext, filedialog, Menu, colorchooser, messagebox, simpledialog, font
import json
import os
import webbrowser  # Import at the top of the file with other imports

class CustomNotepad:
    CONFIG_FILE = os.path.join('configs', 'config.json')
    RECENT_FILES_FILE = os.path.join('configs', 'recent_files.json')

    def __init__(self, root):
        self.root = root
        self.root.title("CNotePad")
        self.root.geometry("600x400")
        
        # Set the window icon
        self.root.iconbitmap('Assets/bpad.ico')
        
        # Create a scrolled text widget with undo enabled
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, bg="black", fg="white", insertbackground="white", undo=True)
        self.text_area.grid(row=0, column=0, sticky='nsew')
        
        # Create a status bar
        self.status_bar = tk.Label(self.root, text="New File", anchor='w')
        self.status_bar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid row and column weights
        self.root.grid_rowconfigure(0, weight=1)  # Gives maximum weight to text_area
        self.root.grid_columnconfigure(0, weight=1)  # Allows text_area to expand fully
        
        # Load color settings
        self.load_settings()
        
        # Load recent files
        self.recent_files = self.load_recent_files()
        
        # Create a menu bar
        self.create_menu()
        
        # Bind shortcuts
        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-o>', self.open_file)
        self.root.bind('<Control-Shift-s>', self.save_as_file)
        self.root.bind('<Control-n>', self.new_file)
        self.root.bind('<Control-z>', self.undo)
        self.root.bind('<Control-f>', self.search_text)
        self.root.bind('<Control-e>', self.search_with_browser)  # Add this line in the __init__ method
        self.text_area.bind('<KeyRelease>', self.update_status)
        self.text_area.bind('<ButtonRelease-1>', self.update_status)  # Updates on mouse click release within the text area
        self.text_area.bind('<Motion>', self.update_status)  # Optional: Updates during mouse movement within the text area

        # Update recent files menu
        self.update_recent_files_menu()

    def undo(self, event=None):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass  # Ignore the error if there's nothing to undo

    def load_settings(self):
        try:
            with open(self.CONFIG_FILE, 'r') as config_file:
                settings = json.load(config_file)
                self.text_area.config(fg=settings.get('text_color', 'white'), bg=settings.get('bg_color', 'black'), insertbackground=settings.get('text_color', 'white'))
                font_settings = settings.get('font', ('Arial', 12))
                self.text_area.config(font=font_settings)
        except FileNotFoundError:
            pass

    def save_settings(self):
        settings = {
            'text_color': self.text_area.cget('fg'),
            'bg_color': self.text_area.cget('bg'),
            'font': self.text_area.cget('font')
        }
        with open(self.CONFIG_FILE, 'w') as config_file:
            json.dump(settings, config_file)

    def load_recent_files(self):
        try:
            with open(self.RECENT_FILES_FILE, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_recent_files(self):
        with open(self.RECENT_FILES_FILE, 'w') as file:
            json.dump(self.recent_files, file)

    def update_recent_files_menu(self):
        recent_menu = self.menu_bar.children.get('recent_files_menu')
        if recent_menu:
            recent_menu.delete(0, tk.END)
            for file in self.recent_files[:5]:  # Show only the last 5 files
                recent_menu.add_command(label=file, command=lambda f=file: self.open_recent_file(f))

    def open_recent_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.INSERT, content)
            self.status_bar.config(text=file_path)
            self.current_file = file_path
            # Move the opened file to the top of the recent files list
            self.recent_files.remove(file_path)
            self.recent_files.insert(0, file_path)
            self.save_recent_files()
            self.update_recent_files_menu()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")

    def create_menu(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)
        self.menu_bar = menu_bar
        
        # File menu
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Search", command=self.search_text, accelerator="Ctrl+F")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # Format menu
        format_menu = Menu(menu_bar, tearoff=0)
        format_menu.add_command(label="Text Color", command=self.change_text_color)
        format_menu.add_command(label="Background Color", command=self.change_bg_color)
        format_menu.add_command(label="Font", command=self.change_font)
        format_menu.add_separator()  # Add a separator before the new toggle option
        format_menu.add_command(label="Status Bar", command=self.toggle_status_bar)  # Toggle status bar option
        menu_bar.add_cascade(label="Format", menu=format_menu)
        
        # Recent files menu
        recent_files_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Recent Files", menu=recent_files_menu)
        recent_files_menu._name = 'recent_files_menu'

                # Misc menu
        misc_menu = Menu(menu_bar, tearoff=0)
        misc_menu.add_command(label="Search with Browser", command=self.search_with_browser, accelerator="Ctrl+E")
        # Add more commands to the Misc menu as needed
        menu_bar.add_cascade(label="Misc", menu=misc_menu)
        
        # Help menu
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

    def toggle_status_bar(self):
        if self.status_bar.winfo_viewable():
            self.status_bar.grid_forget()  # Hide the status bar
        else:
            self.status_bar.grid(row=1, column=0, sticky='ew')  # Show the status bar

        # Optionally save this setting to your settings file if you want it to persist between sessions
        self.save_settings()

    def new_file(self, event=None):
        self.text_area.delete(1.0, tk.END)
        self.status_bar.config(text="New File")
        self.current_file = None

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("All files", "*.*"), ("Text files", "*.txt"), ("Python files", "*.py"), ("JavaScript files", "*.js"), ("HTML files", "*.html")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.INSERT, content)
                self.status_bar.config(text=file_path)
                self.current_file = file_path
                if file_path not in self.recent_files:
                    self.recent_files.insert(0, file_path)
                    self.save_recent_files()
                    self.update_recent_files_menu()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self, event=None):
        if self.current_file:
            try:
                with open(self.current_file, 'w') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.status_bar.config(text=f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self, event=None):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("All files", "*.*"), ("Text files", "*.txt"), ("Python files", "*.py"), ("JavaScript files", "*.js"), ("HTML files", "*.html")], initialfile=self.current_file)
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.status_bar.config(text=f"Saved: {file_path}")
                self.current_file = file_path
                if file_path not in self.recent_files:
                    self.recent_files.insert(0, file_path)
                    self.save_recent_files()
                    self.update_recent_files_menu()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def search_text(self, event=None):
        search_query = simpledialog.askstring("Search", "Enter text to search:")
        if search_query:
            start_pos = '1.0'
            while True:
                start_pos = self.text_area.search(search_query, start_pos, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(search_query)}c"
                self.text_area.tag_add('highlight', start_pos, end_pos)
                self.text_area.tag_config('highlight', background='yellow')
                start_pos = end_pos

    def change_text_color(self):
        color = colorchooser.askcolor(title="Choose text color")[1]
        if color:
            self.text_area.config(fg=color)
            self.save_settings()

    def change_bg_color(self):
        color = colorchooser.askcolor(title="Choose background color")[1]
        if color:
            self.text_area.config(bg=color)
            self.save_settings()

    def change_font(self):
        font_family = simpledialog.askstring("Font", "Enter font family (e.g., Arial):")
        font_size = simpledialog.askinteger("Font", "Enter font size (e.g., 12):")
        if font_family and font_size:
            new_font = (font_family, font_size)
            self.text_area.config(font=new_font)
            self.save_settings()

    def show_about(self):
        messagebox.showinfo("About", "CNotePad\nVersion 1.0\nA Simple Customizable Text Editor")

    def update_status(self, event=None):
        line, column = self.text_area.index(tk.INSERT).split('.')
        self.status_bar.config(text=f"Line: {line} | Column: {column}")

    def enable_syntax_highlighting(self):
        # Basic example for Python syntax highlighting
        keywords = {'import': 'blue', 'def': 'orange', 'class': 'green'}
        for keyword, color in keywords.items():
            start_pos = '1.0'
            while True:
                start_pos = self.text_area.search(r'\m{}\M'.format(keyword), start_pos, stopindex=tk.END, regexp=True)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(keyword)}c"
                self.text_area.tag_add(keyword, start_pos, end_pos)
                self.text_area.tag_config(keyword, foreground=color)
                start_pos = end_pos

    def search_with_browser(self, event=None):
        selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        if selected_text:
            url = f"https://www.google.com/search?q={selected_text}"
            webbrowser.open(url)
        else:
            messagebox.showinfo("Search", "No text selected.")

if __name__ == "__main__":
    root = tk.Tk()
    notepad = CustomNotepad(root)
    root.mainloop()
