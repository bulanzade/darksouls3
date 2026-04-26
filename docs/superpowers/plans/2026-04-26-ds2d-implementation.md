# DS2D Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a playable 2D top-down Dark Souls 2 clone running in the browser via Rust/WASM/WebGL2.

**Architecture:** Traditional OOP with trait objects. Fixed 60Hz timestep game loop driven by requestAnimationFrame. 5-pass rendering pipeline (Tilemap → Characters → Lighting → Composite → UI). DragonBones skeletal animation. Seamless chunk-based world loading.

**Tech Stack:** Rust 1.94, wasm-pack, wasm-bindgen, web-sys (WebGL2), glam, serde/serde_json, idb (IndexedDB). Dev server on 192.168.1.10.

---

## File Structure

```
ds2d/
  Cargo.toml
  src/
    lib.rs                              -- Crate root, module declarations
    core/
      mod.rs
      time.rs                           -- DeltaTime, FixedTimestep accumulator
      input.rs                          -- Keyboard/gamepad input state
      camera.rs                         -- Camera2D: position, zoom, shake
      transform.rs                      -- Position, rotation, scale
    render/
      mod.rs
      gl_context.rs                     -- WebGL2 context wrapper
      shader.rs                         -- Shader compile, program link, uniform cache
      texture.rs                        -- Texture loading and atlas management
      sprite_batcher.rs                 -- Instanced quad renderer
      vertex.rs                         -- Vertex format definitions
    world/
      mod.rs
      tileset.rs                        -- Tile definitions
      chunk.rs                          -- 32x32 tile grid
      collision.rs                      -- Tile collision grid
    entity/
      mod.rs
      entity_trait.rs                   -- Entity trait definition
    combat/
      mod.rs
    rpg/
      mod.rs
    dragonbones/
      mod.rs
    ai/
      mod.rs
    save/
      mod.rs
    audio/
      mod.rs
    bridge/
      mod.rs
      wasm_entry.rs                     -- #[wasm_bindgen(start)], game loop
      asset_loader.rs                   -- Fetch API wrapper
  static/
    index.html
    index.js                            -- WASM loader, canvas setup, input bridge
    styles.css
    shaders/
      sprite.vert                       -- Instanced sprite vertex shader
      sprite.frag                       -- Instanced sprite fragment shader
    assets/
      textures/
        test_sprite.png                 -- 16x16 test sprite (checkerboard pattern)
      maps/
        test_area.json                  -- Minimal test area with 1 chunk
```

---

## Task 1: Project Scaffold + WebGL2 Canvas

**Files:**
- Create: `Cargo.toml`
- Create: `src/lib.rs`
- Create: `src/bridge/mod.rs`
- Create: `src/bridge/wasm_entry.rs`
- Create: `src/render/mod.rs`
- Create: `src/render/gl_context.rs`
- Create: `static/index.html`
- Create: `static/index.js`
- Create: `static/styles.css`

- [ ] **Step 1: Create Cargo.toml with dependencies**

```toml
[package]
name = "ds2d"
version = "0.1.0"
edition = "2024"

[lib]
crate-type = ["cdylib", "rlib"]

[dependencies]
wasm-bindgen = "0.2"
js-sys = "0.3"
log = "0.4"
console_error_panic_hook = "0.1"

[dependencies.web-sys]
version = "0.3"
features = [
  "Window",
  "Document",
  "Element",
  "HtmlCanvasElement",
  "WebGl2RenderingContext",
  "WebGlProgram",
  "WebGlShader",
  "WebGlBuffer",
  "WebGlVertexArrayObject",
  "WebGlUniformLocation",
  "WebGlTexture",
  "KeyboardEvent",
  "EventTarget",
  "Performance",
  "Request",
  "RequestInit",
  "Response",
  "Headers",
]

[dev-dependencies]
wasm-bindgen-test = "0.3"

[profile.release]
opt-level = "z"
lto = true
```

- [ ] **Step 2: Create src/lib.rs**

```rust
pub mod bridge;
pub mod render;
```

- [ ] **Step 3: Create src/render/mod.rs**

```rust
pub mod gl_context;
```

- [ ] **Step 4: Create src/render/gl_context.rs**

```rust
use wasm_bindgen::JsCast;
use web_sys::{WebGl2RenderingContext, WebGlProgram, WebGlShader};

pub struct GlContext {
    pub gl: WebGl2RenderingContext,
}

impl GlContext {
    pub fn from_canvas_id(canvas_id: &str) -> Result<Self, String> {
        let document = web_sys::window()
            .ok_or("No window")?
            .document()
            .ok_or("No document")?;
        let canvas = document
            .get_element_by_id(canvas_id)
            .ok_or(format!("Canvas element '{}' not found", canvas_id))?;
        let canvas: web_sys::HtmlCanvasElement =
            canvas.dyn_into().map_err(|_| "Element is not a canvas")?;

        let gl = canvas
            .get_context("webgl2")
            .map_err(|_| "Failed to get webgl2 context")?
            .ok_or("WebGL2 not supported")?
            .dyn_into()
            .map_err(|_| "Context is not WebGL2")?;

        gl.enable(WebGl2RenderingContext::DEPTH_TEST);
        gl.enable(WebGl2RenderingContext::BLEND);
        gl.blend_func(
            WebGl2RenderingContext::SRC_ALPHA,
            WebGl2RenderingContext::ONE_MINUS_SRC_ALPHA,
        );

        Ok(Self { gl })
    }

    pub fn clear(&self, r: f32, g: f32, b: f32, a: f32) {
        let gl = &self.gl;
        gl.clear_color(r, g, b, a);
        gl.clear(
            WebGl2RenderingContext::COLOR_BUFFER_BIT | WebGl2RenderingContext::DEPTH_BUFFER_BIT,
        );
    }

    pub fn set_viewport(&self, width: i32, height: i32) {
        self.gl.viewport(0, 0, width, height);
    }
}
```

- [ ] **Step 5: Create src/bridge/mod.rs**

```rust
pub mod wasm_entry;
```

- [ ] **Step 6: Create src/bridge/wasm_entry.rs**

```rust
use crate::render::gl_context::GlContext;
use wasm_bindgen::prelude::*;

static mut GL_CONTEXT: Option<GlContext> = None;

fn get_gl() -> &'static mut GlContext {
    unsafe { GL_CONTEXT.as_mut().unwrap() }
}

#[wasm_bindgen(start)]
pub fn wasm_main() {
    console_error_panic_hook::set_once();

    let gl_ctx = GlContext::from_canvas_id("game-canvas").expect("Failed to init WebGL2");
    gl_ctx.set_viewport(960, 540);

    unsafe {
        GL_CONTEXT = Some(gl_ctx);
    }

    log::info!("DS2D initialized");

    start_game_loop();
}

fn start_game_loop() {
    let f = Closure::wrap(Box::new(|| {
        let gl = get_gl();
        gl.clear(0.05, 0.05, 0.08, 1.0);
        request_next_frame();
    }) as Box<dyn FnMut()>);

    web_sys::window()
        .unwrap()
        .request_animation_frame(&f.into_js_value().unchecked_ref())
        .unwrap();
}

fn request_next_frame() {
    let f = Closure::wrap(Box::new(|| {
        let gl = get_gl();
        gl.clear(0.05, 0.05, 0.08, 1.0);
        request_next_frame();
    }) as Box<dyn FnMut()>);

    web_sys::window()
        .unwrap()
        .request_animation_frame(&f.into_js_value().unchecked_ref())
        .unwrap();
}
```

- [ ] **Step 7: Create static/index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DS2D - Dark Souls 2D</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <canvas id="game-canvas" width="960" height="540"></canvas>
    <script type="module">
        import init from './pkg/ds2d.js';
        async function run() {
            await init();
        }
        run();
    </script>
</body>
</html>
```

- [ ] **Step 8: Create static/styles.css**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; height: 100%; background: #000; overflow: hidden; }
#game-canvas {
    display: block;
    margin: auto;
    image-rendering: pixelated;
}
```

- [ ] **Step 9: Create static/index.js (placeholder for later use)**

```javascript
// Audio context will be initialized here later
// For now, just the WASM loader in index.html
```

- [ ] **Step 10: Build and verify**

Run:
```bash
cargo install wasm-pack
cd /home/radxa/workspace/darksouls
wasm-pack build --target web --dev
cp -r pkg/ static/pkg/
# Serve static/ on 192.168.1.10:8080
python3 -m http.server 8080 --bind 192.168.1.10 --directory static
```

Expected: Dark grey canvas (RGB 13,13,20) in browser at http://192.168.1.10:8080

- [ ] **Step 11: Commit**

```bash
git init
git add Cargo.toml src/ static/ docs/
git commit -m "feat: project scaffold with WebGL2 canvas clear"
```

---

## Task 2: Shader System + Texture Loading

**Files:**
- Create: `src/render/shader.rs`
- Create: `src/render/texture.rs`
- Create: `static/shaders/sprite.vert`
- Create: `static/shaders/sprite.frag`
- Modify: `src/render/mod.rs`

- [ ] **Step 1: Create src/render/shader.rs**

