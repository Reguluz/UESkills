# UE材质转换器 - 快速开始指南

## 安装步骤

### 1. 复制Skills包

将整个`ue-material-converter`文件夹复制到Claude的skills目录：

**Windows:**
```cmd
xcopy /E /I ue-material-converter %USERPROFILE%\.claude\skills\ue-material-converter
```

**macOS/Linux:**
```bash
cp -r ue-material-converter ~/.claude/skills/
```

### 2. 重启Claude Code

关闭并重新启动Claude Code应用以加载新的Skills包。

### 3. 验证安装

在Claude Code中输入：
```
/ue-material-converter
```

应该能看到UE材质转换器的欢迎信息。

## 使用场景

### 场景1: Shadertoy着色器转换

**问题**: 你在Shadertoy上找到一个很酷的着色器，想在UE中使用。

**解决**:
1. 复制Shadertoy代码
2. 在Claude中输入：
   ```
   请将这个Shadertoy着色器转换为UE Custom节点：
   [粘贴代码]
   ```
3. Claude会提供转换后的HLSL代码和输入输出说明
4. 在UE材质编辑器中创建Custom节点，粘贴代码
5. 根据说明连接输入引脚

### 场景2: GLSL代码迁移

**问题**: 你有GLSL编写的着色器函数，需要在UE材质中使用。

### 场景2.5: 蓝图节点组合（推荐简单算法）

**问题**: 你有一个简单的算法需求，不确定用蓝图节点还是 Custom 节点。

**解决**:
1. 在Claude中输入需求描述
2. Claude会根据复杂度推荐合适的方式
3. 如果适合蓝图节点，提供节点组合方案

**示例输入**：
```
我需要一个雾颜色混合函数：
- 输入雾密度(0-1)
- 在薄雾颜色和厚雾颜色之间插值
- 可选使用 Curve Atlas 渐变
- 应该用什么方式实现？
```

**Claude 分析**：
这个需求适合使用**蓝图节点组合**，原因：
- ✓ 只需要 Lerp 和 StaticSwitch 节点
- ✓ 蓝图可视化更易维护
- ✓ 可在材质实例中调整参数

**输出：蓝图节点方案**
```
输入参数：
- FogDensity (float): 雾密度 [0,1]
- FogThinColor (float3): 薄雾颜色
- FogThickColor (float3): 厚雾颜色
- UseCurveGradient (bool): 使用曲线渐变

节点组合：
1. StaticSwitch(UseCurveGradient)
   ├─ True: CurveAtlasRowParameter
   │   └─ 输入: ComponentMask(FogDensity, R)
   └─ False: Lerp
       ├─ A: FogThinColor
       ├─ B: FogThickColor
       └─ Alpha: FogDensity
```

**问题**: 你有GLSL编写的着色器函数，需要在UE材质中使用。

**解决**:
1. 准备好GLSL代码
2. 在Claude中输入：
   ```
   帮我将这段GLSL代码转换为UE材质Custom节点：
   [粘贴代码]
   ```
3. Claude会自动转换类型和函数名

### 场景3: 蓝图节点优化

**问题**: 复杂的蓝图材质节点难以维护，想转换为代码。

**解决**:
1. 在UE材质编辑器中，右键节点选择"复制为文本"
2. 在Claude中输入：
   ```
   请分析这个蓝图材质并转换为HLSL函数：
   [粘贴蓝图文本]
   ```
3. Claude会生成对应的HLSL函数

## 实战示例

### 示例1: 创建动态背景效果

**目标**: 使用Shadertoy的"Neon Ripples"效果

**步骤**:
1. 访问Shadertoy，找到Neon Ripples着色器
2. 复制代码
3. 在Claude中输入转换请求
4. 得到类似下面的输出：

```hlsl
// Custom节点: NeonRipples
// Inputs:
//   - UV (float2): 纹理坐标
//   - Time (float): 时间参数
// Output: float3 - RGB颜色

struct MS_NeonRipples
{
    float3 compute(float2 UV, float Time)
    {
        float2 uv = UV * 2.0 - 1.0;
        float d = length(uv);
        float3 col = float3(0.0, 0.0, 0.0);

        for(int i = 0; i < 8; i++) {
            uv = frac(uv * 1.5) - 0.5;
            float d = length(uv) * exp(-length(uv0));
            float3 col = float3(0.0, 0.0, 0.0);
            d = sin(d * 8.0 + Time) / 8.0;
            d = abs(d);
            d = pow(0.01 / d, 1.2);
            col += float3(0.0, 0.0, 0.0) * d;
        }

        return col;
    }
}

MS_NeonRipples_Inst;
return MS_NeonRipples_Inst.compute(UV, Time);
```

