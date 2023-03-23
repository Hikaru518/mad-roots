from tkinter import Tk, Frame, Entry, Label,Button, END
from typing import List
from tkinter.filedialog import askopenfilename, askdirectory
from src.CardGen import convert_to_images

APP_WIDTH = 600
APP_HEIGHT = 130
TEXT_WIDTH = 80


def center_window(tk_app: Tk):
    # get the screen dimension
    screen_width = tk_app.winfo_screenwidth()
    screen_height = tk_app.winfo_screenheight()

    # find the center point
    center_x = int(screen_width/2 - APP_WIDTH / 2)
    center_y = int(screen_height/2 - APP_HEIGHT / 2)

    # set the position of the window to the center of the screen
    tk_app.geometry(f'{APP_WIDTH}x{APP_HEIGHT}+{center_x}+{center_y}')


def fill_entry_with_file_selector(entry: Entry):
    file_path = askopenfilename(
            title = "config file", filetypes=(("json files","*.json"),)
        )
    
    entry.delete(0, END)
    entry.insert(0, file_path)

def run():
    root = Tk()  # create root window
    root.title("Generate Image From CSV")
    root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
    center_window(root)

    # build_csv_frame(root)
    # Input CSV File Frame
    input_config_frame = Frame(root, pady=25)
    input_config_frame.pack()

    input_config_entry = Entry(input_config_frame, width=TEXT_WIDTH)
    input_config_entry.pack(side="left")
    Button(input_config_frame,text="Config file", command = lambda: fill_entry_with_file_selector(input_config_entry), width=10).pack(side="right")

    # Convert Button
    convert_button = Button(root, text="Convert!", command=lambda: convert_to_images(input_config_entry.get()), width=15)
    convert_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    run()