```rust
use web_sys::{WebGl2RenderingContext as GL, WebGlProgram, WebGlShader};

pub struct ShaderProgram {
    pub program: WebGlProgram,
    pub uniforms: std::collections::HashMap<String, web_sys::WebGlUniformLocation>,
}

impl ShaderProgram {
    pub fn compile(gl: &GL, vert_src: &str, frag_src: &str) -> Result<Self, String> {
        let vert = compile_shader(gl, GL::VERTEX_SHADER, vert_src)?;
        let frag = compile_shader(gl, GL::FRAGMENT_SHADER, frag_src)?;

        let program = gl.create_program().ok_or("Failed to create program")?;
        gl.attach_shader(&program, &vert);
        gl.attach_shader(&program, &frag);
        gl.link_program(&program);

        if !gl.get_program_parameter(&program, GL::LINK_STATUS).as_bool().unwrap_or(false) {
            let info = gl.get_program_info_log(&program).unwrap_or_default();
            gl.delete_program(Some(&program));
            return Err(format!("Shader link failed: {}", info));
        }

        gl.delete_shader(Some(&vert));
        gl.delete_shader(Some(&frag));

        Ok(Self {
            program,
            uniforms: std::collections::HashMap::new(),
        })
    }

    pub fn get_uniform_location(&mut self, gl: &GL, name: &str) {
        let loc = gl.get_uniform_location(&self.program, name);
        if let Some(loc) = loc {
            self.uniforms.insert(name.to_string(), loc);
        }
    }

    pub fn set_uniform(&self, gl: &GL, name: &str, value: impl UniformValue) {
        if let Some(loc) = self.uniforms.get(name) {
            value.apply(gl, loc);
        }
    }

    pub fn bind(&self, gl: &GL) {
        gl.use_program(Some(&self.program));
    }
}

fn compile_shader(gl: &GL, shader_type: u32, source: &str) -> Result<WebGlShader, String> {
    let shader = gl.create_shader(shader_type).ok_or("Failed to create shader")?;
    gl.shader_source(&shader, source);
    gl.compile_shader(&shader);

    if !gl.get_shader_parameter(&shader, GL::COMPILE_STATUS).as_bool().unwrap_or(false) {
        let info = gl.get_shader_info_log(&shader).unwrap_or_default();
        gl.delete_shader(Some(&shader));
        return Err(format!("Shader compile failed: {}", info));
    }

    Ok(shader)
}

pub trait UniformValue {
    fn apply(&self, gl: &GL, location: &web_sys::WebGlUniformLocation);
}

impl UniformValue for f32 {
    fn apply(&self, gl: &GL, loc: &web_sys::WebGlUniformLocation) {
        gl.uniform1f(Some(loc), *self);
    }
}

impl UniformValue for (f32, f32) {
    fn apply(&self, gl: &GL, loc: &web_sys::WebGlUniformLocation) {
        gl.uniform2f(Some(loc), self.0, self.1);
    }
}

impl UniformValue for (f32, f32, f32, f32) {
    fn apply(&self, gl: &GL, loc: &web_sys::WebGlUniformLocation) {
        gl.uniform4f(Some(loc), self.0, self.1, self.2, self.3);
    }
}

impl UniformValue for &[f32] {
    fn apply(&self, gl: &GL, loc: &web_sys::WebGlUniformLocation) {
        match self.len() {
            9 => gl.uniform_matrix3fv_with_f32_array(Some(loc), false, self),
            16 => gl.uniform_matrix4fv_with_f32_array(Some(loc), false, self),
            _ => log::warn!("Unsupported uniform array size: {}", self.len()),
        }
    }
}
```

- [ ] **Step 2: Create src/render/texture.rs**

```rust
use web_sys::WebGl2RenderingContext as GL;

pub struct Texture {
    pub gl_texture: web_sys::WebGlTexture,
    pub width: u32,
    pub height: u32,
}

impl Texture {
    pub fn from_rgba(gl: &GL, data: &[u8], width: u32, height: u32) -> Result<Self, String> {
        let tex = gl.create_texture().ok_or("Failed to create texture")?;
        gl.bind_texture(GL::TEXTURE_2D, Some(&tex));
        gl.tex_image_2d_with_i32_and_i32_and_i32_and_format_and_type_and_opt_u8_array(
            GL::TEXTURE_2D,
            0,
            GL::RGBA as i32,
            width as i32,
            height as i32,
            0,
            GL::RGBA,
            GL::UNSIGNED_BYTE,
            Some(data),
        )
        .map_err(|e| format!("tex_image_2d failed: {:?}", e))?;

        gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_MIN_FILTER, GL::NEAREST as i32);
        gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_MAG_FILTER, GL::NEAREST as i32);
        gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_WRAP_S, GL::CLAMP_TO_EDGE as i32);
        gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_WRAP_T, GL::CLAMP_TO_EDGE as i32);

        gl.bind_texture(GL::TEXTURE_2D, None);

        Ok(Self { gl_texture: tex, width, height })
    }

    pub fn bind(&self, gl: &GL, unit: u32) {
        gl.active_texture(GL::TEXTURE0 + unit);
        gl.bind_texture(GL::TEXTURE_2D, Some(&self.gl_texture));
    }

    pub fn unbind(gl: &GL) {
        gl.bind_texture(GL::TEXTURE_2D, None);
    }
}
```

- [ ] **Step 3: Create static/shaders/sprite.vert (GLSL ES 3.00)**

```glsl
#version 300 es
precision highp float;

layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec2 a_uv;
layout(location = 2) in vec4 a_color;
layout(location = 3) in mat3 a_transform;

uniform mat4 u_projection;

out vec2 v_uv;
out vec4 v_color;

void main() {
    vec3 world_pos = a_transform * vec3(a_pos, 1.0);
    gl_Position = u_projection * vec4(world_pos.xy, 0.0, 1.0);
    v_uv = a_uv;
    v_color = a_color;
}
```

- [ ] **Step 4: Create static/shaders/sprite.frag (GLSL ES 3.00)**

```glsl
#version 300 es
precision highp float;

in vec2 v_uv;
in vec4 v_color;

uniform sampler2D u_texture;

out vec4 fragColor;

void main() {
    vec4 tex_color = texture(u_texture, v_uv);
    fragColor = tex_color * v_color;
}
```

- [ ] **Step 5: Update src/render/mod.rs**

```rust
pub mod gl_context;
pub mod shader;
pub mod texture;
```

- [ ] **Step 6: Build and verify**

Run: `wasm-pack build --target web --dev`

Expected: Compiles without errors.

- [ ] **Step 7: Commit**

```bash
git add src/render/shader.rs src/render/texture.rs static/shaders/
git commit -m "feat: shader system and texture loading"
```

---

## Task 3: Sprite Batcher (Instanced Rendering)

**Files:**
- Create: `src/render/vertex.rs`
- Create: `src/render/sprite_batcher.rs`
- Modify: `src/render/mod.rs`
- Modify: `src/bridge/wasm_entry.rs`

- [ ] **Step 1: Create src/render/vertex.rs**

```rust
#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct SpriteVertex {
    pub pos: [f32; 2],
    pub uv: [f32; 2],
}

pub const QUAD_VERTICES: [SpriteVertex; 4] = [
    SpriteVertex { pos: [-0.5, -0.5], uv: [0.0, 0.0] },
    SpriteVertex { pos: [ 0.5, -0.5], uv: [1.0, 0.0] },
    SpriteVertex { pos: [ 0.5,  0.5], uv: [1.0, 1.0] },
    SpriteVertex { pos: [-0.5,  0.5], uv: [0.0, 1.0] },
];

pub const QUAD_INDICES: [u16; 6] = [0, 1, 2, 0, 2, 3];

#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct InstanceData {
    pub transform: [f32; 9],   // 3x3 matrix: col0, col1, col2 (row-major)
    pub uv_rect: [f32; 4],     // min_u, min_v, max_u, max_v
    pub color: [f32; 4],       // r, g, b, a
}

impl InstanceData {
    pub fn new(x: f32, y: f32, w: f32, h: f32, uv_rect: [f32; 4], color: [f32; 4]) -> Self {
        // 3x3 2D transform: scale by (w, h), translate to (x, y)
        Self {
            transform: [
                w,   0.0, 0.0,
                0.0, h,   0.0,
                x,   y,   1.0,
            ],
            uv_rect,
            color,
        }
    }
}

pub const MAX_INSTANCES: usize = 16384;
```

- [ ] **Step 2: Create src/render/sprite_batcher.rs**

