import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import time

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Define modern colors
THEME_COLOR = "#3B8ED0"  # Modern blue
BUTTON_COLOR = "#1F6AA5"  # Darker blue
BUTTON_HOVER_COLOR = "#144870"  # Even darker blue for hover
FRAME_COLOR = "#2B2B2B"  # Dark background
TEXT_COLOR = "#DCE4EE"  # Light text color

# Define fonts
large_font = ("Segoe UI", 13)
title_font = ("Segoe UI", 20, "bold")
button_font = ("Segoe UI", 12)

# Define helper functions first
def create_browse_button(parent, command):
    return ctk.CTkButton(
        parent,
        text="Browse",
        command=command,
        font=button_font,
        width=80,
        height=28,
        fg_color=BUTTON_COLOR,
        hover_color=BUTTON_HOVER_COLOR,
        corner_radius=8
    )

def show_info():
    info_message = (
        "Nuitka Converter v2.0\n\n"
        "Quick Guide:\n"
        "1. Select your Python script file\n"
        "2. Choose output directory\n"
        "3. Select desired build options\n"
        "4. Click Convert to start building\n\n"
        "Note: Standalone mode is recommended for most cases"
    )
    messagebox.showinfo("Information", info_message)

# Create the main window
app = ctk.CTk()
app.title("Nuitka Converter")
app.geometry("750x800")  # More compact window size

# Initialize variables after creating root window
var_standalone = ctk.BooleanVar(value=True)
var_onefile = ctk.BooleanVar()
var_follow_imports = ctk.BooleanVar()
var_debug = ctk.BooleanVar()
var_lto = ctk.BooleanVar()
var_mingw64 = ctk.BooleanVar()
var_disable_console = ctk.BooleanVar()
var_remove_output = ctk.BooleanVar()
var_no_prefer_source = ctk.BooleanVar()

# Configure grid weight
app.grid_columnconfigure(0, weight=1)

# Create main frame with modern styling
main_frame = ctk.CTkFrame(
    app,
    fg_color=FRAME_COLOR,
    corner_radius=15
)
main_frame.pack(fill="both", expand=True, padx=15, pady=15)

# Create header with modern design
header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
header_frame.pack(fill="x", padx=10, pady=(5, 10))

ctk.CTkLabel(
    header_frame, 
    text="Nuitka Converter",
    font=title_font,
    text_color=THEME_COLOR
).pack(side="left", pady=5)

help_btn = ctk.CTkButton(
    header_frame,
    text="Guide",
    command=show_info,
    font=button_font,
    width=90,
    height=32,
    fg_color=BUTTON_COLOR,
    hover_color=BUTTON_HOVER_COLOR,
    corner_radius=8
)
help_btn.pack(side="right", pady=5, padx=5)

# Update scroll frame styling
scroll_frame = ctk.CTkScrollableFrame(
    main_frame,
    fg_color="transparent",
    corner_radius=8
)
scroll_frame.pack(fill="both", expand=True, padx=10)

# Create entry variables
entry_file = ctk.CTkEntry(scroll_frame)
entry_output_dir = ctk.CTkEntry(scroll_frame)
entry_data_file = ctk.CTkEntry(scroll_frame)
entry_icon_file = ctk.CTkEntry(scroll_frame)
entry_plugin_name = ctk.CTkEntry(scroll_frame)

# Replace entry fields with text areas for packages and modules
entry_include_package = ctk.CTkTextbox(scroll_frame, height=60)
entry_include_module = ctk.CTkTextbox(scroll_frame, height=60)

# Create progress and status elements
progress_bar = None
percentage_label = None
status_label = None

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    entry_file.delete(0, ctk.END)
    entry_file.insert(0, filename)

def browse_output_dir():
    directory = filedialog.askdirectory()
    entry_output_dir.delete(0, ctk.END)
    entry_output_dir.insert(0, directory)

def browse_data_file():
    filename = filedialog.askopenfilename()
    entry_data_file.delete(0, ctk.END)
    entry_data_file.insert(0, filename)

def browse_icon_file():
    filename = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
    entry_icon_file.delete(0, ctk.END)
    entry_icon_file.insert(0, filename)

def validate_inputs():
    if not entry_file.get():
        messagebox.showerror("Error", "Please select a Python script file")
        return False
    if not entry_output_dir.get():
        messagebox.showerror("Error", "Please select an output directory")
        return False
    return True

