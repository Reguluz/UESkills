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

**对应蓝图复制文本**（UE 原生格式，粘贴后自动建立连线）：

（完整蓝图文本较长，仅展示 Lerp 部分的简化逻辑说明：ThinColor.Output → Lerp.A, ThickColor.Output → Lerp.B, Density.Output → Lerp.Alpha，格式遵循「蓝图复制文本格式规范」章节的模板，包含完整的 `CustomProperties Pin` 和双向 `LinkedTo`）

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

### 蓝图复制文本格式规范（基于 UE 原生格式）

当生成蓝图复制文本时，**必须严格遵循以下 UE 原生序列化格式**，否则粘贴到 UE 材质编辑器中会导致节点无法连接或崩溃。

#### 禁止规则

1. **禁止生成 `MaterialExpressionComment`（Comment 框）** — AI 无法生成有效的 Comment 框序列化数据，粘贴会导致 UE 材质编辑器崩溃
2. **禁止使用非法 GUID** — 不要使用 `TEXCOORD_PIN_OUT`、`MUL1_A_PERSIST` 等文字标识符代替 GUID，必须使用 32 位十六进制格式

#### GUID 生成规则

所有 GUID（PinId、NodeGuid、MaterialExpressionGuid）使用 **32 位十六进制字符串**，格式为大写字母+数字，左侧补零。为简化生成，使用**递增编号方案**：

- **NodeGuid**: `00000000000000000000000000000N01` — N 从 1 递增（节点编号）
- **MaterialExpressionGuid**: `00000000000000000000000000000N02` — 对应节点的 Expression GUID
- **PinId**: `00000000000000000000000N0P000001` — N=节点编号，P=Pin 序号（1=第一个输入, 2=第二个输入, ..., 9=Output）

例如第 3 个节点的第 2 个输入 Pin：`0000000000000000000000030200001`（补齐到 32 位）

实际生成时，只需确保每个 GUID **全局唯一且为 32 位十六进制**即可。推荐简单递增方案：
- PinId: `A0000000000000000000000000000001`, `A0000000000000000000000000000002`, ...
- NodeGuid: `B0000000000000000000000000000001`, `B0000000000000000000000000000002`, ...
- MaterialExpressionGuid: `C0000000000000000000000000000001`, `C0000000000000000000000000000002`, ...

#### 节点连接机制（双层连接）

UE 材质编辑器粘贴时需要**两层连接信息同时存在**：

**第一层：Expression 引用**（MaterialExpression 对象层面，用于材质编译）
```
A=(Expression="/Script/Engine.MaterialExpressionConstant'MaterialGraphNode_Const.MaterialExpressionConstant_0'")
```

**第二层：CustomProperties Pin 的 LinkedTo**（EdGraph 层面，用于编辑器图形连线）
```
CustomProperties Pin (PinId=A0000000000000000000000000000001,PinName="A",...,LinkedTo=(MaterialGraphNode_Const A0000000000000000000000000000010,),...)
```

**关键：连接必须是双向的**——源节点 Output Pin 的 `LinkedTo` 指向目标节点输入 Pin 的 `PinId`，目标节点输入 Pin 的 `LinkedTo` 也必须指回源节点 Output Pin 的 `PinId`。

#### 标准 Pin 模板

**输入 Pin**（方向默认为 Input，不需要 Direction 字段）：
```
CustomProperties Pin (PinId=<GUID>,PinName="A",PinType.PinCategory="optional",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0.0",LinkedTo=(<SourceNodeName> <SourceOutputPinId>,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
```

**输出 Pin**（必须有 `Direction="EGPD_Output"`）：
```
CustomProperties Pin (PinId=<GUID>,PinName="Output",PinFriendlyName=NSLOCTEXT("MaterialGraphNode", "Space", " "),Direction="EGPD_Output",PinType.PinCategory="",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(<TargetNodeName> <TargetInputPinId>,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
```

**未连接的 Pin**：省略 `LinkedTo` 字段，或不输出该 Pin（如果使用 ConstA/ConstB 内联常量）。

#### 标准节点模板

