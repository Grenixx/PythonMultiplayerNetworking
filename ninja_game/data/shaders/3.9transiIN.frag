precision mediump float;

uniform float u_time;
uniform float u_progress; // 0.0 (fermé) à 1.0 (ouvert)
uniform vec2 u_resolution;
uniform vec2 u_camera;
uniform sampler2D u_texture;

vec2 randomGradient(vec2 p) {
    p += 0.02;
    float x = dot(p, vec2(123.4, 234.5));
    float y = dot(p, vec2(234.5, 345.6));
    vec2 gradient = vec2(x, y);
    gradient = sin(gradient);
    gradient *= 43758.5453;
    gradient = sin(gradient + u_time * 0.15);
    return gradient;
}

vec2 quintic(vec2 p) {
    return p * p * p * (10.0 + p * (-15.0 + p * 6.0));
}

float perlinNoise(vec2 uv) {
    vec2 gridId = floor(uv);
    vec2 gridUv = fract(uv);

    vec2 bl = gridId + vec2(0.0, 0.0);
    vec2 br = gridId + vec2(1.0, 0.0);
    vec2 tl = gridId + vec2(0.0, 1.0);
    vec2 tr = gridId + vec2(1.0, 1.0);

    float dotBl = dot(randomGradient(bl), gridUv - vec2(0.0, 0.0));
    float dotBr = dot(randomGradient(br), gridUv - vec2(1.0, 0.0));
    float dotTl = dot(randomGradient(tl), gridUv - vec2(0.0, 1.0));
    float dotTr = dot(randomGradient(tr), gridUv - vec2(1.0, 1.0));

    vec2 smoothUv = quintic(gridUv);
    return mix(mix(dotBl, dotBr, smoothUv.x), mix(dotTl, dotTr, smoothUv.x), smoothUv.y);
}

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 center = vec2(0.5, 0.5);
    vec2 dir = uv - center;
    dir.x *= u_resolution.x / u_resolution.y;
    float dist = length(dir);

    // Rayon basé sur le progrès
    float radius = u_progress * 1.5; 
    float softness = 0.15;

    // Déformation à la bordure du cercle
    float borderDist = abs(dist - radius);
    float distortionRange = 0.1;
    float distortion = 0.0;
    
    if (borderDist < distortionRange && dist < radius) {
        float force = pow(1.0 - (borderDist / distortionRange), 2.0);
        distortion = sin(dist * 50.0 - u_time * 10.0) * 0.02 * force;
    }

    vec2 distortedUv = uv + normalize(dir) * distortion;

    // Si on est à l'intérieur du cercle (jeu visible)
    if (dist < radius) {
        vec4 sceneColor = texture2D(u_texture, distortedUv);
        
        // Petit flash blanc sur les bords déformés
        float flash = smoothstep(radius - 0.02, radius, dist) * 0.3;
        gl_FragColor = sceneColor + vec4(vec3(flash), 0.0);
    } 
    // Si on est à l'extérieur (le shader background originel 3.9)
    else {
        vec2 noiseUv = (gl_FragCoord.xy + u_camera) / u_resolution.y * 15.0;
        float noise = perlinNoise(noiseUv);
        
        // Couleurs de 3.9
        vec3 bg = vec3(0.0, 0.0, 0.0);
        vec3 ring = vec3(0.6863, 0.0, 0.0);
        
        vec3 color;
        if (noise < 0.0 || (noise > 0.1 && noise < 0.2) || (noise > 0.3 && noise < 0.4) || (noise > 0.6 && noise < 0.8)) {
            color = bg;
        } else {
            color = ring;
        }
        
        gl_FragColor = vec4(color, 1.0);
    }
}