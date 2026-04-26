# DS2D - 2D Dark Souls 2 技术设计文档

## Context

制作一个俯视角 2D 版本的黑暗之魂 2，使用 Rust 编译到 WASM，直接操作 WebGL2 渲染。项目从零开始，目标是完成一个可玩的完整 MVP。

**核心定位：** 俯视角（类暗黑破坏神视角），2.5D 骨骼动画（DragonBones 格式），无缝大地图，忠实还原 DS2 的战斗手感和 RPG 深度。

---

## 1. 架构：传统 OOP Trait Objects

实体数量有限（30-60 活跃敌人），选择 OOP 而非 ECS：

- `Box<dyn Entity>` 扁平数组，每个实体实现 `update()`/`render()`/`take_damage()`
- 骨骼动画树、武器招式、Boss 阶段逻辑天然映射为 trait 实现
- WASM 单线程环境下 ECS 的并行优势无法利用
- 预计 2-3 周完成核心架构

---

## 2. 模块结构

```
ds2d/
  src/
    main.rs / lib.rs
    core/          -- 时间、输入、数学、摄像机、变换
    render/        -- WebGL2 上下文、着色器、纹理、精灵批渲染、骨骼渲染、Tilemap、灯光、后处理
    world/         -- Tileset、Chunk、Area、WorldMap、碰撞、导航网格、实体生成
    entity/        -- Entity trait、Player、Enemy、Boss、Projectile、Prop、交互
    combat/        -- Hitbox/Hurtbox、精力、招式、武器、伤害计算、韧性、状态效果
    rpg/           -- 属性、灵魂等级、装备、灵魂消耗、属性补正
    dragonbones/   -- 解析器、Armature、Bone、Slot、Skin、动画播放器、混合器、IK
    ai/            -- 状态机、行为树、仇恨、巡逻、Boss AI
    save/          -- 存档数据、营火、IndexedDB
    audio/         -- Web Audio 桥接、空间音频、音乐、音效
    bridge/        -- WASM 入口、JS 绑定、资源加载、手柄
  static/
    index.html / index.js / styles.css
    assets/        -- 纹理、DragonBones、音频、地图
    shaders/       -- GLSL ES 3.00 着色器
```

---

## 3. 游戏主循环

- 固定时间步长 60Hz（16.666ms），`requestAnimationFrame` 驱动
- 累加器模式：物理/战斗/动画以固定步长更新，渲染用 alpha 插值平滑
- 最大帧时间 100ms 防止死循环
- 顺序：输入 → AI → 战斗 → 物理/碰撞 → 动画 → 渲染 → 音频

---

## 4. 渲染管线（5 Pass）

| Pass | 内容 | 输出 |
|------|------|------|
| 1. Tilemap | 实例化四边形渲染可见 Chunk | 主 FBO (color + depth) |
| 2. 角色 | 精灵批 + 骨骼渲染，按 Y 坐标排序 | 主 FBO + 法线贴图 FBO |
| 3. 灯光 | 每光源全屏四边形，读取法线+深度 | 灯光累积 FBO |
| 4. 合成 | 颜色 + 灯光 + 暗角 + 色调 + 迷雾 | 屏幕 |
| 5. UI | 正交投影 HUD | 屏幕 |

**精灵批渲染：** 单个单位四边形 VBO + 实例数据 VBO，同纹理图集合并为一个 `drawArraysInstanced` 调用。最大 16384 实例，`bufferSubData` 直接从 WASM 线性内存写入。

**灯光：** 点光源/聚光灯，配合法线贴图产生 2.5D 体积感。活跃光源上限 8-12 个，距离裁剪。

---

## 5. 地图系统

- Tile = 16x16 像素，Chunk = 32x32 Tile（512x512 世界像素）
- 玩家周围加载 5x5 Chunk 环（半径 2），约 160x160 Tile 可见
- Area = 命名的 Chunk 集合 + 元数据（音乐、环境色、迷雾、Boss 定义）
- 区域过渡通过世界空间触发器矩形实现
- 碰撞：预计算 1024-bit 位标记（128 字节/Chunk），AABB 查询
- AI 寻路：降采样导航网格，A* 在 Web Worker 中执行

---

## 6. 战斗系统

**状态机：** IDLE → LIGHT_ATTACK → CHAIN → RECOVERY → IDLE，分支包括 ROLL、BLOCK、PARRY、STAGGERED、BACKSTAB、DEAD。

**Hitbox/Hurtbox：**
- Hitbox 形状：Rect / Circle / Capsule，含伤害、击退、韧性伤害、活跃帧范围
- 每帧收集活跃 Hitbox，与对立 HitGroup 的 Hurtbox 碰撞检测
- 首次接触：伤害 → 韧性检测 → 击退 → 标记 Hitbox 为已消耗
- 无敌帧：翻滚期间 Hurtbox 标记为不可命中

**精力：** 轻击 15-25、重击 25-40、翻滚 20-30、格挡 10-40（视盾牌稳定性）。攻击/翻滚/格挡期间暂停回复，延迟后恢复。

**武器招式：** `WeaponMoveset` trait 提供轻击链、重击、跑攻、滚攻、背刺、弹反。每种武器独立实现。

---

## 7. RPG 系统

**属性：** VIG/END/VIT/STR/DEX/ADP/INT/FTH/ATT/LCK（对应 DS2）
- 派生属性：HP、精力上限、装备负重、敏捷度（影响无敌帧数）
- 敏捷度断点：92=8帧、105=13帧、110=15帧

