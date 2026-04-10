// Shadertoy基础示例 - 彩色渐变
// 原始Shadertoy代码
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;
    vec3 col = 0.5 + 0.5 * cos(iTime + uv.xyx + vec3(0, 2, 4));
    fragColor = vec4(col, 1.0);
}

// 转换为UE Custom节点：
/*
// Custom节点: ShaderToyRainbow
// Inputs:
//   - UV (float2): 纹理坐标
//   - Time (float): 时间参数，连接到View.RealTime或自定义时间
// Output: float3 - RGB颜色

float3 ShaderToyRainbow(float2 UV, float Time)
{
    float3 col = 0.5 + 0.5 * cos(Time + UV.xyx + float3(0.0, 2.0, 0.0));
    return col;
}
*/
