import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Watermark Application")
        
        # Set up the GUI layout
        self.create_widgets()

    def create_widgets(self):
        # Photo selection
        tk.Label(self.root, text="Select Photo:").grid(row=0, column=0, padx=10, pady=10)
        self.photo_path_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.photo_path_var, width=50).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.load_photo).grid(row=0, column=2, padx=10, pady=10)

        # Watermark selection
        tk.Label(self.root, text="Select Watermark:").grid(row=1, column=0, padx=10, pady=10)
        self.watermark_path_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.watermark_path_var, width=50).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.load_watermark).grid(row=1, column=2, padx=10, pady=10)

        # Output path
        tk.Label(self.root, text="Save As:").grid(row=2, column=0, padx=10, pady=10)
        self.output_path_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.output_path_var, width=50).grid(row=2, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.save_output).grid(row=2, column=2, padx=10, pady=10)

        # Watermark position
        tk.Label(self.root, text="Watermark Position (x,y):").grid(row=3, column=0, padx=10, pady=10)
        self.position_x_var = tk.StringVar(value="0")
        self.position_y_var = tk.StringVar(value="0")
        tk.Entry(self.root, textvariable=self.position_x_var, width=10).grid(row=3, column=1, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.position_y_var, width=10).grid(row=3, column=2, padx=10, pady=10)

        # Apply button
        tk.Button(self.root, text="Apply Watermark", command=self.apply_watermark).grid(row=4, column=0, columnspan=3, pady=20)

    def load_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.photo_path_var.set(file_path)

    def load_watermark(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.watermark_path_var.set(file_path)

    def save_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.output_path_var.set(file_path)

    def apply_watermark(self):
        photo_path = self.photo_path_var.get()
        watermark_path = self.watermark_path_var.get()
        output_path = self.output_path_var.get()
        position_x = self.position_x_var.get()
        position_y = self.position_y_var.get()

        if not (photo_path and watermark_path and output_path):
            messagebox.showerror("Input Error", "Please select all input files and output path.")
            return

        try:
            # Validate position values
            position_x = int(position_x)
            position_y = int(position_y)
        except ValueError:
            messagebox.showerror("Input Error", "Position values must be integers.")
            return

        try:
            # Open the images
            photo = Image.open(photo_path).convert("RGBA")
            watermark = Image.open(watermark_path).convert("RGBA")
    
            # Get dimensions
            photo_width, photo_height = photo.size
            watermark_width, watermark_height = watermark.size

            # Define maximum watermark size (e.g., 20% of photo size)
            max_width = int(photo_width * 0.2)
            max_height = int(photo_height * 0.2)
    
            # Resize watermark to fit within the maximum dimensions
            if watermark_width > max_width or watermark_height > max_height:
                scale = min(max_width / watermark_width, max_height / watermark_height)
                new_width = int(watermark_width * scale)
                new_height = int(watermark_height * scale)
                watermark = watermark.resize((new_width, new_height), Image.LANCZOS)
    
            watermark_width, watermark_height = watermark.size  # Update watermark size after resizing
    
            # Ensure watermark position is within photo bounds
            position_x = min(position_x, photo_width - watermark_width)
            position_y = min(position_y, photo_height - watermark_height)
    
            # Add 50% transparency to the watermark
            watermark_with_transparency = Image.new('RGBA', watermark.size)
            watermark_with_transparency.paste(watermark, (0, 0), watermark)
        
            # Adjust the alpha channel for transparency
            alpha = watermark_with_transparency.split()[3]
            alpha = alpha.point(lambda p: p * 0.5)  # 50% transparency
            watermark_with_transparency.putalpha(alpha)
    
            # Create a watermark image with transparency
            watermark_with_transparency_full = Image.new('RGBA', photo.size, (0, 0, 0, 0))
            watermark_with_transparency_full.paste(watermark_with_transparency, (position_x, position_y), watermark_with_transparency)
    
            # Apply watermark to the photo
            watermarked_photo = Image.alpha_composite(photo, watermark_with_transparency_full)

            # Save the result
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                watermarked_photo = watermarked_photo.convert("RGB")  # Convert to RGB for JPEG format
            watermarked_photo.save(output_path)
            messagebox.showinfo("Success", "Watermark applied successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()
