import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageDraw, ImageFont
import json
from watermark_presets import save_preset, load_preset, list_presets

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Watermark Application")
        
        self.preview_image = None
        self.preview_wm_image = None
        self.watermark_prevoew_scale = 1.0
        self.resized_watermark_size = (60, 60)
        self.canvas_watermark = None
        self.canvas_resize_handle = None
        self.drag_data = {"x": 0, "y": 0, "item": None}

        self.opacity_var = tk.DoubleVar(value=50)
        self.rotation_var = tk.DoubleVar(value=0)

        self.watermark_mode = tk.StringVar(value="image")
        self.text_watermark_var = tk.StringVar(value="copyright")
        self.text_fontsize_var = tk.IntVar(value=40)
        self.text_color_var = tk.StringVar(value="white")
    
        
        self.create_widgets()

    def create_widgets(self):

        tk.Label(self.root, text="Select Photo:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.photo_path_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.photo_path_var, width=50).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.load_photo).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(self.root, text="Select Watermark:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.watermark_path_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.watermark_path_var, width=50).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.load_watermark).grid(row=1, column=2, padx=10, pady=5)

        tk.Label(self.root, text="Watermark Type:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tk.Radiobutton(self.root, text="Image", variable=self.watermark_mode, value="image", command=self.update_preview).grid(row=2, column=1, sticky="w")
        tk.Radiobutton(self.root, text="Text", variable=self.watermark_mode, value="text", command=self.update_preview).grid(row=2, column=2, sticky="w")

        # Text watermark inputs
        tk.Label(self.root, text="Text:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.text_watermark_var, width=30).grid(row=3, column=1, columnspan=2, sticky="w", padx=10)

        tk.Label(self.root, text="Font Size:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.text_fontsize_var, width=10).grid(row=4, column=1, sticky="w")

        tk.Label(self.root, text="Color:").grid(row=4, column=2, padx=10, pady=5, sticky="w")
        tk.Entry(self.root, textvariable=self.text_color_var, width=10).grid(row=4, column=2, sticky="e", padx=10)

        tk.Label(self.root, text="Save As:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.output_path_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.output_path_var, width=50).grid(row=2, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.save_output).grid(row=2, column=2, padx=10, pady=5)

        tk.Label(self.root, text="Watermark Position (x, y):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.position_x_var = tk.StringVar(value="0")
        self.position_y_var = tk.StringVar(value="0")
        tk.Entry(self.root, textvariable=self.position_x_var, width=10).grid(row=3, column=1, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.position_y_var, width=10).grid(row=3, column=2, sticky="w", padx=10, pady=5)

        tk.Label(self.root, text="Watermark Size (w × h):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.wm_width_var = tk.StringVar(value=str(self.resized_watermark_size[0]))
        self.wm_height_var = tk.StringVar(value=str(self.resized_watermark_size[1]))
        tk.Entry(self.root, textvariable=self.wm_width_var, width=10).grid(row=4, column=1, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.wm_height_var, width=10).grid(row=4, column=2, sticky="w", padx=10, pady=5)

        tk.Button(self.root, text="Apply Size", command=self.apply_watermark_size).grid(row=5, column=0, columnspan=3, pady=5)

        tk.Button(self.root, text="Apply Watermark", command=self.apply_watermark).grid(row=4, column=0, columnspan=3, pady=10)

        self.preview_canvas = tk.Canvas(self.root, width=300, height=300, bg="gray")
        self.preview_canvas.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="Opacity (%):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        tk.Scale(self.root, variable=self.opacity_var, from_=0, to=100, orient="horizontal", command=self.update_preview).grid(row=6, column=1, columnspan=2, sticky="we", padx=10)

        tk.Label(self.root, text="Rotation (°):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
        tk.Scale(self.root, variable=self.rotation_var, from_=0, to=360, orient="horizontal", command=self.update_preview).grid(row=7, column=1, columnspan=2, sticky="we", padx=10)

        tk.Label(self.root, text="Preset Name:").grid(row=9, column=0, padx=10, pady=5, sticky="e")
        self.preset_name_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.preset_name_var, width=30).grid(row=9, column=1, padx=10, pady=5)

        tk.Button(self.root, text="Save Preset", command=self.save_current_preset).grid(row=9, column=2, padx=5, pady=5)
        tk.Button(self.root, text="Load Preset", command=self.load_selected_preset).grid(row=10, column=2, padx=5, pady=5)

        self.preview_canvas.grid(row=8, column=0, columnspan=3, padx=10, pady=10)


    def load_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.photo_path_var.set(file_path)
            image = self.generate_watermarked_image()
            if image:
                self.show_preview(image)

    def save_current_preset(self):
        name = self.preset_name_var.get().strip()
        if not name:
            messagebox.showerror("Missing Name", "Enter a name for the preset.")
            return

        config = {
            "watermark_mode": self.watermark_mode.get(),
            "position_x": self.position_x_var.get(),
            "position_y": self.position_y_var.get(),
            "opacity": self.opacity_var.get(),
            "rotation": self.rotation_var.get(),
            "wm_width": self.wm_width_var.get(),
            "wm_height": self.wm_height_var.get(),
            "text": self.text_watermark_var.get(),
            "text_fontsize": self.text_fontsize_var.get(),
            "text_color": self.text_color_var.get()
        }

        try:
            save_preset(name, config)
            messagebox.showinfo("Preset Saved", f"Preset '{name}' saved.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_selected_preset(self):
        name = self.preset_name_var.get().strip()
        if not name:
            messagebox.showerror("Missing Name", "Enter a name to load the preset.")
            return

        try:
            config = load_preset(name)
            self.watermark_mode.set(config.get("watermark_mode", "image"))
            self.position_x_var.set(config.get("position_x", "0"))
            self.position_y_var.set(config.get("position_y", "0"))
            self.opacity_var.set(config.get("opacity", 50))
            self.rotation_var.set(config.get("rotation", 0))
            self.wm_width_var.set(config.get("wm_width", "60"))
            self.wm_height_var.set(config.get("wm_height", "60"))
            self.text_watermark_var.set(config.get("text", "© 2025"))
            self.text_fontsize_var.set(config.get("text_fontsize", 40))
            self.text_color_var.set(config.get("text_color", "white"))

            # Sync size state
            self.resized_watermark_size = (int(self.wm_width_var.get()), int(self.wm_height_var.get()))
            image = self.generate_watermarked_image()
            if image:
                self.show_preview(image)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))


    def generate_text_watermark(self, text, font_size=40, color="white", opacity=128):
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        size = font.getSize(text)
        watermark = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)

        if isinstance(color, str):
            fill = color
        else:
            fill = (*color[:3], opacity)
        draw.text((0, 0), text, font=font, fill=fill)
        return watermark

    def apply_watermark_size(self):
        try:
            w = int(self.wm_width_var.get())
            h = int(self.wm_height_var.get())
            if w <= 0 or h <= 0:
                raise ValueError("Size must be positive")
            self.resized_watermark_size = (w,h)
            image = self.generate_watermarked_image()
            if image:
                self.show_preview(image)
        except Exception as e:
            messagebox.showerror("Invalid size", "Please enter a valid positive integers")

    def load_watermark(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.watermark_path_var.set(file_path)
            wm = Image.open(file_path)
            wm.thumbnail((60, 60), Image.LANCZOS)
            self.resized_watermark_size = wm.size
            self.opacity_var.set(50)
            self.rotation_var.set(0)
            self.wm_width_var.set(str(wm.size[0]))
            self.wm_height_var.set(str(wm.size[1]))
            image = self.generate_watermarked_image()
            if image:
                self.show_preview(image)

    def save_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.output_path_var.set(file_path)

    def apply_watermark(self):
        output_path = self.output_path_var.get()
        if not output_path:
            messagebox.showerror("Input Error", "Please select an output file.")
            return

        image = self.generate_watermarked_image()
        if image is None:
            messagebox.showerror("Error", "Failed to generate watermarked image. Check input values.")
            return

        try:
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                image = image.convert("RGB")
            image.save(output_path)
            self.show_preview(image.copy())
            messagebox.showinfo("Success", "Watermark applied successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def generate_watermarked_image(self):
        photo_path = self.photo_path_var.get()
        watermark_path = self.watermark_path_var.get()
        try:
            position_x = int(self.position_x_var.get())
            position_y = int(self.position_y_var.get())
        except ValueError:
            return None

        if not (photo_path and watermark_path):
            return None

        try:
            photo = Image.open(photo_path).convert("RGBA")
            if self.watermark_mode.get() == "image":
                watermark = Image.open(watermark_path).convert("RGBA")
                wm_width, wm_height = self.resized_watermark_size
                watermark = watermark.resize((wm_width, wm_height), Image.LANCZOS)
            else:
                text = self.text_watermark_var.get()
                font_size = self.text_fontsize_var.get()
                color = self.text_color_var.get()
                opacity = int(self.opacity_var.get() * 2.55)
                watermark = self.generate_text_watermark(text, font_size, color, opacity)
                self.resized_watermark_size = watermark.size

            # Apply rotation
            angle = float(self.rotation_var.get())
            watermark = watermark.rotate(angle, expand=True)

            # Apply opacity
            alpha = watermark.split()[3].point(lambda p: p * (self.opacity_var.get() / 100))
            watermark.putalpha(alpha)

            photo_width, photo_height = photo.size
            position_x = min(position_x, photo_width - wm_width)
            position_y = min(position_y, photo_height - wm_height)

            watermark_layer = Image.new('RGBA', photo.size, (0, 0, 0, 0))
            watermark_alpha = watermark.split()[3].point(lambda p: p * 0.5)
            watermark.putalpha(watermark_alpha)
            watermark_layer.paste(watermark, (position_x, position_y), watermark)

            return Image.alpha_composite(photo, watermark_layer)
        except:
            return None

    def show_preview(self, image):
        preview_size = (300, 300)
        preview_img = image.copy()
        preview_img.thumbnail(preview_size, Image.LANCZOS)
        self.preview_image = ImageTk.PhotoImage(preview_img)

        self.preview_canvas.delete("all")
        self.canvas_photo = self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)

        try:
            photo_path = self.photo_path_var.get()
            watermark_path = self.watermark_path_var.get()
            if not (photo_path and watermark_path):
                return

            # Load watermark for preview
            wm = Image.open(watermark_path).convert("RGBA")
            wm = wm.resize(self.resized_watermark_size, Image.LANCZOS)
            self.preview_wm_image = ImageTk.PhotoImage(wm)

            # Scale position from real image to preview
            original = Image.open(photo_path)
            original_size = original.size
            original.thumbnail(preview_size, Image.LANCZOS)
            scale_x = original.size[0] / Image.open(photo_path).size[0]
            scale_y = original.size[1] / Image.open(photo_path).size[1]

            wm_x = int(int(self.position_x_var.get()) * scale_x)
            wm_y = int(int(self.position_y_var.get()) * scale_y)

            # Place watermark image
            self.canvas_watermark = self.preview_canvas.create_image(wm_x, wm_y, anchor="nw", image=self.preview_wm_image, tags="watermark")

            # Place resize handle
            handle_x = wm_x + self.resized_watermark_size[0]
            handle_y = wm_y + self.resized_watermark_size[1]
            self.canvas_resize_handle = self.preview_canvas.create_rectangle(
                handle_x - 5, handle_y - 5, handle_x + 5, handle_y + 5,
                fill="red", tags="resize_handle"
            )

            # Bind drag and resize
            self.preview_canvas.tag_bind("watermark", "<ButtonPress-1>", self.on_drag_start)
            self.preview_canvas.tag_bind("watermark", "<B1-Motion>", self.on_drag_motion)
            self.preview_canvas.tag_bind("watermark", "<ButtonRelease-1>", self.on_drag_release)
            self.preview_canvas.tag_bind("resize_handle", "<ButtonPress-1>", self.on_resize_start)
            self.preview_canvas.tag_bind("resize_handle", "<B1-Motion>", self.on_resizing)
            self.preview_canvas.tag_bind("resize_handle", "<ButtonRelease-1>", self.on_resize_done)
        except:
            pass

    def on_drag_start(self, event):
        self.drag_data["item"] = self.canvas_watermark
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag_motion(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.preview_canvas.move(self.canvas_watermark, dx, dy)
        self.preview_canvas.move(self.canvas_resize_handle, dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag_release(self, event):
        try:
            x, y = self.preview_canvas.coords(self.canvas_watermark)
            preview_img = Image.open(self.photo_path_var.get()).copy()
            preview_img.thumbnail((300, 300), Image.LANCZOS)
            scale_x = Image.open(self.photo_path_var.get()).size[0] / preview_img.size[0]
            scale_y = Image.open(self.photo_path_var.get()).size[1] / preview_img.size[1]
            self.position_x_var.set(str(int(x * scale_x)))
            self.position_y_var.set(str(int(y * scale_y)))
            image = self.generate_watermarked_image()
            if image:
                self.show_preview(image)
        except:
            pass

    def on_resize_start(self, event):
        self.drag_data["item"] = "resize"
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_resizing(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]

        new_width = max(10, self.resized_watermark_size[0] + dx)
        new_height = max(10, self.resized_watermark_size[1] + dy)

        self.resized_watermark_size = (new_width, new_height)
        self.wm_width_var.set(str(new_width))
        self.wm_height_var.set(str(new_height))
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

        try:
            wm_path = self.watermark_path_var.get()
            if not wm_path:
                return

            wm = Image.open(wm_path).convert("RGBA")
            wm = wm.resize((new_width, new_height), Image.LANCZOS)
            self.preview_wm_image = ImageTk.PhotoImage(wm)

            x, y = self.preview_canvas.coords(self.canvas_watermark)
            self.preview_canvas.itemconfig(self.canvas_watermark, image=self.preview_wm_image)

            self.preview_canvas.coords(
                self.canvas_resize_handle,
                x + new_width - 5, y + new_height - 5,
                x + new_width + 5, y + new_height + 5
            )
        except:
            pass

    def on_resize_done(self, event):
        self.drag_data["item"] = None
        image = self.generate_watermarked_image()
        if image:
            self.show_preview(image)
    
    def update_preview(self, *args):
        image = self.generate_watermarked_image()
        if image:
            self.show_preview(image)


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()