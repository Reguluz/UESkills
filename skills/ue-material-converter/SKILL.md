---
name: ue-material-converter
description: Use when converting shader code for Unreal Engine materials: blueprint to HLSL functions, Shadertoy/GLSL/HLSL to Custom nodes, or shader porting. Handles texture sampling, coordinate systems, and UE material expression syntax. For material rendering fundamentals, see ue-materials-rendering.
metadata:
  version: 1.0.0
---

# UE Material Converter

You are an expert in converting shader code between different formats for Unreal Engine material development.

## Context

Read `.agents/ue-project-context.md` for engine version and project-specific material conventions. UE material HLSL has specific restrictions compared to standard HLSL - no bitwise operations on older versions, specific texture sampling syntax, and coordinate system differences.

## Before You Start

Identify the conversion type needed:
- **Blueprint → HLSL** - Convert material blueprint node graphs to HLSL functions
- **Shadertoy → Custom Node** - Port Shadertoy GLSL shaders to UE Custom nodes
- **GLSL → HLSL** - Convert GLSL shaders to UE-compatible HLSL
- **HLSL → Custom Node** - Adapt standard HLSL for UE material expressions

---

## Blueprint to HLSL Conversion

When users provide UE material blueprint text (copied as code), analyze the node graph structure and convert to equivalent HLSL.

### Blueprint Format Recognition

```
// Common blueprint text format:
[NodeName]
  Input: Previous → Output
  Input: Value1 → Output
  Input: Value2 → Output
```

### Conversion Guidelines

1. **Analyze node connections** - Trace the data flow from inputs to outputs
2. **Identify node types** - Math operations, texture sampling, vector operations
3. **Map to HLSL functions** - Convert each node to equivalent HLSL code
4. **Preserve parameters** - Keep input/output parameters clear and typed
5. **Add documentation** - Comment the original blueprint structure

### Common Node Mappings

| Blueprint Node | HLSL Equivalent |
|----------------|-----------------|
| `Add` (Vector) | `A + B` |
| `Multiply` | `A * B` |
| `Dot Product` | `dot(A, B)` |
| `Cross Product` | `cross(A, B)` |
| `Normalize` | `normalize(V)` |
| `Lerp` | `lerp(A, B, Alpha)` |
| `TextureSample` | `Texture2DSample(Tex, TexSampler, UV)` |
| `ComponentMask` | `float2/3/4 swizzle` (.xy, .xyz, etc.) |

---

## Shadertoy/GLSL to Custom Node Conversion

### Shader Variable Mapping

| Shadertoy/GLSL | UE Custom Node |
|----------------|----------------|
| `fragCoord` | `(UV + View.ViewSizeAndInvSize.zw * 0.5) * View.ViewSizeAndInvSize.xy` |
| `iResolution` | `View.ViewSizeAndInvSize.xy` |
| `iTime` | `View.RealTime` |
| `iChannel0-3` | User-provided texture parameters |
| `iMouse` | Custom float4 parameter needed |

### Type Conversions

| GLSL Type | HLSL Type |
|-----------|-----------|
| `vec2` | `float2` |
| `vec3` | `float3` |
| `vec4` | `float4` |
| `mat2` | `float2x2` |
| `mat3` | `float3x3` |
| `mat4` | `float4x4` |
| `float/int/bool` | `float/int/bool` (same) |

### Function Conversions

| GLSL Function | HLSL Function |
|---------------|---------------|
| `mix(a, b, t)` | `lerp(a, b, t)` |
| `fract(x)` | `frac(x)` |
| `texture(tex, uv)` | `Texture2DSample(Tex, TexSampler, UV)` |
| `textureLod(tex, uv, level)` | `Texture2DSampleLevel(Tex, TexSampler, UV, Level)` |
| `dFdx(x)` | `ddx(x)` |
| `dFdy(x)` | `ddy(x)` |
| `mod(x, y)` | `fmod(x, y)` |
| `inversesqrt(x)` | `rsqrt(x)` |

### Coordinate System Differences

**Shadertoy**: UV origin at bottom-left, Y points up
**UE**: UV origin at top-left, Y points down

Apply Y-flip when needed:
```hlsl
float2 ShadertoyUV = float2(UV.x, 1.0 - UV.y);
```

### Texture Sampling in UE

UE material texture sampling requires both texture and sampler:
```hlsl
// Create Texture2D and Sampler parameters in material
// Then use in Custom node:
float4 Color = Texture2DSample(TextureParam, TextureParamSampler, UV);
```

For LOD sampling:
```hlsl
float4 Color = Texture2DSampleLevel(TextureParam, TextureParamSampler, UV, MipLevel);
```

---

## Output Format

### Standard Custom Node Template

用于简单函数，直接返回计算结果：

