# **iChat Conversation Recovery Tool**

A simple cross-platform Python application with a graphical user interface to parse and recover old Apple iChat (.ichat) conversation files, extracting all messages and embedded images into viewable HTML files.

## **Features**

* **Simple GUI:** An easy-to-use interface for selecting your iChat files and an output destination.  
* **Parses .ichat Files:** Handles the binary plist format used by iChat to store message data.  
* **Extracts Embedded Images:** Finds and extracts embedded JPG, PNG, and GIF images and displays them directly in the chat log.  
* **Consolidates Chats:** Groups all .ichat files from a single user into one file and sorts the contents chronologically.  
* **Self-Contained Output:** Creates clean, self-contained HTML files that require no external dependencies to view in any modern web browser.  
* **Cross-Platform:** Runs on Windows, macOS, and Linux.

## **Known Issues**

If you encounter an problem not on this list, please file an [Issue](https://github.com/tuxedocurly/ichat_recovery_tool/issues/new).

* **Windows Defender Warning:** When running the pre-compiled binary, the windows defender screen may appear as the binary is not signed. To bypass this: In the Windows Defender popup, click "More Info" then "Run Anyway"
* **MacOS Refuses to Open Pre-Compiled App:** Apple Gatekeeper may block the pre-compiled binary from launching, as the binary is not signed. Open a terminal window, and enter the following command: ```xattr -d com.apple.quarantine /path/to/your/ichat_recovery_ui_MACOS.app```
* **Re-Running the Tool With the Same Input & Output Produces Duplicate .html message entries:** If you run the tool on the same input folder/data AND use the same output folder, your .html files will contain duplicate message entries. Just something to be aware of. I'll improve this eventually.
* **Folder "Browse" Buttons Not Visible On App Open On MacOS:** If you don't see the "Browse" button to select input and output folders on MacOS after running the app, resize the window until the buttons appear.

## **Requirements**

* **Python 3.6+ (3.8 recommended)**: This version is required by nska-deserialize.
* **[nska-deserialize](https://github.com/ydkhatri/nska_deserialize)**: A Python library for deserializing NSKeyedArchiver-encoded plists.

## **Installation & Usage (Run via Pre-Built Executable)**

If you just want to use the tool directly, this option is for you.

1. Download the executable for your operating system, located in the [release](https://github.com/tuxedocurly/ichat_recovery_tool/tree/main/release) folder.
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

This script utilizes [nska-deserialize](https://github.com/ydkhatri/nska_deserialize), which is released under the MIT license. This project is also released under the MIT license. Weeeeeeeeeeee!
