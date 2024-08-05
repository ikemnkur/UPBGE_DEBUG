import sys
import bge
import math
import mathutils
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QFormLayout,
    QComboBox,
    QScrollArea,
)
from PyQt5.QtCore import QTimer

class DebuggerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BGE Debugger")
        self.setGeometry(100, 100, 800, 600)

        # Layouts
        self.main_layout = QVBoxLayout()
        self.control_layout = QHBoxLayout()
        self.search_layout = QHBoxLayout()

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Game Objects...")
        self.search_bar.textChanged.connect(self.filter_objects)
        self.search_layout.addWidget(QLabel("Search:"))
        self.search_layout.addWidget(self.search_bar)

        # Game Controls
        self.fps_input = QLineEdit("60")
        self.fps_input.setFixedWidth(50)
        self.fps_button = QPushButton("Set FPS")
        self.fps_button.clicked.connect(self.set_fps)

        self.speed_input = QLineEdit("1.0")
        self.speed_input.setFixedWidth(50)
        self.speed_button = QPushButton("Set Game Speed")
        self.speed_button.clicked.connect(self.set_game_speed)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_game)
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_game)
        self.step_button = QPushButton("Step Frame")
        self.step_button.clicked.connect(self.step_frame)

        self.toggle_physics_button = QPushButton("Toggle Physics Viz")
        self.toggle_physics_button.clicked.connect(self.toggle_physics_visualization)
        self.toggle_mouse_button = QPushButton("Toggle Mouse")
        self.toggle_mouse_button.clicked.connect(self.toggle_mouse)

        self.control_layout.addWidget(QLabel("FPS:"))
        self.control_layout.addWidget(self.fps_input)
        self.control_layout.addWidget(self.fps_button)
        self.control_layout.addWidget(QLabel("Game Speed:"))
        self.control_layout.addWidget(self.speed_input)
        self.control_layout.addWidget(self.speed_button)
        self.control_layout.addWidget(self.pause_button)
        self.control_layout.addWidget(self.play_button)
        self.control_layout.addWidget(self.step_button)
        self.control_layout.addWidget(self.toggle_physics_button)
        self.control_layout.addWidget(self.toggle_mouse_button)

        # Tabs for Properties
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_tab_widget("Physics"), "Physics")
        self.tabs.addTab(self.create_tab_widget("Game"), "Game")
        self.tabs.addTab(self.create_tab_widget("Transform"), "Transform")
        self.tabs.addTab(self.create_tab_widget("Materials"), "Materials")
        self.tabs.addTab(self.create_tab_widget("Animations"), "Animations")
        self.tabs.addTab(self.create_tab_widget("Logic Sensors"), "Logic Sensors")

        # Scroll Area for Object List
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.object_list_widget = QWidget()
        self.object_list_layout = QVBoxLayout()
        self.object_list_widget.setLayout(self.object_list_layout)
        self.scroll_area.setWidget(self.object_list_widget)

        self.main_layout.addLayout(self.search_layout)
        self.main_layout.addLayout(self.control_layout)
        self.main_layout.addWidget(QLabel("Objects:"))
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.tabs)
        self.setLayout(self.main_layout)

        # Timer to update properties
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.refresh_properties)
        self.update_timer.start(500)  # Update twice per second

        self.selected_object = None
        self.update_object_list()

    def create_tab_widget(self, category):
        """Creates a tab with a form layout for displaying properties."""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)
        return widget

    def update_object_list(self):
        """Updates the list of game objects."""
        scene = bge.logic.getCurrentScene()
        self.object_list_layout.setParent(None)
        self.object_list_layout = QVBoxLayout()
        self.object_list_widget.setLayout(self.object_list_layout)
        
        for obj in scene.objects:
            button = QPushButton(obj.name)
            button.clicked.connect(lambda checked, name=obj.name: self.select_object(name))
            self.object_list_layout.addWidget(button)

    def filter_objects(self, text):
        """Filter the object list based on the search text."""
        for i in range(self.object_list_layout.count()):
            button = self.object_list_layout.itemAt(i).widget()
            if button:
                button.setVisible(text.lower() in button.text().lower())

    def select_object(self, object_name):
        """Selects a game object and updates the properties tabs."""
        self.selected_object = object_name
        self.update_properties_tabs()

    def update_properties_tabs(self):
        """Updates the property tabs for the selected object."""
        if not self.selected_object:
            return

        scene = bge.logic.getCurrentScene()
        obj = scene.objects.get(self.selected_object)
        if not obj:
            return

        # Clear existing widgets in tabs
        for index in range(self.tabs.count()):
            widget = self.tabs.widget(index)
            layout = widget.layout()
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().deleteLater()

        # Populate tabs with properties
        self.populate_physics_tab(obj)
        self.populate_game_tab(obj)
        self.populate_transform_tab(obj)
        self.populate_materials_tab(obj)
        self.populate_animations_tab(obj)
        self.populate_logic_sensors_tab(obj)

    def populate_physics_tab(self, obj):
        """Populate the physics tab with object physics properties."""
        tab = self.tabs.widget(0)
        layout = tab.layout()

        if obj.getPhysicsId():
            layout.addRow("Mass:", QLabel(str(truncate(obj.mass))))
            layout.addRow("Linear Velocity:", QLabel(str(truncate(obj.linearVelocity))))
            layout.addRow("Angular Velocity:", QLabel(str(truncate(obj.angularVelocity))))
        else:
            layout.addRow(QLabel("No physics properties available."))

    def populate_game_tab(self, obj):
        """Populate the game tab with object game properties."""
        tab = self.tabs.widget(1)
        layout = tab.layout()

        for key in obj.getPropertyNames():
            value = obj[key]
            label = QLabel(f"{key}: {truncate(value)}")
            layout.addRow(label)

    def populate_transform_tab(self, obj):
        """Populate the transform tab with object transform properties."""
        tab = self.tabs.widget(2)
        layout = tab.layout()

        layout.addRow("Position:", QLabel(f"X: {truncate(obj.worldPosition.x)}, Y: {truncate(obj.worldPosition.y)}, Z: {truncate(obj.worldPosition.z)}"))
        layout.addRow("Rotation:", QLabel(f"X: {truncate(math.degrees(obj.worldOrientation.to_euler().x))}, Y: {truncate(math.degrees(obj.worldOrientation.to_euler().y))}, Z: {truncate(math.degrees(obj.worldOrientation.to_euler().z))}"))
        layout.addRow("Scale:", QLabel(f"X: {truncate(obj.worldScale.x)}, Y: {truncate(obj.worldScale.y)}, Z: {truncate(obj.worldScale.z)}"))

    def populate_materials_tab(self, obj):
        """Populate the materials tab with object material properties."""
        tab = self.tabs.widget(3)
        layout = tab.layout()

        if hasattr(obj, 'meshes') and obj.meshes:
            materials = [mat.name for mat in obj.meshes[0].materials]
            layout.addRow("Materials:", QLabel(", ".join(materials)))
        else:
            layout.addRow(QLabel("No materials available."))

    def populate_animations_tab(self, obj):
        """Populate the animations tab with object animation properties."""
        tab = self.tabs.widget(4)
        layout = tab.layout()

        layout.addRow(QLabel("No animation data available."))  # Placeholder for animation data

    def populate_logic_sensors_tab(self, obj):
        """Populate the logic sensors tab with object logic sensors."""
        tab = self.tabs.widget(5)
        layout = tab.layout()

        layout.addRow(QLabel("No logic sensors available."))  # Placeholder for logic sensors

    def refresh_properties(self):
        """Refreshes the displayed property values of the selected object."""
        self.update_object_list()
        self.update_properties_tabs()

    def set_fps(self):
        """Set the game's frames per second."""
        try:
            fps = float(self.fps_input.text())
            bge.logic.setLogicTicRate(fps)
            print(f"FPS set to {fps}")
        except ValueError:
            print("Invalid FPS value.")

    def set_game_speed(self):
        """Set the game speed."""
        try:
            speed = float(self.speed_input.text())
            bge.logic.setTimeScale(speed)
            print(f"Game speed set to {speed}")
        except ValueError:
            print("Invalid game speed value.")

    def pause_game(self):
        """Pause the game."""
        bge.logic.setTimeScale(0)
        print("Game paused.")

    def play_game(self):
        """Resume the game."""
        bge.logic.setTimeScale(1)
        print("Game resumed.")

    def step_frame(self):
        """Step the game one frame forward."""
        bge.logic.nextFrame()
        print("Stepped one frame forward.")

    def toggle_physics_visualization(self):
        """Toggle physics visualization."""
        # Placeholder for actual physics visualization toggling
        print("Physics visualization toggled (not implemented).")

    def toggle_mouse(self):
        """Toggle mouse visibility."""
        global mouse_visible
        mouse_visible = not mouse_visible
        bge.render.showMouse(mouse_visible)
        print(f"Mouse visibility set to {mouse_visible}")

def truncate(value, digits=3):
    """Truncate a float or list of floats to a specific number of decimal places."""
    if isinstance(value, float):
        return round(value, digits)
    elif isinstance(value, (list, mathutils.Vector, mathutils.Euler)):
        return [truncate(v, digits) for v in value]
    return value

def run_gui():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create and show the debugger window
    window = DebuggerWindow()
    window.show()

    return app, window

def start_gui(cont):
    # Get the game object
    obj = cont.owner

    # Check if the GUI is already initialized using an object property
    if 'gui_initialized' not in obj:
        obj['app'], obj['window'] = run_gui()
        obj['gui_initialized'] = True

    # Process PyQt5 events to keep the UI responsive
    if 'app' in obj:
        obj['app'].processEvents()

# Setup the logic brick to run this function every frame
if __name__ == "__main__":
    cont = bge.logic.getCurrentController()
    start_gui(cont)
