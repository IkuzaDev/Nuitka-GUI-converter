import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

THEME_COLOR = "#3B8ED0"
BUTTON_COLOR = "#1F6AA5"
BUTTON_HOVER_COLOR = "#144870"
FRAME_COLOR = "#2B2B2B"
TEXT_COLOR = "#DCE4EE"

large_font = ("Segoe UI", 13)
title_font = ("Segoe UI", 20, "bold")
button_font = ("Segoe UI", 12)

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
        "Nuitka GUI Converter v2.0\n"
        "Created by IkuzaDev\n\n"
        "Quick Guide:\n"
        "1. Select Python file\n"
        "2. Set output directory\n"
        "3. Choose build options\n"
        "4. Click Convert\n\n"
        "Note: Standalone mode recommended"
    )
    messagebox.showinfo("About", info_message)

app = ctk.CTk()
app.title("Nuitka GUI Converter - IkuzaDev")
app.geometry("700x750")

var_standalone = ctk.BooleanVar(value=True)
var_onefile = ctk.BooleanVar()
var_follow_imports = ctk.BooleanVar()
var_debug = ctk.BooleanVar()
var_lto = ctk.BooleanVar()
var_mingw64 = ctk.BooleanVar()
var_disable_console = ctk.BooleanVar()
var_remove_output = ctk.BooleanVar()
var_no_prefer_source = ctk.BooleanVar()

app.grid_columnconfigure(0, weight=1)

main_frame = ctk.CTkFrame(app, fg_color=FRAME_COLOR, corner_radius=15)
main_frame.pack(fill="both", expand=True, padx=15, pady=15)

header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
header_frame.pack(fill="x", padx=10, pady=(5, 10))

title_label = ctk.CTkLabel(
    header_frame, 
    text="Nuitka GUI Converter",
    font=title_font,
    text_color=THEME_COLOR
)
title_label.pack(side="left", pady=5)

credits_label = ctk.CTkLabel(
    header_frame,
    text="by IkuzaDev",
    font=button_font,
    text_color=TEXT_COLOR
)
credits_label.pack(side="left", pady=5, padx=10)

help_btn = ctk.CTkButton(
    header_frame,
    text="About",
    command=show_info,
    font=button_font,
    width=90,
    height=32,
    fg_color=BUTTON_COLOR,
    hover_color=BUTTON_HOVER_COLOR,
    corner_radius=8
)
help_btn.pack(side="right", pady=5, padx=5)

scroll_frame = ctk.CTkScrollableFrame(
    main_frame,
    fg_color="transparent",
    corner_radius=8
)
scroll_frame.pack(fill="both", expand=True, padx=10)

entry_file = ctk.CTkEntry(scroll_frame)
entry_output_dir = ctk.CTkEntry(scroll_frame)
entry_data_file = ctk.CTkEntry(scroll_frame)
entry_icon_file = ctk.CTkEntry(scroll_frame)
entry_plugin_name = ctk.CTkEntry(scroll_frame)

entry_include_package = ctk.CTkTextbox(scroll_frame, height=60)
entry_include_module = ctk.CTkTextbox(scroll_frame, height=60)

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
            progress_bar.configure(fg_color="blue")
            status_label.configure(text="Converting...")
            threading.Thread(target=simulate_progress).start()
            subprocess.run(command, check=True)
            progress_bar.set(1)
            status_label.configure(text="Conversion completed successfully!")
            messagebox.showinfo("Success", "Conversion completed successfully!")
        except subprocess.CalledProcessError as e:
            progress_bar.set(0)
            progress_bar.configure(fg_color="red")
            status_label.configure(text="Conversion failed.")
            messagebox.showerror("Error", f"Conversion failed: {e}")

    def simulate_progress():
        for i in range(101):
            time.sleep(0.1)
            progress_bar.set(i / 100)
            percentage_label.configure(text=f"{i}%")
            app.update_idletasks()

    threading.Thread(target=run_conversion).start()

file_section = ctk.CTkFrame(
    scroll_frame,
    fg_color=FRAME_COLOR,
    corner_radius=10
)
file_section.pack(fill="x", pady=5)

content_frame = ctk.CTkFrame(file_section, fg_color="transparent")
content_frame.pack(fill="x", padx=10, pady=5)

ctk.CTkLabel(file_section, text="File Selection", font=("Arial", 16, "bold")).pack(pady=5)

ctk.CTkLabel(content_frame, text="Add Python Script:", font=large_font).grid(row=0, column=0, sticky="e", pady=5)
entry_file = ctk.CTkEntry(content_frame, width=300, height=30, font=large_font)
entry_file.grid(row=0, column=1, pady=5)
create_browse_button(content_frame, browse_file).grid(row=0, column=2, pady=5, padx=5)

ctk.CTkLabel(content_frame, text="Add Output Directory:", font=large_font).grid(row=1, column=0, sticky="e", pady=5)
entry_output_dir = ctk.CTkEntry(content_frame, width=300, height=30, font=large_font)
entry_output_dir.grid(row=1, column=1, pady=5)
create_browse_button(content_frame, browse_output_dir).grid(row=1, column=2, pady=5, padx=5)

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

ctk.CTkLabel(content_frame, text="Include Packages (one per line):", font=large_font).grid(row=6, column=0, sticky="e", pady=5)
entry_include_package = ctk.CTkTextbox(content_frame, width=300, height=60, font=large_font)
entry_include_package.grid(row=6, column=1, pady=5)
ctk.CTkLabel(content_frame, text="e.g. customtkinter\nuiautomator2", font=("Arial", 10)).grid(row=6, column=2, sticky="w", pady=5, padx=5)

ctk.CTkLabel(content_frame, text="Include Modules (one per line):", font=large_font).grid(row=7, column=0, sticky="e", pady=5)
entry_include_module = ctk.CTkTextbox(content_frame, width=300, height=60, font=large_font)
entry_include_module.grid(row=7, column=1, pady=5)
ctk.CTkLabel(content_frame, text="e.g. concurrent.futures\nurllib.parse", font=("Arial", 10)).grid(row=7, column=2, sticky="w", pady=5, padx=5)

options_section = ctk.CTkFrame(scroll_frame, fg_color=FRAME_COLOR)
options_section.pack(fill="x", pady=10)
ctk.CTkLabel(options_section, text="Build Options", font=("Arial", 16, "bold")).pack(pady=5)

options_grid = ctk.CTkFrame(options_section, fg_color="transparent")
options_grid.pack(fill="x", padx=10)

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