5. 在UE中创建Custom节点，设置输入引脚
6. 连接TexCoord节点到UV输入
7. 连接Time节点到Time输入（或使用View.RealTime）
8. 连接输出到Base Color

### 示例2: 程序化纹理生成

**目标**: 生成柏林噪声纹理

**步骤**:
1. 准备Perlin噪声GLSL代码
2. 转换为UE Custom节点
3. 创建材质函数便于重用

```hlsl
// Custom节点: PerlinNoise
// Inputs:
//   - UV (float2): 采样位置
//   - Scale (float): 缩放系数
//   - Octaves (int): 叠加层数
// Output: float - 噪声值 [0,1]

struct MS_PerlinNoise
{
    float2 hash(float2 p)
    {
        p = float2(dot(p, float2(127.1, 311.7)),
                   dot(p, float2(269.5, 183.3)));
        return -1.0 + 2.0 * frac(sin(p) * 43758.5453123);
    }

    float noise(float2 p)
    {
        float2 i = floor(p);
        float2 f = frac(p);
        float2 u = f * f * (3.0 - 2.0 * f);

        return lerp(lerp(dot(hash(i + float2(0.0, 0.0)), f - float2(0.0, 0.0)),
                         dot(hash(i + float2(1.0, 0.0)), f - float2(1.0, 0.0)), u.x),
                    lerp(dot(hash(i + float2(0.0, 1.0)), f - float2(0.0, 1.0)),
                         dot(hash(i + float2(1.0, 1.0)), f - float2(1.0, 1.0)), u.x), u.y);
    }

    float compute(float2 UV, float Scale, int Octaves)
    {
        float value = 0.0;
        float amplitude = 0.5;
        float frequency = 1.0;

        for(int i = 0; i < Octaves; i++) {
            value += amplitude * noise(UV * Scale * frequency);
            frequency *= 2.0;
            amplitude *= 0.5;
        }

        return value * 0.5 + 0.5;
    }
}

MS_PerlinNoise_Inst;
return MS_PerlinNoise_Inst.compute(UV, Scale, Octaves);
```

## 常见问题解决

### Q: 转换后的代码在UE中报错"undefined identifier"

**A**: 可能原因：
1. 变量名拼写错误
2. 类型转换问题（尝试使用显式转换）
3. 未定义的函数（检查函数映射表）

### Q: Custom节点输出为黑色或白色

**A**: 检查：
1. 输入值范围是否正确（UV应该在[0,1]）
2. 输出是否需要归一化
3. 是否除以了0（添加安全检查）

### Q: 性能太差

**A**: 优化建议：
1. 减少循环次数
2. 使用内置函数而非自定义实现
3. 预计算常量
4. 使用材质函数而非重复代码

## 高级技巧

### 技巧1: 创建参数化的材质函数

1. 将转换后的代码包装为材质函数
2. 暴露关键参数作为函数输入
3. 在多个材质中重用

### 技巧2: 结合材质属性

```hlsl
// 结合材质属性使用
float3 result = CustomFunction(UV, Time);
result *= GetMaterialParameters(MaterialID).BaseColor;
```

### 技巧3: 使用静态开关

```hlsl
#if USE_CUSTOM_FEATURE
    // 自定义功能代码
#else
    // 默认实现
#endif
```

## 参考资源

- [UE材质文档](https://docs.unrealengine.com/)
- [Shadertoy](https://www.shadertoy.com/)
- [HLSL参考](https://docs.microsoft.com/en-us/windows/win32/direct3dhlsl/)
- 函数映射表：参见`examples/function_reference.md`

## 获取帮助

遇到问题时，提供以下信息可以获得更好的帮助：
1. 原始代码片段
2. 转换后的代码
3. 完整的错误信息
4. UE版本号
5. 预期结果和实际结果的对比
