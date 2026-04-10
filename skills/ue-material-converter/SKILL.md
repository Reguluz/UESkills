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

## HLSL to Blueprint Nodes（蓝图节点组合）

当满足以下条件时，应优先使用蓝图节点组合而非 HLSL Custom 节点：

### 使用蓝图节点的条件

1. **蓝图节点功能足够**：算法可以用 UE 内置材质节点完整实现
2. **用户明确要求**：用户明确提出希望使用蓝图节点方式
3. **可读性和可维护性**：蓝图节点更易于理解和调试
4. **性能考虑**：内置节点通常经过优化，性能更好
5. **团队协作**：团队其他成员更熟悉蓝图节点

### 常见适合蓝图节点的算法

以下算法类型通常适合用蓝图节点实现：

| 算法类型 | 推荐方式 | 原因 |
|---------|---------|------|
| 颜色插值/混合 | 蓝图节点 | `Lerp`、`Multiply`、`Add` 等基础节点直观易懂 |
| 简单数学运算 | 蓝图节点 | `Max`、`Min`、`Clamp`、`Abs` 等内置节点足够 |
| 向量操作 | 蓝图节点 | `Dot Product`、`Cross Product`、`Normalize` 节点齐全 |
| 纹理采样 | 蓝图节点 | `TextureSample` 节点支持完整功能 |
| 条件分支 | 蓝图节点 | `StaticSwitch`、`If` 节点功能完善 |
| 简单噪声 | Custom 节点 | Perlin/Simplex 噪声通常需要自定义代码 |
| 复杂 SDF | Custom 节点 | Raymarching 和 SDF 组合逻辑复杂 |
| 自定义数学函数 | Custom 节点 | 特殊数学公式用代码更简洁 |

### 蓝图节点组合示例

#### 示例1：雾颜色渐变混合（适合蓝图节点）

**需求描述**：
- 在两种雾颜色之间基于输入值进行插值
- 使用 Curve Atlas 或直接颜色插值
- 应用静态开关选择模式

**蓝图节点组合方式**：

```
输入参数：
- FogDensity (float): 雾密度 0-1
- FogThinColor (float3): 薄雾颜色 RGB(0.847, 0.888, 1.0)
- FogThickColor (float3): 厚雾颜色 RGB(0.006, 0.091, 0.250)
- GradientColor (bool): 是否使用曲线渐变

节点组合：
1. StaticSwitch (GradientColor)
   ├─ True: CurveAtlasRowParameter
   │   └─ 输入: ComponentMask(FogDensity, R)
   │   └─ 输出: 渐变采样颜色
   └─ False: Lerp (线性插值)
       ├─ A: FogThinColor
       ├─ B: FogThickColor
       └─ Alpha: FogDensity

输出：FogColor (float3)
```

**对应蓝图复制文本**（Expression-Only 格式，所有引用节点自包含）：
```
Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_ThinColor"
   Begin Object Class=/Script/Engine.MaterialExpressionVectorParameter Name="MaterialExpressionVectorParameter_0"
   End Object
   Begin Object Name="MaterialExpressionVectorParameter_0"
      DefaultValue=(R=0.846873,G=0.887923,B=1.000000,A=1.000000)
      ParameterName="FogThinColor"
      Group="Color"
      MaterialExpressionEditorX=2176
      MaterialExpressionEditorY=780
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionVectorParameter'MaterialExpressionVectorParameter_0'"
   NodePosX=2176
   NodePosY=780
   bCanRenameNode=True
End Object

Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_ThickColor"
   Begin Object Class=/Script/Engine.MaterialExpressionVectorParameter Name="MaterialExpressionVectorParameter_1"
   End Object
   Begin Object Name="MaterialExpressionVectorParameter_1"
      DefaultValue=(R=0.005605,G=0.090842,B=0.250158,A=1.000000)
      ParameterName="FogThickColor"
      Group="Color"
      MaterialExpressionEditorX=2176
      MaterialExpressionEditorY=1056
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionVectorParameter'MaterialExpressionVectorParameter_1'"
   NodePosX=2176
   NodePosY=1056
   bCanRenameNode=True
End Object

Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Density"
   Begin Object Class=/Script/Engine.MaterialExpressionScalarParameter Name="MaterialExpressionScalarParameter_0"
   End Object
   Begin Object Name="MaterialExpressionScalarParameter_0"
      DefaultValue=0.500000
      ParameterName="FogDensity"
      Group="Fog"
      MaterialExpressionEditorX=2176
      MaterialExpressionEditorY=920
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionScalarParameter'MaterialExpressionScalarParameter_0'"
   NodePosX=2176
   NodePosY=920
   bCanRenameNode=True
End Object

Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Lerp"
   Begin Object Class=/Script/Engine.MaterialExpressionLinearInterpolate Name="MaterialExpressionLinearInterpolate_0"
   End Object
   Begin Object Name="MaterialExpressionLinearInterpolate_0"
      A=(Expression="/Script/Engine.MaterialExpressionVectorParameter'MaterialGraphNode_ThinColor.MaterialExpressionVectorParameter_0'",Mask=1,MaskR=1,MaskG=1,MaskB=1)
      B=(Expression="/Script/Engine.MaterialExpressionVectorParameter'MaterialGraphNode_ThickColor.MaterialExpressionVectorParameter_1'",Mask=1,MaskR=1,MaskG=1,MaskB=1)
      Alpha=(Expression="/Script/Engine.MaterialExpressionScalarParameter'MaterialGraphNode_Density.MaterialExpressionScalarParameter_0'")
      MaterialExpressionEditorX=2688
      MaterialExpressionEditorY=920
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionLinearInterpolate'MaterialExpressionLinearInterpolate_0'"
   NodePosX=2688
   NodePosY=920
End Object
```

