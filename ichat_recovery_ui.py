"""
ichat_conversation_recovery.py

A script with a graphical user interface (GUI) to parse Apple iChat (.ichat)
files, extract messages and images, and render them as self-contained HTML files.

This script requires the 'nska-deserialize' library to parse the binary
plist format used by iChat files.

Usage:
    python ichat_parser.py
"""

import os
import re
import glob
import html
import base64
import traceback
import sys
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

try:
    from nska_deserialize import deserialize_plist
except ImportError:
    # Show an error popup if the library is missing
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror(
        "Dependency Error",
        "Error: The 'nska-deserialize' library is not installed.\n"
        "Please run: pip install nska-deserialize"
    )
    exit(1)

# --- Configuration ---
# This is now a default, can be changed in the UI
DEFAULT_OUTPUT_DIR = "html_chats"

# Regex to parse "username on YYYY-MM-DD at HH.MM.ichat"
# Captures the username as group 1.
FILENAME_REGEX = re.compile(r'^(.*?) on \d{4}-\d{2}-\d{2} at \d{2}\.\d{2}\.ichat$')

# Define "magic bytes" (file signatures) to identify embedded image types.
IMAGE_SIGNATURES = {
    '.jpg': b'\xff\xd8\xff',
    '.png': b'\x89PNG\r\n\x1a\n',
    '.gif': b'GIF8',  # Covers both GIF87a and GIF89a
}


def find_and_extract_image(data_blob):
    """
    Searches a data blob for known image signatures.

    Args:
        data_blob (bytes): The raw byte blob, which may contain an image.

    Returns:
        bytes: The sliced byte string from the start of the signature to the end.
        None: If no known image signature is found.
    """
    for ext, signature in IMAGE_SIGNATURES.items():
        start_index = data_blob.find(signature)
        if start_index != -1:
            # Return the rest of the blob from the signature onward.
            return data_blob[start_index:]
    return None


def get_mime_type_from_bytes(data_bytes):
    """
    Guesses the MIME type of an image based on its magic bytes.

    Args:
        data_bytes (bytes): The bytes of the image file.

    Returns:
        str: The corresponding MIME type (e.g., 'image/jpeg') or
             'application/octet-stream' as a fallback.
    """
    if data_bytes.startswith(IMAGE_SIGNATURES['.jpg']):
        return 'image/jpeg'
    if data_bytes.startswith(IMAGE_SIGNATURES['.png']):
        return 'image/png'
    if data_bytes.startswith(IMAGE_SIGNATURES['.gif']):
        return 'image/gif'
    return 'application/octet-stream'


def sanitize_filename(filename):
    """
    Removes illegal characters from a string to make it a valid filename.

    Args:
        filename (str): The potentially unsafe filename.

    Returns:
        str: A sanitized, safe filename.
    """
    return re.sub(r'[\\/*?:"<>|]', "_", filename)


def extract_messages_from_file(file_path, logger_func):
    """
    Deserializes a single .ichat file and extracts its list of messages.

    Args:
        file_path (str): The path to the .ichat file.
        logger_func (callable): Function to call for logging messages.

    Returns:
        list: A list of message objects (dictionaries), or an empty list
              if parsing fails.
    """
    logger_func(f"  -> Reading {os.path.basename(file_path)}")
    try:
        with open(file_path, "rb") as fp:
            # Use nska-deserialize to parse the binary plist.
            objects = deserialize_plist(fp)
    except Exception as e:
        logger_func(f"    -> Error deserializing file: {e}")
        return []

    # The message list is nested deep within the deserialized object.
    try:
        messages = objects[1][2]
        if not isinstance(messages, list):
            logger_func(f"    -> Error: Could not find messages list.")
            return []
        return messages
    except (IndexError, TypeError):
        logger_func(f"    -> Error: File structure not as expected.")
        return []


