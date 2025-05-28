
class centerWindow():
        def center_window(self,root, w, h):
                """
                Calculates the geometry string to center a window of given width and height
                on the screen.
                
                Args:
                        root: The Tkinter/CustomTkinter root window or Toplevel instance.
                        w (int): The desired width of the window.
                        h (int): The desired height of the window.
                        
                Returns:
                        str: A geometry string in the format "WxH+X+Y".
                """
                # Get screen width and height
                ws = root.winfo_screenwidth()
                hs = root.winfo_screenheight()

                # Calculate x and y coordinates for centering
                x = (ws / 2) - (w / 2)
                y = (hs / 2) - (h / 2)

                # Return geometry string
                return f"{w}x{h}+{int(x)}+{int(y)}"