#### 示例2：亮度计算（适合蓝图节点）

**需求**：使用感知亮度公式计算颜色亮度

**蓝图节点组合**：
```
1. Constant3Vector: (0.2126, 0.7152, 0.0722) - 感知亮度权重
2. DotProduct: Color.rgb ⊙ Weight
3. Max(DotResult, 0.0001) - 避免除零
```

#### 示例3：复杂算法应使用 Custom 节点（对比）

**需要 HLSL 的情况**：
```hlsl
// 这种复杂算法应该使用 Custom 节点
struct MS_PerlinNoiseFBM
{
    float hash3(float3 p) { ... }
    float perlinNoise(float3 p) { ... }
    float fbm(float3 p, int iter) { ... }
    float compute(float2 uv, float time, float scale, float speed, int iter) { ... }
}
MS_PerlinNoiseFBM_Inst;
return MS_PerlinNoiseFBM_Inst.compute(UV, Time, Scale, Speed, Iter);
```

### 蓝图节点组合输出格式

当决定使用蓝图节点时，按以下格式输出：

```markdown
## 蓝图节点组合方案

### 输入参数
| 参数名 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| Density | float | 0.5 | 雾密度 [0,1] |
| ThinColor | float3 | (0.847,0.888,1.0) | 薄雾颜色 |
| ThickColor | float3 | (0.006,0.091,0.250) | 厚雾颜色 |
| UseGradient | bool | false | 是否使用曲线渐变 |

### 节点组合流程
```
[可使用 ASCII 图或 Mermaid 图表示节点连接]
```

### 节点详细说明
1. **StaticSwitch_节点**
   - 用途：模式切换
   - 输入：UseGradient (bool)
   
2. **Lerp_节点**
   - 用途：颜色线性插值
   - A输入：ThinColor
   - B输入：ThickColor  
   - Alpha输入：Density

### 蓝图复制文本
[提供可复制粘贴的蓝图文本]

### 优势说明
- ✓ 使用内置节点，性能优化
- ✓ 可视化连接，易于理解
- ✓ 参数可在外部调整
- ✓ 无需维护 HLSL 代码
```

### 蓝图复制文本格式规范

当生成蓝图复制文本时，**必须严格遵循以下格式规范**，否则粘贴到 UE 材质编辑器中会失败或导致崩溃。

#### 禁止规则

1. **禁止生成 `MaterialExpressionComment`（Comment 框）** — AI 无法生成有效的 Comment 框序列化数据，粘贴会导致 UE 材质编辑器崩溃
2. **禁止生成 `CustomProperties Pin` 块** — 其中的 PinId、PersistentGuid、LinkedTo 等字段由 UE 编辑器内部自动管理，AI 无法生成合法的 GUID 值，包含这些字段会导致连接失败
3. **禁止使用假 GUID** — 不要使用 `TEXCOORD_PIN_OUT`、`MUL1_A_PERSIST` 等非法标识符代替 GUID

#### 节点连接机制（Expression-Only 格式）

节点之间的连接**仅通过** MaterialExpression 内部对象的输入属性 `Expression=` 引用来建立：

```
A=(Expression="/Script/Engine.MaterialExpressionType'OuterNodeName.InnerExpressionName'")
```

- `OuterNodeName` = MaterialGraphNode 的 `Name` 属性
- `InnerExpressionName` = 内部 MaterialExpression 对象的 `Name` 属性
- UE 粘贴时会根据 Expression 引用路径自动重建所有 Pin 连接

