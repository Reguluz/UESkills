// 噪声函数示例 - 多函数结构体封装

// 原始GLSL代码
float hash(float2 p) {
    return fract(sin(dot(p, float2(12.9898, 78.233))) * 43758.5453);
}

float noise(float2 p) {
    float2 i = floor(p);
    float2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
        mix(hash(i), hash(i + float2(1.0, 0.0)), f.x),
        mix(hash(i + float2(0.0, 1.0)), hash(i + float2(1.0, 1.0)), f.x),
        f.y
    );
}

// 转换为UE Custom节点（结构体封装）：
/*
// Custom节点: ValueNoise
// Inputs:
//   - Position (float2): 采样位置
// Output: float - 噪声值 [0,1]

struct FValueNoise
{
    // 哈希函数
    static float Hash(float2 p)
    {
        return frac(sin(dot(p, float2(12.9898, 78.233))) * 43758.5453);
    }

    // 平滑插值
    static float2 SmoothFade(float2 t)
    {
        return t * t * (3.0 - 2.0 * t);
    }

    // 2D值噪声
    static float Noise(float2 p)
    {
        float2 i = floor(p);
        float2 f = frac(p);
        f = f * f * (3.0 - 2.0 * f);

        float a = Hash(i);
        float b = Hash(i + float2(1.0, 0.0));
        float c = Hash(i + float2(0.0, 1.0));
        float d = Hash(i + float2(1.0, 1.0));

        return lerp(
            lerp(a, b, f.x),
            lerp(c, d, f.x),
            f.y
        );
    }
};

float ValueNoise(float2 Position)
{
    return FValueNoise::Noise(Position);
}
*/
