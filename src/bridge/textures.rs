use crate::render::texture::Texture;

pub fn create_test_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let size: u32 = 16;
    let mut data = Vec::with_capacity((size * size * 4) as usize);

    for y in 0..size {
        for x in 0..size {
            let checker = ((x / 8) + (y / 8)) % 2 == 0;
            if checker {
                data.extend_from_slice(&[0xFF, 0x00, 0xFF, 0xFF]);
            } else {
                data.extend_from_slice(&[0x80, 0x00, 0x80, 0xFF]);
            }
        }
    }

    Texture::from_rgba(gl, &data, size, size).expect("Failed to create test texture")
}

pub fn create_player_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let frame_w: u32 = 16;
    let total_w: u32 = 64;
    let h: u32 = 16;
    let mut data = vec![0u8; (total_w * h * 4) as usize];
    let set = |data: &mut Vec<u8>, frame: u32, x: u32, y: u32, r: u8, g: u8, b: u8, a: u8| {
        let px = frame * frame_w + x;
        let i = ((y * total_w + px) * 4) as usize;
        data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = a;
    };

    // Frame 0: Idle — standing with sword at rest
    {
        let f = 0;
        for x in 6..10 { set(&mut data, f, x, 1, 180, 180, 200, 255); }
        for x in 5..11 { set(&mut data, f, x, 2, 160, 160, 180, 255); }
        for x in 5..11 { set(&mut data, f, x, 3, 140, 140, 160, 255); }
        set(&mut data, f, 6, 2, 40, 40, 60, 255); set(&mut data, f, 9, 2, 40, 40, 60, 255);
        for x in 6..10 { set(&mut data, f, x, 4, 220, 180, 140, 255); }
        for y in 5..9 { for x in 5..11 { set(&mut data, f, x, y, 100, 100, 120, 255); } }
        for x in 5..11 { set(&mut data, f, x, 8, 80, 60, 30, 255); }
        for y in 9..12 { set(&mut data, f, 6, y, 80, 80, 90, 255); set(&mut data, f, 9, y, 80, 80, 90, 255); }
        for y in 2..10 { set(&mut data, f, 12, y, 200, 200, 210, 255); }
        set(&mut data, f, 11, 5, 160, 140, 60, 255); set(&mut data, f, 13, 5, 160, 140, 60, 255);
        for y in 4..8 { for x in 2..5 { set(&mut data, f, x, y, 60, 80, 140, 255); } }
        for y in 12..14 { set(&mut data, f, 5, y, 60, 50, 40, 255); set(&mut data, f, 6, y, 60, 50, 40, 255); }
        for y in 12..14 { set(&mut data, f, 9, y, 60, 50, 40, 255); set(&mut data, f, 10, y, 60, 50, 40, 255); }
    }

    // Frame 1: Walk — legs spread, slight lean
    {
        let f = 1;
        for x in 6..10 { set(&mut data, f, x, 1, 180, 180, 200, 255); }
        for x in 5..11 { set(&mut data, f, x, 2, 160, 160, 180, 255); }
        for x in 5..11 { set(&mut data, f, x, 3, 140, 140, 160, 255); }
        set(&mut data, f, 6, 2, 40, 40, 60, 255); set(&mut data, f, 9, 2, 40, 40, 60, 255);
        for x in 6..10 { set(&mut data, f, x, 4, 220, 180, 140, 255); }
        for y in 5..9 { for x in 5..11 { set(&mut data, f, x, y, 100, 100, 120, 255); } }
        for x in 5..11 { set(&mut data, f, x, 8, 80, 60, 30, 255); }
        for y in 9..12 { set(&mut data, f, 5, y, 80, 80, 90, 255); set(&mut data, f, 10, y, 80, 80, 90, 255); }
        for y in 2..10 { set(&mut data, f, 12, y, 200, 200, 210, 255); }
        set(&mut data, f, 11, 5, 160, 140, 60, 255); set(&mut data, f, 13, 5, 160, 140, 60, 255);
        for y in 4..8 { for x in 2..5 { set(&mut data, f, x, y, 60, 80, 140, 255); } }
        for y in 12..14 { set(&mut data, f, 4, y, 60, 50, 40, 255); set(&mut data, f, 5, y, 60, 50, 40, 255); }
        for y in 12..14 { set(&mut data, f, 10, y, 60, 50, 40, 255); set(&mut data, f, 11, y, 60, 50, 40, 255); }
    }

    // Frame 2: Attack — sword swung forward
    {
        let f = 2;
        for x in 6..10 { set(&mut data, f, x, 1, 180, 180, 200, 255); }
        for x in 5..11 { set(&mut data, f, x, 2, 160, 160, 180, 255); }
        for x in 5..11 { set(&mut data, f, x, 3, 140, 140, 160, 255); }
        set(&mut data, f, 6, 2, 40, 40, 60, 255); set(&mut data, f, 9, 2, 40, 40, 60, 255);
        for x in 6..10 { set(&mut data, f, x, 4, 220, 180, 140, 255); }
        for y in 5..9 { for x in 5..11 { set(&mut data, f, x, y, 100, 100, 120, 255); } }
        for x in 5..11 { set(&mut data, f, x, 8, 80, 60, 30, 255); }
        for y in 9..12 { set(&mut data, f, 6, y, 80, 80, 90, 255); set(&mut data, f, 9, y, 80, 80, 90, 255); }
        for x in 11..15 { set(&mut data, f, x, 5, 200, 200, 210, 255); }
        set(&mut data, f, 10, 5, 160, 140, 60, 255);
        set(&mut data, f, 11, 4, 160, 140, 60, 255);
        for y in 4..8 { for x in 2..5 { set(&mut data, f, x, y, 60, 80, 140, 255); } }
        for y in 12..14 { set(&mut data, f, 5, y, 60, 50, 40, 255); set(&mut data, f, 6, y, 60, 50, 40, 255); }
        for y in 12..14 { set(&mut data, f, 9, y, 60, 50, 40, 255); set(&mut data, f, 10, y, 60, 50, 40, 255); }
    }

    // Frame 3: Block — shield raised
    {
        let f = 3;
        for x in 6..10 { set(&mut data, f, x, 1, 180, 180, 200, 255); }
        for x in 5..11 { set(&mut data, f, x, 2, 160, 160, 180, 255); }
        for x in 5..11 { set(&mut data, f, x, 3, 140, 140, 160, 255); }
        set(&mut data, f, 6, 2, 40, 40, 60, 255); set(&mut data, f, 9, 2, 40, 40, 60, 255);
        for x in 6..10 { set(&mut data, f, x, 4, 220, 180, 140, 255); }
        for y in 5..9 { for x in 5..11 { set(&mut data, f, x, y, 100, 100, 120, 255); } }
        for x in 5..11 { set(&mut data, f, x, 8, 80, 60, 30, 255); }
        for y in 9..12 { set(&mut data, f, 6, y, 80, 80, 90, 255); set(&mut data, f, 9, y, 80, 80, 90, 255); }
        for y in 2..10 { set(&mut data, f, 12, y, 200, 200, 210, 255); }
        for y in 2..8 { for x in 1..5 { set(&mut data, f, x, y, 50, 70, 150, 255); } }
        for y in 2..8 { set(&mut data, f, 1, y, 80, 100, 180, 255); }
        for y in 12..14 { set(&mut data, f, 5, y, 60, 50, 40, 255); set(&mut data, f, 6, y, 60, 50, 40, 255); }
        for y in 12..14 { set(&mut data, f, 9, y, 60, 50, 40, 255); set(&mut data, f, 10, y, 60, 50, 40, 255); }
    }

    Texture::from_rgba(gl, &data, total_w, h).expect("Failed to create player texture")
}

