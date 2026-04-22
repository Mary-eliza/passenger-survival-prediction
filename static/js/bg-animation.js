let scene, camera, renderer, plane;
let mode = "idle";
let clock = new THREE.Clock();

let rainLines = [];
let smokeParticles = [];

function init() {

    const container = document.getElementById("bg-animation");

    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(
        55,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(0, 5, 25);

    renderer = new THREE.WebGLRenderer({ alpha: false });
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);

    const light = new THREE.AmbientLight(0xffffff, 1.3);
    scene.add(light);

    const loader = new THREE.GLTFLoader();
    loader.load("/static/models/plane.glb", function (gltf) {

        plane = gltf.scene;

        plane.scale.set(0.22, 0.22, 0.22);

        // Hard lock orientation once
        plane.rotation.set(0, Math.PI / 2, -0.1);

        plane.position.set(-15, -3, 8);
        plane.visible = false;

        scene.add(plane);
    });

    animate();
}

function clearRain() {
    rainLines.forEach(r => scene.remove(r));
    rainLines = [];
}

function clearSmoke() {
    smokeParticles.forEach(s => scene.remove(s));
    smokeParticles = [];
}

function createRain() {

    clearRain();

    for (let i = 0; i < 300; i++) {

        const material = new THREE.LineBasicMaterial({
            color: 0xcccccc,
            transparent: true,
            opacity: 0.6
        });

        const points = [];
        const x = Math.random() * 40 - 20;
        const y = Math.random() * 20;
        const z = Math.random() * 30 - 15;

        points.push(new THREE.Vector3(x, y, z));
        points.push(new THREE.Vector3(x, y - 1.2, z));

        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const line = new THREE.Line(geometry, material);

        rainLines.push(line);
        scene.add(line);
    }
}

function createSmoke() {

    clearSmoke();

    for (let i = 0; i < 150; i++) {

        const geometry = new THREE.SphereGeometry(0.2, 6, 6);
        const material = new THREE.MeshBasicMaterial({
            color: 0x555555,
            transparent: true,
            opacity: 0.6
        });

        const particle = new THREE.Mesh(geometry, material);

        particle.position.set(
            plane.position.x - 1,
            plane.position.y,
            plane.position.z
        );

        smokeParticles.push(particle);
        scene.add(particle);
    }
}

function animate() {

    requestAnimationFrame(animate);

    if (plane && mode !== "idle") {

        // ================= SAFE =================
        if (mode === "safe") {

            scene.background = new THREE.Color(0x87CEEB);

            clearRain();
            clearSmoke();

            plane.visible = true;

            plane.position.x += 0.08;
            plane.position.y += 0.05;

            if (plane.position.x > 15) {
                plane.position.set(-15, -3, 8);
            }
        }

        // ================= MODERATE =================
        else if (mode === "moderate") {

            scene.background = new THREE.Color(0x1e2b3a);

            plane.visible = true;

            plane.position.x += 0.05;
            plane.position.y = -2;

            plane.rotation.z =
                -0.1 + Math.sin(clock.getElapsedTime() * 5) * 0.04;

            rainLines.forEach(line => {
                line.position.y -= 0.5;
                if (line.position.y < -10)
                    line.position.y = 10;
            });

            if (plane.position.x > 15) {
                plane.position.set(-15, -2, 8);
            }
        }

        // ================= DANGER =================
        else if (mode === "danger") {

            scene.background = new THREE.Color(0x0a0f16);
            scene.fog = new THREE.Fog(0x0a0f16, 5, 40);

            plane.visible = true;

            plane.position.x += 0.05;
            plane.position.y -= 0.06;

            plane.rotation.z = -0.25;

            smokeParticles.forEach(p => {
                p.position.x -= 0.1;
                p.position.y += 0.02;
                p.material.opacity -= 0.01;
            });

            if (plane.position.y < -8) {
                plane.position.set(-15, 3, 8);
            }
        }
    }

    renderer.render(scene, camera);
}

function triggerBackground(type) {

    mode = type;
    clock = new THREE.Clock();

    if (!plane) return;

    if (type === "safe") {
        plane.position.set(-15, -3, 8);
    }

    if (type === "moderate") {
        plane.position.set(-15, -2, 8);
        createRain();
    }

    if (type === "danger") {
        plane.position.set(-15, 3, 8);
        createSmoke();
    }
}

window.triggerBackground = triggerBackground;

document.addEventListener("DOMContentLoaded", init);
