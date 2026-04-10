# UE材质转换器 - Skill

用于Unreal Engine材质开发的代码转换工具。

## 功能

1. **蓝图转HLSL函数** - 将UE材质蓝图的文本表示转换为HLSL函数
2. **着色器转Custom节点** - 将Shadertoy/GLSL/HLSL着色器转换为UE Custom节点代码
3. **结构体封装** - 对复杂算法使用结构体进行封装和调用

## 安装

此 skill 符合 Claude Code 标准 skill 格式。

### 自动安装（推荐）

将此 skill 目录复制到你的全局 skills 目录：

**Windows:**
```bash
xcopy /E /I skills\ue-material-converter %USERPROFILE%\.agents\skills\ue-material-converter
mklink /D %USERPROFILE%\.claude\skills\ue-material-converter %USERPROFILE%\.agents\skills\ue-material-converter
```

**Linux/Mac:**
```bash
cp -r skills/ue-material-converter ~/.agents/skills/
ln -s ~/.agents/skills/ue-material-converter ~/.claude/skills/ue-material-converter
```

### 手动安装

1. 复制 `ue-material-converter` 目录到 `~/.agents/skills/`
2. 在 `~/.claude/skills/` 创建符号链接指向该目录

## 目录结构

```
ue-material-converter/
├── SKILL.md           # 主 skill 文件（标准格式）
├── README.md          # 说明文档
└── references/        # 参考文档
    ├── advanced_raymarching.glsl    # 高级光线追踪示例
    ├── blueprint_example.txt         # 蓝图示例
    ├── function_reference.md         # 函数参考
    ├── noise_functions.hlsl          # 噪声函数
    ├── quickstart.md                 # 快速入门
    ├── shadertoy_basics.glsl         # Shadertoy 基础
    └── test_cases.md                 # 测试用例
```

## 使用方法

### 方式1: 直接对话

在对话中直接提及相关需求：
- "请将这个蓝图转换为HLSL函数"
- "这个Shadertoy着色器怎么转换为UE Custom节点？"
- "帮我转换这段GLSL代码"

### 方式2: 自动触发

Claude Code 会根据关键词自动触发此 skill：
- 蓝图转HLSL
- 材质节点转换
- Shadertoy转UE
- GLSL转Custom节点
- HLSL转Custom节点

## 示例

### 示例1: Shadertoy转换（简单函数格式）

**输入**：
```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    vec2 uv = fragCoord/iResolution.xy;
    vec3 col = 0.5 + 0.5*cos(iTime+uv.xyx+vec3(0,2,4));
    fragColor = vec4(col,1.0);
}
```

**输出**：
```hlsl
// Custom节点: CosinePalette
// Inputs:
//   - UV (float2): 纹理坐标
//   - Time (float): 时间参数
// Output: float3 - RGB颜色

float3 MS_CosinePalette_compute(float2 UV, float Time)
{
    float3 col = 0.5 + 0.5 * cos(Time + UV.xyx + float3(0.0, 2.0, 4.0));
    return col;
}

return MS_CosinePalette_compute(UV, Time);
```

### 示例2: 复杂算法转换（结构体格式）

**输入**：
```glsl
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float scene(vec2 uv) {
    return noise(uv * 3.0) * 0.5 + 0.5;
}
```

**输出**：
```hlsl
// Custom节点: ValueNoise
// Inputs:
//   - UV (float2): 纹理坐标
//   - Scale (float): 缩放系数
// Output: float - 噪声值 [0,1]

struct MS_ValueNoise
{
    float hash(float2 p)
    {
        return frac(sin(dot(p, float2(12.9898, 78.233))) * 43758.5453);
    }

    float noise(float2 p)
    {
        float2 i = floor(p);
        float2 f = frac(p);
        f = f * f * (3.0 - 2.0 * f);

        float a = hash(i);
        float b = hash(i + float2(1.0, 0.0));
        float c = hash(i + float2(0.0, 1.0));
        float d = hash(i + float2(1.0, 1.0));

        return lerp(lerp(a, b, f.x), lerp(c, d, f.x), f.y);
    }

    float compute(float2 UV, float Scale)
    {
        return noise(UV * Scale) * 0.5 + 0.5;
    }
}

MS_ValueNoise_Inst;
return MS_ValueNoise_Inst.compute(UV, Scale);
```

## 依赖关系

- Unreal Engine 5.0+
- 材质编辑器Custom节点
- 基础HLSL知识

## 常见问题

**Q: 转换后的代码报错？**
A: 检查UE版本差异，某些函数在不同版本中可能有所不同。

**Q: 纹理采样如何处理？**
A: 需要在材质中创建Texture2D参数，然后使用`Texture2DSample(Tex, TexSampler, UV)`。

**Q: Shadertoy的iTime如何替换？**
A: 使用`View.RealTime`或创建自定义时间参数。

## 相关技能

- **ue-materials-rendering** - 材质基础、MID、后处理等渲染概念
- **ue-niagara-effects** - VFX 和粒子系统的自定义 HLSL

## 贡献

欢迎提交问题和改进建议！