pub fn create_enemy_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let mut data = vec![0u8; 16 * 16 * 4];
    let set = |data: &mut Vec<u8>, x: u32, y: u32, r: u8, g: u8, b: u8, a: u8| {
        let i = ((y * 16 + x) * 4) as usize;
        data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = a;
    };
    for x in 6..10 { set(&mut data, x, 2, 100, 90, 80, 255); }
    for x in 5..11 { set(&mut data, x, 3, 90, 80, 70, 255); }
    for x in 5..11 { set(&mut data, x, 4, 110, 95, 80, 255); }
    set(&mut data, 6, 3, 20, 20, 20, 255); set(&mut data, 9, 3, 20, 20, 20, 255);
    for y in 5..9 { for x in 5..11 { set(&mut data, x, y, 70, 60, 50, 255); } }
    set(&mut data, 5, 6, 80, 70, 55, 255); set(&mut data, 10, 7, 80, 70, 55, 255);
    for y in 9..12 { set(&mut data, 6, y, 60, 55, 45, 255); set(&mut data, 9, y, 60, 55, 45, 255); }
    for y in 3..8 { set(&mut data, 12, y, 140, 140, 140, 255); }
    set(&mut data, 11, 5, 100, 80, 40, 255);
    for y in 12..14 { set(&mut data, 5, y, 50, 45, 35, 255); set(&mut data, 6, y, 50, 45, 35, 255); }
    for y in 12..14 { set(&mut data, 9, y, 50, 45, 35, 255); set(&mut data, 10, y, 50, 45, 35, 255); }
    Texture::from_rgba(gl, &data, 16, 16).expect("Failed to create enemy texture")
}