def convert():
    if not validate_inputs():
        return

    script_file = entry_file.get()
    output_dir = entry_output_dir.get()
    data_file = entry_data_file.get()
    icon_file = entry_icon_file.get()
    plugin_name = entry_plugin_name.get()
    options = [
        "--assume-yes-for-downloads",
        "--enable-plugin=tk-inter"
    ]

    # Updated Nuitka options for latest version
    if var_standalone.get():
        options.append("--standalone")
    if var_onefile.get():
        options.append("--onefile")
    if var_debug.get():
        options.append("--debug")
    if var_lto.get():
        options.append("--lto=yes")
    if var_mingw64.get():
        options.append("--mingw64")
    if var_disable_console.get():
        options.append("--windows-console-mode=disable")
    if var_remove_output.get():
        options.append("--remove-output")
    if var_no_prefer_source.get():
        options.append("--prefer-source-code")
    
    # Package and module inclusions - Updated for multiple lines
    include_packages = entry_include_package.get("1.0", ctk.END).strip()
    if include_packages:
        for pkg in include_packages.splitlines():
            pkg = pkg.strip()
            if pkg:
                options.append(f"--include-package={pkg}")
    
    include_modules = entry_include_module.get("1.0", ctk.END).strip()
    if include_modules:
        for mod in include_modules.splitlines():
            mod = mod.strip()
            if mod:
                options.append(f"--include-module={mod}")

    # Output Options
    if output_dir:
        options.append(f"--output-dir={output_dir}")
    if data_file:
        options.append(f"--include-data-file={data_file}={data_file}")
    if icon_file:
        options.append(f"--windows-icon-from-ico={icon_file}")
    if plugin_name:
        options.append(f"--enable-plugin={plugin_name}")

    command = ["python", "-m", "nuitka"] + options + [script_file]

    def run_conversion():
        try:
            progress_bar.set(0)
            progress_bar.configure(fg_color="blue")  # Reset color to blue
            status_label.configure(text="Converting...")
            threading.Thread(target=simulate_progress).start()
            subprocess.run(command, check=True)
            progress_bar.set(1)
            status_label.configure(text="Conversion completed successfully!")
            messagebox.showinfo("Success", "Conversion completed successfully!")
        except subprocess.CalledProcessError as e:
            progress_bar.set(0)
            progress_bar.configure(fg_color="red")  # Change color to red on failure
            status_label.configure(text="Conversion failed.")
            messagebox.showerror("Error", f"Conversion failed: {e}")

    def simulate_progress():
        for i in range(101):
            time.sleep(0.1)  # Simulate time delay for progress
            progress_bar.set(i / 100)
            percentage_label.configure(text=f"{i}%")
            app.update_idletasks()

    threading.Thread(target=run_conversion).start()

# File Selection Section
file_section = ctk.CTkFrame(
    scroll_frame,
    fg_color=FRAME_COLOR,
    corner_radius=10
)
file_section.pack(fill="x", pady=5)

# Create a sub-frame for the actual content using grid
content_frame = ctk.CTkFrame(file_section, fg_color="transparent")
content_frame.pack(fill="x", padx=10, pady=5)

# Title label using pack
ctk.CTkLabel(file_section, text="File Selection", font=("Arial", 16, "bold")).pack(pady=5)

# Add file selection widgets with consistent spacing
ctk.CTkLabel(content_frame, text="Add Python Script:", font=large_font).grid(row=0, column=0, sticky="e", pady=5)
entry_file = ctk.CTkEntry(content_frame, width=300, height=30, font=large_font)
entry_file.grid(row=0, column=1, pady=5)
create_browse_button(content_frame, browse_file).grid(row=0, column=2, pady=5, padx=5)

ctk.CTkLabel(content_frame, text="Add Output Directory:", font=large_font).grid(row=1, column=0, sticky="e", pady=5)
entry_output_dir = ctk.CTkEntry(content_frame, width=300, height=30, font=large_font)
entry_output_dir.grid(row=1, column=1, pady=5)
create_browse_button(content_frame, browse_output_dir).grid(row=1, column=2, pady=5, padx=5)

# Fix the Browse button parent frame and layout
ctk.CTkLabel(content_frame, text="Additional Files(optional):", font=large_font).grid(row=2, column=0, sticky="e", pady=5)
entry_data_file = ctk.CTkEntry(content_frame, width=300, height=30, font=large_font)
entry_data_file.grid(row=2, column=1, pady=5)
create_browse_button(content_frame, browse_data_file).grid(row=2, column=2, pady=5, padx=5)