#### 标准节点模板

**单输入节点**（如 Floor、Frac、Sin）：
```
Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Floor"
   Begin Object Class=/Script/Engine.MaterialExpressionFloor Name="MaterialExpressionFloor_0"
   End Object
   Begin Object Name="MaterialExpressionFloor_0"
      Input=(Expression="/Script/Engine.MaterialExpressionMultiply'MaterialGraphNode_Multiply.MaterialExpressionMultiply_0'")
      MaterialExpressionEditorX=400
      MaterialExpressionEditorY=200
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionFloor'MaterialExpressionFloor_0'"
   NodePosX=400
   NodePosY=200
End Object
```

**双输入节点**（如 Add、Multiply、Lerp）：
```
Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Multiply"
   Begin Object Class=/Script/Engine.MaterialExpressionMultiply Name="MaterialExpressionMultiply_0"
   End Object
   Begin Object Name="MaterialExpressionMultiply_0"
      A=(Expression="/Script/Engine.MaterialExpressionTextureCoordinate'MaterialGraphNode_TexCoord.MaterialExpressionTextureCoordinate_0'")
      ConstB=10.000000
      MaterialExpressionEditorX=224
      MaterialExpressionEditorY=32
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionMultiply'MaterialExpressionMultiply_0'"
   NodePosX=224
   NodePosY=32
End Object
```

**常量节点**（无输入连接）：
```
Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Const1"
   Begin Object Class=/Script/Engine.MaterialExpressionConstant Name="MaterialExpressionConstant_0"
   End Object
   Begin Object Name="MaterialExpressionConstant_0"
      R=0.500000
      MaterialExpressionEditorX=100
      MaterialExpressionEditorY=300
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionConstant'MaterialExpressionConstant_0'"
   NodePosX=100
   NodePosY=300
End Object
```

**VectorParameter 节点**：
```
Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Color"
   Begin Object Class=/Script/Engine.MaterialExpressionVectorParameter Name="MaterialExpressionVectorParameter_0"
   End Object
   Begin Object Name="MaterialExpressionVectorParameter_0"
      DefaultValue=(R=0.846873,G=0.887923,B=1.000000,A=1.000000)
      ParameterName="MyColor"
      Group="Color"
      MaterialExpressionEditorX=200
      MaterialExpressionEditorY=780
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionVectorParameter'MaterialExpressionVectorParameter_0'"
   NodePosX=200
   NodePosY=780
   bCanRenameNode=True
End Object
```

#### 常用节点 Expression 输入属性映射

| 节点类型 | 输入属性名 | 说明 |
|---------|-----------|------|
| `MaterialExpressionAdd` | `A=`, `B=` | 加法 A+B |
| `MaterialExpressionMultiply` | `A=`, `B=` | 乘法 A*B，可用 `ConstA`/`ConstB` 替代常量输入 |
| `MaterialExpressionSubtract` | `A=`, `B=` | 减法 A-B |
| `MaterialExpressionDivide` | `A=`, `B=` | 除法 A/B |
| `MaterialExpressionLinearInterpolate` | `A=`, `B=`, `Alpha=` | 线性插值 |
| `MaterialExpressionDotProduct` | `A=`, `B=` | 点积 |
| `MaterialExpressionCrossProduct` | `A=`, `B=` | 叉积 |
| `MaterialExpressionFloor` | `Input=` | 向下取整 |
| `MaterialExpressionFraction` | `Input=` | 小数部分 (frac) |
| `MaterialExpressionSine` | `Input=` | 正弦（注意 UE 默认周期为 0-1 而非 0-2π） |
| `MaterialExpressionCosine` | `Input=` | 余弦 |
| `MaterialExpressionAbs` | `Input=` | 绝对值 |
| `MaterialExpressionSaturate` | `Input=` | Clamp 到 [0,1] |
| `MaterialExpressionOneMinus` | `Input=` | 1-X |
| `MaterialExpressionClamp` | `Input=`, `Min=`, `Max=` | 范围限制 |
| `MaterialExpressionIf` | `A=`, `B=`, `AGreaterThanB=`, `AEqualsB=`, `ALessThanB=` | 条件分支 |
| `MaterialExpressionStaticSwitchParameter` | `A=`, `B=` | 静态开关，A=True 分支，B=False 分支 |
| `MaterialExpressionAppendVector` | `A=`, `B=` | 向量拼接 |
| `MaterialExpressionComponentMask` | `Input=` | 分量掩码，配合 `R=True`/`G=True` 等 |
| `MaterialExpressionTextureCoordinate` | 无输入 | UV 坐标，配合 `CoordinateIndex=` |
| `MaterialExpressionConstant` | 无输入 | 标量常量，值设置在 `R=` |
| `MaterialExpressionConstant2Vector` | 无输入 | 二维常量，`R=`, `G=` |
| `MaterialExpressionConstant3Vector` | 无输入 | 三维常量，`Constant=(R=,G=,B=)` |
| `MaterialExpressionScalarParameter` | 无输入 | 标量参数，`ParameterName=`, `DefaultValue=` |
| `MaterialExpressionVectorParameter` | 无输入 | 向量参数，`ParameterName=`, `DefaultValue=(R=,G=,B=,A=)` |
| `MaterialExpressionCustom` | `Code="..."` | Custom 节点，HLSL 代码 |
| `MaterialExpressionFunctionInput` | 无输入 | 材质函数输入，`InputName=`, `InputType=` |
| `MaterialExpressionFunctionOutput` | `A=` | 材质函数输出，`OutputName=` |

