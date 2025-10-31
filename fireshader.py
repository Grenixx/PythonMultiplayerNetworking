"""
fireball_pygame.py
Pygame + PyOpenGL demo running your GLSL fragment shader (ported from the GLSL sandbox code).
Requirements:
    pip install pygame PyOpenGL numpy
"""

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
uniform vec4 iMouse;

// port from http://glslsandbox.com/e#8625.0 by Duke 
// Fireball
// Awd
// @AlexWDunn

#define saturate(oo) clamp(oo, 0.0, 1.0)

// Quality Settings
#define MarchSteps 8
// Scene Settings
#define ExpPosition vec3(0.0)
#define Radius 2.0
#define Background vec4(0.1, 0.0, 0.0, 1.0)
// Noise Settings
#define NoiseSteps 1
#define NoiseAmplitude 0.06
#define NoiseFrequency 4.0
#define Animation vec3(0.0, -3.0, 0.5)
// Colour Gradient
#define Color1 vec4(1.0, 1.0, 1.0, 1.0)
#define Color2 vec4(1.0, 0.8, 0.2, 1.0)
#define Color3 vec4(1.0, 0.03, 0.0, 1.0)
#define Color4 vec4(0.05, 0.02, 0.02, 1.0)

// GLSL noise functions (Ashima)
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
vec4 taylorInvSqrt(vec4 r){ return 1.79284291400159 - 0.85373472095314 * r; }

float snoise(vec3 v)
{
    const vec2  C = vec2(1.0/6.0, 1.0/3.0);
    const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
    vec3 i  = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);
    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;
    i = mod289(i);
    vec4 p = permute( permute( permute( i.z + vec4(0.0, i1.z, i2.z, 1.0)) + i.y + vec4(0.0, i1.y, i2.y, 1.0 )) + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
    float n_ = 0.142857142857; // 1.0/7.0
    vec3  ns = n_ * D.wyz - D.xzx;
    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);
    vec4 x = x_ *ns.x + ns.yyyy;
    vec4 y = y_ *ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);
    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);
    vec4 s0 = floor(b0) * 2.0 + 1.0;
    vec4 s1 = floor(b1) * 2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));
    vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;
    vec3 p0 = vec3(a0.xy, h.x);
    vec3 p1 = vec3(a0.zw, h.y);
    vec3 p2 = vec3(a1.xy, h.z);
    vec3 p3 = vec3(a1.zw, h.w);
    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
    p0 *= norm.x;
    p1 *= norm.y;
    p2 *= norm.z;
    p3 *= norm.w;
    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
}

float Turbulence(vec3 position, float minFreq, float maxFreq, float qWidth)
{
    float value = 0.0;
    float cutoff = clamp(0.5/qWidth, 0.0, maxFreq);
    float fade;
    float fOut = minFreq;
    for(int i=NoiseSteps ; i>=0 ; i--)
    {
        if(fOut >= 0.5 * cutoff) break;
        fOut *= 2.0;
        value += abs(snoise(position * fOut))/fOut;
    }
    fade = clamp(2.0 * (cutoff-fOut)/cutoff, 0.0, 1.0);
    value += fade * abs(snoise(position * fOut))/fOut;
    return 1.0-value;
}

float SphereDist(vec3 position)
{
    return length(position - ExpPosition) - Radius;
}

vec4 Shade(float distance)
{
    float c1 = saturate(distance*5.0 + 0.5);
    float c2 = saturate(distance*5.0);
    float c3 = saturate(distance*3.4 - 0.5);
    vec4 a = mix(Color1,Color2, c1);
    vec4 b = mix(a,     Color3, c2);
    return      mix(b,     Color4, c3);
}

float RenderScene(vec3 position, out float distance)
{
    float noise = Turbulence(position * NoiseFrequency + Animation*iTime, 0.1, 1.5, 0.03) * NoiseAmplitude;
    noise = saturate(abs(noise));
    distance = SphereDist(position) - noise;
    return noise;
}

vec4 March(vec3 rayOrigin, vec3 rayStep)
{
    vec3 position = rayOrigin;
    float distance;
    float displacement;
    for(int step = MarchSteps; step >=0  ; --step)
    {
        displacement = RenderScene(position, distance);
        if(distance < 0.05) break;
        position += rayStep * distance;
    }
    return mix(Shade(displacement), Background, float(distance >= 0.5));
}

bool IntersectSphere(vec3 ro, vec3 rd, vec3 pos, float radius, out vec3 intersectPoint)
{
    vec3 relDistance = (ro - pos);
    float b = dot(relDistance, rd);
    float c = dot(relDistance, relDistance) - radius*radius;
    float d = b*b - c;
    intersectPoint = ro + rd*(-b - sqrt(d));
    return d >= 0.0;
}