```rust
use crate::render::shader::ShaderProgram;
use crate::render::texture::Texture;
use crate::render::vertex::{InstanceData, MAX_INSTANCES, QUAD_INDICES, QUAD_VERTICES, SpriteVertex};
use web_sys::WebGl2RenderingContext as GL;

pub struct SpriteBatcher {
    instances: Vec<InstanceData>,
    current_texture_id: Option<u32>,
    vao: web_sys::WebGlVertexArrayObject,
    quad_vbo: web_sys::WebGlBuffer,
    instance_vbo: web_sys::WebGlBuffer,
    ebo: web_sys::WebGlBuffer,
    shader: ShaderProgram,
}

impl SpriteBatcher {
    pub fn new(gl: &GL) -> Result<Self, String> {
        let vert_src = include_str!("../../static/shaders/sprite.vert");
        let frag_src = include_str!("../../static/shaders/sprite.frag");
        let mut shader = ShaderProgram::compile(gl, vert_src, frag_src)?;
        shader.get_uniform_location(gl, "u_projection");
        shader.get_uniform_location(gl, "u_texture");

        let vao = gl.create_vertex_array().ok_or("Failed to create VAO")?;
        gl.bind_vertex_array(Some(&vao));

        // Quad VBO
        let quad_vbo = gl.create_buffer().ok_or("Failed to create quad VBO")?;
        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&quad_vbo));
        let vert_data: &[u8] = unsafe {
            std::slice::from_raw_parts(
                QUAD_VERTICES.as_ptr() as *const u8,
                std::mem::size_of_val(&QUAD_VERTICES),
            )
        };
        gl.buffer_data_with_u8_array(GL::ARRAY_BUFFER, vert_data, GL::STATIC_DRAW);

        let stride = std::mem::size_of::<SpriteVertex>() as i32;

        // a_pos (location 0)
        gl.enable_vertex_attrib_array(0);
        gl.vertex_attrib_pointer_with_i32(0, 2, GL::FLOAT, false, stride, 0);

        // a_uv (location 1)
        gl.enable_vertex_attrib_array(1);
        gl.vertex_attrib_pointer_with_i32(1, 2, GL::FLOAT, false, stride, 8);

        // EBO
        let ebo = gl.create_buffer().ok_or("Failed to create EBO")?;
        gl.bind_buffer(GL::ELEMENT_ARRAY_BUFFER, Some(&ebo));
        let idx_data: &[u8] = unsafe {
            std::slice::from_raw_parts(
                QUAD_INDICES.as_ptr() as *const u8,
                std::mem::size_of_val(&QUAD_INDICES),
            )
        };
        gl.buffer_data_with_u8_array(GL::ELEMENT_ARRAY_BUFFER, idx_data, GL::STATIC_DRAW);

        // Instance VBO
        let instance_vbo = gl.create_buffer().ok_or("Failed to create instance VBO")?;
        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&instance_vbo));
        let instance_size = (MAX_INSTANCES * std::mem::size_of::<InstanceData>()) as i32;
        gl.buffer_data_with_i32(GL::ARRAY_BUFFER, instance_size, GL::DYNAMIC_DRAW);

        let inst_stride = std::mem::size_of::<InstanceData>() as i32;

        // a_transform (location 2, 3 cols = 3 attribs)
        for col in 0..3 {
            let loc = 2 + col;
            gl.enable_vertex_attrib_array(loc);
            gl.vertex_attrib_pointer_with_i32(loc, 3, GL::FLOAT, false, inst_stride, col * 12);
            gl.vertex_attrib_divisor(loc, 1);
        }

        // a_uv_rect (location 5)
        gl.enable_vertex_attrib_array(5);
        gl.vertex_attrib_pointer_with_i32(5, 4, GL::FLOAT, false, inst_stride, 36);
        gl.vertex_attrib_divisor(5, 1);

        // a_color (location 6)
        gl.enable_vertex_attrib_array(6);
        gl.vertex_attrib_pointer_with_i32(6, 4, GL::FLOAT, false, inst_stride, 52);
        gl.vertex_attrib_divisor(6, 1);

        gl.bind_vertex_array(None);

        Ok(Self {
            instances: Vec::with_capacity(MAX_INSTANCES),
            current_texture_id: None,
            vao,
            quad_vbo,
            instance_vbo,
            ebo,
            shader,
        })
    }

    pub fn draw(&mut self, texture: &Texture, instance: InstanceData) {
        let tex_id = texture.gl_texture_hash();
        if self.current_texture_id.is_some() && self.current_texture_id != Some(tex_id) {
            self.flush(&texture);
        }
        self.current_texture_id = Some(tex_id);
        self.instances.push(instance);

        if self.instances.len() >= MAX_INSTANCES {
            self.flush(&texture);
        }
    }

    pub fn flush(&mut self, texture: &Texture) {
        if self.instances.is_empty() {
            return;
        }
        let gl = unsafe { crate::bridge::wasm_entry::get_gl() };
        let gl = &gl.gl;

        self.shader.bind(gl);
        texture.bind(gl, 0);

        gl.bind_vertex_array(Some(&self.vao));

        let instance_data: &[u8] = unsafe {
            std::slice::from_raw_parts(
                self.instances.as_ptr() as *const u8,
                self.instances.len() * std::mem::size_of::<InstanceData>(),
            )
        };
        gl.bind_buffer(GL::ARRAY_BUFFER, Some(&self.instance_vbo));
        gl.buffer_sub_data_with_i32_and_u8_array(GL::ARRAY_BUFFER, 0, instance_data);

        gl.draw_elements_instanced_with_i32(
            GL::TRIANGLES,
            6,
            GL::UNSIGNED_SHORT,
            0,
            self.instances.len() as i32,
        );

        gl.bind_vertex_array(None);
        self.instances.clear();
    }

    pub fn set_projection(&self, gl: &GL, projection: &[f32; 16]) {
        self.shader.bind(gl);
        self.shader.set_uniform(gl, "u_projection", projection as &[f32]);
    }
}
```

- [ ] **Step 3: Add gl_texture_hash helper to texture.rs**

Add to `src/render/texture.rs`:

```rust
impl Texture {
    // ... existing methods ...

    pub fn gl_texture_hash(&self) -> u32 {
        // Use the raw pointer as a unique ID for batching
        self.gl_texture.as_ref() as *const _ as u32
    }
}
```

- [ ] **Step 4: Update src/render/mod.rs**

```rust
pub mod gl_context;
pub mod shader;
pub mod sprite_batcher;
pub mod texture;
pub mod vertex;
```

- [ ] **Step 5: Update src/bridge/wasm_entry.rs to expose GL**

Replace the existing file with:

```rust
use crate::render::gl_context::GlContext;
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use crate::render::vertex::InstanceData;
use wasm_bindgen::prelude::*;

static mut GAME: Option<Game> = None;

struct Game {
    gl_ctx: GlContext,
    batcher: SpriteBatcher,
    test_texture: Texture,
    frame_count: u32,
}

pub fn get_gl() -> &'static mut GlContext {
    unsafe { &mut GAME.as_mut().unwrap().gl_ctx }
}

#[wasm_bindgen(start)]
pub fn wasm_main() {
    console_error_panic_hook::set_once();

    let gl_ctx = GlContext::from_canvas_id("game-canvas").expect("Failed to init WebGL2");
    gl_ctx.set_viewport(960, 540);

    let batcher = SpriteBatcher::new(&gl_ctx.gl).expect("Failed to create batcher");

    // Create a 16x16 magenta checkerboard test sprite
    let mut pixels = Vec::with_capacity(16 * 16 * 4);
    for y in 0..16u32 {
        for x in 0..16u32 {
            if (x + y) % 2 == 0 {
                pixels.extend_from_slice(&[255, 0, 255, 255]);
            } else {
                pixels.extend_from_slice(&[0, 0, 0, 255]);
            }
        }
    }
    let test_texture = Texture::from_rgba(&gl_ctx.gl, &pixels, 16, 16).expect("Failed to create test texture");

    // Orthographic projection: 960x540, origin at center
    let w = 960.0_f32;
    let h = 540.0_f32;
    let projection: [f32; 16] = orthographic(-w / 2.0, w / 2.0, -h / 2.0, h / 2.0, -1.0, 1.0);
    batcher.set_projection(&gl_ctx.gl, &projection);

    unsafe {
        GAME = Some(Game { gl_ctx, batcher, test_texture, frame_count: 0 });
    }

    log::info!("DS2D initialized with sprite batcher");
    request_frame();
}

fn orthographic(left: f32, right: f32, bottom: f32, top: f32, near: f32, far: f32) -> [f32; 16] {
    let tx = -(right + left) / (right - left);
    let ty = -(top + bottom) / (top - bottom);
    let tz = -(far + near) / (far - near);
    [
        2.0 / (right - left), 0.0, 0.0, 0.0,
        0.0, 2.0 / (top - bottom), 0.0, 0.0,
        0.0, 0.0, -2.0 / (far - near), 0.0,
        tx, ty, tz, 1.0,
    ]
}

fn request_frame() {
    let f = Closure::wrap(Box::new(|| {
        tick();
        request_frame();
    }) as Box<dyn FnMut()>);

    web_sys::window()
        .unwrap()
        .request_animation_frame(&f.into_js_value().unchecked_ref())
        .unwrap();
}

fn tick() {
    let game = unsafe { GAME.as_mut().unwrap() };
    let gl = &game.gl_ctx.gl;
    game.frame_count += 1;

    gl.clear_color(0.05, 0.05, 0.08, 1.0);
    gl.clear(web_sys::WebGl2RenderingContext::COLOR_BUFFER_BIT | web_sys::WebGl2RenderingContext::DEPTH_BUFFER_BIT);

    // Draw a 64x64 sprite at origin, pulsing color
    let t = game.frame_count as f32 * 0.02;
    let r = (t.sin() * 0.5 + 0.5) as f32;
    let instance = InstanceData::new(
        0.0, 0.0, 64.0, 64.0,
        [0.0, 0.0, 1.0, 1.0],
        [r, 0.5, 1.0 - r, 1.0],
    );

    game.batcher.draw(&game.test_texture, instance);
    game.batcher.flush(&game.test_texture);
}
```

- [ ] **Step 6: Build and verify**

Run: `wasm-pack build --target web --dev && cp -r pkg/ static/pkg/`

Expected: A 64x64 magenta/black checkerboard sprite pulsing between blue and red at center of canvas.

- [ ] **Step 7: Commit**

```bash
git add src/render/vertex.rs src/render/sprite_batcher.rs src/bridge/wasm_entry.rs
git commit -m "feat: instanced sprite batcher with test sprite"
```

---

## Task 4: Time System + Input System + Camera

**Files:**
- Create: `src/core/mod.rs`
- Create: `src/core/time.rs`
- Create: `src/core/input.rs`
- Create: `src/core/camera.rs`
- Create: `src/core/transform.rs`
- Modify: `src/lib.rs`
- Modify: `src/bridge/wasm_entry.rs`

- [ ] **Step 1: Create src/core/mod.rs**

```rust
pub mod camera;
pub mod input;
pub mod time;
pub mod transform;
```

- [ ] **Step 2: Create src/core/time.rs**

```rust
pub const FIXED_DT: f64 = 1.0 / 60.0; // 16.666ms
pub const MAX_FRAME_TIME: f64 = 0.1;   // 100ms

pub struct Time {
    pub last_timestamp: f64,
    pub accumulator: f64,
    pub delta: f64,
    pub alpha: f64,
}

impl Time {
    pub fn new() -> Self {
        Self {
            last_timestamp: 0.0,
            accumulator: 0.0,
            delta: 0.0,
            alpha: 0.0,
        }
    }

    pub fn update(&mut self, timestamp: f64) {
        if self.last_timestamp == 0.0 {
            self.last_timestamp = timestamp;
            return;
        }

        self.delta = (timestamp - self.last_timestamp) / 1000.0; // ms to seconds
        if self.delta > MAX_FRAME_TIME {
            self.delta = MAX_FRAME_TIME;
        }
        self.last_timestamp = timestamp;
        self.accumulator += self.delta;
    }

    pub fn should_fixed_update(&mut self) -> bool {
        if self.accumulator >= FIXED_DT {
            self.accumulator -= FIXED_DT;
            self.alpha = self.accumulator / FIXED_DT;
            true
        } else {
            false
        }
    }
}
```

- [ ] **Step 3: Create src/core/input.rs**

