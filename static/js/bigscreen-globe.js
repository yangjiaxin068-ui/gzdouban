(function () {
    var canvas = document.getElementById("globeCanvas");
    if (!canvas || !window.THREE) {
        return;
    }

    var THREE = window.THREE;
    var countryData = Array.isArray(window.__COUNTRY_DATA__) ? window.__COUNTRY_DATA__ : [];
    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var stage = canvas.parentElement;
    var renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        alpha: true,
        antialias: true,
        powerPreference: "high-performance"
    });
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
    var earthGroup = new THREE.Group();
    var textureLoader = new THREE.TextureLoader();
    var trackedMarkers = [];
    var baseRotationY = THREE.Math.degToRad(-104);
    var textureRotationY = THREE.Math.degToRad(-84);
    var clock = new THREE.Clock();

    var countryCoords = {
        "中国大陆": [104, 35],
        "中国": [104, 35],
        "中国香港": [114.16, 22.28],
        "香港": [114.16, 22.28],
        "中国台湾": [121, 23.7],
        "台湾": [121, 23.7],
        "美国": [-98, 39],
        "英国": [-3, 55],
        "日本": [138, 36],
        "韩国": [128, 36],
        "法国": [2, 46],
        "德国": [10, 51],
        "加拿大": [-106, 56],
        "澳大利亚": [134, -25],
        "印度": [78, 22],
        "意大利": [12, 43],
        "西班牙": [-4, 40],
        "泰国": [101, 15],
        "俄罗斯": [100, 60],
        "巴西": [-51, -10],
        "墨西哥": [-102, 23],
        "伊朗": [53, 32],
        "丹麦": [10, 56],
        "瑞典": [15, 62],
        "波兰": [19, 52],
        "荷兰": [5, 52],
        "阿根廷": [-64, -34],
        "新西兰": [174, -41],
        "土耳其": [35, 39],
        "比利时": [4, 50],
        "爱尔兰": [-8, 53],
        "捷克": [15, 49]
    };

    function asset(path) {
        return "/static/images/earth/" + path;
    }

    function resolveCoord(name) {
        if (!name) {
            return null;
        }
        var normalized = String(name).replace(/\s/g, "");
        var keys = Object.keys(countryCoords);
        for (var i = 0; i < keys.length; i += 1) {
            if (normalized.indexOf(keys[i]) !== -1) {
                return countryCoords[keys[i]];
            }
        }
        return null;
    }

    function lonLatToVector(lon, lat, radius) {
        var phi = THREE.Math.degToRad(lat);
        var theta = THREE.Math.degToRad(lon);
        return new THREE.Vector3(
            radius * Math.cos(phi) * Math.sin(theta),
            radius * Math.sin(phi),
            radius * Math.cos(phi) * Math.cos(theta)
        );
    }

    function makeDotTexture() {
        var size = 128;
        var dotCanvas = document.createElement("canvas");
        var ctx = dotCanvas.getContext("2d");
        dotCanvas.width = size;
        dotCanvas.height = size;

        var glow = ctx.createRadialGradient(size / 2, size / 2, 6, size / 2, size / 2, size / 2);
        glow.addColorStop(0, "rgba(39, 231, 134, 0.95)");
        glow.addColorStop(0.42, "rgba(39, 231, 134, 0.78)");
        glow.addColorStop(0.72, "rgba(39, 231, 134, 0.28)");
        glow.addColorStop(1, "rgba(39, 231, 134, 0)");
        ctx.fillStyle = glow;
        ctx.fillRect(0, 0, size, size);

        ctx.beginPath();
        ctx.arc(size / 2, size / 2, 34, 0, Math.PI * 2);
        ctx.fillStyle = "#24df83";
        ctx.fill();
        ctx.lineWidth = 7;
        ctx.strokeStyle = "rgba(255, 255, 255, 0.92)";
        ctx.stroke();

        var texture = new THREE.CanvasTexture(dotCanvas);
        texture.needsUpdate = true;
        return texture;
    }

    function makeLabelTexture(name, value) {
        var labelCanvas = document.createElement("canvas");
        var ctx = labelCanvas.getContext("2d");
        var title = String(name || "");
        var count = String(value || "");
        var width = Math.max(160, Math.min(260, title.length * 18 + 32));
        var height = 78;
        labelCanvas.width = width * 2;
        labelCanvas.height = height * 2;
        ctx.scale(2, 2);
        ctx.font = "700 18px Microsoft YaHei, sans-serif";
        ctx.textAlign = "center";
        ctx.shadowColor = "rgba(0, 0, 0, 0.86)";
        ctx.shadowBlur = 8;
        ctx.lineWidth = 4;
        ctx.strokeStyle = "rgba(0, 0, 0, 0.74)";
        ctx.fillStyle = "#ffffff";
        ctx.strokeText(title, width / 2, 26);
        ctx.fillText(title, width / 2, 26);
        ctx.font = "800 18px Microsoft YaHei, sans-serif";
        ctx.strokeText(count, width / 2, 52);
        ctx.fillText(count, width / 2, 52);

        var texture = new THREE.CanvasTexture(labelCanvas);
        texture.needsUpdate = true;
        return { texture: texture, width: width, height: height };
    }

    function makeAtmosphereMaterial() {
        return new THREE.ShaderMaterial({
            transparent: true,
            side: THREE.BackSide,
            blending: THREE.AdditiveBlending,
            uniforms: {
                glowColor: { value: new THREE.Color(0x5fdcff) },
                coeficient: { value: 0.35 },
                power: { value: 2.4 }
            },
            vertexShader: [
                "varying vec3 vNormal;",
                "void main() {",
                "  vNormal = normalize(normalMatrix * normal);",
                "  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);",
                "}"
            ].join("\n"),
            fragmentShader: [
                "uniform vec3 glowColor;",
                "uniform float coeficient;",
                "uniform float power;",
                "varying vec3 vNormal;",
                "void main() {",
                "  float intensity = pow(coeficient + dot(vNormal, vec3(0.0, 0.0, 1.0)), power);",
                "  gl_FragColor = vec4(glowColor, intensity * 0.7);",
                "}"
            ].join("\n")
        });
    }

    function addStars() {
        var positions = [];
        for (var i = 0; i < 360; i += 1) {
            var radius = 14 + Math.random() * 20;
            var theta = Math.random() * Math.PI * 2;
            var phi = Math.acos(2 * Math.random() - 1);
            positions.push(
                radius * Math.sin(phi) * Math.cos(theta),
                radius * Math.sin(phi) * Math.sin(theta),
                radius * Math.cos(phi)
            );
        }

        var geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
        var material = new THREE.PointsMaterial({
            color: 0xb8ecff,
            size: 0.035,
            transparent: true,
            opacity: 0.62,
            depthWrite: false
        });
        scene.add(new THREE.Points(geometry, material));
    }

    function addMarkers(dotTexture) {
        var sorted = countryData
            .map(function (item) {
                return {
                    name: item.name,
                    value: Number(item.value) || 0,
                    coord: resolveCoord(item.name)
                };
            })
            .filter(function (item) {
                return item.coord;
            })
            .sort(function (a, b) {
                return b.value - a.value;
            })
            .slice(0, 14);

        sorted.forEach(function (item, index) {
            var position = lonLatToVector(item.coord[0], item.coord[1], 2.06);
            var valueScale = Math.min(0.42, 0.12 + Math.sqrt(item.value) * 0.018);
            var dot = new THREE.Sprite(new THREE.SpriteMaterial({
                map: dotTexture,
                transparent: true,
                depthTest: true,
                depthWrite: false
            }));
            dot.position.copy(position);
            dot.scale.set(valueScale, valueScale, 1);
            dot.renderOrder = item.value;
            earthGroup.add(dot);

            var labelData = makeLabelTexture(item.name, item.value);
            var label = new THREE.Sprite(new THREE.SpriteMaterial({
                map: labelData.texture,
                transparent: true,
                depthTest: false,
                depthWrite: false
            }));
            label.position.copy(position.clone().normalize().multiplyScalar(2.55 + index * 0.01));
            label.scale.set(labelData.width / 300, labelData.height / 300, 1);
            label.renderOrder = item.value + 1;
            earthGroup.add(label);

            trackedMarkers.push({
                dot: dot,
                label: label,
                normal: position.clone().normalize(),
                baseScale: valueScale
            });
        });
    }

    function buildScene() {
        scene.add(earthGroup);
        camera.position.set(0, 0.08, 7.45);

        var ambientLight = new THREE.AmbientLight(0x9fc7ff, 0.36);
        var sunLight = new THREE.DirectionalLight(0xffffff, 1.35);
        sunLight.position.set(-3.5, 2.8, 4.2);
        var rimLight = new THREE.DirectionalLight(0x4bd9ff, 0.82);
        rimLight.position.set(4, 0.2, -3);
        scene.add(ambientLight, sunLight, rimLight);
        addStars();

        var earthMap = textureLoader.load(asset("earth_atmos_2048.jpg"));
        var specularMap = textureLoader.load(asset("earth_specular_2048.jpg"));
        var cloudMap = textureLoader.load(asset("earth_clouds_1024.png"));
        [earthMap, specularMap, cloudMap].forEach(function (texture) {
            texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
        });

        var earth = new THREE.Mesh(
            new THREE.SphereGeometry(2, 96, 96),
            new THREE.MeshPhongMaterial({
                map: earthMap,
                specularMap: specularMap,
                specular: new THREE.Color(0x20365f),
                shininess: 18
            })
        );
        earth.rotation.y = textureRotationY;
        earthGroup.add(earth);

        var clouds = new THREE.Mesh(
            new THREE.SphereGeometry(2.025, 96, 96),
            new THREE.MeshPhongMaterial({
                map: cloudMap,
                transparent: true,
                opacity: 0.38,
                depthWrite: false
            })
        );
        clouds.rotation.y = textureRotationY;
        earthGroup.add(clouds);

        var atmosphere = new THREE.Mesh(
            new THREE.SphereGeometry(2.13, 96, 96),
            makeAtmosphereMaterial()
        );
        earthGroup.add(atmosphere);

        addMarkers(makeDotTexture());
        earthGroup.rotation.x = THREE.Math.degToRad(18);
        earthGroup.rotation.y = baseRotationY;

        return { clouds: clouds };
    }

    var sceneParts = buildScene();

    function resize() {
        var rect = stage.getBoundingClientRect();
        var width = Math.max(1, rect.width);
        var height = Math.max(1, rect.height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
    }

    function updateMarkerVisibility() {
        var worldPosition = new THREE.Vector3();
        trackedMarkers.forEach(function (marker) {
            marker.dot.getWorldPosition(worldPosition);
            var visible = worldPosition.z > 0.02;
            marker.dot.visible = visible;
            marker.label.visible = visible;
            if (visible) {
                var scale = 1 + Math.sin(clock.elapsedTime * 2.4 + marker.normal.x * 6) * 0.05;
                marker.dot.scale.set(marker.baseScale * scale, marker.baseScale * scale, 1);
            }
        });
    }

    function render() {
        var elapsed = clock.getElapsedTime();
        if (!reduceMotion) {
            earthGroup.rotation.y = baseRotationY + Math.sin(elapsed * 0.14) * 0.045;
            sceneParts.clouds.rotation.y += 0.0008;
        }
        updateMarkerVisibility();
        renderer.render(scene, camera);
        requestAnimationFrame(render);
    }

    resize();
    window.addEventListener("resize", resize);
    render();
})();