**常量节点**（Constant，1 个输出 Pin）：
```
Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Const1"
   Begin Object Class=/Script/Engine.MaterialExpressionConstant Name="MaterialExpressionConstant_0"
   End Object
   Begin Object Name="MaterialExpressionConstant_0"
      R=0.750000
      MaterialExpressionEditorX=-200
      MaterialExpressionEditorY=100
      MaterialExpressionGuid=C0000000000000000000000000000001
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionConstant'MaterialExpressionConstant_0'"
   NodePosX=-200
   NodePosY=100
   NodeGuid=B0000000000000000000000000000001
   CustomProperties Pin (PinId=A0000000000000000000000000000001,PinName="Value",PinType.PinCategory="optional",PinType.PinSubCategory="red",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0.75",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=True,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=A0000000000000000000000000000002,PinName="Output",PinFriendlyName=NSLOCTEXT("MaterialGraphNode", "Space", " "),Direction="EGPD_Output",PinType.PinCategory="",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(MaterialGraphNode_Mul1 A0000000000000000000000000000003,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
```

**双输入节点**（Multiply，2 个输入 Pin + 1 个输出 Pin）：
```
Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Mul1"
   Begin Object Class=/Script/Engine.MaterialExpressionMultiply Name="MaterialExpressionMultiply_0"
   End Object
   Begin Object Name="MaterialExpressionMultiply_0"
      A=(Expression="/Script/Engine.MaterialExpressionConstant'MaterialGraphNode_Const1.MaterialExpressionConstant_0'")
      MaterialExpressionEditorX=0
      MaterialExpressionEditorY=0
      MaterialExpressionGuid=C0000000000000000000000000000002
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionMultiply'MaterialExpressionMultiply_0'"
   NodePosX=0
   NodePosY=0
   NodeGuid=B0000000000000000000000000000002
   CustomProperties Pin (PinId=A0000000000000000000000000000003,PinName="A",PinType.PinCategory="optional",PinType.PinSubCategory="red",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0.0",LinkedTo=(MaterialGraphNode_Const1 A0000000000000000000000000000002,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=A0000000000000000000000000000004,PinName="B",PinType.PinCategory="optional",PinType.PinSubCategory="red",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="1.0",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=A0000000000000000000000000000005,PinName="Output",PinFriendlyName=NSLOCTEXT("MaterialGraphNode", "Space", " "),Direction="EGPD_Output",PinType.PinCategory="",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
```

注意上面示例中 **Const1 的 Output** (`A...0002`) → **Mul1 的 A** (`A...0003`) 是**双向 LinkedTo**。

#### 常用节点 Pin 结构

| 节点类型 | 输入 Pin (PinName) | Expression 属性 | 输出 Pin |
|---------|-------------------|----------------|---------|
| `Constant` | Value (bNotConnectable=True) | `R=` | Output |
| `Constant2Vector` | Value (bNotConnectable=True) | `R=`, `G=` | Output |
| `Constant3Vector` | Value (bNotConnectable=True) | `Constant=(R=,G=,B=)` | Output |
| `Add` | A, B | `A=`, `B=` | Output |
| `Multiply` | A, B | `A=`, `B=`（或 `ConstA`/`ConstB`） | Output |
| `Subtract` | A, B | `A=`, `B=` | Output |
| `Divide` | A, B | `A=`, `B=` | Output |
| `LinearInterpolate` | A, B, Alpha | `A=`, `B=`, `Alpha=` | Output |
| `DotProduct` | A, B | `A=`, `B=` | Output |
| `Floor` | Input | `Input=` | Output |
| `Frac` | Input | `Input=` | Output |
| `Sine` | Input | `Input=` | Output |
| `Cosine` | Input | `Input=` | Output |
| `Abs` | Input | `Input=` | Output |
| `OneMinus` | Input | `Input=` | Output |
| `Saturate` | Input | `Input=` | Output |
| `Clamp` | Input, Min, Max | `Input=`, `Min=`, `Max=` | Output |
| `If` | A, B, AGreaterThanB, AEqualsB, ALessThanB | 同名 | Output |
| `AppendVector` | A, B | `A=`, `B=` | Output |
| `ComponentMask` | Input | `Input=`，配合 `R=True`/`G=True` | Output |
| `TextureCoordinate` | 无 | `CoordinateIndex=` | Output |
| `ScalarParameter` | Value (bNotConnectable=True) | `ParameterName=`, `DefaultValue=` | Output |
| `VectorParameter` | Value (bNotConnectable=True) | `ParameterName=`, `DefaultValue=` | Output |
| `FunctionInput` | Preview (可选) | `InputName=`, `InputType=` | Output |
| `FunctionOutput` | A | `A=`, `OutputName=` | 无 |
| `StaticSwitchParameter` | A (True), B (False) | `A=`, `B=`, `ParameterName=` | Output |