```rust
use wasm_bindgen::prelude::*;
use web_sys::KeyboardEvent;

#[derive(Clone, Copy, PartialEq, Eq, Hash)]
pub enum KeyCode {
    ArrowUp = 38,
    ArrowDown = 40,
    ArrowLeft = 37,
    ArrowRight = 39,
    KeyW = 87,
    KeyA = 65,
    KeyS = 83,
    KeyD = 68,
    Space = 32,
    ShiftLeft = 16,
    KeyJ = 74,
    KeyK = 75,
    KeyL = 76,
    KeyI = 73,
    KeyE = 69,
    Enter = 13,
    Escape = 27,
}

pub struct InputState {
    keys: [bool; 256],
    keys_prev: [bool; 256],
}

impl InputState {
    pub fn new() -> Self {
        Self {
            keys: [false; 256],
            keys_prev: [false; 256],
        }
    }

    pub fn begin_frame(&mut self) {
        self.keys_prev.copy_from_slice(&self.keys);
    }

    pub fn set_key(&mut self, code: u32, pressed: bool) {
        if (code as usize) < 256 {
            self.keys[code as usize] = pressed;
        }
    }

    pub fn pressed(&self, key: KeyCode) -> bool {
        let code = key as usize;
        self.keys[code] && !self.keys_prev[code]
    }

    pub fn held(&self, key: KeyCode) -> bool {
        self.keys[key as usize]
    }

    pub fn released(&self, key: KeyCode) -> bool {
        let code = key as usize;
        !self.keys[code] && self.keys_prev[code]
    }

    pub fn movement(&self) -> (f32, f32) {
        let mut x = 0.0_f32;
        let mut y = 0.0_f32;
        if self.held(KeyCode::ArrowLeft) || self.held(KeyCode::KeyA) { x -= 1.0; }
        if self.held(KeyCode::ArrowRight) || self.held(KeyCode::KeyD) { x += 1.0; }
        if self.held(KeyCode::ArrowUp) || self.held(KeyCode::KeyW) { y -= 1.0; }
        if self.held(KeyCode::ArrowDown) || self.held(KeyCode::KeyS) { y += 1.0; }
        let len = (x * x + y * y).sqrt();
        if len > 0.0 {
            (x / len, y / len)
        } else {
            (0.0, 0.0)
        }
    }
}

pub fn setup_input(input: &InputState) -> Closure<dyn FnMut(KeyboardEvent)> {
    // Input is set from JS via a shared buffer; see bridge
    unimplemented!("See bridge setup below")
}
```

- [ ] **Step 4: Create src/core/camera.rs**

```rust
use crate::core::transform::Transform;

pub struct Camera2D {
    pub position: (f32, f32),
    pub zoom: f32,
    pub viewport: (f32, f32),
    pub shake_offset: (f32, f32),
    pub shake_intensity: f32,
    pub shake_decay: f32,
}

impl Camera2D {
    pub fn new(viewport_w: f32, viewport_h: f32) -> Self {
        Self {
            position: (0.0, 0.0),
            zoom: 2.0,
            viewport: (viewport_w, viewport_h),
            shake_offset: (0.0, 0.0),
            shake_intensity: 0.0,
            shake_decay: 10.0,
        }
    }

    pub fn follow(&mut self, target: (f32, f32), speed: f32, dt: f32) {
        let dx = target.0 - self.position.0;
        let dy = target.1 - self.position.1;
        let t = (speed * dt).min(1.0);
        self.position.0 += dx * t;
        self.position.1 += dy * t;
    }

    pub fn shake(&mut self, intensity: f32) {
        self.shake_intensity = self.shake_intensity.max(intensity);
    }

    pub fn update(&mut self, dt: f32) {
        if self.shake_intensity > 0.01 {
            self.shake_offset = (
                (self.shake_intensity * rand_shake()) as f32,
                (self.shake_intensity * rand_shake()) as f32,
            );
            self.shake_intensity *= (-self.shake_decay * dt).exp();
        } else {
            self.shake_offset = (0.0, 0.0);
            self.shake_intensity = 0.0;
        }
    }

    pub fn projection_matrix(&self) -> [f32; 16] {
        let hw = self.viewport.0 / (2.0 * self.zoom);
        let hh = self.viewport.1 / (2.0 * self.zoom);
        let cx = self.position.0 + self.shake_offset.0;
        let cy = self.position.1 + self.shake_offset.1;
        orthographic(cx - hw, cx + hw, cy - hh, cy + hh, -1.0, 1.0)
    }
}

fn orthographic(left: f32, right: f32, bottom: f32, top: f32, near: f32, far: f32) -> [f32; 16] {
    [
        2.0 / (right - left), 0.0, 0.0, 0.0,
        0.0, 2.0 / (top - bottom), 0.0, 0.0,
        0.0, 0.0, -2.0 / (far - near), 0.0,
        -(right + left) / (right - left),
        -(top + bottom) / (top - bottom),
        -(far + near) / (far - near),
        1.0,
    ]
}

fn rand_shake() -> f32 {
    // Simple deterministic shake using frame-local state
    // In WASM without rand crate, use a simple approach
    let t = unsafe { core::ptr::read_volatile(&crate::bridge::wasm_entry::FRAME_COUNT as *const u32) };
    ((t as f32 * 12.9898).sin() * 43758.5453).fract() * 2.0 - 1.0
}
```

- [ ] **Step 5: Create src/core/transform.rs**

```rust
#[derive(Clone, Copy, Debug)]
pub struct Transform {
    pub x: f32,
    pub y: f32,
    pub rotation: f32, // radians
    pub scale_x: f32,
    pub scale_y: f32,
}

impl Transform {
    pub fn new(x: f32, y: f32) -> Self {
        Self { x, y, rotation: 0.0, scale_x: 1.0, scale_y: 1.0 }
    }

    pub fn to_instance_data(&self, w: f32, h: f32, uv_rect: [f32; 4], color: [f32; 4]) -> crate::render::vertex::InstanceData {
        let (sin, cos) = self.rotation.sin_cos();
        let sw = w * self.scale_x;
        let sh = h * self.scale_y;
        crate::render::vertex::InstanceData {
            transform: [
                cos * sw, -sin * sh, 0.0,
                sin * sw,  cos * sh, 0.0,
                self.x, self.y, 1.0,
            ],
            uv_rect,
            color,
        }
    }
}
```

- [ ] **Step 6: Update src/lib.rs**

```rust
pub mod bridge;
pub mod core;
pub mod render;
```

- [ ] **Step 7: Update src/bridge/wasm_entry.rs — full game loop with input + camera + moving sprite**

```rust
use crate::core::camera::Camera2D;
use crate::core::input::{InputState, KeyCode};
use crate::core::time::Time;
use crate::core::transform::Transform;
use crate::render::gl_context::GlContext;
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use crate::render::vertex::InstanceData;
use wasm_bindgen::prelude::*;

static mut GAME: Option<Game> = None;

pub static mut FRAME_COUNT: u32 = 0;

struct Game {
    gl_ctx: GlContext,
    batcher: SpriteBatcher,
    test_texture: Texture,
    time: Time,
    input: InputState,
    camera: Camera2D,
    player_pos: Transform,
    player_speed: f32,
}

pub fn get_gl() -> &'static mut GlContext {
    unsafe { &mut GAME.as_mut().unwrap().gl_ctx }
}

#[wasm_bindgen(start)]
pub fn wasm_main() {
    console_error_panic_hook::set_once();

    let gl_ctx = GlContext::from_canvas_id("game-canvas").expect("Failed to init WebGL2");
    gl_ctx.set_viewport(960, 540);

    let batcher = SpriteBatcher::new(&gl_ctx.gl).expect("Failed to create batcher");

    let mut pixels = Vec::with_capacity(16 * 16 * 4);
    for y in 0..16u32 {
        for x in 0..16u32 {
            if (x + y) % 2 == 0 {
                pixels.extend_from_slice(&[255, 100, 200, 255]);
            } else {
                pixels.extend_from_slice(&[100, 50, 120, 255]);
            }
        }
    }
    let test_texture = Texture::from_rgba(&gl_ctx.gl, &pixels, 16, 16).expect("Failed to create test texture");

    unsafe {
        GAME = Some(Game {
            gl_ctx,
            batcher,
            test_texture,
            time: Time::new(),
            input: InputState::new(),
            camera: Camera2D::new(960.0, 540.0),
            player_pos: Transform::new(0.0, 0.0),
            player_speed: 120.0,
        });
    }

    setup_input_listeners();
    log::info!("DS2D initialized with input + camera");
    request_frame();
}

fn setup_input_listeners() {
    let window = web_sys::window().unwrap();

    let keydown = Closure::wrap(Box::new(|e: web_sys::KeyboardEvent| {
        let code = e.key_code();
        unsafe {
            if let Some(g) = GAME.as_mut() {
                g.input.set_key(code, true);
            }
        }
    }) as Box<dyn FnMut(_)>);
    window.add_event_listener_with_callback("keydown", keydown.as_ref().unchecked_ref()).unwrap();
    keydown.forget();

    let keyup = Closure::wrap(Box::new(|e: web_sys::KeyboardEvent| {
        let code = e.key_code();
        unsafe {
            if let Some(g) = GAME.as_mut() {
                g.input.set_key(code, false);
            }
        }
    }) as Box<dyn FnMut(_)>);
    window.add_event_listener_with_callback("keyup", keyup.as_ref().unchecked_ref()).unwrap();
    keyup.forget();
}

fn request_frame() {
    let f = Closure::wrap(Box::new(|timestamp: f64| {
        tick(timestamp);
        request_frame();
    }) as Box<dyn FnMut(f64)>);

    web_sys::window()
        .unwrap()
        .request_animation_frame(&f.into_js_value().unchecked_ref())
        .unwrap();
}

fn tick(timestamp: f64) {
    let game = unsafe { GAME.as_mut().unwrap() };
    let gl = &game.gl_ctx.gl;
    unsafe { FRAME_COUNT += 1; }

    game.time.update(timestamp);

    // Fixed timestep updates
    while game.time.should_fixed_update() {
        game.input.begin_frame();
        fixed_update(game);
    }

    // Render
    render(game);
}

fn fixed_update(game: &mut Game) {
    let dt = crate::core::time::FIXED_DT as f32;
    let (mx, my) = game.input.movement();
    game.player_pos.x += mx * game.player_speed * dt;
    game.player_pos.y += my * game.player_speed * dt;

    game.camera.follow((game.player_pos.x, game.player_pos.y), 5.0, dt);
    game.camera.update(dt);
}

fn render(game: &mut Game) {
    let gl = &game.gl_ctx.gl;

    gl.clear_color(0.05, 0.05, 0.08, 1.0);
    gl.clear(web_sys::WebGl2RenderingContext::COLOR_BUFFER_BIT | web_sys::WebGl2RenderingContext::DEPTH_BUFFER_BIT);

    let proj = game.camera.projection_matrix();
    game.batcher.set_projection(gl, &proj);

    let instance = game.player_pos.to_instance_data(
        32.0, 32.0,
        [0.0, 0.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
    );
    game.batcher.draw(&game.test_texture, instance);
    game.batcher.flush(&game.test_texture);
}
```