ctk.CTkLabel(content_frame, text="Icon File(optional):", font=large_font).grid(row=3, column=0, sticky="e", pady=5)
entry_icon_file = ctk.CTkEntry(content_frame, width=300, height=30, font=large_font)
entry_icon_file.grid(row=3, column=1, pady=5)
create_browse_button(content_frame, browse_icon_file).grid(row=3, column=2, pady=5, padx=5)

ctk.CTkLabel(content_frame, text="Plugin Name(optional):", font=large_font).grid(row=4, column=0, sticky="e", pady=5)
entry_plugin_name = ctk.CTkEntry(content_frame, width=300, height=30, font=large_font)
entry_plugin_name.grid(row=4, column=1, pady=5)

ctk.CTkLabel(content_frame, text="Python Version(optional):", font=large_font).grid(row=5, column=0, sticky="e", pady=5)
entry_python_version = ctk.CTkEntry(content_frame, width=300, height=30, font=large_font)
entry_python_version.grid(row=5, column=1, pady=5)

# Add package and module input sections with explanatory labels
ctk.CTkLabel(content_frame, text="Include Packages (one per line):", font=large_font).grid(row=6, column=0, sticky="e", pady=5)
entry_include_package = ctk.CTkTextbox(content_frame, width=300, height=60, font=large_font)
entry_include_package.grid(row=6, column=1, pady=5)
ctk.CTkLabel(content_frame, text="e.g. customtkinter\nuiautomator2", font=("Arial", 10)).grid(row=6, column=2, sticky="w", pady=5, padx=5)

ctk.CTkLabel(content_frame, text="Include Modules (one per line):", font=large_font).grid(row=7, column=0, sticky="e", pady=5)
entry_include_module = ctk.CTkTextbox(content_frame, width=300, height=60, font=large_font)
entry_include_module.grid(row=7, column=1, pady=5)
ctk.CTkLabel(content_frame, text="e.g. concurrent.futures\nurllib.parse", font=("Arial", 10)).grid(row=7, column=2, sticky="w", pady=5, padx=5)

# Options Section
options_section = ctk.CTkFrame(scroll_frame, fg_color=FRAME_COLOR)
options_section.pack(fill="x", pady=10)
ctk.CTkLabel(options_section, text="Build Options", font=("Arial", 16, "bold")).pack(pady=5)

# Add options in a grid layout
options_grid = ctk.CTkFrame(options_section, fg_color="transparent")
options_grid.pack(fill="x", padx=10)

# Create a more organized checkbox layout
checkboxes = [
    ("Standalone", var_standalone, 0, 0),
    ("Onefile", var_onefile, 0, 1),
    ("Follow Imports", var_follow_imports, 1, 0),
    ("Debug", var_debug, 1, 1),
    ("Optimization (LTO)", var_lto, 2, 0),
    ("Use MinGW64", var_mingw64, 2, 1),
    ("Disable Console", var_disable_console, 3, 0),
    ("Remove Output", var_remove_output, 3, 1),
    ("No Prefer Source", var_no_prefer_source, 4, 0)
]

for text, var, row, col in checkboxes:
    ctk.CTkCheckBox(options_grid, text=text, variable=var, font=large_font).grid(
        row=row, column=col, padx=10, pady=5, sticky="w"
    )

# Update progress section
progress_frame = ctk.CTkFrame(
    app,
    fg_color=FRAME_COLOR,
    corner_radius=10
)
progress_frame.pack(fill="x", padx=15, pady=10)

convert_btn = ctk.CTkButton(
    progress_frame, 
    text="Convert",
    command=convert,
    font=("Segoe UI", 14, "bold"),
    height=38,
    fg_color=THEME_COLOR,
    hover_color=BUTTON_COLOR,
    corner_radius=8
)
convert_btn.pack(pady=8)

progress_bar = ctk.CTkProgressBar(
    progress_frame, 
    width=500,
    height=15,
    corner_radius=5,
    border_width=0,
    progress_color=THEME_COLOR,
    bg_color="#404040"
)
progress_bar.pack(pady=5)
progress_bar.set(0)

percentage_label = ctk.CTkLabel(progress_frame, text="0%", font=large_font)
percentage_label.pack()

status_label = ctk.CTkLabel(progress_frame, text="", font=large_font)
status_label.pack()

app.mainloop()