void main()
{
    // reconstruct fragCoord similar to shadertoy's gl_FragCoord
    vec2 fragCoord = gl_FragCoord.xy;
    vec2 p = (fragCoord.xy / iResolution.xy) * 2.0 - 1.0;
    p.x *= iResolution.x/iResolution.y;
    float rotx = iMouse.y * 0.01;
    float roty = -iMouse.x * 0.01;
    float zoom = 5.0;
    vec3 ro = zoom * normalize(vec3(cos(roty), cos(rotx), sin(roty)));
    vec3 ww = normalize(vec3(0.0, 0.0, 0.0) - ro);
    vec3 uu = normalize(cross( vec3(0.0, 1.0, 0.0), ww));
    vec3 vv = normalize(cross(ww, uu));
    vec3 rd = normalize(p.x*uu + p.y*vv + 1.5*ww);
    vec4 col = Background;
    vec3 origin;
    if(IntersectSphere(ro, rd, ExpPosition, Radius + NoiseAmplitude*6.0, origin))
    {
        col = March(origin, rd);
    }
    fragColor = col;
}
"""

def compile_shader(source, shader_type):
    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    # check compile status
    result = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
    if not result:
        err = gl.glGetShaderInfoLog(shader).decode()
        raise RuntimeError("Shader compile error: " + err)
    return shader

def create_program(vertex_src, fragment_src):
    vs = compile_shader(vertex_src, gl.GL_VERTEX_SHADER)
    fs = compile_shader(fragment_src, gl.GL_FRAGMENT_SHADER)
    prog = gl.glCreateProgram()
    gl.glAttachShader(prog, vs)
    gl.glAttachShader(prog, fs)
    gl.glLinkProgram(prog)
    # check link status
    linked = gl.glGetProgramiv(prog, gl.GL_LINK_STATUS)
    if not linked:
        err = gl.glGetProgramInfoLog(prog).decode()
        raise RuntimeError("Program link error: " + err)
    # shaders can be deleted after linking
    gl.glDeleteShader(vs)
    gl.glDeleteShader(fs)
    return prog

def main():
    pygame.init()
    # Request OpenGL 3.3 core profile if possible
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

    width, height = 960, 540
    screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Fireball shader - Pygame + OpenGL")

    program = create_program(VERTEX_SHADER_SRC, FRAGMENT_SHADER_SRC)
    gl.glUseProgram(program)

    # full-screen quad (two triangles)
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
    # attribute 0 -> aPos (vec2)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 0, None)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

    # uniforms
    loc_iResolution = gl.glGetUniformLocation(program, "iResolution")
    loc_iTime = gl.glGetUniformLocation(program, "iTime")
    loc_iMouse = gl.glGetUniformLocation(program, "iMouse")

    start_time = time.time()
    clock = pygame.time.Clock()

    mouse_pressed_pos = (0.0, 0.0)
    mouse_down = False

    running = True
    while running:
        # event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    mouse_pressed_pos = pygame.mouse.get_pos()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

        # clear
        gl.glViewport(0, 0, width, height)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # set uniforms
        current_time = time.time() - start_time
        mx, my = pygame.mouse.get_pos()
        # convert Pygame mouse (0,0 top-left) to shadertoy style (x, y)
        # For convenience we map to pixel coords
        mouse_x = float(mx)
        mouse_y = float(height - my)  # flip Y so origin bottom-left like Shadertoy
        if mouse_down:
            # store pressed pos if mouse is down
            pmx, pmy = mouse_pressed_pos
            pmx = float(pmx)
            pmy = float(height - pmy)
            iMouse_val = (mouse_x, mouse_y, pmx, pmy)
        else:
            # no click; put z, w = 0
            iMouse_val = (mouse_x, mouse_y, 0.0, 0.0)

        # send uniforms
        gl.glUseProgram(program)
        gl.glUniform3f(loc_iResolution, float(width), float(height), 0.0)
        gl.glUniform1f(loc_iTime, float(current_time))
        gl.glUniform4f(loc_iMouse, float(iMouse_val[0]), float(iMouse_val[1]), float(iMouse_val[2]), float(iMouse_val[3]))

        # draw
        gl.glBindVertexArray(vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        gl.glBindVertexArray(0)

        pygame.display.flip()
        clock.tick(60)

    # cleanup
    gl.glDeleteProgram(program)
    gl.glDeleteBuffers(1, [vbo])
    gl.glDeleteVertexArrays(1, [vao])
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