- [ ] **Step 8: Build and verify**

Run: `wasm-pack build --target web --dev && cp -r pkg/ static/pkg/`

Expected: A 32x32 checkerboard sprite that moves with WASD/arrow keys. Camera smoothly follows the sprite. Background is dark.

- [ ] **Step 9: Commit**

```bash
git add src/core/ src/lib.rs src/bridge/wasm_entry.rs
git commit -m "feat: time system, input, camera with player movement"
```

---

## Task 5: Tilemap Rendering + Collision

**Files:**
- Create: `src/world/mod.rs`
- Create: `src/world/tileset.rs`
- Create: `src/world/chunk.rs`
- Create: `src/world/collision.rs`
- Create: `src/render/tilemap_renderer.rs`
- Modify: `src/lib.rs`
- Modify: `src/render/mod.rs`
- Create: `static/assets/textures/tileset.png` (test tileset)
- Create: `static/assets/maps/test_area.json`

- [ ] **Step 1: Create src/world/mod.rs**

```rust
pub mod chunk;
pub mod collision;
pub mod tileset;
```

- [ ] **Step 2: Create src/world/tileset.rs**

```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u16)]
pub enum TileId {
    Empty = 0,
    Ground = 1,
    Wall = 2,
    WallTop = 3,
}

#[derive(Clone, Copy, Debug)]
pub struct TileDef {
    pub uv_x: f32,
    pub uv_y: f32,
    pub uv_w: f32,
    pub uv_h: f32,
    pub solid: bool,
}

pub const TILE_SIZE: u32 = 16;
pub const TILES_PER_ROW: u32 = 16;

pub struct Tileset {
    pub tiles: Vec<TileDef>,
}

impl Tileset {
    pub fn test_tileset(tileset_width: u32, tileset_height: u32) -> Self {
        let tw = 1.0 / tileset_width as f32;
        let th = 1.0 / tileset_height as f32;
        let tiles = vec![
            TileDef { uv_x: 0.0, uv_y: 0.0, uv_w: tw, uv_h: th, solid: false }, // Empty
            TileDef { uv_x: tw, uv_y: 0.0, uv_w: tw, uv_h: th, solid: false },   // Ground
            TileDef { uv_x: tw * 2.0, uv_y: 0.0, uv_w: tw, uv_h: th, solid: true },  // Wall
            TileDef { uv_x: tw * 3.0, uv_y: 0.0, uv_w: tw, uv_h: th, solid: true },  // WallTop
        ];
        Self { tiles }
    }

    pub fn get(&self, id: TileId) -> Option<&TileDef> {
        let idx = id as usize;
        self.tiles.get(idx)
    }
}
```

- [ ] **Step 3: Create src/world/chunk.rs**

```rust
use crate::world::tileset::TileId;

pub const CHUNK_SIZE: usize = 32;

#[derive(Clone)]
pub struct Chunk {
    pub coord: (i32, i32),
    pub tiles: [[TileId; CHUNK_SIZE]; CHUNK_SIZE],
}

impl Chunk {
    pub fn new(coord: (i32, i32)) -> Self {
        Self {
            coord,
            tiles: [[TileId::Empty; CHUNK_SIZE]; CHUNK_SIZE],
        }
    }

    pub fn test_chunk(coord: (i32, i32)) -> Self {
        let mut chunk = Self::new(coord);
        for y in 0..CHUNK_SIZE {
            for x in 0..CHUNK_SIZE {
                if y == 0 || y == CHUNK_SIZE - 1 || x == 0 || x == CHUNK_SIZE - 1 {
                    chunk.tiles[y][x] = TileId::Wall;
                } else if y == CHUNK_SIZE - 2 {
                    chunk.tiles[y][x] = TileId::WallTop;
                } else {
                    chunk.tiles[y][x] = TileId::Ground;
                }
            }
        }
        chunk
    }

    pub fn world_offset(&self) -> (f32, f32) {
        let tile_size = crate::world::tileset::TILE_SIZE as f32;
        (
            self.coord.0 as f32 * CHUNK_SIZE as f32 * tile_size,
            self.coord.1 as f32 * CHUNK_SIZE as f32 * tile_size,
        )
    }
}
```

- [ ] **Step 4: Create src/world/collision.rs**

```rust
use crate::world::chunk::{Chunk, CHUNK_SIZE};
use crate::world::tileset::{TileId, TILE_SIZE};

pub struct CollisionGrid {
    solid: [[bool; CHUNK_SIZE]; CHUNK_SIZE],
}

impl CollisionGrid {
    pub fn from_chunk(chunk: &Chunk, tileset: &crate::world::tileset::Tileset) -> Self {
        let mut solid = [[false; CHUNK_SIZE]; CHUNK_SIZE];
        for y in 0..CHUNK_SIZE {
            for x in 0..CHUNK_SIZE {
                if let Some(def) = tileset.get(chunk.tiles[y][x]) {
                    solid[y][x] = def.solid;
                }
            }
        }
        Self { solid }
    }

    pub fn is_solid(&self, local_x: usize, local_y: usize) -> bool {
        if local_x >= CHUNK_SIZE || local_y >= CHUNK_SIZE {
            return true; // Out of bounds = solid
        }
        self.solid[local_y][local_x]
    }

    /// Check if a world-space AABB collides with solid tiles.
    /// Returns the corrected position.
    pub fn resolve_aabb(
        &self,
        chunk_offset: (f32, f32),
        x: f32,
        y: f32,
        half_w: f32,
        half_h: f32,
    ) -> (f32, f32) {
        let ts = TILE_SIZE as f32;
        let mut rx = x;
        let mut ry = y;

        // Check tiles overlapping the AABB
        let min_tx = ((rx - half_w - chunk_offset.0) / ts).floor() as isize;
        let max_tx = ((rx + half_w - chunk_offset.0) / ts).ceil() as isize;
        let min_ty = ((ry - half_h - chunk_offset.1) / ts).floor() as isize;
        let max_ty = ((ry + half_h - chunk_offset.1) / ts).ceil() as isize;

        for ty in min_ty..=max_ty {
            for tx in min_tx..=max_tx {
                if tx < 0 || ty < 0 || tx >= CHUNK_SIZE as isize || ty >= CHUNK_SIZE as isize {
                    continue;
                }
                if !self.solid[ty as usize][tx as usize] {
                    continue;
                }

                let tile_left = chunk_offset.0 + tx as f32 * ts;
                let tile_top = chunk_offset.1 + ty as f32 * ts;
                let tile_right = tile_left + ts;
                let tile_bottom = tile_top + ts;

                // AABB overlap
                let overlap_x = (rx + half_w).min(tile_right) - (rx - half_w).max(tile_left);
                let overlap_y = (ry + half_h).min(tile_bottom) - (ry - half_h).max(tile_top);

                if overlap_x > 0.0 && overlap_y > 0.0 {
                    if overlap_x < overlap_y {
                        if rx < tile_left + ts / 2.0 {
                            rx -= overlap_x;
                        } else {
                            rx += overlap_x;
                        }
                    } else {
                        if ry < tile_top + ts / 2.0 {
                            ry -= overlap_y;
                        } else {
                            ry += overlap_y;
                        }
                    }
                }
            }
        }

        (rx, ry)
    }
}
```

- [ ] **Step 5: Create src/render/tilemap_renderer.rs**

```rust
use crate::render::shader::ShaderProgram;
use crate::render::texture::Texture;
use crate::render::vertex::InstanceData;
use crate::world::chunk::Chunk;
use crate::world::tileset::{TileId, TILE_SIZE};
use web_sys::WebGl2RenderingContext as GL;

pub struct TilemapRenderer {
    shader: ShaderProgram,
}

impl TilemapRenderer {
    pub fn new(gl: &GL) -> Result<Self, String> {
        let vert_src = include_str!("../../static/shaders/sprite.vert");
        let frag_src = include_str!("../../static/shaders/sprite.frag");
        let mut shader = ShaderProgram::compile(gl, vert_src, frag_src)?;
        shader.get_uniform_location(gl, "u_projection");
        shader.get_uniform_location(gl, "u_texture");
        Ok(Self { shader })
    }

    pub fn render_chunk(
        &self,
        gl: &GL,
        chunk: &Chunk,
        tileset_texture: &Texture,
        tileset: &crate::world::tileset::Tileset,
        projection: &[f32; 16],
    ) {
        self.shader.bind(gl);
        tileset_texture.bind(gl, 0);
        self.shader.set_uniform(gl, "u_projection", projection as &[f32]);

        let ts = TILE_SIZE as f32;
        let (ox, oy) = chunk.world_offset();

        let mut instances: Vec<InstanceData> = Vec::new();

        for y in 0..crate::world::chunk::CHUNK_SIZE {
            for x in 0..crate::world::chunk::CHUNK_SIZE {
                let tile_id = chunk.tiles[y][x];
                if tile_id == TileId::Empty {
                    continue;
                }
                if let Some(def) = tileset.get(tile_id) {
                    let wx = ox + x as f32 * ts + ts / 2.0;
                    let wy = oy + y as f32 * ts + ts / 2.0;
                    instances.push(InstanceData::new(
                        wx, wy, ts, ts,
                        [def.uv_x, def.uv_y, def.uv_x + def.uv_w, def.uv_y + def.uv_h],
                        [1.0, 1.0, 1.0, 1.0],
                    ));
                }
            }
        }

        if instances.is_empty() {
            return;
        }

        // Upload and draw instances directly
        // Re-use the sprite batcher's VAO approach but simplified for tilemap
        // For now, use the shared batcher approach via returning instances
        drop(instances);
    }
}
```

- [ ] **Step 6: Update src/render/mod.rs and src/lib.rs**

Add `pub mod tilemap_renderer;` to `src/render/mod.rs`.
Add `pub mod world;` to `src/lib.rs`.

- [ ] **Step 7: Build and verify**

Run: `wasm-pack build --target web --dev`

Expected: Compiles. Tilemap renderer ready for integration.