def write_html_file(username, sorted_messages, output_dir, logger_func):
    """
    Renders a list of messages into a single, self-contained HTML file.

    Args:
        username (str): The name of the user for this chat log.
        sorted_messages (list): A list of message objects, pre-sorted by time.
        output_dir (str): The directory to save the final HTML file in.
        logger_func (callable): Function to call for logging messages.
    """
    save_name = f"{sanitize_filename(username)}.html"
    save_path = os.path.join(output_dir, save_name)

    logger_func(f"  -> Rendering HTML for {username}...")

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            # Write HTML Header and CSS
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Chat with {html.escape(username)}</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 20px; background-color: #f9f9f9; }}
                    .container {{ max-width: 800px; margin: auto; background-color: #fff; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }}
                    .message {{ padding: 10px 20px; border-bottom: 1px solid #eee; }}
                    .message:last-child {{ border-bottom: none; }}
                    .header {{ font-size: 0.8em; color: #555; }}
                    .sender {{ font-weight: bold; }}
                    .content {{ margin-top: 5px; word-wrap: break-word; }}
                    p {{ white-space: pre-wrap; margin: 0.5em 0 0 0; }}
                    p:first-child {{ margin-top: 0; }}
                    p:empty {{ display: none; }}
                    .content img {{ max-width: 400px; max-height: 400px; border-radius: 6px; margin-top: 5px; display: block; }}
                </style>
            </head>
            <body>
                <div class="container">
                <h1>Chat with {html.escape(username)}</h1>
            """)

            # Iterate through all sorted messages and write them to HTML
            for msg in sorted_messages:
                # Extract sender name
                sender_obj = msg.get('Sender')
                sender_name = "Unknown"
                if isinstance(sender_obj, dict):
                    sender_name = sender_obj.get('ID', 'Unknown Sender')

                # Extract and format timestamp
                timestamp_obj = msg.get('Time')
                time_str = "No Timestamp"
                if isinstance(timestamp_obj, datetime):
                    time_str = timestamp_obj.strftime('%Y-%m-%d %I:%M:%S %p')

                f.write(f'<div class="message">')
                f.write(
                    f'<div class="header"><span class="sender">{html.escape(sender_name)}</span> - {time_str}</div>')
                f.write('<div class="content">')

                # Extract message content (text and attachments)
                content_obj = msg.get('MessageText')
                if content_obj:
                    # Get the text string
                    # \ufffc is a placeholder for an attachment; remove it.
                    text = content_obj.get('NSString', '').replace('\ufffc', '')
                    if text.strip():
                        f.write(f'<p>{html.escape(text)}</p>')

                    # Get attributes, which may contain attachments
                    attributes = content_obj.get('NSAttributes', [])

                    # Ensure attributes are always iterable (list)
                    attributes_list = []
                    if isinstance(attributes, dict):
                        attributes_list = [attributes]
                    elif isinstance(attributes, list):
                        attributes_list = attributes

                    # Loop through attributes to find and embed images
                    for attr in attributes_list:
                        # Image data is nested deep in the attachment structure
                        data_blob = attr.get('NSAttachment', {}).get('NSFileWrapper', {}).get('NSFileWrapperData',
                                                                                              {}).get('NS.data')

                        if data_blob and isinstance(data_blob, bytes):
                            img_bytes = find_and_extract_image(data_blob)
                            if img_bytes:
                                # Embed the image as a base64 data URI
                                mime_type = get_mime_type_from_bytes(img_bytes)
                                b64_string = base64.b64encode(img_bytes).decode('ascii')
                                f.write(f'<img src="data:{mime_type};base64,{b64_string}">')

                f.write('</div></div>')

            # Write HTML Footer
            f.write("""
                </div>
            </body>
            </html>
            """)

        logger_func(f"  -> Successfully saved: {save_path}")

    except Exception as e:
        logger_func(f"  -> FAILED to write HTML {save_path}: {e}")
        logger_func(traceback.format_exc())


class ChatConverterApp:
    """
    Main application class for the iChat Converter GUI.
    """
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("iChat Conversation Recovery")
        self.root.geometry("600x550") # Increased height for progress bar
        self.root.minsize(500, 450)

        # --- Style Configuration ---
        # Configure a custom style for the green progress bar
        style = ttk.Style(self.root)
        style.layout('green.Horizontal.TProgressbar',
             [('green.Horizontal.TProgressbar.trough',
               {'children': [('green.Horizontal.TProgressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'})])
        style.configure('green.Horizontal.TProgressbar', background='green')

        # Variables to store selected paths
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar(value=DEFAULT_OUTPUT_DIR)

        # --- Create Widgets ---
        self.create_widgets()

    def create_widgets(self):
        """Creates and lays out all the GUI widgets."""

        # Use a main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # --- Source Folder Selection ---
        source_frame = ttk.LabelFrame(main_frame, text=" 1. Select iChat Files Folder ", padding="10")
        source_frame.pack(fill="x", pady=5)

        source_entry = ttk.Entry(source_frame, textvariable=self.source_dir, state="readonly", width=70)
        source_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        source_button = ttk.Button(source_frame, text="Browse...", command=self.select_source_dir)
        source_button.pack(side="left")

        # --- Destination Folder Selection ---
        dest_frame = ttk.LabelFrame(main_frame, text=" 2. Select Output HTML Folder ", padding="10")
        dest_frame.pack(fill="x", pady=5)

        dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_dir, state="readonly", width=70)
        dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        dest_button = ttk.Button(dest_frame, text="Browse...", command=self.select_dest_dir)
        dest_button.pack(side="left")

        # --- Action Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Conversion", command=self.start_processing, state="disabled")
        self.start_button.pack(side="left", padx=5)

        self.open_output_button = ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder, state="disabled")
        self.open_output_button.pack(side="left", padx=5)

        # --- Progress Bar ---
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill="x", pady=5, padx=5)

        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", style='green.Horizontal.TProgressbar')
        self.progress_bar.pack(fill="x", expand=True)


        # --- Log/Status Window ---
        log_frame = ttk.LabelFrame(main_frame, text=" Log ", padding="10")
        log_frame.pack(fill="both", expand=True)

        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.pack(side="right", fill="y")

        self.log_text = tk.Text(log_frame, wrap="word", state="disabled", yscrollcommand=log_scrollbar.set)
        self.log_text.pack(fill="both", expand=True)

        log_scrollbar.config(command=self.log_text.yview)

    def select_source_dir(self):
        """Opens a dialog to select the source .ichat folder."""
        directory = filedialog.askdirectory(title="Select the folder containing your .ichat files")
        if directory:
            self.source_dir.set(directory)
            self.start_button.config(state="normal")  # Enable start button
            self.log_message(f"Source folder set: {directory}")

    def select_dest_dir(self):
        """Opens a dialog to select the output HTML folder."""
        directory = filedialog.askdirectory(title="Select where to save HTML files")
        if directory:
            self.dest_dir.set(directory)
            self.log_message(f"Destination folder set: {directory}")

    def log_message(self, message):
        """Appends a message to the log window."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Auto-scroll to the bottom
        self.log_text.config(state="disabled")
        self.root.update_idletasks()  # Force GUI update

    def open_output_folder(self):
        """Opens the selected output directory in the file explorer."""
        output_dir = self.dest_dir.get()
        if not os.path.isdir(output_dir):
            self.log_message(f"Error: Output directory '{output_dir}' does not exist.")
            return

        try:
            # Cross-platform open folder
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", output_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", output_dir])
            self.log_message(f"Opened output folder: {output_dir}")
        except Exception as e:
            self.log_message(f"Error opening folder: {e}")

    def start_processing(self):
        """
        The main logic loop, triggered by the 'Start' button.
        """
        self.start_button.config(state="disabled")  # Prevent re-clicks
        self.open_output_button.config(state="disabled") # Disable during processing
        self.log_message("\n--- Starting Conversion Process ---")

        # Reset progress bar
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0%")
        self.root.update_idletasks()

        source_directory = self.source_dir.get()
        output_dir = self.dest_dir.get()

        if not source_directory:
            self.log_message("Error: No source directory selected. Aborting.")
            self.start_button.config(state="normal")
            return

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            self.log_message(f"HTML files will be saved to: {os.path.abspath(output_dir)}")

            # --- Find and group all .ichat files by user ---
            search_path = os.path.join(source_directory, '*.ichat')
            ichat_files = glob.glob(search_path)

            if not ichat_files:
                self.log_message(f"No .ichat files found in '{source_directory}'.")
                self.start_button.config(state="normal")
                # Reset progress bar on abort
                self.progress_bar['value'] = 0
                self.progress_label.config(text="0%")
                return

            self.log_message(f"Found {len(ichat_files)} total .ichat files.")

            # Group file paths by the username found in the filename
            user_files = {}
            for file_path in ichat_files:
                filename = os.path.basename(file_path)
                match = FILENAME_REGEX.match(filename)

                if match:
                    username = match.group(1)
                    if username not in user_files:
                        user_files[username] = []
                    user_files[username].append(file_path)
                else:
                    self.log_message(f"Warning: Skipping file with unexpected name format: {filename}")

            # --- Process each user ---
            self.log_message(f"\nFound {len(user_files)} unique users. Starting processing...")

            total_users = len(user_files)
            if total_users == 0:
                 self.log_message("No users found to process.")
                 self.start_button.config(state="normal")
                 return

            self.progress_bar['maximum'] = total_users
            processed_count = 0

            for username, files_list in user_files.items():
                self.log_message(f"\n--- Processing user: {username} ({len(files_list)} files) ---")

                all_messages_for_user = []
                # Consolidate all messages from all of that user's files
                for file_path in files_list:
                    all_messages_for_user.extend(extract_messages_from_file(file_path, self.log_message))

                if not all_messages_for_user:
                    self.log_message(f"  -> No messages found for {username}. Skipping.")
                    processed_count += 1 # Still count as processed for progress bar
                    continue

                # Sort the consolidated list by timestamp
                try:
                    all_messages_for_user.sort(key=lambda m: m.get('Time') or datetime.min)
                except Exception as e:
                    self.log_message(f"  -> Warning: Could not sort messages for {username}. Error: {e}")

                # Render the final HTML file for this user
                write_html_file(username, all_messages_for_user, output_dir, self.log_message)

                # Update progress bar after each user is processed
                processed_count += 1
                self.progress_bar['value'] = processed_count
                percent = (processed_count / total_users) * 100
                self.progress_label.config(text=f"{percent:.0f}%")
                self.root.update_idletasks() # Force GUI update

            self.log_message(f"\n--- All processing complete ---")
            # Ensure it shows 100% on success
            self.progress_label.config(text="100%")
            self.progress_bar['value'] = total_users

        except Exception as e:
            self.log_message(f"\n--- AN ERROR OCCURRED ---")
            self.log_message(str(e))
            self.log_message(traceback.format_exc())

        finally:
            self.start_button.config(state="normal")  # Re-enable button
            # Enable the open folder button if the output dir exists
            if os.path.isdir(self.dest_dir.get()):
                self.open_output_button.config(state="normal")


if __name__ == "__main__":
    # Set up and run the Tkinter application
    root = tk.Tk()
    app = ChatConverterApp(root)
    root.mainloop()

