import tkinter as tk
from models.model import CardForgeModel
from views.view import CardForgeView
from controllers.controller import CardForgeController

def main():
    root = tk.Tk()
    
    model = CardForgeModel()
    view = CardForgeView(root)
    controller = CardForgeController(model, view)
    
    root.mainloop()

if __name__ == "__main__":
    main()