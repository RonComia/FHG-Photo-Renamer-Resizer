import os
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import tkinter as tk
import hashlib
import logging
from datetime import datetime

# Set default color theme and appearance
ctk.set_default_color_theme("green")  # Built-in green theme
ctk.set_appearance_mode("light")  # Default to light mode

def setup_logging():
    log_file = f"renamer_log_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def verify_image_file(file_path):
    """Verify if file is a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

class ImageRenamerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        setup_logging()
        logging.info("Application started")
        self.title("Forest Hills Garden Photo Editor")
        self.geometry(self.get_adjusted_window_size())
        self.minsize(600, 400)

        # Create main background frame with blue color
        self.main_bg = ctk.CTkFrame(
            self,
            fg_color=("#B3E0FF", "#104E8B"),  # Light blue, Dark blue for dark mode
        )
        self.main_bg.pack(fill='both', expand=True, padx=2, pady=2)

        # Create content frame with green color
        self.content_frame = ctk.CTkFrame(
            self.main_bg,
            fg_color=("#90EE90", "#2E8B57"),  # Light green, Dark green for dark mode
        )
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Theme switch frame
        self.theme_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("#A7D8A7", "#1E5631")  # Light mint green, Dark forest green
        )
        self.theme_frame.pack(pady=5, padx=10, fill='x')
        
        # Add refresh button to theme frame
        self.refresh_button = ctk.CTkButton(
            self.theme_frame,
            text="↻ Refresh",
            command=self.refresh_images,
            fg_color="green",
            hover_color="dark green",
            width=100
        )
        self.refresh_button.pack(side='left', padx=10)
        
        # Add resize all button
        self.resize_all_button = ctk.CTkButton(
            self.theme_frame,
            text="Resize All",
            command=self.show_resize_all_options,
            fg_color="blue",
            hover_color="dark blue",
            width=100
        )
        self.resize_all_button.pack(side='left', padx=10)
        
        # Theme switch
        self.theme_switch = ctk.CTkSwitch(
            self.theme_frame, 
            text="Light Mode",
            command=self.toggle_theme,
            onvalue="dark",
            offvalue="light",
            button_color="green",
            button_hover_color="dark green",
            progress_color=("#B3E0FF", "#104E8B")
        )
        self.theme_switch.pack(side='right', padx=10)
        
        # Set application icon
        icon_path = os.path.join(get_base_path(), "photo", "fhg.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        
        self.folder_path = ctk.StringVar()
        self.images_per_page = 10
        self.renamed_images = {}  # Stores entered names
        self.selected_image = None  # Track the currently viewed image
        self.row_frames = []  # Store frame references for highlighting

        # Top Frame for images and folder selection
        self.top_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("#A7D8A7", "#1E5631")  # Light mint green, Dark forest green
        )
        self.top_frame.pack(pady=5, fill='x')

        # Left Image
        self.left_image_label = ctk.CTkLabel(self.top_frame, text="")
        self.left_image_label.pack(side='left', padx=10)
        left_image_path = os.path.join(get_base_path(), "photo", "fhvi.png")
        self.load_image(self.left_image_label, left_image_path, 250, 100)

        # Folder Selection with green styling
        self.folder_frame = ctk.CTkFrame(
            self.top_frame,
            fg_color=("#A7D8A7", "#1E5631")  # Light mint green, Dark forest green
        )
        self.folder_frame.pack(side='left', padx=20, expand=True)
        
        ctk.CTkLabel(
            self.folder_frame, 
            text="Select Folder:",
            font=("Helvetica", 12, "bold")
        ).pack()
        
        folder_display = ctk.CTkLabel(
            self.folder_frame, 
            textvariable=self.folder_path,
            width=300,
            fg_color=("#EEEEEE", "#333333"),  # Light grey/Dark grey background
            corner_radius=6,
            pady=5
        )
        folder_display.pack(pady=5)
        
        ctk.CTkButton(
            self.folder_frame, 
            text="Browse", 
            command=self.select_folder,
            fg_color="green",
            hover_color="dark green"
        ).pack(pady=5)

        # Right Image
        self.right_image_label = ctk.CTkLabel(self.top_frame, text="")
        self.right_image_label.pack(side='right', padx=10)
        right_image_path = os.path.join(get_base_path(), "photo", "fhg.png")
        self.load_image(self.right_image_label, right_image_path, 250, 100)
        
        # List frame with green styling
        self.list_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=("#A7D8A7", "#1E5631"),  # Light mint green, Dark forest green
            height=200
        )
        self.list_frame.pack(pady=10, fill='both', expand=True)
        
        # Buttons with green styling
        self.close_image_button = ctk.CTkButton(
            self.content_frame, 
            text="Close Image", 
            command=self.close_image,
            fg_color="green",
            hover_color="dark green"
        )
        self.close_image_button.pack(pady=5)
        
        self.image_name_label = ctk.CTkLabel(
            self.content_frame, 
            text="",
            font=("Helvetica", 12, "bold")
        )
        self.image_name_label.pack(pady=5)
        
        self.image_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            fg_color=("#A7D8A7", "#1E5631")  # Light mint green, Dark forest green
        )
        self.image_label.pack(pady=10)
        
        # Navigation frame with green styling
        self.nav_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("#A7D8A7", "#1E5631")  # Light mint green, Dark forest green
        )
        self.nav_frame.pack(pady=5)
        
        self.first_button = ctk.CTkButton(
            self.nav_frame,
            text="First",
            command=self.first_page,
            fg_color="green",
            hover_color="dark green",
            width=100
        )
        self.first_button.pack(side='left', padx=5)
        
        self.prev_button = ctk.CTkButton(
            self.nav_frame, 
            text="Previous", 
            command=self.prev_page,
            fg_color="green",
            hover_color="dark green",
            width=100
        )
        self.prev_button.pack(side='left', padx=5)
        
        self.page_label = ctk.CTkLabel(
            self.nav_frame, 
            text="Page 1 of 1",
            font=("Helvetica", 12, "bold")
        )
        self.page_label.pack(side='left', padx=5)
        
        self.next_button = ctk.CTkButton(
            self.nav_frame, 
            text="Next", 
            command=self.next_page,
            fg_color="green",
            hover_color="dark green",
            width=100
        )
        self.next_button.pack(side='left', padx=5)
        
        self.last_button = ctk.CTkButton(
            self.nav_frame,
            text="Last",
            command=self.last_page,
            fg_color="green",
            hover_color="dark green",
            width=100
        )
        self.last_button.pack(side='left', padx=5)
        
        self.rename_button = ctk.CTkButton(
            self.content_frame, 
            text="Rename Images", 
            command=self.rename_images,
            fg_color="green",
            hover_color="dark green"
        )
        self.rename_button.pack(pady=10)
        
        # Footer frame for watermark
        self.footer_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("#A7D8A7", "#1E5631")  # Light mint green, Dark forest green
        )
        self.footer_frame.pack(side='bottom', fill='x', pady=5)
        
        self.watermark_label = ctk.CTkLabel(
            self.footer_frame,
            text="© Forest Hills Garden Photo Editor V2.0| Ron Michael Comia @ 2025",
            font=("Helvetica", 10, "italic"),
            text_color=("#333333", "#CCCCCC")  # Dark gray for light mode, light gray for dark mode
        )
        self.watermark_label.pack(pady=5)
        
        self.entries = []
        self.image_list = []
        self.current_viewer = None

    def get_adjusted_window_size(self):
        """Calculate an appropriate window size based on screen dimensions"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Use 80% of screen size as max dimensions
        width = min(800, int(screen_width * 0.8))
        height = min(600, int(screen_height * 0.8))
        
        return f"{width}x{height}"

    def toggle_theme(self):
        """Toggle between light and dark mode"""
        if ctk.get_appearance_mode() == "Light":
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="Dark Mode")
        else:
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="Light Mode")

    def load_image(self, label, image_path, width, height):
        try:
            if os.path.exists(image_path) and verify_image_file(image_path):
                img = Image.open(image_path)
                img = img.resize((width, height))
                img = ImageTk.PhotoImage(img)
                label.configure(image=img)
                label.image = img
            else:
                logging.warning(f"Invalid or missing image: {image_path}")
        except Exception as e:
            logging.error(f"Error loading image {image_path}: {str(e)}")
    
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            try:
                self.folder_path.set(folder)
                self.image_list = [
                    f for f in os.listdir(folder) 
                    if f.lower().endswith((".jpg", ".png", ".jpeg")) 
                    and verify_image_file(os.path.join(folder, f))
                ]
                logging.info(f"Selected folder: {folder}")
                self.current_page = 0
                self.renamed_images.clear()
                self.selected_image = None  # Clear highlight on new folder
                self.row_frames.clear()  # Clear frame references
                self.load_images()
            except Exception as e:
                logging.error(f"Error accessing folder: {str(e)}")
                messagebox.showerror("Error", "Unable to access selected folder")
    
    def update_highlights(self):
        """Update the highlight colors of all rows based on selected_image"""
        for image_name, frame, entry_frame in self.row_frames:
            frame_color = ("#FFFF99", "#666633") if image_name == self.selected_image else ("#B8E2B8", "#2E6B44")
            frame.configure(fg_color=frame_color)
            entry_frame.configure(fg_color=frame_color)

    def load_images(self):
        self.save_current_entries()  # Save entries before clearing
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        self.entries.clear()
        self.row_frames.clear()
        start = self.current_page * self.images_per_page
        end = start + self.images_per_page
        images = self.image_list[start:end]
        
        for image in images:
            frame_color = ("#FFFF99", "#666633") if image == self.selected_image else ("#B8E2B8", "#2E6B44")
            frame = ctk.CTkFrame(
                self.list_frame,
                fg_color=frame_color  # Yellow for selected, default green otherwise
            )
            frame.pack(pady=2, fill='x')
            
            image_button = ctk.CTkButton(
                frame, 
                text=image, 
                command=lambda img=image: self.display_image(img),
                fg_color="green",
                hover_color="dark green",
                width=200
            )
            image_button.pack(side='left', padx=5)
            
            entry_frame = ctk.CTkFrame(
                frame,
                fg_color=frame_color  # Match the parent frame's color
            )
            entry_frame.pack(side='right', padx=5)
            
            entry = ctk.CTkEntry(
                entry_frame, 
                width=200, 
                border_color="green",
                fg_color=("#FFFFFF", "#2B2B2B")
            )
            entry.pack(side='left', padx=(0, 5))
            
            resize_button = ctk.CTkButton(
                entry_frame,
                text="Resize",
                command=lambda img=image: self.show_resize_options(img),
                fg_color="blue",
                hover_color="dark blue",
                width=70
            )
            resize_button.pack(side='left', padx=(0, 5))
            
            delete_button = ctk.CTkButton(
                entry_frame,
                text="Delete",
                command=lambda img=image: self.delete_image(img),
                fg_color="red",
                hover_color="dark red",
                width=70
            )
            delete_button.pack(side='left')
            
            if image in self.renamed_images:
                entry.insert(0, self.renamed_images[image])

            self.entries.append((image, entry))
            self.row_frames.append((image, frame, entry_frame))
        
        total_pages = max(1, (len(self.image_list) - 1) // self.images_per_page + 1)
        self.page_label.configure(text=f"Page {self.current_page + 1} of {total_pages}")
        self.update_nav_buttons()
        self.close_image()
    
    def update_nav_buttons(self):
        total_pages = max(1, (len(self.image_list) - 1) // self.images_per_page + 1)
        self.first_button.configure(state="normal" if self.current_page > 0 else "disabled")
        self.prev_button.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_button.configure(state="normal" if self.current_page < total_pages - 1 else "disabled")
        self.last_button.configure(state="normal" if self.current_page < total_pages - 1 else "disabled")
    
    def first_page(self):
        self.save_current_entries()
        self.current_page = 0
        self.load_images()
    
    def prev_page(self):
        self.save_current_entries()
        if self.current_page > 0:
            self.current_page -= 1
            self.load_images()
    
    def next_page(self):
        self.save_current_entries()
        total_pages = max(1, (len(self.image_list) - 1) // self.images_per_page + 1)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.load_images()
    
    def last_page(self):
        self.save_current_entries()
        total_pages = max(1, (len(self.image_list) - 1) // self.images_per_page + 1)
        self.current_page = total_pages - 1
        self.load_images()
    
    def save_current_entries(self):
        for old_name, entry in self.entries:
            new_name = entry.get().strip()
            if new_name:
                self.renamed_images[old_name] = new_name

    def show_resize_options(self, image_name):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder")
            return
        
        resize_window = ctk.CTkToplevel(self)
        resize_window.title(f"Resize {image_name}")
        resize_window.attributes('-topmost', True)
        resize_window.geometry("300x150")
        
        main_frame = ctk.CTkFrame(resize_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            main_frame,
            text="Select size:",
            font=("Helvetica", 12, "bold")
        ).pack(pady=5)
        
        size_options = [
            "Original",
            "320x240",
            "800x600",
            "1024x768",
            "1280x720",
            "1920x1080"
        ]
        size_var = ctk.StringVar(value="Original")
        size_dropdown = ctk.CTkOptionMenu(
            main_frame,
            values=size_options,
            variable=size_var
        )
        size_dropdown.pack(pady=5)
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Apply",
            command=lambda: [self.resize_image(image_name, size_var.get()), resize_window.destroy()],
            fg_color="green",
            hover_color="dark green",
            width=100
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=resize_window.destroy,
            fg_color="red",
            hover_color="dark red",
            width=100
        ).pack(side='left', padx=5)

    def show_resize_all_options(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder")
            return
        
        resize_window = ctk.CTkToplevel(self)
        resize_window.title("Resize All Images")
        resize_window.attributes('-topmost', True)
        resize_window.geometry("300x150")
        
        main_frame = ctk.CTkFrame(resize_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            main_frame,
            text="Select size for all images:",
            font=("Helvetica", 12, "bold")
        ).pack(pady=5)
        
        size_options = [
            "Original",
            "320x240",
            "800x600",
            "1024x768",
            "1280x720",
            "1920x1080"
        ]
        size_var = ctk.StringVar(value="Original")
        size_dropdown = ctk.CTkOptionMenu(
            main_frame,
            values=size_options,
            variable=size_var
        )
        size_dropdown.pack(pady=5)
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Apply",
            command=lambda: [self.resize_all_images(size_var.get()), resize_window.destroy()],
            fg_color="green",
            hover_color="dark green",
            width=100
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=resize_window.destroy,
            fg_color="red",
            hover_color="dark red",
            width=100
        ).pack(side='left', padx=5)

    def resize_image(self, image_name, size_str):
        folder = self.folder_path.get()
        image_path = os.path.join(folder, image_name)
        
        try:
            if size_str == "Original":
                return
            
            width, height = map(int, size_str.split('x'))
            img = Image.open(image_path)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            img.save(image_path)
            
            logging.info(f"Resized {image_name} to {size_str}")
            messagebox.showinfo("Success", f"Resized {image_name} to {size_str}")
            self.refresh_images()
            
        except Exception as e:
            logging.error(f"Error resizing {image_name}: {str(e)}")
            messagebox.showerror("Error", f"Failed to resize {image_name}: {str(e)}")

    def resize_all_images(self, size_str):
        folder = self.folder_path.get()
        if size_str == "Original":
            return
        
        try:
            width, height = map(int, size_str.split('x'))
            resized_count = 0
            
            for image_name in self.image_list:
                image_path = os.path.join(folder, image_name)
                if verify_image_file(image_path):
                    img = Image.open(image_path)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                    img.save(image_path)
                    resized_count += 1
                    logging.info(f"Resized {image_name} to {size_str}")
            
            messagebox.showinfo("Success", f"Resized {resized_count} images to {size_str}")
            self.refresh_images()
            
        except Exception as e:
            logging.error(f"Error resizing all images: {str(e)}")
            messagebox.showerror("Error", f"Failed to resize images: {str(e)}")

    def rename_images(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder")
            return
        
        self.save_current_entries()
        
        try:
            renamed_count = 0
            old_to_new = {}
            existing_conflicts = []
            
            for old_name, new_name in self.renamed_images.items():
                if new_name:
                    new_name = "".join(c for c in new_name if c.isalnum() or c in (' ', '-', '_'))
                    ext = os.path.splitext(old_name)[1].lower()
                    new_full_name = f"{new_name}{ext}"
                    new_path = os.path.join(folder, new_full_name)
                    if os.path.exists(new_path) and old_name != new_full_name:
                        existing_conflicts.append((old_name, new_full_name))
            
            if existing_conflicts:
                conflict_window = ctk.CTkToplevel(self)
                conflict_window.title("Name Conflict")
                conflict_window.attributes('-topmost', True)
                conflict_window.geometry("500x400")
                conflict_window.minsize(500, 300)
                
                main_frame = ctk.CTkFrame(conflict_window)
                main_frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                ctk.CTkLabel(
                    main_frame,
                    text="The following files will conflict with existing files:",
                    font=("Helvetica", 12, "bold"),
                    wraplength=450
                ).pack(pady=(5, 10))
                
                scroll_frame = ctk.CTkScrollableFrame(
                    main_frame,
                    height=200
                )
                scroll_frame.pack(fill='x', expand=True, pady=5)
                
                for old_name, new_full_name in existing_conflicts:
                    ctk.CTkLabel(
                        scroll_frame,
                        text=f"'{old_name}' → '{new_full_name}' (exists)",
                        justify="left",
                        wraplength=450
                    ).pack(pady=2, anchor='w')
                
                button_frame = ctk.CTkFrame(main_frame)
                button_frame.pack(fill='x', pady=10)
                
                def remove_and_proceed():
                    for old_name, new_full_name in existing_conflicts:
                        new_path = os.path.join(folder, new_full_name)
                        os.remove(new_path)
                        logging.info(f"Removed existing file: {new_full_name}")
                    conflict_window.destroy()
                    self.continue_rename(old_to_new, renamed_count)
                
                def cancel_and_clear():
                    for old_name, entry in self.entries:
                        if (old_name, self.renamed_images.get(old_name, "") + os.path.splitext(old_name)[1].lower()) in existing_conflicts:
                            entry.delete(0, 'end')
                            if old_name in self.renamed_images:
                                del self.renamed_images[old_name]
                    conflict_window.destroy()
                    self.load_images()
                
                ctk.CTkButton(
                    button_frame,
                    text="Remove Old Versions",
                    command=remove_and_proceed,
                    fg_color="green",
                    hover_color="dark green",
                    width=150
                ).pack(side='left', padx=10, pady=5)
                
                ctk.CTkButton(
                    button_frame,
                    text="Cancel & Clear",
                    command=cancel_and_clear,
                    fg_color="red",
                    hover_color="dark red",
                    width=150
                ).pack(side='left', padx=10, pady=5)
                
                conflict_window.update_idletasks()
                x = self.winfo_x() + (self.winfo_width() - conflict_window.winfo_width()) // 2
                y = self.winfo_y() + (self.winfo_height() - conflict_window.winfo_height()) // 2
                conflict_window.geometry(f"+{x}+{y}")
                
                return
            
            self.continue_rename(old_to_new, renamed_count)

        except Exception as e:
            logging.error(f"Error during rename operation: {str(e)}")
            messagebox.showerror("Error", "An error occurred while renaming files")

    def continue_rename(self, old_to_new, renamed_count):
        folder = self.folder_path.get()
        
        for old_name, new_name in list(self.renamed_images.items()):
            if new_name:
                new_name = "".join(c for c in new_name if c.isalnum() or c in (' ', '-', '_'))
                ext = os.path.splitext(old_name)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png']:
                    continue
                
                new_full_name = f"{new_name}{ext}"
                old_path = os.path.join(folder, old_name)
                new_path = os.path.join(folder, new_full_name)

                if not os.path.exists(old_path):
                    logging.warning(f"Source file missing: {old_path}")
                    continue
                
                if verify_image_file(old_path):
                    with open(old_path, 'rb') as f:
                        old_checksum = hashlib.md5(f.read()).hexdigest()
                    
                    os.rename(old_path, new_path)
                    
                    with open(new_path, 'rb') as f:
                        new_checksum = hashlib.md5(f.read()).hexdigest()
                        
                    if old_checksum == new_checksum:
                        renamed_count += 1
                        old_to_new[old_name] = new_full_name
                        logging.info(f"Successfully renamed: {old_name} -> {new_full_name}")
                    else:
                        logging.error(f"Checksum mismatch after renaming: {old_name}")

        self.update_viewer_and_show_success(old_to_new, renamed_count)

    def update_viewer_and_show_success(self, old_to_new, renamed_count):
        folder = self.folder_path.get()
        
        if self.current_viewer is not None and self.current_viewer.winfo_exists():
            current_image = self.image_list[self.current_viewer.current_index]
            self.image_list = [
                f for f in os.listdir(folder) 
                if f.lower().endswith((".jpg", ".png", ".jpeg"))
                and verify_image_file(os.path.join(folder, f))
            ]
            self.current_viewer.image_list = self.image_list
            if current_image in old_to_new:
                new_name = old_to_new[current_image]
                try:
                    self.current_viewer.current_index = self.image_list.index(new_name)
                except ValueError:
                    self.current_viewer.current_index = 0
            self.current_viewer.image_name_label.configure(
                text=self.image_list[self.current_viewer.current_index]
            )
            self.current_viewer.update_nav_buttons()
            # Update the rename entry in the viewer
            self.current_viewer.rename_entry.delete(0, 'end')
            new_name = self.renamed_images.get(self.image_list[self.current_viewer.current_index], "")
            self.current_viewer.rename_entry.insert(0, new_name)
            # Update selected_image and highlights
            self.selected_image = self.image_list[self.current_viewer.current_index]
            self.update_highlights()
        
        # Clear the renamed_images dictionary to reset input boxes
        self.renamed_images.clear()
        
        # Refresh the image list to update UI
        self.refresh_images()
        
        msg_window = ctk.CTkToplevel(self)
        msg_window.title("Success")
        msg_window.geometry("300x100")
        msg_window.attributes('-topmost', True)
        
        msg_window.geometry("+%d+%d" % (
            self.winfo_rootx() + self.winfo_width()/2 - 150,
            self.winfo_rooty() + self.winfo_height()/2 - 50
        ))
        
        ctk.CTkLabel(
            msg_window, 
            text=f"{renamed_count} images renamed successfully!",
            font=("Helvetica", 12)
        ).pack(pady=10)
        
        ctk.CTkButton(
            msg_window,
            text="OK",
            command=msg_window.destroy,
            fg_color="green",
            hover_color="dark green"
        ).pack(pady=5)
        
        msg_window.bind('<Return>', lambda e: msg_window.destroy())
    
    def close_image(self):
        self.image_label.configure(image="")
        self.image_label.image = None
        self.image_name_label.configure(text="")
    
    def display_image(self, image_name):
        folder = self.folder_path.get()
        image_path = os.path.join(folder, image_name)
        if os.path.exists(image_path):
            if self.current_viewer is not None and self.current_viewer.winfo_exists():
                self.current_viewer.destroy()
            
            self.save_current_entries()  # Save entries before opening viewer
            self.selected_image = image_name  # Set the selected image
            self.update_highlights()  # Update highlight without refreshing
            current_index = self.image_list.index(image_name)
            self.current_viewer = ImageViewer(self, image_path, self.image_list, current_index)
            self.current_viewer.focus()

    def delete_image(self, image_name):
        try:
            image_path = os.path.join(self.folder_path.get(), image_name)
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {image_name}?"):
                os.remove(image_path)
                logging.info(f"Deleted image: {image_name}")
                
                if image_name in self.renamed_images:
                    del self.renamed_images[image_name]
                
                if self.selected_image == image_name:
                    self.selected_image = None  # Clear highlight if deleted
                
                self.image_list = [
                    f for f in os.listdir(self.folder_path.get()) 
                    if f.lower().endswith((".jpg", ".png", ".jpeg")) 
                    and verify_image_file(os.path.join(self.folder_path.get(), f))
                ]
                
                total_pages = max(1, (len(self.image_list) - 1) // self.images_per_page + 1)
                if self.current_page >= total_pages and self.current_page > 0:
                    self.current_page -= 1
                
                self.load_images()
                messagebox.showinfo("Success", f"Image {image_name} deleted successfully")
        except Exception as e:
            logging.error(f"Error deleting image {image_name}: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete image: {str(e)}")

    def refresh_images(self):
        try:
            folder = self.folder_path.get()
            if folder:
                self.save_current_entries()  # Save entries before refreshing
                current_page = self.current_page
                
                self.image_list = [
                    f for f in os.listdir(folder) 
                    if f.lower().endswith((".jpg", ".png", ".jpeg")) 
                    and verify_image_file(os.path.join(folder, f))
                ]
                self.image_list.sort()
                
                total_pages = max(1, (len(self.image_list) - 1) // self.images_per_page + 1)
                self.current_page = min(current_page, max(0, total_pages - 1))
                
                self.load_images()
                logging.info("Image list refreshed")
                
                if self.current_viewer is not None and self.current_viewer.winfo_exists():
                    self.current_viewer.image_list = self.image_list
                    self.current_viewer.current_index = min(
                        self.current_viewer.current_index,
                        len(self.image_list) - 1
                    )
                    current_image = self.image_list[self.current_viewer.current_index]
                    image_path = os.path.join(folder, current_image)
                    self.current_viewer.load_image(image_path)
                    self.current_viewer.update_nav_buttons()
                    # Update the rename entry in the viewer
                    self.current_viewer.rename_entry.delete(0, 'end')
                    new_name = self.renamed_images.get(current_image, "")
                    self.current_viewer.rename_entry.insert(0, new_name)
                    # Update selected_image and highlights
                    self.selected_image = current_image
                    self.update_highlights()
                
        except Exception as e:
            logging.error(f"Error refreshing images: {str(e)}")
            messagebox.showerror("Error", "Failed to refresh images")

class ImageViewer(ctk.CTkToplevel):
    def __init__(self, parent, image_path, image_list, current_index):
        super().__init__(parent)
        
        self.attributes('-topmost', True)
        self.transient(parent)
        
        try:
            icon_path = os.path.join(get_base_path(), "photo", "fhg.ico")
            if os.path.exists(icon_path):
                self.after(200, lambda: self.iconbitmap(icon_path))
                self.after(200, lambda: self.tk.call('wm', 'iconphoto', self._w, tk.PhotoImage(file=icon_path)))
        except Exception as e:
            logging.error(f"Error setting viewer icon: {str(e)}")
        
        self.parent = parent
        self.image_list = image_list
        self.current_index = current_index
        self.folder_path = os.path.dirname(image_path)
        
        self.title("Image Viewer")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        viewer_width = min(720, int(screen_width * 0.8))
        viewer_height = min(720, int(screen_height * 0.8))
        self.geometry(f"{viewer_width}x{viewer_height}")
        self.minsize(400, 300)
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Navigation and rename frame
        self.nav_frame = ctk.CTkFrame(self.main_frame)
        self.nav_frame.pack(fill='x', pady=5)
        
        self.prev_button = ctk.CTkButton(
            self.nav_frame,
            text="Previous",
            command=self.show_previous,
            width=100,
            fg_color="green",
            hover_color="dark green"
        )
        self.prev_button.pack(side='left', padx=5)
        
        self.image_name_label = ctk.CTkLabel(
            self.nav_frame,
            text=os.path.basename(image_path),
            font=("Helvetica", 12, "bold")
        )
        self.image_name_label.pack(side='left', expand=True)
        
        self.next_button = ctk.CTkButton(
            self.nav_frame,
            text="Next",
            command=self.show_next,
            width=100,
            fg_color="green",
            hover_color="dark green"
        )
        self.next_button.pack(side='right', padx=5)
        
        # Rename entry frame
        self.rename_frame = ctk.CTkFrame(self.main_frame)
        self.rename_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            self.rename_frame,
            text="Rename:",
            font=("Helvetica", 12)
        ).pack(side='left', padx=5)
        
        self.rename_entry = ctk.CTkEntry(
            self.rename_frame,
            width=300,
            border_color="green",
            fg_color=("#FFFFFF", "#2B2B2B")
        )
        self.rename_entry.pack(side='left', padx=5)
        # Initialize with any existing rename value
        current_image = self.image_list[self.current_index]
        if current_image in self.parent.renamed_images:
            self.rename_entry.insert(0, self.parent.renamed_images[current_image])
        
        # Image display frame
        self.image_frame = ctk.CTkFrame(self.main_frame)
        self.image_frame.pack(fill='both', expand=True)
        
        self.image_label = ctk.CTkLabel(self.image_frame, text="")
        self.image_label.pack(expand=True)
        
        self.load_image(image_path)
        self.update_nav_buttons()
        
        # Bind arrow keys at the window level to ensure navigation works even when entry has focus
        self.bind_all('<Left>', lambda e: self.show_previous())
        self.bind_all('<Right>', lambda e: self.show_next())
        self.bind('<Escape>', lambda e: self.close_viewer())
        self.bind('<Configure>', self.on_resize)
        self._resize_job = None
        
        # Bind Enter key in rename entry to save the rename value
        self.rename_entry.bind('<Return>', self.save_rename)

    def close_viewer(self):
        self.parent.selected_image = None  # Clear highlight
        self.parent.update_highlights()  # Update highlights without refreshing
        self.destroy()

    def save_rename(self, event=None):
        """Save the rename entry to the parent's renamed_images dictionary"""
        current_image = self.image_list[self.current_index]
        new_name = self.rename_entry.get().strip()
        if new_name:
            self.parent.renamed_images[current_image] = new_name
        elif current_image in self.parent.renamed_images:
            del self.parent.renamed_images[current_image]

    def load_image(self, image_path):
        try:
            img = Image.open(image_path)
            frame_width = self.image_frame.winfo_width() - 20
            frame_height = self.image_frame.winfo_height() - 20
            
            if frame_width < 50 or frame_height < 50:
                frame_width = min(600, int(self.winfo_screenwidth() * 0.7))
                frame_height = min(400, int(self.winfo_screenheight() * 0.7))
            
            aspect_ratio = img.width / img.height
            
            if aspect_ratio > 1:
                new_width = min(img.width, frame_width)
                new_height = int(new_width / aspect_ratio)
                if new_height > frame_height:
                    new_height = frame_height
                    new_width = int(new_height * aspect_ratio)
            else:
                new_height = min(img.height, frame_height)
                new_width = int(new_height * aspect_ratio)
                if new_width > frame_width:
                    new_width = frame_width
                    new_height = int(new_width / aspect_ratio)
            
            new_width = max(100, new_width)
            new_height = max(100, new_height)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.image_label.configure(image=photo)
            self.image_label.image = photo
            self.image_name_label.configure(text=os.path.basename(image_path))
            
            # Update rename entry when loading a new image
            self.rename_entry.delete(0, 'end')
            current_image = self.image_list[self.current_index]
            if current_image in self.parent.renamed_images:
                self.rename_entry.insert(0, self.parent.renamed_images[current_image])
            
        except Exception as e:
            logging.error(f"Error loading image {image_path}: {str(e)}")
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def on_resize(self, event):
        if event.widget == self:
            if hasattr(self, '_resize_job') and self._resize_job:
                self.after_cancel(self._resize_job)
            self._resize_job = self.after(200, self.resize_image)

    def resize_image(self):
        self._resize_job = None
        if hasattr(self, 'current_index') and len(self.image_list) > self.current_index:
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            if os.path.exists(image_path):
                self.load_image(image_path)
    
    def show_previous(self, event=None):
        if self.current_index > 0:
            # Save rename entry in viewer and main window entries
            self.save_rename()
            self.parent.save_current_entries()
            self.current_index -= 1
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            self.load_image(image_path)
            self.update_nav_buttons()
            # Update highlight in main window without refreshing
            self.parent.selected_image = self.image_list[self.current_index]
            self.parent.update_highlights()

    def show_next(self, event=None):
        if self.current_index < len(self.image_list) - 1:
            # Save rename entry in viewer and main window entries
            self.save_rename()
            self.parent.save_current_entries()
            self.current_index += 1
            image_path = os.path.join(self.folder_path, self.image_list[self.current_index])
            self.load_image(image_path)
            self.update_nav_buttons()
            # Update highlight in main window without refreshing
            self.parent.selected_image = self.image_list[self.current_index]
            self.parent.update_highlights()
    
    def update_nav_buttons(self):
        self.prev_button.configure(state="normal" if self.current_index > 0 else "disabled")
        self.next_button.configure(state="normal" if self.current_index < len(self.image_list) - 1 else "disabled")

if __name__ == "__main__":
    os.chdir(get_base_path())
    app = ImageRenamerApp()
    app.mainloop()