pub fn create_boss_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let s = 24u32;
    let mut data = vec![0u8; (s * s * 4) as usize];
    let set = |data: &mut Vec<u8>, x: u32, y: u32, r: u8, g: u8, b: u8, a: u8| {
        let i = ((y * s + x) * 4) as usize;
        data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = a;
    };
    set(&mut data, 6, 0, 80, 20, 20, 255); set(&mut data, 5, 1, 80, 20, 20, 255);
    set(&mut data, 17, 0, 80, 20, 20, 255); set(&mut data, 18, 1, 80, 20, 20, 255);
    for x in 8..16 { set(&mut data, x, 2, 60, 15, 15, 255); }
    for x in 7..17 { for y in 3..6 { set(&mut data, x, y, 70, 20, 25, 255); } }
    set(&mut data, 9, 4, 255, 200, 50, 255); set(&mut data, 10, 4, 255, 200, 50, 255);
    set(&mut data, 13, 4, 255, 200, 50, 255); set(&mut data, 14, 4, 255, 200, 50, 255);
    for x in 10..14 { set(&mut data, x, 5, 40, 10, 10, 255); }
    for x in 6..18 { for y in 6..14 { set(&mut data, x, y, 55, 15, 20, 255); } }
    for x in 8..16 { for y in 7..10 { set(&mut data, x, y, 80, 30, 35, 255); } }
    for y in 7..12 { set(&mut data, 4, y, 60, 20, 25, 255); set(&mut data, 5, y, 60, 20, 25, 255); }
    for y in 7..12 { set(&mut data, 18, y, 60, 20, 25, 255); set(&mut data, 19, y, 60, 20, 25, 255); }
    for y in 1..14 { set(&mut data, 21, y, 150, 150, 160, 255); set(&mut data, 22, y, 130, 130, 140, 255); }
    set(&mut data, 20, 8, 120, 100, 40, 255); set(&mut data, 23, 8, 120, 100, 40, 255);
    for y in 14..20 { set(&mut data, 8, y, 50, 15, 18, 255); set(&mut data, 9, y, 50, 15, 18, 255); }
    for y in 14..20 { set(&mut data, 14, y, 50, 15, 18, 255); set(&mut data, 15, y, 50, 15, 18, 255); }
    for y in 20..22 { for x in 7..11 { set(&mut data, x, y, 40, 12, 12, 255); } }
    for y in 20..22 { for x in 13..17 { set(&mut data, x, y, 40, 12, 12, 255); } }
    Texture::from_rgba(gl, &data, s, s).expect("Failed to create boss texture")
}

pub fn create_white_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let data: [u8; 4] = [0xFF, 0xFF, 0xFF, 0xFF];
    Texture::from_rgba(gl, &data, 1, 1).expect("Failed to create white texture")
}

