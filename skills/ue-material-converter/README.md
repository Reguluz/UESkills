# UE材质转换器 - Skills包

用于Unreal Engine材质开发的代码转换工具。

## 功能

1. **蓝图转HLSL函数** - 将UE材质蓝图的文本表示转换为HLSL函数
2. **着色器转Custom节点** - 将Shadertoy/GLSL/HLSL着色器转换为UE Custom节点代码
3. **结构体封装** - 对复杂算法使用结构体进行封装和调用

## 安装

将此Skills包复制到你的Claude Code项目的`.claude/skills/`目录下：

```bash
cp -r ue-material-converter ~/.claude/skills/
# 或Windows
xcopy /E /I ue-material-converter %USERPROFILE%\.claude\skills\ue-material-converter
```

## 使用方法

### 方式1: 直接对话
在对话中直接提及相关需求：
- "请将这个蓝图转换为HLSL函数"
- "这个Shadertoy着色器怎么转换为UE Custom节点？"
- "帮我转换这段GLSL代码"

### 方式2: 使用斜杠命令
```
/ue-material-converter
```

## 示例

### 示例1: Shadertoy转换

**输入**：
```glsl
// Shadertoy代码
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord/iResolution.xy;
    vec3 col = 0.5 + 0.5*cos(iTime+uv.xyx+vec3(0,2,4));
    fragColor = vec4(col,1.0);
}
```

**输出**：
```hlsl
// Custom节点: ShaderToyCosinePalette
// Inputs:
//   - UV (float2): 纹理坐标
//   - Time (float): 时间参数
// Output: float3 - RGB颜色

float3 ShaderToyCosinePalette(float2 UV, float Time)
{
    float3 col = 0.5 + 0.5 * cos(Time + UV.xyx + float3(0.0, 2.0, 4.0));
    return col;
}
```

### 示例2: GLSL转换

**输入**：
```glsl
vec3 palette( in float t, in vec3 a, in vec3 b, in vec3 c, in vec3 d )
{
    return a + b*cos( 6.28318*(c*t+d) );
}
```

**输出**：
```hlsl
// Custom节点: CosinePalette
// Inputs:
//   - T (float): 插值参数
//   - A (float3): 偏移参数
//   - B (float3): 振幅参数
//   - C (float3): 频率参数
//   - D (float3): 相位参数
// Output: float3 - 调色板颜色

float3 CosinePalette(float T, float3 A, float3 B, float3 C, float3 D)
{
    return A + B * cos(6.28318 * (C * T + D));
}
```

## 配置选项

在`skill.json`中可配置：
- `ueVersion`: 目标UE版本（默认5.3）
- `outputFormat`: 输出格式（function/struct/materialFunction）

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

## 贡献

欢迎提交问题和改进建议！
