precision mediump float;

uniform float u_time;
uniform vec2 u_resolution;
uniform sampler2D u_texture;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 dir = uv - vec2(0.5, 0.5);
    dir.x *= u_resolution.x / u_resolution.y;
    float dist = length(dir);

    vec2 totalDistortion = vec2(0.0);
    float totalFlash = 0.0;

    // On crée 3 ondes décalées dans le temps
    for (float i = 0.0; i < 3.0; i++) {
        // Chaque onde commence avec un retard (i * 0.2)
        float waveTime = fract(u_time * 0.5 - (i * 0.2)); 
        
        float radius = waveTime * 0.8; // L'onde s'étend
        float thickness = 0.05;
        float force = 0.02 * (1.0 - waveTime); // L'onde faiblit en s'éloignant

        // Masque de l'anneau pour l'onde i
        float mask = pow(1.0 - abs(dist - radius), 15.0);
        mask *= step(dist, radius + thickness);
        mask *= step(radius - thickness, dist);

        // On accumule la déformation
        totalDistortion += normalize(dir) * mask * force;
        // On accumule un petit effet de lumière
        totalFlash += mask * 0.15;
    }

    // On applique la déformation totale sur la texture du jeu
    vec3 sceneColor = texture2D(u_texture, uv - totalDistortion).rgb;
    
    // On ajoute l'éclat blanc des ondes
    sceneColor += totalFlash;

    gl_FragColor = vec4(sceneColor, 1.0);
}