pub fn create_bonfire_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let s: u32 = 32;
    let mut data = vec![0u8; (s * s * 4) as usize];
    let set = |data: &mut Vec<u8>, x: u32, y: u32, r: u8, g: u8, b: u8, a: u8| {
        let i = ((y * s + x) * 4) as usize;
        data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = a;
    };
    for x in 8..24 { for y in 22..28 {
        let shade = if (x + y) % 3 == 0 { 80 } else { 90 };
        set(&mut data, x, y, shade, shade, shade + 10, 255);
    }}
    for x in 8..24 {
        set(&mut data, x, 21, 60, 60, 65, 255);
        set(&mut data, x, 28, 60, 60, 65, 255);
    }
    for y in 21..29 {
        set(&mut data, 7, y, 60, 60, 65, 255);
        set(&mut data, 24, y, 60, 60, 65, 255);
    }
    for x in 10..22 { for y in 20..23 {
        let glow = if (x * 7 + y * 13) % 5 < 2 { 255 } else { 200 };
        set(&mut data, x, y, glow, glow / 3, 0, 255);
    }}
    for x in 13..19 { for y in 12..20 {
        set(&mut data, x, y, 255, 220, 100, 255);
    }}
    for x in 12..20 { for y in 8..16 {
        let a = if (x + y) % 3 == 0 { 200 } else { 255 };
        set(&mut data, x, y, 255, 140, 20, a);
    }}
    for x in 11..21 { for y in 6..12 {
        let a = if (x * 3 + y * 7) % 4 < 2 { 180 } else { 230 };
        set(&mut data, x, y, 220, 80, 10, a);
    }}
    set(&mut data, 14, 5, 200, 60, 10, 200);
    set(&mut data, 15, 4, 180, 50, 10, 160);
    set(&mut data, 16, 3, 160, 40, 5, 120);
    set(&mut data, 17, 4, 180, 50, 10, 160);
    set(&mut data, 18, 5, 200, 60, 10, 200);
    set(&mut data, 10, 7, 255, 200, 50, 200);
    set(&mut data, 21, 8, 255, 180, 40, 180);
    set(&mut data, 12, 5, 255, 220, 80, 150);
    set(&mut data, 19, 6, 255, 200, 60, 170);
    for y in 10..22 { set(&mut data, 15, y, 160, 160, 170, 255); set(&mut data, 16, y, 140, 140, 150, 255); }
    set(&mut data, 15, 14, 200, 180, 100, 255);
    set(&mut data, 16, 15, 200, 180, 100, 255);
    Texture::from_rgba(gl, &data, s, s).expect("Failed to create bonfire texture")
}

pub fn create_scene_fbo(
    gl: &web_sys::WebGl2RenderingContext,
    width: f32,
    height: f32,
) -> (web_sys::WebGlFramebuffer, web_sys::WebGlTexture) {
    use web_sys::WebGl2RenderingContext as GL;
    let tex = gl.create_texture().unwrap();
    gl.bind_texture(GL::TEXTURE_2D, Some(&tex));
    gl.tex_image_2d_with_i32_and_i32_and_i32_and_format_and_type_and_opt_u8_array(
        GL::TEXTURE_2D, 0, GL::RGBA as i32,
        width as i32, height as i32, 0,
        GL::RGBA, GL::UNSIGNED_BYTE, None,
    ).unwrap();
    gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_MIN_FILTER, GL::LINEAR as i32);
    gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_MAG_FILTER, GL::LINEAR as i32);
    gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_WRAP_S, GL::CLAMP_TO_EDGE as i32);
    gl.tex_parameteri(GL::TEXTURE_2D, GL::TEXTURE_WRAP_T, GL::CLAMP_TO_EDGE as i32);
    let fbo = gl.create_framebuffer().unwrap();
    gl.bind_framebuffer(GL::FRAMEBUFFER, Some(&fbo));
    gl.framebuffer_texture_2d(GL::FRAMEBUFFER, GL::COLOR_ATTACHMENT0, GL::TEXTURE_2D, Some(&tex), 0);
    gl.bind_framebuffer(GL::FRAMEBUFFER, None);
    gl.bind_texture(GL::TEXTURE_2D, None);
    (fbo, tex)
}

