import pygame
from pygame.locals import *
import OpenGL.GL as gl
import numpy as np
import time
import sys

VERTEX_SHADER_SRC = """
#version 330 core
layout(location = 0) in vec2 aPos;
out vec2 vUV;
void main()
{
    vUV = aPos * 0.5 + 0.5;
    gl_Position = vec4(aPos, 0.0, 1.0);
}
"""

FRAGMENT_SHADER_SRC = """
#version 330 core
out vec4 fragColor;
in vec2 vUV;

uniform vec3 iResolution;
uniform float iTime;

// Simple sinusoidal noise-based color background
float noise(vec2 p) {
    return sin(p.x) * cos(p.y);
}

void main() {
    vec2 uv = vUV * iResolution.xy / iResolution.y;
    float t = iTime * 0.3;

    // Compose sinusoidal patterns
    float n = sin(uv.x * 2.0 + t) 
            + cos(uv.y * 3.0 - t * 1.5)
            + sin((uv.x + uv.y) * 1.5 + t * 0.7);
    n = n / 3.0; // normalize [-1,1]
    
    // Color gradient
    vec3 col = vec3(0.4 + 0.3 * sin(n * 2.0 + t),
                    0.2 + 0.4 * cos(n * 3.0 - t * 0.5),
                    0.5 + 0.5 * sin(n * 1.5 + t * 0.3));
    
    fragColor = vec4(col, 1.0);
}
"""

def compile_shader(source, shader_type):
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        raise RuntimeError(gl.glGetShaderInfoLog(shader).decode())
    return shader

def create_program(vs_src, fs_src):
    vs = compile_shader(vs_src, gl.GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, gl.GL_FRAGMENT_SHADER)
    prog = gl.glCreateProgram()
    gl.glAttachShader(prog, vs)
    gl.glAttachShader(prog, fs)
    gl.glLinkProgram(prog)
    if not gl.glGetProgramiv(prog, gl.GL_LINK_STATUS):
        raise RuntimeError(gl.glGetProgramInfoLog(prog).decode())
    gl.glDeleteShader(vs)
    gl.glDeleteShader(fs)
    return prog

def main():
    pygame.init()
    width, height = 960, 540
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Sinusoidal Noise Background")

    program = create_program(VERTEX_SHADER_SRC, FRAGMENT_SHADER_SRC)
    gl.glUseProgram(program)

    # Full-screen quad
    verts = np.array([
        -1.0, -1.0,
         1.0, -1.0,
         1.0,  1.0,
        -1.0, -1.0,
         1.0,  1.0,
        -1.0,  1.0
    ], dtype=np.float32)

    vao = gl.glGenVertexArrays(1)
    vbo = gl.glGenBuffers(1)
    gl.glBindVertexArray(vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, verts.nbytes, verts, gl.GL_STATIC_DRAW)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 0, None)

    loc_res = gl.glGetUniformLocation(program, "iResolution")
    loc_time = gl.glGetUniformLocation(program, "iTime")

    start_time = time.time()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

        t = time.time() - start_time
        gl.glViewport(0, 0, width, height)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glUseProgram(program)
        gl.glUniform3f(loc_res, float(width), float(height), 0.0)
        gl.glUniform1f(loc_time, float(t))

        gl.glBindVertexArray(vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        gl.glBindVertexArray(0)

        pygame.display.flip()
        clock.tick(60)

    gl.glDeleteProgram(program)
    gl.glDeleteBuffers(1, [vbo])
    gl.glDeleteVertexArrays(1, [vao])
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
