from math import sin, cos, pi, sqrt

from pyglet.gl import *

from mostro.modeling import *


class GameEventHandler(object):
    mouse_down = False
    mouse_orig_pos = [0, 0]
    rx, ry = 0, 0
    track = []  # 物体运行的轨迹点

    def on_mouse_drag(self, mouse_curr_x, mouse_curr_y, dx, dy, buttons, modifiers):
        if self.mouse_down:
            self.rx += mouse_curr_x - self.mouse_orig_pos[0]
            self.ry += 0.03 * (mouse_curr_y - self.mouse_orig_pos[1])
            if self.ry > 1.0:
                self.ry = 1.0
            elif self.ry < -1.0:
                self.ry = -1.0
            self.mouse_orig_pos[0] = mouse_curr_x
            self.mouse_orig_pos[1] = mouse_curr_y
        else:
            self.rx, self.ry = 0, 0

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.mouse_down = True
        self.mouse_orig_pos[0] = x
        self.mouse_orig_pos[1] = y
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_down = False
        pass

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        position = (2 * sin(model.integral_drift[0] / 2) / sqrt(model.integral_drift[0]),
                    2 * cos(model.integral_drift[1] / 2) / sqrt(model.integral_drift[1]))

        if len(self.track) < 200:  # 数组限制长度
            self.track.append(position)
        else:
            self.track.append(position)
            self.track.pop(0)

        gluLookAt(1.5 * cos(pi / 180 * self.rx), -self.ry, 1.5 * sin(pi / 180 * self.rx)
                  , 0, 0, 0, 0, 1, 0)

        glPushMatrix()
        glTranslatef(position[0], position[1], 0)
        model.batch.draw()
        glPopMatrix()

        glColor3f(1, 1, 1)
        glBegin(GL_LINE_STRIP)
        for v in self.track:
            glVertex3f(model.start_location[0] + v[0], model.start_location[1] + v[1], model.start_location[2])
        glEnd()

        glPushMatrix()
        glTranslatef(0, position[0], position[1])
        model.batch.draw()
        glPopMatrix()

        glColor3f(1, 1, 1)
        glBegin(GL_LINE_STRIP)
        for v in self.track:
            glVertex3f(model.start_location[0], model.start_location[1] + v[0], model.start_location[2] + v[1])
        glEnd()

    def on_key_press(self, symbol, modifiers):
        pass

    @staticmethod
    def on_resize(width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70., width / float(height), .1, 1000.)
        glMatrixMode(GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED


def scene_init():
    # One-time GL setup
    glClearColor(0, 0, 0, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glEnable(GL_BLEND)  # 启用混合功能，将图形颜色同周围颜色相混合
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_POLYGON_SMOOTH)  # 多边形抗锯齿
    # glHint(GL_POLYGON_SMOOTH, GL_NICEST)

    glEnable(GL_LINE_SMOOTH)  # 线抗锯齿
    # glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    glEnable(GL_POINT_SMOOTH)  # 点抗锯齿
    # glHint(GL_POINT_SMOOTH, GL_NICEST)

    # 材质如何设置？
    properties = model.scene.materials[0].properties
    ambient = properties['ambient']
    diffuse = properties['diffuse']
    specular = properties['specular']
    emission = properties['emissive']

    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, properties['shininess'])
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, array(ambient[0], ambient[1], ambient[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, array(diffuse[0], diffuse[1], diffuse[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, array(specular[0], specular[1], specular[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, array(emission[0], emission[1], emission[2], 0))
    pass


if __name__ == '__main__':
    window = pyglet.window.Window(resizable=True)  # , config=config)
    model = Model('face.obj', 'brmarble.png', 500)
    scene_init()  # 灯光和整体材质设置

    window.push_handlers(GameEventHandler())
    pyglet.app.event_loop.clock.schedule(model.update)

    pyglet.app.run()