#### 布局指南

- 节点从左到右排列，X 坐标递增（间距建议 160-200）
- 同层节点 Y 坐标对齐，不同层 Y 偏移 64-80
- 输入节点（TexCoord、Constant、Parameter）放在最左侧
- 输出节点（FunctionOutput、Material 属性）放在最右侧

#### 完整示例：简单 Lerp 连接

```
Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_ThinColor"
   Begin Object Class=/Script/Engine.MaterialExpressionVectorParameter Name="MaterialExpressionVectorParameter_0"
   End Object
   Begin Object Name="MaterialExpressionVectorParameter_0"
      DefaultValue=(R=0.846873,G=0.887923,B=1.000000,A=1.000000)
      ParameterName="FogThinColor"
      Group="Color"
      MaterialExpressionEditorX=2176
      MaterialExpressionEditorY=780
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionVectorParameter'MaterialExpressionVectorParameter_0'"
   NodePosX=2176
   NodePosY=780
   bCanRenameNode=True
End Object

Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_ThickColor"
   Begin Object Class=/Script/Engine.MaterialExpressionVectorParameter Name="MaterialExpressionVectorParameter_1"
   End Object
   Begin Object Name="MaterialExpressionVectorParameter_1"
      DefaultValue=(R=0.005605,G=0.090842,B=0.250158,A=1.000000)
      ParameterName="FogThickColor"
      Group="Color"
      MaterialExpressionEditorX=2176
      MaterialExpressionEditorY=1056
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionVectorParameter'MaterialExpressionVectorParameter_1'"
   NodePosX=2176
   NodePosY=1056
   bCanRenameNode=True
End Object

Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Density"
   Begin Object Class=/Script/Engine.MaterialExpressionScalarParameter Name="MaterialExpressionScalarParameter_0"
   End Object
   Begin Object Name="MaterialExpressionScalarParameter_0"
      DefaultValue=0.500000
      ParameterName="FogDensity"
      Group="Fog"
      MaterialExpressionEditorX=2176
      MaterialExpressionEditorY=920
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionScalarParameter'MaterialExpressionScalarParameter_0'"
   NodePosX=2176
   NodePosY=920
   bCanRenameNode=True
End Object

Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Lerp"
   Begin Object Class=/Script/Engine.MaterialExpressionLinearInterpolate Name="MaterialExpressionLinearInterpolate_0"
   End Object
   Begin Object Name="MaterialExpressionLinearInterpolate_0"
      A=(Expression="/Script/Engine.MaterialExpressionVectorParameter'MaterialGraphNode_ThinColor.MaterialExpressionVectorParameter_0'",Mask=1,MaskR=1,MaskG=1,MaskB=1)
      B=(Expression="/Script/Engine.MaterialExpressionVectorParameter'MaterialGraphNode_ThickColor.MaterialExpressionVectorParameter_1'",Mask=1,MaskR=1,MaskG=1,MaskB=1)
      Alpha=(Expression="/Script/Engine.MaterialExpressionScalarParameter'MaterialGraphNode_Density.MaterialExpressionScalarParameter_0'")
      MaterialExpressionEditorX=2688
      MaterialExpressionEditorY=920
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionLinearInterpolate'MaterialExpressionLinearInterpolate_0'"
   NodePosX=2688
   NodePosY=920
End Object
```

粘贴此文本到 UE 材质编辑器后，四个节点会自动出现并正确连接：ThinColor → Lerp.A，ThickColor → Lerp.B，Density → Lerp.Alpha。

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
