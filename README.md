# Coordinate Transformation

A Python-based GUI application for converting coordinates between different coordinate systems and performing 3D vector operations.

## Features

* **Coordinate Conversion:** Convert coordinates between Cartesian, Cylindrical, and Spherical systems.
* **Vector Addition:** Add two vectors represented in different coordinate systems.
* **Vector Subtraction:** Subtract one vector from another, even when they use different coordinate systems.
* **Independent Coordinate Systems:** Choose a separate coordinate system for each vector.
* **3D Visualization:** Display vectors in a three-dimensional plot.
* **Graphical User Interface:** Interact with the application through a user-friendly desktop interface.

## Supported Coordinate Systems

### 1. Cartesian Coordinates

Represented by:

* `x`: X-coordinate
* `y`: Y-coordinate
* `z`: Z-coordinate

### 2. Cylindrical Coordinates

Represented by:

* `ρ (rho)`: Radial distance from the Z-axis
* `φ (phi)`: Angle in the XY-plane, in degrees
* `z`: Height along the Z-axis

### 3. Spherical Coordinates

Represented by:

* `r`: Distance from the origin
* `θ (theta)`: Angle measured from the positive Z-axis, in degrees
* `φ (phi)`: Azimuthal angle in the XY-plane, in degrees

## Technologies Used

* Python
* NumPy
* CustomTkinter
* Matplotlib

## Installation

### Prerequisites

Make sure Python is installed on your computer.

### Steps

1. Clone the repository:

   ```bash
   git clone <YOUR_REPOSITORY_URL>
   ```

2. Navigate to the project directory:

   ```bash
   cd Coordinate-Transformation
   ```

3. (Optional but recommended) Create a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment.

   **Windows:**

   ```bash
   venv\Scripts\activate
   ```

5. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

6. Run the application:

   ```bash
   python main.py
   ```

> Replace `main.py` with the actual name of your main Python file if it is different.

## Project Structure

```text
Coordinate-Transformati
```

