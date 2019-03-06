import glfw
import ShaderLoader as sl
import numpy
import pyrr
from OpenGL.GL import *
from PIL import Image
from ObjLoader import *


# Растягивание основного окна
def window_resize(window, width, height):
    glViewport(0, 0, width, height)


# Попытка сделать перемещение окна не "проблемой" для анимации
def main():
    # Инициализация
    if not glfw.init():
        return

    window_width, window_height = 800, 600
    window = glfw.create_window(window_width, window_height, "anton.nikolaev.kazan@gmail.com // Python 3.6.2", None, None)

    # если не удалось создать окно
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, window_resize)

    obj = ObjLoader()
    obj.load_model('resource/face.obj')

    # Смещение текстуры и нормалей
    texture_offset = len(obj.vertex_index) * 12
    normal_offset = (texture_offset + len(obj.texture_index) * 8)

    shader = sl.compile_shader('shaders/vertex.vs', 'shaders/fragment.fs')

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, obj.model.itemsize * len(obj.model), obj.model, GL_STATIC_DRAW)

    # Позиции
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, obj.model.itemsize * 3, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Текстуры
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, obj.model.itemsize * 2, ctypes.c_void_p(texture_offset))
    glEnableVertexAttribArray(1)

    # Нормали
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, obj.model.itemsize * 3, ctypes.c_void_p(normal_offset))
    glEnableVertexAttribArray(2)

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # Параметры обертки текстуры
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # Пармаетры фильтрации текстуры
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Загрузка
    image = Image.open('resource/african_head_diffuse.tga')
    flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = numpy.array(list(flipped_image.getdata()), numpy.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glEnable(GL_TEXTURE_2D)

    glUseProgram(shader)

    # Фон
    glClearColor(0.0, 0.0, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Показать только ребра полигонов без текстур
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Настройки "камеры"
    view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -3.0]))
    projection = pyrr.matrix44.create_perspective_projection_matrix(50.0, window_width / window_height, 0.1, 100.0)
    model = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -1.0]))  # x y z "отступы"

    # Работа с шейдером
    view_loc = glGetUniformLocation(shader, 'view')
    proj_loc = glGetUniformLocation(shader, 'projection')
    model_loc = glGetUniformLocation(shader, 'model')
    transform_loc = glGetUniformLocation(shader, 'transform')
    light_loc = glGetUniformLocation(shader, 'light')

    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

    # Главный цикл
    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Матрицы вращения
        rot_x = pyrr.Matrix44.from_x_rotation(0.0 * glfw.get_time())
        rot_y = pyrr.Matrix44.from_y_rotation(0.15 * glfw.get_time())
        rot_z = pyrr.Matrix44.from_z_rotation(0.0 * glfw.get_time())

        # Вращение модели по xyz
        glUniformMatrix4fv(transform_loc, 1, GL_FALSE, rot_x * rot_y * rot_z)
        glUniformMatrix4fv(light_loc, 1, GL_FALSE, rot_x * rot_y * rot_z * 5)  # 5 == "сила света"

        glDrawArrays(GL_TRIANGLES, 0, len(obj.vertex_index))

        glfw.swap_buffers(window)

    # Выход
    glfw.terminate()


if __name__ == "__main__":
    main()
