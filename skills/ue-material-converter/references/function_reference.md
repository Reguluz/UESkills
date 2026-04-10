# GLSL到HLSL函数映射参考

## 类型映射

| GLSL类型 | HLSL/UE类型 | 说明 |
|---------|------------|------|
| `float` | `float` | 32位浮点 |
| `vec2` | `float2` | 2D浮点向量 |
| `vec3` | `float3` | 3D浮点向量 |
| `vec4` | `float4` | 4D浮点向量 |
| `int` | `int` | 32位整数 |
| `ivec2/3/4` | `int2/3/4` | 整数向量 |
| `mat2` | `float2x2` | 2x2矩阵 |
| `mat3` | `float3x3` | 3x3矩阵 |
| `mat4` | `float4x4` | 4x4矩阵 |
| `sampler2D` | `Texture2D` | 2D纹理类型 |

## 内置函数映射

| GLSL函数 | HLSL/UE函数 | 说明 |
|---------|------------|------|
| `mix(a, b, t)` | `lerp(a, b, t)` | 线性插值 |
| `fract(x)` | `frac(x)` | 小数部分 |
| `clamp(x, a, b)` | `clamp(x, a, b)` | 范围限制 |
| `smoothstep(a, b, x)` | `smoothstep(a, b, x)` | 平滑阶跃 |
| `step(edge, x)` | `step(edge, x)` | 阶跃函数 |
| `mod(x, y)` | `fmod(x, y)` | 浮点取模 |
| `abs(x)` | `abs(x)` | 绝对值 |
| `sign(x)` | `sign(x)` | 符号函数 |
| `floor(x)` | `floor(x)` | 向下取整 |
| `ceil(x)` | `ceil(x)` | 向上取整 |
| `round(x)` | `round(x)` | 四舍五入 |
| `sqrt(x)` | `sqrt(x)` | 平方根 |
| `inversesqrt(x)` | `rsqrt(x)` | 反平方根 |
| `pow(x, y)` | `pow(x, y)` | 幂运算 |
| `exp(x)` | `exp(x)` | e的x次方 |
| `log(x)` | `log(x)` | 自然对数 |
| `exp2(x)` | `exp2(x)` | 2的x次方 |
| `log2(x)` | `log2(x)` | 以2为底对数 |
| `min(a, b)` | `min(a, b)` | 最小值 |
| `max(a, b)` | `max(a, b)` | 最大值 |
| `dot(a, b)` | `dot(a, b)` | 点积 |
| `cross(a, b)` | `cross(a, b)` | 叉积 |
| `length(v)` | `length(v)` | 向量长度 |
| `distance(a, b)` | `distance(a, b)` | 两点距离 |
| `normalize(v)` | `normalize(v)` | 归一化 |
| `reflect(I, N)` | `reflect(I, N)` | 反射向量 |
| `refract(I, N, eta)` | `refract(I, N, eta)` | 折射向量 |
| `sin(x)` | `sin(x)` | 正弦 |
| `cos(x)` | `cos(x)` | 余弦 |
| `tan(x)` | `tan(x)` | 正切 |
| `asin(x)` | `asin(x)` | 反正弦 |
| `acos(x)` | `acos(x)` | 反余弦 |
| `atan(x)` | `atan(x)` | 反正切 |
| `atan2(y, x)` | `atan2(y, x)` | 反正切2参数 |

## Shadertoy特殊变量映射

| Shadertoy | UE材质 | 说明 |
|----------|--------|------|
| `iResolution` | `View.ViewSizeAndInvSize.xy` | 分辨率 |
| `iTime` | `View.RealTime` | 时间 |
| `iTimeDelta` | `View.DeltaTime` | 帧时间 |
| `iFrame` | `View.FrameNumber` | 帧数 |
| `iMouse` | 自定义参数 | 鼠标位置 |
| `iChannel0-3` | 自定义纹理参数 | 纹理输入 |
| `fragCoord` | `View.ViewSizeAndInvSize.xy * UV` | 像素坐标 |

## 纹理采样

### GLSL
```glsl
vec4 color = texture(iChannel0, uv);
vec4 color = texture(tex, uv, lod); // 带LOD
```

### HLSL/UE
```hlsl
float4 color = Texture2DSample(Tex, TexSampler, UV);
float4 color = Texture2DSampleLevel(Tex, TexSampler, UV, LOD);
```

## 向量操作

### GLSL
```glsl
vec3 v = vec3(1.0, 2.0, 3.0);
vec3 v2 = vec3(1.0); // vec3(1.0, 1.0, 1.0)
v.xy = vec2(4.0, 5.0); // swizzle赋值
```

### HLSL/UE
```hlsl
float3 v = float3(1.0, 2.0, 3.0);
float3 v2 = float3(1.0, 1.0, 1.0);
v.xy = float2(4.0, 5.0); // swizzle赋值
```

## 常见模式

### 渐变色（Cosine Palette）
```glsl
vec3 palette(float t) {
    return a + b * cos(6.28318 * (c * t + d));
}
```
```hlsl
float3 Palette(float t, float3 a, float3 b, float3 c, float3 d) {
    return a + b * cos(6.28318 * (c * t + d));
}
```

### 坐标变换
```glsl
uv = uv * 2.0 - 1.0; // [0,1] → [-1,1]
uv.x *= iResolution.x / iResolution.y; // 宽高比修正
```
```hlsl
uv = uv * 2.0 - 1.0;
uv.x *= View.ViewSizeAndInvSize.x / View.ViewSizeAndInvSize.y;
```

### 旋转
```glsl
mat2 rot(float a) {
    float s = sin(a), c = cos(a);
    return mat2(c, -s, s, c);
}
uv *= rot(angle);
```
```hlsl
float2x2 rot(float a) {
    float s = sin(a), c = cos(a);
    return float2x2(c, -s, s, c);
}
uv = mul(rot(angle), uv);
```

## 注意事项

1. UE材质不支持递归函数
2. 避免使用动态循环（使用常量循环）
3. 纹理采样需要同时提供Texture和Sampler
4. 一些GLSL内置函数在UE中可能不可用或名称不同
5. 注意Y轴方向差异（OpenGL向上，DX向下）