```hlsl
// {{Description}}
// Inputs: {{InputList}}
// Output: {{OutputType}}

{{ReturnType}} {{FunctionName}}({{Parameters}})
{
    {{FunctionBody}}
}
```

### Struct-Based Template (推荐)

用于复杂算法，使用 struct 包装所有函数：

```hlsl
struct MS_{{FunctionName}}
{
    // 辅助函数定义
    {{ReturnType}} {{HelperFunctionName}}({{Parameters}})
    {
        {{FunctionBody}}
    }

    // 主计算函数
    {{ReturnType}} compute({{Parameters}})
    {
        {{FunctionBody}}
    }
}

MS_{{FunctionName}}_Inst;
return MS_{{FunctionName}}_Inst.compute({{Arguments}});
```

**Struct 命名规则**：
- 使用 `MS_` 前缀（Material Structure）
- 结构体函数使用驼峰命名，如 `perlinNoise`, `fbm`
- 主计算函数统一命名为 `compute`
- 实例名使用 `MS_{{FunctionName}}_Inst` 格式

### Example Output

**简单函数示例**：

**Input (Shadertoy)**:
```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    vec2 uv = fragCoord / iResolution.xy;
    vec3 col = 0.5 + 0.5 * cos(iTime + uv.xyx + vec3(0, 2, 4));
    fragColor = vec4(col, 1.0);
}
```

**Output (UE Custom Node)**:
```hlsl
// Cosine Palette - 简单函数格式
// Inputs:
//   - UV (float2): Texture coordinates
//   - Time (float): Time parameter
// Output: float3 - RGB color

float3 MS_CosinePalette_compute(float2 UV, float Time)
{
    float3 col = 0.5 + 0.5 * cos(Time + UV.xyx + float3(0.0, 2.0, 4.0));
    return col;
}

return MS_CosinePalette_compute(UV, Time);
```

**复杂算法示例（Struct 格式）**：

```hlsl
// Perlin Noise FBM
// Inputs:
//   - UV (float2): Texture coordinates
//   - Time (float): Time parameter
//   - Scale (float): Noise scale
//   - Speed (float): Animation speed
//   - Iter (int): FBM iterations
// Output: float - Noise value 0-1

struct MS_PerlinNoiseFBM
{
    float3 hash3(float3 p)
    {
        p = float3(
            dot(p, float3(127.1, 311.7, 74.7)),
            dot(p, float3(269.5, 183.3, 246.1)),
            dot(p, float3(113.5, 271.9, 124.6))
        );
        return -1.0 + 2.0 * frac(sin(p) * 43758.5453123);
    }

    float perlinNoise(float3 p)
    {
        float3 i = floor(p);
        float3 f = frac(p);
        float3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
        return lerp(
            lerp(
                lerp(dot(hash3(i + float3(0,0,0)), f - float3(0,0,0)),
                     dot(hash3(i + float3(1,0,0)), f - float3(1,0,0)), u.x),
                lerp(dot(hash3(i + float3(0,1,0)), f - float3(0,1,0)),
                     dot(hash3(i + float3(1,1,0)), f - float3(1,1,0)), u.x), u.y),
            lerp(
                lerp(dot(hash3(i + float3(0,0,1)), f - float3(0,0,1)),
                     dot(hash3(i + float3(1,0,1)), f - float3(1,0,1)), u.x),
                lerp(dot(hash3(i + float3(0,1,1)), f - float3(0,1,1)),
                     dot(hash3(i + float3(1,1,1)), f - float3(1,1,1)), u.x), u.y),
            u.z
        ) * 0.5 + 0.5;
    }

    float fbm(float3 p, int iter)
    {
        float value = 0.0;
        float amplitude = 0.5;
        float frequency = 1.0;
        for (int i = 0; i < iter; i++)
        {
            value += amplitude * perlinNoise(p * frequency);
            frequency *= 2.0;
            amplitude *= 0.5;
        }
        return value;
    }

    float compute(float2 uv, float time, float scale, float speed, int iter)
    {
        float3 p = float3(uv * scale + float2(0.0, time * speed), 0.0);
        float col = fbm(p, iter);
        col = pow(saturate(col), 0.4545);
        return col;
    }
}

MS_PerlinNoiseFBM_Inst;
return MS_PerlinNoiseFBM_Inst.compute(UV, Time, Scale, Speed, Iter);
```

---

## Struct-Based Organization (标准格式)

对于包含多个函数的复杂算法，统一使用以下 struct 格式：

**命名规范**：
- 结构体：`MS_{{FunctionName}}`（MS = Material Structure）
- 实例变量：`MS_{{FunctionName}}_Inst`
- 主函数：`compute()`
- 辅助函数：驼峰命名，如 `hash3()`, `perlinNoise()`