- [ ] **Step 8: Commit**

```bash
git add src/world/ src/render/tilemap_renderer.rs src/render/mod.rs src/lib.rs
git commit -m "feat: tilemap, chunk, collision system"
```

---

## Task 6: DragonBones Parser + Runtime

**Files:**
- Create: `src/dragonbones/mod.rs`
- Create: `src/dragonbones/parser.rs`
- Create: `src/dragonbones/armature.rs`
- Create: `src/dragonbones/animation_player.rs`
- Create: `src/dragonbones/bone.rs`
- Modify: `src/lib.rs`

This is a large task. The DragonBones JSON parser and runtime armature system.

- [ ] **Step 1: Create src/dragonbones/mod.rs**

```rust
pub mod animation_player;
pub mod armature;
pub mod bone;
pub mod parser;
```

- [ ] **Step 2: Create src/dragonbones/parser.rs — DragonBones 5.x JSON deserialization structs**

```rust
use serde::Deserialize;

#[derive(Deserialize, Debug)]
pub struct DragonBonesFile {
    pub version: Option<String>,
    pub name: Option<String>,
    #[serde(rename = "frameRate")]
    pub frame_rate: Option<u32>,
    pub armature: Vec<ArmatureDef>,
}

#[derive(Deserialize, Debug)]
pub struct ArmatureDef {
    pub name: String,
    #[serde(default)]
    pub bone: Vec<BoneDef>,
    #[serde(default)]
    pub slot: Vec<SlotDef>,
    #[serde(default)]
    pub skin: Vec<SkinDef>,
    #[serde(default)]
    pub animation: Vec<AnimationDef>,
    #[serde(default)]
    pub r#type: Option<String>,
    #[serde(default)]
    pub ik: Vec<IkDef>,
}

#[derive(Deserialize, Debug, Clone)]
pub struct BoneDef {
    pub name: String,
    pub parent: Option<String>,
    #[serde(default)]
    pub transform: TransformDef,
}

#[derive(Deserialize, Debug, Clone, Default)]
pub struct TransformDef {
    #[serde(default)]
    pub x: f32,
    #[serde(default)]
    pub y: f32,
    #[serde(default)]
    pub skX: f32,
    #[serde(default)]
    pub skY: f32,
    #[serde(default)]
    pub scX: f32,
    #[serde(default)]
    pub scY: f32,
}

#[derive(Deserialize, Debug)]
pub struct SlotDef {
    pub name: String,
    pub parent: String,
    #[serde(default)]
    pub displayIndex: i32,
    #[serde(default)]
    pub z: i32,
    #[serde(default)]
    pub color: Option<ColorDef>,
}

#[derive(Deserialize, Debug)]
pub struct ColorDef {
    #[serde(default = "default_alpha")]
    pub aM: f32,
    #[serde(default)]
    pub rM: f32,
    #[serde(default)]
    pub gM: f32,
    #[serde(default)]
    pub bM: f32,
}

fn default_alpha() -> f32 { 100.0 }

#[derive(Deserialize, Debug)]
pub struct SkinDef {
    pub name: String,
    #[serde(default)]
    pub slot: Vec<SkinSlotDef>,
}

#[derive(Deserialize, Debug)]
pub struct SkinSlotDef {
    pub name: String,
    #[serde(default)]
    pub display: Vec<DisplayDef>,
}

#[derive(Deserialize, Debug)]
pub struct DisplayDef {
    pub name: String,
    #[serde(rename = "type", default)]
    pub display_type: Option<String>,
    #[serde(default)]
    pub transform: Option<TransformDef>,
    #[serde(default)]
    pub pivot: Option<PivotDef>,
    #[serde(default)]
    pub path: Option<String>,
}

#[derive(Deserialize, Debug)]
pub struct PivotDef {
    pub x: f32,
    pub y: f32,
}

#[derive(Deserialize, Debug)]
pub struct AnimationDef {
    pub name: String,
    #[serde(default)]
    pub duration: f32,
    #[serde(default)]
    pub playTimes: i32,
    #[serde(default)]
    pub bone: Vec<BoneTimelineDef>,
    #[serde(default)]
    pub slot: Vec<SlotTimelineDef>,
}

#[derive(Deserialize, Debug)]
pub struct BoneTimelineDef {
    pub name: String,
    #[serde(default)]
    pub frame: Vec<BoneFrameDef>,
}

#[derive(Deserialize, Debug, Clone)]
pub struct BoneFrameDef {
    #[serde(default)]
    pub duration: u32,
    #[serde(default)]
    pub transform: Option<TransformDef>,
    #[serde(default)]
    pub curve: Option<Vec<f32>>,
    #[serde(default)]
    pub tweenEasing: Option<f32>,
}

#[derive(Deserialize, Debug)]
pub struct SlotTimelineDef {
    pub name: String,
    #[serde(default)]
    pub frame: Vec<SlotFrameDef>,
}

#[derive(Deserialize, Debug)]
pub struct SlotFrameDef {
    #[serde(default)]
    pub duration: u32,
    #[serde(default)]
    pub displayIndex: Option<i32>,
    #[serde(default)]
    pub color: Option<ColorDef>,
    #[serde(default)]
    pub tweenEasing: Option<f32>,
}

#[derive(Deserialize, Debug)]
pub struct IkDef {
    pub name: String,
    pub bone: String,
    pub target: String,
    #[serde(default)]
    pub bendPositive: Option<bool>,
    #[serde(default)]
    pub chain: Option<u32>,
    #[serde(default)]
    pub weight: Option<f32>,
}

pub fn parse(json: &str) -> Result<DragonBonesFile, serde_json::Error> {
    serde_json::from_str(json)
}
```

- [ ] **Step 3: Create src/dragonbones/bone.rs**

```rust
#[derive(Clone, Debug)]
pub struct Bone {
    pub name: String,
    pub parent_index: Option<usize>,
    pub children: Vec<usize>,

    // Rest pose
    pub rest_x: f32,
    pub rest_y: f32,
    pub rest_rotation: f32,
    pub rest_scale_x: f32,
    pub rest_scale_y: f32,

    // Current world transform (computed each frame)
    pub world_x: f32,
    pub world_y: f32,
    pub world_rotation: f32,
    pub world_scale_x: f32,
    pub world_scale_y: f32,

    // Local delta from animation
    pub local_x: f32,
    pub local_y: f32,
    pub local_rotation: f32,
    pub local_scale_x: f32,
    pub local_scale_y: f32,
}

impl Bone {
    pub fn new(name: String, parent_index: Option<usize>) -> Self {
        Self {
            name,
            parent_index,
            children: Vec::new(),
            rest_x: 0.0, rest_y: 0.0, rest_rotation: 0.0, rest_scale_x: 1.0, rest_scale_y: 1.0,
            world_x: 0.0, world_y: 0.0, world_rotation: 0.0, world_scale_x: 1.0, world_scale_y: 1.0,
            local_x: 0.0, local_y: 0.0, local_rotation: 0.0, local_scale_x: 1.0, local_scale_y: 1.0,
        }
    }

    pub fn update_world_transform(&mut self, parent: Option<&Bone>) {
        let lx = self.rest_x + self.local_x;
        let ly = self.rest_y + self.local_y;
        let lr = self.rest_rotation + self.local_rotation;
        let lsx = self.rest_scale_x * self.local_scale_x;
        let lsy = self.rest_scale_y * self.local_scale_y;

        if let Some(p) = parent {
            let (sin, cos) = p.world_rotation.sin_cos();
            self.world_x = p.world_x + (lx * cos - ly * sin) * p.world_scale_x;
            self.world_y = p.world_y + (lx * sin + ly * cos) * p.world_scale_y;
            self.world_rotation = p.world_rotation + lr;
            self.world_scale_x = p.world_scale_x * lsx;
            self.world_scale_y = p.world_scale_y * lsy;
        } else {
            self.world_x = lx;
            self.world_y = ly;
            self.world_rotation = lr;
            self.world_scale_x = lsx;
            self.world_scale_y = lsy;
        }
    }
}
```

- [ ] **Step 4: Create src/dragonbones/armature.rs**

