# UE材质转换器 - 测试案例

## 测试案例集合

用于验证转换功能的测试用例。

---

## 测试案例1: 基础数学运算

### 输入（GLSL）
```glsl
float calculate(float2 uv, float time) {
    return sin(uv.x * 10.0 + time) * cos(uv.y * 10.0 + time);
}
```

### 预期输出（HLSL）
```hlsl
float Calculate(float2 UV, float Time)
{
    return sin(UV.x * 10.0 + Time) * cos(UV.y * 10.0 + Time);
}
```

### 验证点
- [ ] vec2 → float2
- [ ] 函数名保持（或转换为PascalCase）
- [ ] 内置函数正确转换

---

## 测试案例2: 插值函数

### 输入（GLSL）
```glsl
vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b * cos(6.28318 * (c * t + d));
}
```

### 预期输出（HLSL）
```hlsl
float3 Palette(float t, float3 a, float3 b, float3 c, float3 d)
{
    return a + b * cos(6.28318 * (c * t + d));
}
```

### 验证点
- [ ] vec3 → float3
- [ ] cos函数保持不变
- [ ] 参数类型正确

---

## 测试案例3: Shadertoy完整着色器

### 输入（Shadertoy）
```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    vec3 col = 0.5 + 0.5 * cos(iTime + uv.xyx + vec3(0, 2, 4));
    fragColor = vec4(col, 1.0);
}
```

### 预期输出（UE Custom节点）
```hlsl
float3 ShaderToyRainbow(float2 UV, float Time)
{
    float3 col = 0.5 + 0.5 * cos(Time + UV.xyx + float3(0.0, 2.0, 4.0));
    return col;
}
```

### 验证点
- [ ] mainImage函数体提取
- [ ] fragCoord/iResolution处理
- [ ] iTime转换
- [ ] vec3类型转换
- [ ] 输入输出说明

---

## 测试案例4: 多函数结构

### 输入（GLSL）
```glsl
float hash(float2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

float noise(float2 p) {
    float2 i = floor(p);
    float2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
```

### 预期输出（带结构体封装）
```hlsl
struct FNoiseGenerator
{
    static float Hash(float2 p)
    {
        return frac(sin(dot(p, float2(12.9898, 78.233))) * 43758.5453);
    }

    static float Noise(float2 p)
    {
        float2 i = floor(p);
        float2 f = frac(p);
        f = f * f * (3.0 - 2.0 * f);

        float a = Hash(i);
        float b = Hash(i + float2(1.0, 0.0));
        float c = Hash(i + float2(0.0, 1.0));
        float d = Hash(i + float2(1.0, 1.0));

        return lerp(lerp(a, b, f.x), lerp(c, d, f.x), f.y);
    }
};

float ValueNoise(float2 Position)
{
    return FNoiseGenerator::Noise(Position);
}
```

### 验证点
- [ ] 结构体创建
- [ ] 静态函数
- [ ] fract → frac
- [ ] mix → lerp
- [ ] vec2 → float2
- [ ] 主函数暴露

---

## 测试案例5: 矩阵操作

### 输入（GLSL）
```glsl
mat2 rotate2d(float angle) {
    return mat2(cos(angle), -sin(angle),
                sin(angle), cos(angle));
}

vec2 transform(vec2 p, float angle) {
    return rotate2d(angle) * p;
}
```

### 预期输出（HLSL）
```hlsl
float2x2 Rotate2D(float Angle)
{
    float s = sin(Angle);
    float c = cos(Angle);
    return float2x2(c, -s, s, c);
}

float2 Transform(float2 p, float Angle)
{
    return mul(Rotate2D(Angle), p);
}
```

### 验证点
- [ ] mat2 → float2x2
- [ ] 矩阵初始化语法
- [ ] 矩阵乘法语法（mul）

---

## 测试案例6: 纹理采样

### 输入（GLSL）
```glsl
vec4 sampleTexture(vec2 uv, sampler2D tex) {
    return texture(tex, uv);
}
```

### 预期输出（UE Custom节点）
```hlsl
float4 SampleTexture(float2 UV, Texture2D Tex)
{
    return Texture2DSample(Tex, TexSampler, UV);
}
```

### 验证点
- [ ] sampler2D → Texture2D
- [ ] texture → Texture2DSample
- [ ] 添加Sampler参数说明

---

## 测试案例7: 条件分支

### 输入（GLSL）
```glsl
float pattern(vec2 uv) {
    if (length(uv) < 0.5) {
        return 1.0;
    } else {
        return 0.0;
    }
}
```

### 预期输出（HLSL）
```hlsl
float Pattern(float2 UV)
{
    if (length(UV) < 0.5)
    {
        return 1.0;
    }
    else
    {
        return 0.0;
    }
}
```

### 验证点
- [ ] 条件语句保持
- [ ] 代码格式

---

## 测试案例8: 循环结构

### 输入（GLSL）
```glsl
float fractal(float2 uv) {
    float value = 0.0;
    for (int i = 0; i < 4; i++) {
        uv = fract(uv * 2.0) - 0.5;
        value += length(uv);
    }
    return value;
}
```

### 预期输出（HLSL）
```hlsl
float Fractal(float2 UV)
{
    float value = 0.0;
    for (int i = 0; i < 4; i++)
    {
        UV = frac(UV * 2.0) - 0.5;
        value += length(UV);
    }
    return value;
}
```

### 验证点
- [ ] 循环保持
- [ ] fract → frac
- [ ] 变量累积

---

## 测试案例9: 向量Swizzle

### 输入（GLSL）
```glsl
vec3 rgb = vec3(1.0, 0.5, 0.0);
vec2 rg = rgb.xy;
float grayscale = dot(rgb, vec3(0.299, 0.587, 0.114));
```

### 预期输出（HLSL）
```hlsl
float3 rgb = float3(1.0, 0.5, 0.0);
float2 rg = rgb.xy;
float grayscale = dot(rgb, float3(0.299, 0.587, 0.114));
```

### 验证点
- [ ] swizzle操作保持

---

## 测试案例10: 复杂着色器（SDF）

### 输入（Shadertoy）
```glsl
float sdSphere(vec3 p, float s) {
    return length(p) - s;
}

float sdBox(vec3 p, vec3 b) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
}

float map(vec3 p) {
    float s = sdSphere(p - vec3(0.0, 1.0, 0.0), 1.0);
    float b = sdBox(p - vec3(2.0, 0.5, 0.0), vec3(0.5));
    return min(s, b);
}
```

### 预期输出（带结构体）
```hlsl
struct FSDF
{
    static float SDSphere(float3 p, float s)
    {
        return length(p) - s;
    }

    static float SDBox(float3 p, float3 b)
    {
        float3 q = abs(p) - b;
        return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
    }

    static float Map(float3 p)
    {
        float s = SDSphere(p - float3(0.0, 1.0, 0.0), 1.0);
        float b = SDBox(p - float3(2.0, 0.5, 0.0), float3(0.5));
        return min(s, b);
    }
};
```

### 验证点
- [ ] 多函数结构体
- [ ] SDF函数正确转换
- [ ] vec3 → float3

---

## 使用测试案例

1. 选择一个测试案例
2. 复制"输入"代码
3. 在Claude中请求转换
4. 与"预期输出"对比
5. 检查"验证点"项目

## 报告问题

如果发现转换结果不符合预期，请提供：
1. 测试案例编号
2. 输入代码
3. 实际输出
4. 预期输出
5. UE版本

这样可以帮助改进转换器的准确性。