pub fn create_tileset_texture(gl: &web_sys::WebGl2RenderingContext) -> Texture {
    let width: u32 = 80;
    let height: u32 = 16;
    let mut data = vec![0u8; (width * height * 4) as usize];
    let set_px = |data: &mut Vec<u8>, px: u32, py: u32, r: u8, g: u8, b: u8, a: u8| {
        let offset = ((py * width + px) * 4) as usize;
        data[offset] = r; data[offset+1] = g; data[offset+2] = b; data[offset+3] = a;
    };

    // Tile 1: Ground
    {
        let tx_off = 1 * 16;
        for ty in 0..16u32 {
            for tx in 0..16u32 {
                let px = tx_off + tx;
                let noise = ((tx * 7 + ty * 13) % 17) as u8;
                let base_r = 100u8.saturating_add(noise / 3);
                let base_g = 75u8.saturating_add(noise / 4);
                let base_b = 45u8.saturating_add(noise / 5);
                set_px(&mut data, px, ty, base_r, base_g, base_b, 255);
            }
        }
        for i in 3..9 { set_px(&mut data, tx_off + i, 7, 70, 50, 30, 255); }
        for i in 5..12 { set_px(&mut data, tx_off + i, 11, 65, 45, 25, 255); }
        for x in 0..16 { set_px(&mut data, tx_off + x, 0, 85, 60, 35, 255); }
        for y in 0..16 { set_px(&mut data, tx_off, y, 85, 60, 35, 255); }
    }

    // Tile 2: Wall
    {
        let tx_off = 2 * 16;
        for ty in 0..16u32 {
            for tx in 0..16u32 {
                let px = tx_off + tx;
                let noise = ((tx * 11 + ty * 7) % 13) as u8;
                let base = 85u8.saturating_add(noise / 2);
                set_px(&mut data, px, ty, base, base, base + 5, 255);
            }
        }
        for x in 0..16 { set_px(&mut data, tx_off + x, 4, 55, 55, 58, 255); }
        for x in 0..16 { set_px(&mut data, tx_off + x, 9, 55, 55, 58, 255); }
        for x in 0..16 { set_px(&mut data, tx_off + x, 14, 55, 55, 58, 255); }
        for y in 0..4 { set_px(&mut data, tx_off + 5, y, 55, 55, 58, 255); set_px(&mut data, tx_off + 11, y, 55, 55, 58, 255); }
        for y in 5..9 { set_px(&mut data, tx_off + 3, y, 55, 55, 58, 255); set_px(&mut data, tx_off + 8, y, 55, 55, 58, 255); set_px(&mut data, tx_off + 13, y, 55, 55, 58, 255); }
        for y in 10..14 { set_px(&mut data, tx_off + 6, y, 55, 55, 58, 255); set_px(&mut data, tx_off + 12, y, 55, 55, 58, 255); }
        for x in 0..16 { set_px(&mut data, tx_off + x, 0, 105, 105, 110, 255); }
    }

    // Tile 3: Dark wall
    {
        let tx_off = 3 * 16;
        for ty in 0..16u32 {
            for tx in 0..16u32 {
                let px = tx_off + tx;
                let noise = ((tx * 5 + ty * 9) % 11) as u8;
                let base = 50u8.saturating_add(noise / 3);
                set_px(&mut data, px, ty, base, base, base + 3, 255);
            }
        }
        for x in 2..6 { set_px(&mut data, tx_off + x, 14, 40, 55, 35, 255); set_px(&mut data, tx_off + x, 15, 35, 50, 30, 255); }
        for x in 10..14 { set_px(&mut data, tx_off + x, 13, 40, 55, 35, 255); }
    }

    // Tile 4: Poison
    {
        let tx_off = 4 * 16;
        for ty in 0..16u32 {
            for tx in 0..16u32 {
                let px = tx_off + tx;
                let noise = ((tx * 7 + ty * 11) % 9) as u8;
                set_px(&mut data, px, ty, 20 + noise / 2, 50 + noise, 20 + noise / 3, 220);
            }
        }
        set_px(&mut data, tx_off + 4, 6, 60, 120, 40, 255);
        set_px(&mut data, tx_off + 5, 5, 60, 130, 40, 255);
        set_px(&mut data, tx_off + 10, 8, 50, 110, 35, 255);
        set_px(&mut data, tx_off + 11, 7, 55, 120, 38, 255);
        set_px(&mut data, tx_off + 7, 12, 45, 100, 30, 255);
        set_px(&mut data, tx_off + 8, 11, 50, 110, 32, 255);
        set_px(&mut data, tx_off + 3, 3, 80, 160, 50, 240);
        set_px(&mut data, tx_off + 12, 4, 70, 150, 45, 240);
    }

    Texture::from_rgba(gl, &data, width, height).expect("Failed to create tileset texture")
}