#### Pin 的 PinSubCategory 颜色映射

| PinSubCategory | 含义 |
|---------------|------|
| `"red"` | 通用输入（float/vector） |
| `""` (空) | 输出 Pin 使用空字符串 |

#### 布局指南

- 节点从左到右排列，X 坐标递增（间距建议 160-200）
- 同层节点 Y 坐标对齐，不同层 Y 偏移 64-80
- 输入节点（TexCoord、Constant、Parameter）放在最左侧
- 输出节点（FunctionOutput、Material 属性）放在最右侧

#### 完整示例：Constant → Multiply 连接（最小可验证示例）

以下示例展示了两个节点的完整连接格式，可直接复制粘贴到 UE 材质编辑器中验证：

```
Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Const"
   Begin Object Class=/Script/Engine.MaterialExpressionConstant Name="MaterialExpressionConstant_0"
   End Object
   Begin Object Name="MaterialExpressionConstant_0"
      R=0.750000
      MaterialExpressionEditorX=-200
      MaterialExpressionEditorY=0
      MaterialExpressionGuid=C0000000000000000000000000000001
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionConstant'MaterialExpressionConstant_0'"
   NodePosX=-200
   NodePosY=0
   NodeGuid=B0000000000000000000000000000001
   CustomProperties Pin (PinId=A0000000000000000000000000000001,PinName="Value",PinType.PinCategory="optional",PinType.PinSubCategory="red",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0.75",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=True,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=A0000000000000000000000000000002,PinName="Output",PinFriendlyName=NSLOCTEXT("MaterialGraphNode", "Space", " "),Direction="EGPD_Output",PinType.PinCategory="",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(MaterialGraphNode_Mul A0000000000000000000000000000003,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object

Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="MaterialGraphNode_Mul"
   Begin Object Class=/Script/Engine.MaterialExpressionMultiply Name="MaterialExpressionMultiply_0"
   End Object
   Begin Object Name="MaterialExpressionMultiply_0"
      A=(Expression="/Script/Engine.MaterialExpressionConstant'MaterialGraphNode_Const.MaterialExpressionConstant_0'")
      MaterialExpressionEditorX=0
      MaterialExpressionEditorY=0
      MaterialExpressionGuid=C0000000000000000000000000000002
   End Object
   MaterialExpression="/Script/Engine.MaterialExpressionMultiply'MaterialExpressionMultiply_0'"
   NodePosX=0
   NodePosY=0
   NodeGuid=B0000000000000000000000000000002
   CustomProperties Pin (PinId=A0000000000000000000000000000003,PinName="A",PinType.PinCategory="optional",PinType.PinSubCategory="red",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0.0",LinkedTo=(MaterialGraphNode_Const A0000000000000000000000000000002,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=A0000000000000000000000000000004,PinName="B",PinType.PinCategory="optional",PinType.PinSubCategory="red",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="1.0",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=A0000000000000000000000000000005,PinName="Output",PinFriendlyName=NSLOCTEXT("MaterialGraphNode", "Space", " "),Direction="EGPD_Output",PinType.PinCategory="",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
```

**连接验证**：Const(0.75) 的 Output Pin (`A...0002`) 双向连接到 Mul 的 A Pin (`A...0003`)。粘贴后应自动出现连线。

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
