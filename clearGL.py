import sys
from PyQt5.QtWidgets import *
from OpenGL.GL import *
from OpenGL.GLU import *
from scipy.spatial.transform import Rotation as R
import numpy as np


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        # camera quaternion
        self.camera_rot = R.identity()
        # object quaternion
        self.object_rot = R.identity()

        self.camera_distance = -10
        self.pointCloud = []
        self.model_loaded = False

    def initializeGL(self):
        # enable depth test
        glEnable(GL_DEPTH_TEST)
        # background color
        glClearColor(0.1, 0.1, 0.1, 1.0)
        if not self.model_loaded:
            self.pointCloud = self.parser("3z16.ply")
            self.model_loaded = True

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h != 0 else 1, 1, 100)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        cam_pos = self.camera_rot.apply([0, 0, self.camera_distance])
        gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2],
                  0, 0, 0,
                  0, 1, 0)

        # Applying object rotation
        # 4x4 identity matrix because OpenGL requires that size
        rotation_matrix = np.eye(4)
        # replacing a 3x3 submatrix with a quaternion
        rotation_matrix[:3, :3] = self.object_rot.as_matrix()
        # Transpose, array conversion and multiplication
        glMultMatrixf(rotation_matrix.T.flatten())

        self.drawObject()

    @staticmethod
    def parser(ply_obj=None):
        if ply_obj is not None:
            with open(ply_obj, 'r') as f:
                lines = f.readlines()

            # Variables for storing data
            header = []
            vertices = []

            # Reading header
            in_header = True
            vertex_count = 0

            for line in lines:
                if in_header:
                    header.append(line.strip())
                    if line.startswith('element vertex'):
                        vertex_count = int(line.split()[2])
                    elif line.startswith('end_header'):
                        in_header = False
                else:
                    # Reading data
                    if vertex_count > 0:
                        line_vert = line.strip().split()
                        if len(line_vert) >= 3:
                            if line_vert[0] != -0.0 and line_vert[1] != 0.0 and line_vert[2] != 0.0:
                                vertices.append(line_vert[:3])
                            vertex_count -= 1

            vertex_float = [[float(item) for item in row] for row in vertices]
            return vertex_float

    def drawObject(self):
        vertices = self.pointCloud

        glBegin(GL_POINTS)
        glColor3f(0, 1, 0.5)

        for vertex in vertices:
            glVertex3fv(vertex)

        glEnd()

    # rot * self.camera_rot - global
    # self.camera_rot * rot - local
    def rotate_camera_horizontal(self, rad):
        rot = R.from_euler('x', rad)
        self.camera_rot = rot * self.camera_rot
        self.update()

    def rotate_camera_vertical(self, rad):
        rot = R.from_euler('y', rad)
        self.camera_rot = rot * self.camera_rot
        self.update()

    def rotate_camera_side(self, rad):
        rot = R.from_euler('z', rad)
        self.object_rot = self.object_rot * rot
        self.update()

    def zoom_camera(self, delta):
        self.camera_distance += delta
        self.update()

    def default_camera_set(self):
        self.camera_rot = R.identity()
        self.object_rot = R.identity()
        self.camera_distance = -10
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("OpenGLGUI")
        self.resize(800, 600)

        # MAIN WIDGET
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # LAYOUT
        layout = QGridLayout(central_widget)

        # OpenGL-WIDGET
        self.opengl_widget = OpenGLWidget()
        layout.addWidget(self.opengl_widget, 0, 0, 1, 4)

        # Button panel
        btn_rotate_x = QPushButton("←")
        btn_rotate_y = QPushButton("↓")
        btn_rotate_z = QPushButton("↻")
        btn_rotate__x = QPushButton("→")
        btn_rotate__y = QPushButton("↑")
        btn_rotate__z = QPushButton("↺")
        btn_zoom_in = QPushButton("+")
        btn_zoom_out = QPushButton("-")
        btn_default = QPushButton("Default")

        layout.addWidget(btn_rotate_x, 1, 0)
        layout.addWidget(btn_rotate__x, 1, 1)
        layout.addWidget(btn_rotate_y, 2, 0)
        layout.addWidget(btn_rotate__y, 2, 1)
        layout.addWidget(btn_rotate_z, 3, 0)
        layout.addWidget(btn_rotate__z, 3, 1)
        layout.addWidget(btn_zoom_in, 1, 3)
        layout.addWidget(btn_zoom_out, 2, 3)
        layout.addWidget(btn_default, 3, 3)

        # Button bindings
        ## x - left/right, y - up/down, z - clockwise/counterclockwise ##
        btn_rotate_x.clicked.connect(lambda: self.opengl_widget.rotate_camera_vertical(0.1))
        btn_rotate_y.clicked.connect(lambda: self.opengl_widget.rotate_camera_horizontal(0.1))
        btn_rotate_z.clicked.connect(lambda: self.opengl_widget.rotate_camera_side(0.1))
        btn_rotate__x.clicked.connect(lambda: self.opengl_widget.rotate_camera_vertical(-0.1))
        btn_rotate__y.clicked.connect(lambda: self.opengl_widget.rotate_camera_horizontal(-0.1))
        btn_rotate__z.clicked.connect(lambda: self.opengl_widget.rotate_camera_side(-0.1))
        btn_zoom_in.clicked.connect(lambda: self.opengl_widget.zoom_camera(0.5))
        btn_zoom_out.clicked.connect(lambda: self.opengl_widget.zoom_camera(-0.5))
        btn_default.clicked.connect(lambda: self.opengl_widget.default_camera_set())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
