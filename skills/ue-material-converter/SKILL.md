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

### Custom Node Template

```hlsl
// {{Description}}
// Inputs: {{InputList}}
// Output: {{OutputType}}

{{ReturnType}} {{FunctionName}}({{Parameters}})
{
    {{FunctionBody}}
}
```

### Example Output

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
// Custom Node: ShaderToyCosinePalette
// Inputs:
//   - UV (float2): Texture coordinates
//   - Time (float): Time parameter
// Output: float3 - RGB color

float3 ShaderToyCosinePalette(float2 UV, float Time)
{
    float3 col = 0.5 + 0.5 * cos(Time + UV.xyx + float3(0.0, 2.0, 4.0));
    return col;
}
```

---

## Struct-Based Organization

For complex algorithms with multiple functions, organize using structs:

```hlsl
struct F{{AlgorithmName}}
{
    // Input parameters
    {{InputType}} {{InputName}};

    // Main computation function
    static {{ReturnType}} Compute({{Parameters}})
    {
        {{Implementation}}
    }

    // Helper functions
    static {{ReturnType}} HelperFunction({{Parameters}})
    {
        {{Implementation}}
    }
};
```

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
