# UNI RedCode

A 3D first-person shooter prototype built with Python and ModernGL.

---

## 📌 Description

**UNI RedCode** is a tech demo exploring 3D game development using Python. It features custom model loading, an interactive camera, real-time lighting, collision detection, and basic enemy AI — all built from scratch using ModernGL.

This project began as an educational experiment, and despite its simplicity, it reflects a growing understanding of OpenGL, shader programming, and engine structure.

> It may not be AAA, but it's fully mine.

---

## 🔧 Features

- ✅ 3D rendering with ModernGL
- ✅ First-person camera with collision detection
- ✅ Custom `OBJ` model loader with material/texture support
- ✅ Enemies that track and shoot at the player (`GreenDrone`, `BlueDrone`)
- ✅ Dynamic lighting (directional, spot, and point lights)
- ✅ Skybox implementation
- ✅ Bullet collision system (player and enemy projectiles)
- ✅ Weapon view model (`WeaponView`) with aiming and recoil animations
- ✅ Sound effect support (in progress)
- ✅ Includes a full-scale 3D model of the **Universidad Nacional de Ingeniería (UNI)** in Nicaragua

---

## ⚙️ Why Python + ModernGL?

Python was chosen for its ease of use and flexibility in rapid prototyping, especially when combined with [ModernGL](https://github.com/moderngl/moderngl), a simple and powerful wrapper over OpenGL. It allowed us to focus on gameplay systems and graphics logic without getting bogged down in verbose boilerplate.

For collision detection, **Oriented Bounding Boxes (OBB)** were used instead of axis-aligned boxes for better performance and accuracy when dealing with rotated or irregular 3D models.

The combination of Python + ModernGL + OBB collisions strikes a balance between **performance**, **simplicity**, and **flexibility** — making it ideal for a learning-oriented engine prototype.

---

## 🚀 Getting Started

### Prerequisites

Make sure you have **Python 3.12+** and the following packages installed:

--- 
bash
pip install PyQt5 moderngl numpy pywavefront pillow
python3 main.py --- Ubuntu
python main.py  --- Windows



## 🕹️ Controls

- WASD — Move
- Mouse — Look around
- Left Click — Shoot
- Right Click — Aim (Weapon animation)
- ESC — Exit (or close window)


## Project Structure

.
- ├── main.py                # Main application entry
- ├── model.py               # Custom 3D model class
- ├── bullet.py              # Bullet logic and collision
- ├── weapon.py              # Weapon base class
- ├── rifle.py / pistol.py / # FPS weapons
- ├── player.py              # Player controller
- ├── skybox.py              # Skybox rendering
- ├── entity.py              # Base class for every moving model
- ├── drone.py               # Base class for enemies
- ├── OrangeDrone            # Enemy with simple AI
- ├── GreenDrone.py          # Enemy with healing AI
- ├── BlueDrone.py           # Enemy with simple AI
- ├── crosshair.py           # crosshair visualization
- ├── bullet_manager.py      # bullet control and interactions
- └── models/                # OBJ models & mtl files
- └── textures/              # textures-skybox


## Credits
Built by Andres Aguilar, Henry Lechado and Brigham Lara, passionate students about learning game development from the ground up.
- Collaborators:
- @l3ch4d0301205-net
- @Bieliam 

Models by
- lev_229   https://sketchfab.com/lev_229
- bachklamk https://sketchfab.com/Bachklamk
- f3nix     https://sketchfab.com/f3nix


Based on personal research, experimentation, and docs from:
    ModernGL
    PyWavefront
    OpenGL & GLSL tutorials


## 📜 License
This project is open-source under the MIT License. Feel free to explore, learn, or contribute!



## 💬 Final Words

Even though this project is not finished, it's a clear representation of how much you can build with passion and Python. The journey has just begun — more features and polish will be added as learning continues.