```hlsl
struct MS_{{FunctionName}}
{
    // 辅助函数 - 不使用 static
    {{ReturnType}} {{HelperFunctionName}}({{Parameters}})
    {
        {{Implementation}}
    }

    // 主计算函数 - 统一命名为 compute
    {{ReturnType}} compute({{Parameters}})
    {
        {{Implementation}}
    }
}

// 创建实例
MS_{{FunctionName}}_Inst;
// 调用并返回
return MS_{{FunctionName}}_Inst.compute({{Arguments}});
```

**关键规则**：
1. 结构体内部函数不使用 `static` 关键字
2. 主计算函数统一命名为 `compute`
3. 结构体命名使用 `MS_` 前缀，实例名使用 `_Inst` 后缀
4. 辅助函数可以被 `compute` 或其他辅助函数调用
5. 最后必须返回 `compute` 函数的调用结果

---

## UE Material HLSL Restrictions

### Version-Specific Limitations

- **UE 5.0-**: No bitwise operations on `float` types
- **UE 5.1+**: Some bitwise operations supported, but prefer intrinsic functions
- **No recursion**: Material HLSL doesn't support recursive functions
- **Limited loops**: Prefer unrolled loops, avoid dynamic iteration counts

### Performance Considerations

- Avoid complex dynamic loops
- Use built-in functions (`lerp`, `smoothstep`, etc.) over manual implementations
- Minimize texture samples
- Prefer vectorized operations
- Consider moving complex logic to Material Functions for reuse

---

## 格式选择指南

### 使用简单函数格式
适用于以下场景：
- 单一计算函数，无辅助函数
- 代码量少于 10 行
- 简单的数学运算或颜色计算

**示例**：
```hlsl
float3 MS_SimpleColor_compute(float2 UV, float Time)
{
    float3 col = 0.5 + 0.5 * cos(Time + UV.xyx + float3(0.0, 2.0, 4.0));
    return col;
}

return MS_SimpleColor_compute(UV, Time);
```

### 使用结构体格式（推荐用于复杂算法）
适用于以下场景：
- 需要多个辅助函数
- 代码量超过 10 行
- 复杂的噪声、SDF、光线追踪等算法
- 函数之间需要相互调用

**命名规范**：
- 结构体：`MS_{{FunctionName}}`
- 实例：`MS_{{FunctionName}}_Inst`
- 主函数：`compute()`
- 辅助函数：驼峰命名，不使用 `static`

**示例结构**：
```hlsl
struct MS_AlgorithmName
{
    // 辅助函数可以相互调用
    float helper1(float3 p) { ... }
    float helper2(float3 p) { ... }

    // 主计算函数
    float compute(float2 UV, float Time) { ... }
}

MS_AlgorithmName_Inst;
return MS_AlgorithmName_Inst.compute(UV, Time);
```

---

## Conversion Workflow

1. **Analyze input** - Identify code type (Blueprint/Shadertoy/GLSL/HLSL)
2. **Extract logic** - Understand algorithm core and dependencies
3. **Convert syntax** - Rewrite in target format
4. **Handle differences** - Map coordinate systems, uniforms, and built-ins
5. **Verify output** - Check syntax and logical correctness
6. **Document usage** - Explain inputs, outputs, and usage notes

---

## Common Issues and Solutions

### Issue: Division by Zero
```hlsl
// Add protection
float Result = (Denominator != 0.0) ? Numerator / Denominator : 0.0;
```

### Issue: Texture Sampling without Sampler
```hlsl
// WRONG: float4 Color = Texture2D.Sample(UV);
// CORRECT: Requires both texture and sampler
float4 Color = Texture2DSample(TextureParam, TextureParamSampler, UV);
```

### Issue: Coordinate System Mismatch
```hlsl
// Flip Y for Shadertoy conversions
float2 CorrectUV = float2(UV.x, 1.0 - UV.y);
```

### Issue: Array Indexing
```hlsl
// Materials don't support dynamic array indexing
// Use manual expansion or constant indices
float3 Result = (Index == 0) ? Arr[0] : (Index == 1) ? Arr[1] : Arr[2];
```

---

## Related Skills

- **ue-materials-rendering** - Material fundamentals, MID, post-processing, and rendering concepts
- **ue-niagara-effects** - VFX and particle systems with custom HLSL

---

## References

See [references/](references/) for:
- [function_reference.md](references/function_reference.md) - Complete UE material function reference
- [quickstart.md](references/quickstart.md) - Quick start examples
- [test_cases.md](references/test_cases.md) - Test cases and edge cases
- [noise_functions.hlsl](references/noise_functions.hlsl) - Noise function implementations
- [advanced_raymarching.glsl](references/advanced_raymarching.glsl) - Advanced ray marching example
- [shadertoy_basics.glsl](references/shadertoy_basics.glsl) - Shadertoy basics
- [blueprint_example.txt](references/blueprint_example.txt) - Blueprint node examples
