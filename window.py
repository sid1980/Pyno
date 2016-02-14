import pyglet
from pyglet.gl import *
from random import randint
import clipboard

import draw
from node import Node
from codeEditor import CodeEditor
from field import Field
from utils import *

# pyglet.options['debug_gl'] = False  # performance boost?


class PynoWindow(pyglet.window.Window):
    # Main pyno window. It's gray with logo in bottom.
    # It handles all elements and controls

    nodes = []
    selectedNodes = []

    pynoSpace = {}  # local space for in-pyno programms

    codeEditor = None
    field = None
    nodeDrag = False
    select = False
    connection = False
    connectNode = None

    w, c = (0, 0), (0, 0)
    pointer = (0, 0)
    pan_scale = [[0.0, 0.0], 1]

    flipper = False

    def __init__(self, config):
        super().__init__(resizable=True, caption='Pyno', config=config)
        self.set_minimum_size(320, 200)
        self.set_size(800, 600)
        # set window position to center
        screen = self.display.get_default_screen()
        self.set_location(screen.width // 2 - 400, screen.height // 2 - 300)

        pyglet.gl.glClearColor(0.14, 0.14, 0.14, 0)

        pyglet.clock.schedule(self.update)
        pyglet.clock.set_fps_limit(60)

        self.pynoSpace['G'] = self.pynoSpace

        self.batch = pyglet.graphics.Batch()
        # load pyno-logo in left bottom
        self.pyno_logo = pyglet.image.load('imgs/corner.png')
        # first-meta-node to be
        Node(-9000, 9000, self.batch, (0, 0, 0))

    def update(self, dt):
        self.pynoSpace['dt'] = dt

        # ---- Calculations ----

        for node in self.nodes:
            # if not node.problem:
            node.proc_result = None

        for node in self.nodes:
            node.processor(self.pynoSpace)

    def on_draw(self):
        # ---- BG ----

        self.clear()
        self.pyno_logo.blit(0, 0)

        # ---- NODES ----

        ps = self.pan_scale
        glTranslatef(self.width / 2, self.height / 2, 0)
        glScalef(ps[1], ps[1], ps[1])
        glTranslatef(-self.width / 2 + ps[0][0],
                     -self.height / 2 + ps[0][1], 0.0)

        for node in self.nodes:
            node.render_base(self.batch)

        if self.connection:
            p = self.pointer
            cn = self.connectNode
            n = self.connectNode['node']

            if self.connectNode['mode'] == 'input':
                start = n.put_pos_by_name(cn['put']['name'], 'inputs')
                draw.line((start, n.y + n.ch + n.offset // 2),
                          (start, n.y + n.ch + n.offset), self.batch)
                draw.line((start, n.y + n.ch + n.offset),
                          (p[0], p[1]), self.batch)

            elif self.connectNode['mode'] == 'output':
                start = n.put_pos_by_name(cn['put']['name'], 'outputs')
                draw.line((start, n.y - n.ch - n.offset // 2),
                          (start, n.y - n.ch - n.offset), self.batch)
                draw.line((start, n.y - n.ch - n.offset),
                          (p[0], p[1]), self.batch)

        self.batch.draw()

        if ps[1] > 0.4:
            for node in self.nodes:
                node.render()

        if self.codeEditor:
            self.codeEditor.render()

        if self.select:
            draw.selector(self.w, self.c)

        # ---- GUI ----

        glLoadIdentity()
        # self.fps.draw()

    # ---- Inputs ----

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = x_y_pan_scale(x, y, self.pan_scale, self.get_size())

        self.pointer = (x, y)

        self.flipper = True if not self.flipper else False

        if len(self.selectedNodes) == 0:
            if self.codeEditor:
                if self.codeEditor.intersect_point((x, y)):
                    if not self.codeEditor.hover and not self.field:
                        self.push_handlers(self.codeEditor)
                    self.codeEditor.pan_scale = self.pan_scale
                    self.codeEditor.screen_size = self.get_size()
                    self.codeEditor.hover = True
                    self.codeEditor.node.hover = True
                    return
            elif self.field:
                if self.field.intersect_point((x, y)):
                    self.field.pan_scale = self.pan_scale
                    self.field.screen_size = self.get_size()

            nodes_length = len(self.nodes)
            if nodes_length > 10:
                if self.flipper:
                    check_nodes = self.nodes[nodes_length // 2:]
                else:
                    check_nodes = self.nodes[:nodes_length // 2]
            else:
                check_nodes = self.nodes

            for node in check_nodes:
                node.intersect_point((x, y))

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = x_y_pan_scale(x, y, self.pan_scale, self.get_size())

        if button == 1:
            if self.field:
                self.pop_handlers()
                self.push_handlers()
                self.field = None
            if self.codeEditor:
                if self.codeEditor.intersect_point((x, y)):
                    return
                else:
                    if self.codeEditor.hover:
                        self.pop_handlers()
                        self.push_handlers()
                    self.codeEditor.node.code = self.codeEditor.document.text
                    self.codeEditor.update_node()
                    self.codeEditor = None
            for node in self.nodes:
                if node.intersect_point((x, y), False):
                    if (node in self.selectedNodes
                    and len(self.selectedNodes) > 1):
                        self.nodeDrag = True
                        return
                    else:
                        if (node.selectedInput['name'] != 'none'
                        or node.selectedOutput['name'] != 'none'):
                            self.pointer = (x, y)
                            self.connection = True
                            if node.selectedInput['name'] != 'none':
                                for c in node.connectedTo:
                                    a = c['output']
                                    if (c['input']['put']['name'] ==
                                        node.selectedInput['name']):
                                        self.connectNode = {'node': a['node'],
                                              'put': {'name': a['put']['name']},
                                              'mode': 'output'}
                                        n = node.connectedTo
                                        del n[n.index(c)]
                                        return
                                self.connectNode = {'node': node,
                                                 'put': node.selectedInput,
                                                 'mode': 'input'}
                                return
                            elif node.selectedOutput['name'] != 'none':
                                self.connectNode = {'node': node,
                                                 'put': node.selectedOutput,
                                                 'mode': 'output'}
                            return
                        if isinstance(node, Node):
                            self.codeEditor = CodeEditor(node)
                        elif (isinstance(node, Field)
                              and not self.field):
                            self.push_handlers(node)
                            self.field = node
                        self.selectedNodes = [node]
                        self.nodeDrag = True
                        return
            self.select = True
            self.selectPoint = (x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x, y = x_y_pan_scale(x, y, self.pan_scale, self.get_size())
        dx, dy = int(dx / self.pan_scale[1]), int(dy / self.pan_scale[1])

        if self.nodeDrag and buttons != 5:
            for node in self.selectedNodes:
                node.x += dx
                node.y += dy
                if isinstance(node, Field):
                    node.style()
        elif self.select:
            self.w = self.selectPoint
            self.c = (x, y)
            for node in self.nodes:
                if point_intersect_quad((node.x, node.y), (self.c + self.w)):
                    node.draw_color = node.inverse(node.color)
                else:
                    node.draw_color = node.color
        elif self.connection:
            self.pointer = (x, y)
            for node in self.nodes:
                node.intersect_point((x, y))

        if buttons == 4 or buttons == 5:
            self.pan_scale[0][0] += dx
            self.pan_scale[0][1] += dy

    def on_mouse_release(self, x, y, button, modifiers):
        x, y = x_y_pan_scale(x, y, self.pan_scale, self.get_size())

        if button == 1:
            self.nodeDrag = False
            self.connection = False

            if self.select:
                self.select = []
                for node in self.nodes:
                    if point_intersect_quad((node.x, node.y),
                                            (self.c + self.w)):
                        self.select.append(node)
                        node.draw_color = node.inverse(node.color)
                self.selectedNodes = self.select
                self.w, self.c = (0, 0), (0, 0)
                self.select = False
            else:
                self.selectedNodes = []

            if self.connectNode:
                for node in self.nodes:
                    if node.intersect_point((x, y)):
                        if node != self.connectNode['node']:

                            if (node.selectedInput['name'] != 'none'
                            and self.connectNode['mode'] == 'output'):
                                del self.connectNode['mode']
                                another = {'node': node,
                                           'put': node.selectedInput}
                                insert = {'output': self.connectNode,
                                          'input': another}

                                i = node.selectedInput
                                for input in node.connectedTo:
                                    if (input['input']['put']['name']
                                                                  == i['name']):
                                        n = node.connectedTo
                                        del n[n.index(input)]
                                        break

                                if not (insert in node.connectedTo):
                                    node.connectedTo.append(insert)
                                    print('Connect output to input')

                            elif (node.selectedOutput['name'] != 'none'
                            and self.connectNode['mode'] == 'input'):
                                del self.connectNode['mode']
                                another = {'node': node,
                                           'put': node.selectedOutput}
                                insert = {'output': another,
                                          'input': self.connectNode}

                                n = self.connectNode['node']
                                if not (insert in n.connectedTo):
                                    n.connectedTo.append(insert)
                                    print('Connect input to output')

                self.connectNode = None

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        di = 10
        max_zoom = 1

        ps = self.pan_scale
        zoom = scroll_y / di * ps[1]

        if ps[1] + zoom < max_zoom:
            ps[1] += zoom
            ps[0][0] -= ((-self.width / 2 + x) / ps[1] * scroll_y) // di
            ps[0][1] -= ((-self.height / 2 + y) / ps[1] * scroll_y) // di
        elif ps[1] < max_zoom:
            ps[1] = max_zoom
            ps[0][0] -= ((-self.width / 2 + x) / 2 * scroll_y) // di
            ps[0][1] -= ((-self.height / 2 + y) / 2 * scroll_y) // di

    def on_key_press(self, symbol, modifiers):
        key = pyglet.window.key

        if not (self.codeEditor or self.field):
            if symbol == key.N:
                self.nodes.append(Node(self.pointer[0],
                                  self.pointer[1], self.batch,
                                  (randint(80, 130),
                                   randint(80, 130),
                                   randint(80, 130))))

            elif symbol == key.F:
                self.nodes.append(Field(self.pointer[0], self.pointer[1],
                                        self.batch))

            if modifiers & key.MOD_CTRL:
                x, y = self.pointer[0], self.pointer[1]

                # ---- Copy paste ----

                if symbol == key.C:
                    nodesBuffer = []
                    for node in self.selectedNodes:
                        if isinstance(node, Node):
                            nodesBuffer.append({'type': 'node',
                                                'x': node.x - x,
                                                'y': node.y - y,
                                                'size': node.editorSize,
                                                'color': node.color,
                                                'code': node.code,
                                                'connects': node.get_con_id(),
                                                'parent': node.id})
                        elif isinstance(node, Field):
                            nodesBuffer.append({'type': 'field',
                                                'x': node.x - x,
                                                'y': node.y - y,
                                                'size': (node.w, node.h),
                                                'code': node.document.text,
                                                'connects': node.get_con_id(),
                                                'parent': node.id})
                    clipboard.copy(str(nodesBuffer))
                    print('Copy ' + str(len(nodesBuffer)) + ' nodes')

                elif symbol == key.V:
                    buff = []
                    try:
                        paste = eval(clipboard.paste())
                        for node in paste:
                            if node['type'] == 'node':
                                buff.append([Node(node['x'] + x,
                                                  node['y'] + y,
                                                  self.batch,
                                                  node['color'],
                                                  node['code'],
                                                  node['connects'],
                                                  node['size']),
                                             node['parent']])
                            elif node['type'] == 'field':
                                buff.append([Field(node['x'] + x,
                                                   node['y'] + y,
                                                   node['code'],
                                                   node['connects'],
                                                   node['size']),
                                             node['parent']])
                    except:
                        print('Wrong paste!')
                    else:
                        for node in buff:
                            node[0].reconnect(buff)
                            self.nodes.append(node[0])
                        print('Paste ' + str(len(buff)) + ' nodes')

            if symbol == key.DELETE:
                for node in self.selectedNodes:
                    node.delete()
                    self.nodes[self.nodes.index(node)].outputs = ()
                    del self.nodes[self.nodes.index(node)]
                    print('Delete node')
                self.selectedNodes = []

            elif symbol == key.HOME:
                self.pan_scale = [[0.0, 0.0], 1]

            elif symbol == key.F1:
                for node in self.self.selectedNodes:
                    print(node.proc_result)

            elif symbol == key.END:
                print(len(self.nodes))
                for node in self.selectedNodes:
                    print(str(node))