# **iChat Conversation Recovery Tool**

A simple cross-platform Python application with a graphical user interface to parse and recover old Apple iChat (.ichat) conversation files, extracting all messages and embedded images into viewable HTML files.

## **Features**

* **Simple GUI:** An easy-to-use interface for selecting your iChat files and an output destination.  
* **Parses .ichat Files:** Handles the binary plist format used by iChat to store message data.  
* **Extracts Embedded Images:** Finds and extracts embedded JPG, PNG, and GIF images and displays them directly in the chat log.  
* **Consolidates Chats:** Groups all .ichat files from a single user into one file and sorts the contents chronologically.  
* **Self-Contained Output:** Creates clean, self-contained HTML files that require no external dependencies to view in any modern web browser.  
* **Cross-Platform:** Runs on Windows, macOS, and Linux.

## **Requirements**

* **Python 3.6+ (3.8 recommended)**: This version is required by nska-deserialize.
* **nska-deserialize**: A Python library for deserializing NSKeyedArchiver-encoded plists.

## **Installation & Usage (Run via Pre-Built Executable)**

If you just want to use the tool directly, this option is for you.

1. Download the executable for your operating system, locaed in the [release](https://github.com/tuxedocurly/ichat_recovery_tool/tree/main/release) folder.
2. Run it!

## **Installation & Usage (Running from Source)**

For the tinkerers, the curious, and the skeptical. Clone this repo or download the .py script directly, then:

1. Install the required dependency:  
   Open your terminal or command prompt and run:  
   ```
   pip install nska-deserialize
   ```
2. Run the application:  
   Navigate to the project directory and run:  
   ```
   python ichat\_parser.py
   ```
3. **Using the App:**  
   * **Step 1:** Click "Browse..." next to "Select iChat Files Folder" and choose the folder that contains all your .ichat files.  
   * **Step 2:** Click "Browse..." next to "Select Output HTML Folder" and choose a folder where you want to save the converted HTML files.  
   * **Step 3:** Click "Start Conversion".  
   * The progress bar will show the status, and the log window will display details.  
   * Once complete, you can click "Open Output Folder" to view your files.

## **Bundling (For Developers)**

If you wish to bundle this application into a standalone executable (.exe, .app, etc.) so that it can be run without installing Python, you can use PyInstaller.

1. **Install PyInstaller:**  
   ```
   pip install pyinstaller
   ```
2. Build the executable:  
   From the project directory, run the following command. The \--windowed flag is essential for GUI apps as it prevents a console window from opening in the background.  
   ```
   pyinstaller \--onefile \--windowed ichat\_parser.py
   ```
3. Your executable will be located in the dist folder.

**Note on Cross-Platform Building:** PyInstaller does *not* cross-compile. You must run the build command on the target operating system (e.g., run it on Windows to create a .exe, run it on macOS to create a .app).

## **Acknowledgements**

This script utilizes nska-deserialize, which is released under the MIT license. This project, itself, is also released under the MIT license. Weeeeeeeeeeee!