**升级：** 灵魂消耗近似立方增长，需找到对应 NPC 才能升级。

**装备：** 右手x2、左手x2、头/胸/手/腿、戒指x4。双手持握获得 1.5x 力量加成。

**伤害公式（简化 DS2）：**
- AR = 武器基础伤害 + 属性补正
- 防御减免按 AR 与防御力比值分三档计算
- counter 加成 1.2-1.6x（攻击动画期间命中）

---

## 8. DragonBones 集成

**解析：** 用 serde 反序列化 DragonBones JSON 5.x，Bone 的 parent 字符串引用在解析后转换为索引。

**运行时：**
- 扁平 Bone 数组（父在前子在后）
- 每帧：动画时间线求值 → 插值变换叠加到休息姿态 → 自顶向下计算世界变换 → IK 约束求解 → Slot 渲染

**动画混合：**
- 多层 BlendLayer（上半身/下半身分离）
- 交叉淡入淡出：线性插值两段动画的骨骼变换
- 常见场景：待机→行走 150ms、任意→翻滚 50ms 快速切换

**MVP 渲染：** 仅使用 image 类型 Slot（无网格形变），足够实现 2.5D 效果。

---

## 9. AI 系统

**敌人状态机：** IDLE → ALERT → COMBAT → ATTACK → RETREAT → DESPERATE（低血量）
- 每个状态评估转移条件（距离、精力、血量阈值、计时器）

**仇恨表：** 检测半径 + 视线检测，伤害产生仇恨值，治疗行为大幅增加仇恨。

**Boss：** 阶段控制器，每个阶段有独立血量阈值、可用攻击列表、速度倍率、AI 模式（序列/反应/狂暴）。阶段转换触发无敌时间和特殊动画。

---

## 10. 存档系统

- 营火休息触发自动存档到 IndexedDB（`ds2d_save` 数据库，3 个存档槽）
- 存档内容：角色属性/装备/背包、已解锁营火、Boss 击杀记录、世界状态（门/道具/捷径）、当前位置
- 死亡：灵魂掉落在死亡位置（血迹），在营火复活
- 营火间快速旅行（DS2 初始即可用）

---

## 11. 音频

- JS 端 Web Audio API 处理（AudioContext、音乐总线、音效总线）
- Rust 通过 `wasm_bindgen` 外部函数发送命令
- 空间音效：基于听众/声源位置计算声像和音量衰减
- 区域音乐：进入新区域时 2-3 秒交叉淡入淡出

---

## 12. WASM/Web 桥接

**构建：** `wasm-pack build --target web`，GLSL ES 3.00 着色器。

**输入：** JS 注册 keydown/keyup 写入共享 Uint8Array（WASM 线性内存），Rust 每帧轮询。手柄通过 Gamepad API。

**资源加载：** JS fetch → 传递字符串/位图给 Rust → serde 反序列化 / WebGL2 上传。加载屏幕显示进度。

**关键依赖：** wasm-bindgen, web-sys, glam, serde/serde_json, idb, console_error_panic_hook

---

## 13. 开发服务器

运行在 `192.168.1.10`，提供：
- 静态资源服务（纹理、JSON、音频）
- 视觉模型图展示
- WebSocket 热重载桥接（资源变更时通知 WASM 客户端重新加载）

---

## 14. 实现阶段（17 步，每步产出可测试里程碑）

| 阶段 | 内容 | 里程碑 |
|------|------|--------|
| 1 | WASM 入口 + WebGL2 上下文 + 清屏 | 彩色画布 |
| 2 | 着色器 + 纹理 + 精灵批渲染 | 显示单个精灵 |
| 3 | 时间 + 输入 + 摄像机 | 键盘移动精灵，摄像机跟随 |
| 4 | Tilemap 渲染 + Tileset + Chunk | 显示 Tile 地图，可行走 |
| 5 | 碰撞 + 区域 + WorldMap | 碰撞检测，多 Chunk 加载 |
| 6 | DragonBones 解析 + 骨骼动画 | 显示并播放 DragonBones 角色 |
| 7 | Entity trait + Player 实体 | 玩家实体含动画、移动、碰撞 |
| 8 | Hitbox + 精力 + 招式 + 武器 | 攻击碰撞，精力消耗 |
| 9 | Enemy + AI 状态机 + 仇恨 | 敌人检测、接近、攻击 |
| 10 | 伤害计算 + RPG 属性 + 装备 | 完整伤害公式，装备效果 |
| 11 | Boss + Boss AI | 多阶段 Boss 战 |
| 12 | 营火 + 存档 + IndexedDB | 营火休息、存档/读档 |
| 13 | 灯光 + 法线贴图 + 后处理 | 动态光照，氛围效果 |
| 14 | 音频引擎 + 空间音频 | 音效和音乐 |
| 15 | 导航网格 + 巡逻 | 敌人寻路 |
| 16 | 动画混合 | 平滑交叉淡入淡出 |
| 17 | UI + 菜单 + 死亡/重生 | 完整游戏循环 |

---

## 15. 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| WASM 体积过大 | wasm-opt -Oz，裁剪 web-sys features |
| 灯光 Pass 帧率低于 30fps | 光源上限 8，半分辨率渲染灯光 |
| DragonBones 网格蒙皮复杂 | MVP 仅用 image 类型，mesh 延后 |
| IndexedDB 写入中断 | 原子写入：先写临时 key 再重命名 |
| wasm-bindgen Closure 内存泄漏 | 谨慎管理生命周期，持久 Closure 存入 thread_local |