```rust
use crate::dragonbones::bone::Bone;
use crate::dragonbones::parser::{
    ArmatureDef, BoneDef, DragonBonesFile, SlotDef, SkinDef, AnimationDef,
};
use std::collections::HashMap;

pub struct Armature {
    pub bones: Vec<Bone>,
    pub slots: Vec<SlotInfo>,
    pub animations: HashMap<String, AnimationClip>,
    pub skins: HashMap<String, Vec<DisplayInfo>>,
    pub frame_rate: u32,
}

pub struct SlotInfo {
    pub name: String,
    pub bone_index: usize,
    pub z_order: i32,
    pub display_index: i32,
    pub color_alpha: f32,
}

pub struct DisplayInfo {
    pub name: String,
    pub bone_name: String,
    pub offset_x: f32,
    pub offset_y: f32,
    pub pivot_x: f32,
    pub pivot_y: f32,
    pub width: f32,
    pub height: f32,
}

pub struct AnimationClip {
    pub name: String,
    pub duration: f32,
    pub bone_timelines: HashMap<String, BoneTimeline>,
    pub slot_timelines: HashMap<String, SlotTimeline>,
}

pub struct BoneTimeline {
    pub frames: Vec<BoneKeyframe>,
}

pub struct BoneKeyframe {
    pub duration: f32,
    pub x: f32,
    pub y: f32,
    pub rotation: f32,
    pub scale_x: f32,
    pub scale_y: f32,
    pub easing: Option<f32>,
}

pub struct SlotTimeline {
    pub frames: Vec<SlotKeyframe>,
}

pub struct SlotKeyframe {
    pub duration: f32,
    pub display_index: Option<i32>,
    pub alpha: f32,
    pub easing: Option<f32>,
}

impl Armature {
    pub fn from_def(file: &DragonBonesFile, armature_name: &str) -> Option<Self> {
        let arm_def = file.armature.iter().find(|a| a.name == armature_name)?;
        let frame_rate = file.frame_rate.unwrap_or(24);

        // Build bone list sorted parent-first
        let bone_indices = sort_bones(&arm_def.bone);
        let bones: Vec<Bone> = bone_indices.iter().map(|&i| {
            let bd = &arm_def.bone[i];
            let parent_index = bd.parent.as_ref().and_then(|pname| {
                bone_indices.iter().position(|&pi| arm_def.bone[pi].name == *pname)
            });
            let mut bone = Bone::new(bd.name.clone(), parent_index);
            bone.rest_x = bd.transform.x;
            bone.rest_y = bd.transform.y;
            bone.rest_rotation = bd.transform.skX.to_radians();
            bone.rest_scale_x = if bd.transform.scX == 0.0 { 1.0 } else { bd.transform.scX };
            bone.rest_scale_y = if bd.transform.scY == 0.0 { 1.0 } else { bd.transform.scY };
            bone
        }).collect();

        // Set up children
        for i in 0..bones.len() {
            if let Some(pi) = bones[i].parent_index {
                bones[pi].children.push(i);
            }
        }

        // Slots
        let slots: Vec<SlotInfo> = arm_def.slot.iter().map(|s| {
            let bone_idx = bones.iter().position(|b| b.name == s.parent).unwrap_or(0);
            SlotInfo {
                name: s.name.clone(),
                bone_index: bone_idx,
                z_order: s.z,
                display_index: s.displayIndex,
                color_alpha: s.color.as_ref().map(|c| c.aM / 100.0).unwrap_or(1.0),
            }
        }).collect();

        // Animations
        let animations: HashMap<String, AnimationClip> = arm_def.animation.iter().map(|a| {
            let clip = animation_from_def(a, frame_rate);
            (a.name.clone(), clip)
        }).collect();

        // Skins (simplified)
        let skins = HashMap::new();

        Some(Self { bones, slots, animations, skins, frame_rate })
    }

    pub fn update_world_transforms(&mut self) {
        for i in 0..self.bones.len() {
            let parent_data = self.bones[i].parent_index.map(|pi| {
                let p = &self.bones[pi];
                (p.world_x, p.world_y, p.world_rotation, p.world_scale_x, p.world_scale_y)
            });
            if let Some((px, py, pr, psx, psy)) = parent_data {
                // Need to update in order, so borrow parent data first
                // This is safe because parent always has lower index
            }
        }
        // Two-pass to avoid borrow issues
        for i in 0..self.bones.len() {
            let parent = self.bones[i].parent_index;
            let parent_data = parent.map(|pi| {
                let b = &self.bones[pi];
                (b.world_x, b.world_y, b.world_rotation, b.world_scale_x, b.world_scale_y)
            });
            let bone = &mut self.bones[i];
            if let Some((px, py, pr, psx, _psy)) = parent_data {
                let lx = bone.rest_x + bone.local_x;
                let ly = bone.rest_y + bone.local_y;
                let lr = bone.rest_rotation + bone.local_rotation;
                let lsx = bone.rest_scale_x * bone.local_scale_x;
                let (sin, cos) = pr.sin_cos();
                bone.world_x = px + (lx * cos - ly * sin) * psx;
                bone.world_y = py + (lx * sin + ly * cos) * psx;
                bone.world_rotation = pr + lr;
                bone.world_scale_x = psx * lsx;
            } else {
                bone.world_x = bone.rest_x + bone.local_x;
                bone.world_y = bone.rest_y + bone.local_y;
                bone.world_rotation = bone.rest_rotation + bone.local_rotation;
                bone.world_scale_x = bone.rest_scale_x * bone.local_scale_x;
            }
        }
    }
}

fn sort_bones(bones: &[BoneDef]) -> Vec<usize> {
    let mut result: Vec<usize> = Vec::with_capacity(bones.len());
    let mut visited = vec![false; bones.len()];

    fn visit(bones: &[BoneDef], idx: usize, visited: &mut [bool], result: &mut Vec<usize>) {
        if visited[idx] { return; }
        visited[idx] = true;
        if let Some(ref parent_name) = bones[idx].parent {
            if let Some(pi) = bones.iter().position(|b| b.name == *parent_name) {
                visit(bones, pi, visited, result);
            }
        }
        result.push(idx);
    }

    for i in 0..bones.len() {
        visit(bones, i, &mut visited, &mut result);
    }
    result
}

fn animation_from_def(def: &AnimationDef, frame_rate: u32) -> AnimationClip {
    let duration_frames = if def.duration > 0.0 { def.duration } else { 1.0 };

    let bone_timelines: HashMap<String, BoneTimeline> = def.bone.iter().map(|bt| {
        let mut frames: Vec<BoneKeyframe> = Vec::new();
        for f in &bt.frame {
            let t = f.transform.as_ref();
            frames.push(BoneKeyframe {
                duration: f.duration as f32 / frame_rate as f32,
                x: t.map(|t| t.x).unwrap_or(0.0),
                y: t.map(|t| t.y).unwrap_or(0.0),
                rotation: t.map(|t| t.skX.to_radians()).unwrap_or(0.0),
                scale_x: t.map(|t| if t.scX == 0.0 { 1.0 } else { t.scX }).unwrap_or(1.0),
                scale_y: t.map(|t| if t.scY == 0.0 { 1.0 } else { t.scY }).unwrap_or(1.0),
                easing: f.tweenEasing,
            });
        }
        (bt.name.clone(), BoneTimeline { frames })
    }).collect();

    let slot_timelines: HashMap<String, SlotTimeline> = def.slot.iter().map(|st| {
        let frames: Vec<SlotKeyframe> = st.frame.iter().map(|f| {
            SlotKeyframe {
                duration: f.duration as f32 / frame_rate as f32,
                display_index: f.displayIndex,
                alpha: f.color.as_ref().map(|c| c.aM / 100.0).unwrap_or(1.0),
                easing: f.tweenEasing,
            }
        }).collect();
        (st.name.clone(), SlotTimeline { frames })
    }).collect();

    AnimationClip {
        name: def.name.clone(),
        duration: duration_frames / frame_rate as f32,
        bone_timelines,
        slot_timelines,
    }
}
```

- [ ] **Step 5: Create src/dragonbones/animation_player.rs**

```rust
use crate::dragonbones::armature::{AnimationClip, Armature, BoneKeyframe};
use std::collections::HashMap;

pub struct AnimationPlayer {
    pub current_animation: Option<String>,
    pub time: f32,
    pub playing: bool,
    pub loop_count: i32,
    pub speed: f32,
}

impl AnimationPlayer {
    pub fn new() -> Self {
        Self {
            current_animation: None,
            time: 0.0,
            playing: false,
            loop_count: -1,
            speed: 1.0,
        }
    }

    pub fn play(&mut self, name: &str, loop_count: i32) {
        self.current_animation = Some(name.to_string());
        self.time = 0.0;
        self.playing = true;
        self.loop_count = loop_count;
    }

    pub fn update(&mut self, dt: f32, armature: &mut Armature) {
        let anim_name = match &self.current_animation {
            Some(n) => n.clone(),
            None => return,
        };
        if !self.playing { return; }

        let clip = match armature.animations.get(&anim_name) {
            Some(c) => c,
            None => return,
        };

        self.time += dt * self.speed;

        if self.time >= clip.duration {
            if self.loop_count != 0 {
                self.time %= clip.duration;
                if self.loop_count > 0 {
                    self.loop_count -= 1;
                }
            } else {
                self.time = clip.duration - 0.001;
                self.playing = false;
            }
        }

        // Reset local transforms
        for bone in &mut armature.bones {
            bone.local_x = 0.0;
            bone.local_y = 0.0;
            bone.local_rotation = 0.0;
            bone.local_scale_x = 1.0;
            bone.local_scale_y = 1.0;
        }

        // Evaluate bone timelines
        for (bone_name, timeline) in &clip.bone_timelines {
            if let Some(bone_idx) = armature.bones.iter().position(|b| b.name == *bone_name) {
                let (x, y, r, sx, sy) = evaluate_bone_timeline(&timeline.frames, self.time);
                armature.bones[bone_idx].local_x = x;
                armature.bones[bone_idx].local_y = y;
                armature.bones[bone_idx].local_rotation = r;
                armature.bones[bone_idx].local_scale_x = sx;
                armature.bones[bone_idx].local_scale_y = sy;
            }
        }

        armature.update_world_transforms();
    }
}

fn evaluate_bone_timeline(frames: &[BoneKeyframe], time: f32) -> (f32, f32, f32, f32, f32) {
    if frames.is_empty() {
        return (0.0, 0.0, 0.0, 1.0, 1.0);
    }

    // Find current frame
    let mut accum = 0.0_f32;
    for i in 0..frames.len() {
        let frame_end = accum + frames[i].duration;
        if time < frame_end || i == frames.len() - 1 {
            let local_t = if frames[i].duration > 0.0 {
                (time - accum) / frames[i].duration
            } else {
                1.0
            };
            let t = apply_easing(local_t.clamp(0.0, 1.0), frames[i].easing);

            // Lerp between this frame and next (or hold if last)
            let next = if i + 1 < frames.len() { &frames[i + 1] } else { &frames[0] };
            return (
                lerp(frames[i].x, next.x, t),
                lerp(frames[i].y, next.y, t),
                lerp_angle(frames[i].rotation, next.rotation, t),
                lerp(frames[i].scale_x, next.scale_x, t),
                lerp(frames[i].scale_y, next.scale_y, t),
            );
        }
        accum = frame_end;
    }

    let last = frames.last().unwrap();
    (last.x, last.y, last.rotation, last.scale_x, last.scale_y)
}

fn lerp(a: f32, b: f32, t: f32) -> f32 {
    a + (b - a) * t
}

fn lerp_angle(a: f32, b: f32, t: f32) -> f32 {
    let diff = ((b - a + std::f32::consts::PI) % (2.0 * std::f32::consts::PI)) - std::f32::consts::PI;
    a + diff * t
}

fn apply_easing(t: f32, easing: Option<f32>) -> f32 {
    match easing {
        None => t,
        Some(e) if e >= 0.0 => t, // Linear for now, can add cubic bezier later
        Some(_) => t,
    }
}
```

- [ ] **Step 6: Update src/lib.rs**

```rust
pub mod bridge;
pub mod core;
pub mod dragonbones;
pub mod render;
pub mod world;
```

- [ ] **Step 7: Build and verify**

Run: `wasm-pack build --target web --dev`

