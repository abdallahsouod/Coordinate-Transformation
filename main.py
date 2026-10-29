import customtkinter as ctk
import numpy as np

from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from transformations import transform, to_cartesian


# =========================
# Application Configuration
# =========================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CoordinateApp(ctk.CTk):

    SYSTEMS = ["Cartesian", "Cylindrical", "Spherical"]

    COORDINATES = {
        "Cartesian": ["x", "y", "z"],
        "Cylindrical": ["rho (ρ)", "phi (φ) [deg]", "z"],
        "Spherical": ["r", "theta (θ) [deg]", "phi (φ) [deg]"]
    }

    def __init__(self):
        super().__init__()

        self.title("Coordinate Transformation System")
        self.geometry("1200x800")
        self.minsize(1050, 700)

        self.input_entries = []
        self.second_entries = []

        self.create_widgets()

        self.update_input_fields()
        self.update_output_labels()

    # =========================
    # Build Interface
    # =========================

    def create_widgets(self):

        # Main title
        self.title_label = ctk.CTkLabel(
            self,
            text="COORDINATE TRANSFORMATION",
            font=("Arial", 26, "bold")
        )
        self.title_label.pack(pady=(20, 5))

        self.subtitle = ctk.CTkLabel(
            self,
            text="Cartesian  |  Cylindrical  |  Spherical  •  Coordinate Conversion & Vector Operations",
            font=("Arial", 14)
        )
        self.subtitle.pack(pady=(0, 15))

        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        # Left panel: input
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(
            side="left",
            fill="y",
            padx=15,
            pady=15
        )

        self.input_heading = ctk.CTkLabel(
            self.input_frame,
            text="INPUT COORDINATES",
            font=("Arial", 17, "bold")
        )
        self.input_heading.pack(padx=15, pady=(20, 12))

        ctk.CTkLabel(
            self.input_frame,
            text="Operation"
        ).pack(anchor="w", padx=15)

        self.operation_var = ctk.StringVar(value="Convert Coordinates")
        self.operation_menu = ctk.CTkOptionMenu(
            self.input_frame,
            values=[
                "Convert Coordinates",
                "Vector Addition",
                "Vector Subtraction"
            ],
            variable=self.operation_var,
            command=self.on_operation_changed
        )
        self.operation_menu.pack(fill="x", padx=15, pady=(5, 12))

        self.source_label = ctk.CTkLabel(
            self.input_frame,
            text="Source System"
        )
        self.source_label.pack(anchor="w", padx=15)

        self.source_var = ctk.StringVar(value="Cartesian")

        self.source_menu = ctk.CTkOptionMenu(
            self.input_frame,
            values=self.SYSTEMS,
            variable=self.source_var,
            command=self.on_source_changed
        )
        self.source_menu.pack(
            fill="x",
            padx=15,
            pady=(5, 15)
        )

        # Independent source system for Vector A (used in vector-operation mode)
        self.source_a_var = ctk.StringVar(value="Cartesian")
        self.source_a_label = ctk.CTkLabel(
            self.input_frame, text="Vector A Source System"
        )
        self.source_a_menu = ctk.CTkOptionMenu(
            self.input_frame,
            values=self.SYSTEMS,
            variable=self.source_a_var,
            command=self.on_source_a_changed
        )
        self.source_a_label.pack_forget()
        self.source_a_menu.pack_forget()

        self.input_fields_frame = ctk.CTkFrame(
            self.input_frame,
            fg_color="transparent"
        )
        self.input_fields_frame.pack(
            fill="x",
            padx=10
        )

        self.source_b_var = ctk.StringVar(value="Cartesian")
        self.source_b_label = ctk.CTkLabel(
            self.input_frame, text="Vector B Source System"
        )
        self.source_b_menu = ctk.CTkOptionMenu(
            self.input_frame,
            values=self.SYSTEMS,
            variable=self.source_b_var,
            command=self.on_source_b_changed
        )
        self.source_b_label.pack_forget()
        self.source_b_menu.pack_forget()

        self.second_input_title = ctk.CTkLabel(
            self.input_frame,
            text="VECTOR B",
            font=("Arial", 13, "bold")
        )
        self.second_input_frame = ctk.CTkFrame(
            self.input_frame,
            fg_color="transparent"
        )

        self.target_label = ctk.CTkLabel(
            self.input_frame,
            text="Target System"
        )
        self.target_label.pack(anchor="w", padx=15, pady=(20, 0))

        self.target_var = ctk.StringVar(
            value="Cylindrical"
        )

        self.target_menu = ctk.CTkOptionMenu(
            self.input_frame,
            values=self.SYSTEMS,
            variable=self.target_var,
            command=self.on_target_changed
        )
        self.target_menu.pack(
            fill="x",
            padx=15,
            pady=(5, 15)
        )

        # Buttons
        self.convert_button = ctk.CTkButton(
            self.input_frame,
            text="CONVERT",
            height=40,
            font=("Arial", 14, "bold"),
            command=self.convert_coordinates
        )
        self.convert_button.pack(
            fill="x",
            padx=15,
            pady=(15, 8)
        )

        self.apply_button = ctk.CTkButton(
            self.input_frame,
            text="APPLY",
            height=40,
            font=("Arial", 14, "bold"),
            command=self.apply_operation
        )
        # Only shown for Vector Addition / Vector Subtraction.
        self.apply_button.pack_forget()

        self.swap_button = ctk.CTkButton(
            self.input_frame,
            text="SWAP SYSTEMS ⇄",
            command=self.swap_systems,
            fg_color="transparent",
            border_width=1
        )
        self.swap_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.clear_button = ctk.CTkButton(
            self.input_frame,
            text="CLEAR",
            command=self.clear_fields,
            fg_color="transparent",
            border_width=1
        )
        self.clear_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        # Right panel: result and plot
        self.right_frame = ctk.CTkFrame(
            self.main_frame
        )
        self.right_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(0, 15),
            pady=15
        )

        ctk.CTkLabel(
            self.right_frame,
            text="RESULT",
            font=("Arial", 19, "bold")
        ).pack(pady=(15, 5))

        self.result_label = ctk.CTkLabel(
            self.right_frame,
            text="Enter coordinates and press CONVERT",
            font=("Consolas", 15),
            justify="left",
            wraplength=500
        )
        self.result_label.pack(
            padx=15,
            pady=10
        )

        # Matplotlib figure
        self.figure = Figure(
            figsize=(6, 4),
            dpi=100
        )

        self.ax = self.figure.add_subplot(
            111,
            projection="3d"
        )

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self.right_frame
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.draw_empty_plot()

    # =========================
    # Dynamic Input Fields
    # =========================

    def _build_coordinate_fields(self, parent, system, store_list):
        for widget in parent.winfo_children():
            widget.destroy()

        store_list.clear()
        labels = self.COORDINATES[system]

        for label in labels:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row,
                text=label,
                width=110,
                anchor="w"
            ).pack(side="left", padx=(5, 8))

            entry = ctk.CTkEntry(
                row,
                width=130,
                placeholder_text="Enter value"
            )
            entry.pack(side="right", padx=5)
            store_list.append(entry)

    def update_input_fields(self):
        """Show the conversion form or two independently configured vectors."""
        operation = self.operation_var.get()

        if operation == "Convert Coordinates":
            self.input_heading.configure(text="INPUT COORDINATES")
            self.source_label.pack(anchor="w", padx=15, before=self.input_fields_frame)
            self.source_menu.pack(fill="x", padx=15, pady=(5, 15), before=self.input_fields_frame)

            self.source_a_label.pack_forget()
            self.source_a_menu.pack_forget()
            self.source_b_label.pack_forget()
            self.source_b_menu.pack_forget()
            self.second_input_title.pack_forget()
            self.second_input_frame.pack_forget()
            self.apply_button.pack_forget()
            self.swap_button.pack(fill="x", padx=15, pady=5)
            self.convert_button.pack(fill="x", padx=15, pady=(15, 8), before=self.swap_button)

            self._build_coordinate_fields(
                self.input_fields_frame, self.source_var.get(), self.input_entries
            )
        else:
            self.input_heading.configure(text="VECTOR A")
            self.source_label.pack_forget()
            self.source_menu.pack_forget()
            self.swap_button.pack_forget()

            self.source_a_label.pack(anchor="w", padx=15, pady=(0, 2), before=self.input_fields_frame)
            self.source_a_menu.pack(fill="x", padx=15, pady=(2, 8), before=self.input_fields_frame)
            self._build_coordinate_fields(
                self.input_fields_frame, self.source_a_var.get(), self.input_entries
            )

            self.second_input_title.configure(text="VECTOR B")
            self.second_input_title.pack(
                anchor="w", padx=15, pady=(8, 0), before=self.target_label
            )
            self.source_b_label.pack(
                anchor="w", padx=15, pady=(5, 2), before=self.target_label
            )
            self.source_b_menu.pack(
                fill="x", padx=15, pady=(2, 8), before=self.target_label
            )
            self.second_input_frame.pack(fill="x", padx=10, before=self.target_label)
            self._build_coordinate_fields(
                self.second_input_frame, self.source_b_var.get(), self.second_entries
            )

            self.convert_button.pack_forget()
            self.apply_button.pack(fill="x", padx=15, pady=(15, 8), before=self.clear_button)

    def on_source_a_changed(self, _value=None):
        if self.operation_var.get() != "Convert Coordinates":
            self._build_coordinate_fields(
                self.input_fields_frame, self.source_a_var.get(), self.input_entries
            )

    def on_source_b_changed(self, _value=None):
        if self.operation_var.get() != "Convert Coordinates":
            self._build_coordinate_fields(
                self.second_input_frame, self.source_b_var.get(), self.second_entries
            )

    def update_output_labels(self):
        operation = self.operation_var.get()
        target = self.target_var.get()
        labels = self.COORDINATES[target]

        if operation == "Convert Coordinates":
            text = (
                "Converted coordinates in " + target + ":\n"
                + ", ".join(labels)
            )
        else:
            symbol = "+" if operation == "Vector Addition" else "−"
            text = (
                f"Vector operation: A {symbol} B\n"
                f"Result in {target}:\n"
                + ", ".join(labels)
            )

        self.result_label.configure(text=text)

    def on_source_changed(self, _value=None):
        if self.operation_var.get() == "Convert Coordinates":
            self.update_input_fields()
        self.update_output_labels()

    def on_target_changed(self, _value=None):
        self.update_output_labels()

    def on_operation_changed(self, _value=None):
        """Switch between coordinate conversion and vector-operation forms."""
        self.update_input_fields()
        self.update_output_labels()
        self.convert_button.configure(text="CONVERT")
        self.apply_button.configure(text="APPLY")

    # =========================
    # Coordinate Conversion and Vector Operations
    # =========================

    def _read_entries(self, entries, label):
        try:
            values = [float(entry.get()) for entry in entries]
        except ValueError as error:
            raise ValueError(
                f"Please enter three valid numerical values for {label}."
            ) from error

        if len(values) != 3 or not np.all(np.isfinite(values)):
            raise ValueError(
                f"{label} must contain exactly three finite numerical values."
            )
        return values

    def apply_operation(self):
        """Apply the selected vector addition or subtraction."""
        if self.operation_var.get() == "Convert Coordinates":
            self.convert_coordinates()
            return
        self.convert_coordinates()

    def convert_coordinates(self):
        try:
            target = self.target_var.get()
            operation = self.operation_var.get()

            if operation == "Convert Coordinates":
                source = self.source_var.get()
                values_a = self._read_entries(self.input_entries, "Input coordinates")
                cart_a = to_cartesian(values_a, source)
                result = transform(values_a, source, target)
                result_text = "Converted coordinates:\n\n"
                for label, value in zip(self.COORDINATES[target], result):
                    result_text += f"{label} = {value:.4f}\n"

                self.result_label.configure(text=result_text)
                self.draw_point(cart_a)
                return

            source_a = self.source_a_var.get()
            source_b = self.source_b_var.get()
            values_a = self._read_entries(self.input_entries, "Vector A")
            values_b = self._read_entries(self.second_entries, "Vector B")
            cart_a = to_cartesian(values_a, source_a)
            cart_b = to_cartesian(values_b, source_b)

            if operation == "Vector Addition":
                result_cart = cart_a + cart_b
                operation_symbol = "+"
            else:
                result_cart = cart_a - cart_b
                operation_symbol = "−"

            # Convert the Cartesian result to the selected output system.
            result = transform(result_cart, "Cartesian", target)

            result_text = (
                f"Vector operation: A {operation_symbol} B\n\n"
                "Result in Cartesian coordinates:\n"
                f"x = {result_cart[0]:.4f}\n"
                f"y = {result_cart[1]:.4f}\n"
                f"z = {result_cart[2]:.4f}\n\n"
                f"Result in {target}:\n"
            )
            for label, value in zip(self.COORDINATES[target], result):
                result_text += f"{label} = {value:.4f}\n"

            self.result_label.configure(text=result_text)
            self.draw_vectors(cart_a, cart_b, result_cart, operation_symbol)

        except ValueError as error:
            messagebox.showerror(
                "Invalid Input",
                str(error)
            )
        except Exception as error:
            messagebox.showerror(
                "Error",
                f"An unexpected error occurred:\n{error}"
            )

    # =========================
    # 3D Visualization
    # =========================

    def draw_empty_plot(self):
        self.ax.clear()
        self._style_3d_axes()
        self.ax.set_title(
            "3D Coordinate Visualization",
            color="white",
            fontsize=12,
            fontweight="bold",
            pad=14
        )
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.set_zlim(-10, 10)
        self._draw_origin_axes(10)
        self.ax.view_init(elev=25, azim=40)
        self.ax.set_box_aspect((1, 1, 1))
        self.canvas.draw_idle()

    def _style_3d_axes(self):
        self.ax.set_facecolor("#20252B")
        self.figure.patch.set_facecolor("#20252B")
        self.ax.xaxis.set_pane_color((0.12, 0.14, 0.17, 1.0))
        self.ax.yaxis.set_pane_color((0.12, 0.14, 0.17, 1.0))
        self.ax.zaxis.set_pane_color((0.12, 0.14, 0.17, 1.0))
        self.ax.set_xlabel("X", color="white", labelpad=8)
        self.ax.set_ylabel("Y", color="white", labelpad=8)
        self.ax.set_zlabel("Z", color="white", labelpad=8)
        self.ax.tick_params(colors="white", labelsize=8)
        self.ax.grid(True, linestyle=":", linewidth=0.6, alpha=0.45)

    def _draw_origin_axes(self, limit):
        self.ax.plot(
            [-limit, limit], [0, 0], [0, 0],
            color="#FF5555", linewidth=1.5, label="X-axis"
        )
        self.ax.plot(
            [0, 0], [-limit, limit], [0, 0],
            color="#55DD88", linewidth=1.5, label="Y-axis"
        )
        self.ax.plot(
            [0, 0], [0, 0], [-limit, limit],
            color="#5599FF", linewidth=1.5, label="Z-axis"
        )
        self.ax.scatter(
            [0], [0], [0], color="white", s=28,
            label="Origin", depthshade=False
        )

    def _draw_arrow(self, vector, color, label, linewidth=2.0):
        x, y, z = [float(value) for value in vector]
        if np.linalg.norm(vector) < 1e-12:
            self.ax.scatter([x], [y], [z], color=color, s=65, label=label)
            return
        self.ax.quiver(
            0, 0, 0, x, y, z,
            color=color,
            linewidth=linewidth,
            arrow_length_ratio=0.08,
            label=label
        )
        self.ax.scatter(
            [x], [y], [z],
            color=color, s=65,
            edgecolors="white", linewidths=0.7,
            depthshade=False
        )
        self.ax.text(
            x, y, z,
            f"  {label} ({x:.2f}, {y:.2f}, {z:.2f})",
            color="white", fontsize=8
        )

    def _finish_plot(self, vectors, title):
        values = [abs(float(component)) for vector in vectors for component in vector]
        max_range = max(values + [1.0]) * 1.3
        self._draw_origin_axes(max_range)

        self.ax.set_xlim(-max_range, max_range)
        self.ax.set_ylim(-max_range, max_range)
        self.ax.set_zlim(-max_range, max_range)
        self.ax.set_title(
            title, color="white", fontsize=12,
            fontweight="bold", pad=14
        )
        self.ax.view_init(elev=25, azim=40)
        self.ax.set_box_aspect((1, 1, 1))
        self.ax.legend(
            loc="upper left",
            fontsize=7,
            facecolor="#20252B",
            edgecolor="#555555",
            labelcolor="white"
        )
        self.canvas.draw_idle()

    def draw_point(self, point):
        self.ax.clear()
        self._style_3d_axes()
        point = np.asarray(point, dtype=float)
        self._draw_arrow(point, "#00D4FF", "Point P")
        self._finish_plot([point], "3D Coordinate Visualization")

    def draw_vectors(self, vector_a, vector_b, result, operation_symbol):
        self.ax.clear()
        self._style_3d_axes()

        # Draw input vectors and the result from the same origin.
        self._draw_arrow(vector_a, "#00D4FF", "Vector A")
        self._draw_arrow(vector_b, "#FFB84D", "Vector B")
        self._draw_arrow(result, "#D98CFF", f"Result A {operation_symbol} B", 2.6)

        # For addition, draw the parallelogram construction using dashed lines.
        # For subtraction, show A - B = A + (-B).
        if operation_symbol == "+":
            a = np.asarray(vector_a, dtype=float)
            b = np.asarray(vector_b, dtype=float)
            result_array = np.asarray(result, dtype=float)
            self.ax.plot(
                [a[0], result_array[0]], [a[1], result_array[1]],
                [a[2], result_array[2]],
                linestyle="--", color="#00D4FF", alpha=0.65, linewidth=1.2
            )
            self.ax.plot(
                [b[0], result_array[0]], [b[1], result_array[1]],
                [b[2], result_array[2]],
                linestyle="--", color="#FFB84D", alpha=0.65, linewidth=1.2
            )

        self._finish_plot(
            [vector_a, vector_b, result],
            f"3D Vector Operation: A {operation_symbol} B"
        )

    # =========================
    # Utility Buttons
    # =========================

    def swap_systems(self):
        old_source = self.source_var.get()
        old_target = self.target_var.get()
        self.source_var.set(old_target)
        self.target_var.set(old_source)
        self.update_input_fields()
        self.update_output_labels()

    def clear_fields(self):
        for entry in self.input_entries + self.second_entries:
            entry.delete(0, "end")

        self.result_label.configure(
            text="Enter coordinates and choose an operation."
        )
        self.draw_empty_plot()


# =========================
# Run Application
# =========================

if __name__ == "__main__":

    app = CoordinateApp()
    app.mainloop()