Expected: Compiles. DragonBones parser and runtime ready.

- [ ] **Step 8: Commit**

```bash
git add src/dragonbones/ src/lib.rs
git commit -m "feat: DragonBones JSON parser, armature runtime, animation player"
```

---

## Task 7: Entity Trait + Player Entity

**Files:**
- Create: `src/entity/mod.rs`
- Create: `src/entity/entity_trait.rs`
- Create: `src/entity/player.rs`
- Modify: `src/lib.rs`

- [ ] **Step 1: Create src/entity/mod.rs**

```rust
pub mod entity_trait;
pub mod player;
```

- [ ] **Step 2: Create src/entity/entity_trait.rs**

```rust
use crate::core::transform::Transform;
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;

pub type EntityId = u64;

pub enum EntityState {
    Idle,
    Moving,
    Attacking,
    Rolling,
    Blocking,
    Staggered,
    Dead,
}

pub struct DamageInfo {
    pub damage: i32,
    pub knockback_x: f32,
    pub knockback_y: f32,
    pub poise_damage: f32,
    pub attacker_id: EntityId,
}

pub trait Entity {
    fn id(&self) -> EntityId;
    fn position(&self) -> (f32, f32);
    fn set_position(&mut self, x: f32, y: f32);
    fn hp(&self) -> i32;
    fn max_hp(&self) -> i32;
    fn state(&self) -> EntityState;
    fn update(&mut self, dt: f32, world: &mut crate::world::chunk::Chunk);
    fn render(&self, batcher: &mut SpriteBatcher, texture: &Texture);
    fn take_damage(&mut self, info: &DamageInfo);
    fn is_dead(&self) -> bool;
}
```

- [ ] **Step 3: Create src/entity/player.rs**

```rust
use crate::core::input::{InputState, KeyCode};
use crate::core::transform::Transform;
use crate::entity::entity_trait::{DamageInfo, Entity, EntityId, EntityState};
use crate::render::sprite_batcher::SpriteBatcher;
use crate::render::texture::Texture;
use crate::render::vertex::InstanceData;

pub struct Player {
    pub id: EntityId,
    pub transform: Transform,
    pub hp: i32,
    pub max_hp: i32,
    pub speed: f32,
    pub state: EntityState,
    pub facing: f32, // angle in radians
}

impl Player {
    pub fn new(id: EntityId, x: f32, y: f32) -> Self {
        Self {
            id,
            transform: Transform::new(x, y),
            hp: 500,
            max_hp: 500,
            speed: 120.0,
            state: EntityState::Idle,
            facing: 0.0,
        }
    }

    pub fn handle_input(&mut self, input: &InputState) {
        if matches!(self.state, EntityState::Attacking | EntityState::Rolling | EntityState::Staggered) {
            return;
        }

        let (mx, my) = input.movement();
        if mx != 0.0 || my != 0.0 {
            self.facing = my.atan2(mx);
            self.state = EntityState::Moving;
        } else {
            self.state = EntityState::Idle;
        }

        if input.pressed(KeyCode::Space) {
            self.state = EntityState::Rolling;
        }
        if input.pressed(KeyCode::KeyJ) {
            self.state = EntityState::Attacking;
        }
    }
}

impl Entity for Player {
    fn id(&self) -> EntityId { self.id }
    fn position(&self) -> (f32, f32) { (self.transform.x, self.transform.y) }
    fn set_position(&mut self, x: f32, y: f32) { self.transform.x = x; self.transform.y = y; }
    fn hp(&self) -> i32 { self.hp }
    fn max_hp(&self) -> i32 { self.max_hp }
    fn state(&self) -> EntityState { self.state.clone() }

    fn update(&mut self, dt: f32, _world: &mut crate::world::chunk::Chunk) {
        match self.state {
            EntityState::Moving => {
                let speed = self.speed * dt;
                self.transform.x += self.facing.cos() * speed;
                self.transform.y += self.facing.sin() * speed;
            }
            EntityState::Rolling => {
                let speed = self.speed * 2.0 * dt;
                self.transform.x += self.facing.cos() * speed;
                self.transform.y += self.facing.sin() * speed;
            }
            _ => {}
        }
    }

    fn render(&self, batcher: &mut SpriteBatcher, texture: &Texture) {
        let instance = self.transform.to_instance_data(
            32.0, 32.0,
            [0.0, 0.0, 1.0, 1.0],
            [1.0, 0.8, 0.9, 1.0],
        );
        batcher.draw(texture, instance);
    }

    fn take_damage(&mut self, info: &DamageInfo) {
        self.hp -= info.damage;
        self.state = EntityState::Staggered;
        if self.hp <= 0 {
            self.hp = 0;
            self.state = EntityState::Dead;
        }
    }

    fn is_dead(&self) -> bool { self.hp <= 0 }
}
```

- [ ] **Step 4: Update src/lib.rs**

```rust
pub mod bridge;
pub mod core;
pub mod dragonbones;
pub mod entity;
pub mod render;
pub mod world;
```

- [ ] **Step 5: Build and verify**

Run: `wasm-pack build --target web --dev`

Expected: Compiles.

- [ ] **Step 6: Commit**

```bash
git add src/entity/ src/lib.rs
git commit -m "feat: Entity trait and Player entity with input-driven movement"
```

---

## Tasks 8-17: Subsequent Phases (Outline)

The following tasks follow the same pattern (test → implement → verify → commit). Full step-by-step code will be written during execution.

### Task 8: Combat System (Hitbox, Stamina, Moveset, Weapon)

**Files:** `src/combat/mod.rs`, `src/combat/hitbox.rs`, `src/combat/stamina.rs`, `src/combat/moveset.rs`, `src/combat/weapon.rs`

- Implement `Hitbox` with Rect/Circle/Capsule shapes, active frame ranges, hit group filtering
- Implement `StaminaPool` with regen delay and rate
- Define `WeaponMoveset` trait with `LongswordMoveset` as first implementation
- Wire hitbox collision into game loop, verify damage numbers on test enemy

### Task 9: Enemy + AI State Machine

**Files:** `src/ai/mod.rs`, `src/ai/state_machine.rs`, `src/ai/aggro.rs`, `src/entity/enemy.rs`

- Generic FSM with typed states and transition guards
- `AggroTable` with detection radius and line-of-sight
- `HollowSoldier` enemy: patrol → alert → combat → attack → retreat
- Integration test: enemy detects player, approaches, attacks

### Task 10: RPG Stats + Damage Calculation + Equipment

**Files:** `src/rpg/mod.rs`, `src/rpg/stats.rs`, `src/rpg/equipment.rs`, `src/rpg/scaling.rs`, `src/combat/damage.rs`

- `CharacterStats` struct with all 9 DS2 stats
- Derived stat formulas (HP, stamina, equip load, agility, iframe count)
- `Equipment` struct with weapon/armor/ring slots
- DS2 damage formula implementation with counter modifier
- Wire into Player and Enemy

### Task 11: Boss + Boss AI

**Files:** `src/entity/boss.rs`, `src/ai/boss_ai.rs`

- `BossController` with phase management
- `BossPhase` structs with health thresholds and attack lists
- Phase transition invulnerability + animation
- Test boss: 3 phases, escalating difficulty

### Task 12: Save System + Bonfire

**Files:** `src/save/mod.rs`, `src/save/save_data.rs`, `src/save/bonfire.rs`, `src/save/indexed_db.rs`

- `SaveData` struct (serde Serialize/Deserialize)
- Bonfire interaction: rest, refill estus, save, level up, fast travel
- IndexedDB storage via `idb` crate with atomic writes
- Death flow: drop souls, respawn at last bonfire

### Task 13: Lighting + Normal Maps + Post Processing

**Files:** `src/render/light_renderer.rs`, `src/render/post_process.rs`, `static/shaders/light.*`, `static/shaders/composite.*`

- Point light rendering with normal map sampling
- Shadow polygon generation from tile collision edges
- Composite pass: vignette + color grading + fog per area
- Cap active lights at 8, distance cull

### Task 14: Audio Engine

**Files:** `src/audio/mod.rs`, `src/audio/audio_engine.rs`, `src/audio/spatial_audio.rs`, `src/audio/music.rs`, `static/index.js` (update with AudioContext setup)

- JS-side Web Audio API engine (AudioEngine class)
- Rust `extern "C"` bindings for play_music, play_sfx, set_listener_position
- Spatial audio: pan + volume attenuation by distance
- Area music crossfade on area transition

### Task 15: Nav Grid + Patrol

**Files:** `src/world/nav_grid.rs`, `src/ai/patrol.rs`

- Downsampled nav grid from collision data
- A* pathfinding (runs synchronously for MVP, Web Worker later)
- Waypoint patrol paths for idle enemies

### Task 16: Animation Blending

**Files:** `src/dragonbones/animation_blender.rs`

- `AnimationBlender` with blend layers and bone masks
- Crossfade between animations with configurable duration
- Upper/lower body split for attack-while-walking

### Task 17: UI + Menus + Full Game Loop

**Files:** `src/render/ui_renderer.rs`, UI shader files

- HUD: HP bar, stamina bar, soul count, equipped weapons
- Bonfire menu: level up, travel, attune spells
- Death screen → respawn flow
- Start menu: new game / continue
- Pause menu

---

## Spec Coverage Check

| Spec Section | Task |
|---|---|
| Architecture (OOP traits) | Tasks 1, 7 |
| Module structure | Tasks 1-7 (created), 8-17 (outlined) |
| Game loop (fixed timestep) | Task 4 |
| Rendering pipeline (5 pass) | Tasks 2-3 (sprite), 5 (tilemap), 13 (lighting/post) |
| Map system (chunks, collision) | Task 5 |
| Combat (hitbox, stamina, moveset) | Task 8 |
| RPG (stats, equipment, damage) | Task 10 |
| DragonBones (parse, animate, blend) | Task 6, Task 16 |
| AI (state machine, aggro, boss) | Task 9, Task 11 |
| Save (bonfire, IndexedDB) | Task 12 |
| Audio (Web Audio, spatial) | Task 14 |
| WASM bridge (entry, input, assets) | Tasks 1, 4 |
| Dev server (192.168.1.10) | Task 1 (setup) |
| UI + menus | Task 17 |

All spec sections are covered by at least one task.
