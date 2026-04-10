// 高级示例：光线步进（Raymarching）着色器
// 原始Shadertoy代码 - 复杂多函数场景

// ============================================================================
// 原始Shadertoy代码（来自Shadertoy用户"Shane"）
// ============================================================================

/*
// Distance functions
float sdPlane(float3 p) {
    return p.y;
}

float sdSphere(float3 p, float s) {
    return length(p) - s;
}

float map(float3 p) {
    float d = sdPlane(p);
    d = min(d, sdSphere(p - float3(0.0, 1.0, 0.0), 1.0));
    return d;
}

// Ray marching
float rayMarch(float3 ro, float3 rd) {
    float dO = 0.0;
    for(int i = 0; i < 80; i++) {
        float3 p = ro + rd * dO;
        float dS = map(p);
        dO += dS;
        if(dO > 100.0 || dS < 0.001) break;
    }
    return dO;
}

// Normal calculation
float3 calcNormal(float3 p) {
    float2 e = float2(0.001, 0.0);
    return normalize(float3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}

// Rendering
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;

    vec3 ro = vec3(0.0, 2.0, -3.0);
    vec3 rd = normalize(vec3(uv, 1.0));

    float d = rayMarch(ro, rd);
    float3 col = vec3(0.0);

    if(d < 100.0) {
        float3 p = ro + rd * d;
        float3 n = calcNormal(p);
        float3 lightPos = vec3(2.0, 5.0, -3.0);
        float3 lightDir = normalize(lightPos - p);

        float diff = max(dot(n, lightDir), 0.0);
        col = vec3(diff);
    }

    fragColor = vec4(col, 1.0);
}
*/

// ============================================================================
// 转换为UE Custom节点（结构体封装）
// ============================================================================

/*
// Custom节点: RaymarchingScene
// Inputs:
//   - UV (float2): 屏幕坐标 [-1,1]
//   - CameraPos (float3): 相机位置
//   - Time (float): 时间参数（可用于动画）
// Output: float3 - 最终RGB颜色

// ============================================================================
// 完整的Custom节点HLSL代码
// ============================================================================

// 场景描述结构体 - 包含所有SDF（有向距离场）函数
struct FSceneMap
{
    // 平面SDF
    static float SDPlane(float3 p)
    {
        return p.z;
    }

    // 球体SDF
    static float SDSphere(float3 p, float s)
    {
        return length(p) - s;
    }

    // 场景组合 - 返回最近物体的距离
    static float Map(float3 p)
    {
        float d = SDPlane(p);
        float spherePos = 1.0 + sin(Time * 2.0) * 0.3; // 动画球体位置
        d = min(d, SDSphere(p - float3(0.0, spherePos, 0.0), 1.0));
        return d;
    }
};

// 光线步进器
struct FRaymarcher
{
    static float RayMarch(float3 ro, float3 rd, float Time)
    {
        float dO = 0.0; // 原点距离

        // UE材质中建议使用固定次数循环
        for(int i = 0; i < 64; i++) // 从80减少到64以提高性能
        {
            float3 p = ro + rd * dO;
            float dS = FSceneMap::Map(p); // 场景距离

            dO += dS;

            // 提前退出条件
            if(dO > 100.0 || dS < 0.001)
            {
                break;
            }
        }

        return dO;
    }
};

// 法线计算器
struct FNormalCalculator
{
    static float3 CalcNormal(float3 p, float Time)
    {
        float2 e = float2(0.001, 0.0);

        return normalize(float3(
            FSceneMap::Map(p + e.xyy) - FSceneMap::Map(p - e.xyy),
            FSceneMap::Map(p + e.yxy) - FSceneMap::Map(p - e.yxy),
            FSceneMap::Map(p + e.yyx) - FSceneMap::Map(p - e.yyx)
        ));
    }
};

// 着色器
struct FShader
{
    static float3 Shade(float3 p, float3 n, float Time)
    {
        // 简单的漫反射光照
        float3 lightPos = float3(2.0, 5.0, -3.0);
        float3 lightDir = normalize(lightPos - p);

        float diff = max(dot(n, lightDir), 0.0);

        // 基于位置的颜色
        float3 baseColor = float3(0.2, 0.5, 1.0);

        return baseColor * diff;
    }
};

// 主函数
float3 RaymarchingScene(float2 UV, float3 CameraPos, float Time)
{
    // 从UV构建光线方向
    // 注意：UV需要转换为[-1,1]范围
    float3 rd = normalize(float3(UV, 1.0)); // 光线方向
    float3 ro = CameraPos; // 射线原点（相机位置）

    // 执行光线步进
    float d = FRaymarcher::RayMarch(ro, rd, Time);

    // 默认背景色（深色）
    float3 col = float3(0.05, 0.05, 0.1);

    // 如果击中物体（d < 最大距离）
    if(d < 100.0)
    {
        // 计算击中点
        float3 p = ro + rd * d;

        // 计算法线
        float3 n = FNormalCalculator::CalcNormal(p, Time);

        // 着色
        col = FShader::Shade(p, n, Time);

        // 简单的雾效果
        col = lerp(col, float3(0.05, 0.05, 0.1), 1.0 - exp(-0.01 * d * d));
    }

    return col;
}

// ============================================================================
// 使用说明
// ============================================================================

/*
在UE材质编辑器中：

1. 创建Custom节点，命名为"RaymarchingScene"
2. 添加输入引脚：
   - UV (float2): 从TexCoord节点获取，然后：
     * 添加一个"乘法"节点：TexCoord * 2.0 - 1.0
     * 添加一个"除法"节点：除以材质的宽高比
     * 或者简单地：TexCoord * 2.0 - 1.0（如果不需要精确宽高比）

   - CameraPos (float3): 可以设置为：
     * 常量：float3(0.0, 2.0, -3.0)
     * 或者连接到相机位置参数

   - Time (float): 从"Time"节点获取或连接到自定义参数

3. 输出连接到：
   - Base Color（如果输出的是颜色）
   - 或其他需要的材质属性

4. 性能优化建议：
   - 减少循环次数（目前是64次）
   - 使用材质函数封装以便重用
   - 考虑使用Celsius或自定义节点进行进一步优化
   - 可以添加细节级别（LOD）支持

5. 额外改进：
   - 添加软阴影
   - 添加环境光遮蔽（AO）
   - 添加反射
   - 使用多个物体创建复杂场景
*/

// ============================================================================
// 简化版本（用于性能关键场景）
// ============================================================================

/*
// Custom节点: SimpleRaymarch
// Inputs: UV, Time
// Output: float3

float3 SimpleRaymarch(float2 UV, float Time)
{
    float3 ro = float3(0.0, 2.0, -3.0);
    float3 rd = normalize(float3(UV, 1.0));

    float dO = 0.0;
    float3 col = float3(0.05, 0.05, 0.1);

    // 单球体场景
    for(int i = 0; i < 32; i++)
    {
        float3 p = ro + rd * dO;
        float d = length(p - float3(0.0, 1.0, 0.0)) - 1.0;
        dO += d;

        if(dO > 50.0 || d < 0.001)
        {
            if(d < 0.001)
            {
                float3 n = normalize(p - float3(0.0, 1.0, 0.0));
                float diff = max(dot(n, normalize(float3(1.0, 1.0, -1.0))), 0.0);
                col = float3(diff);
            }
            break;
        }
    }

    return col;
}
*/

// ============================================================================
// 常见问题
// ============================================================================

/*
Q: 为什么我的结果是全黑或全白？
A: 检查UV坐标范围。Shadertoy使用fragCoord（像素坐标），需要转换：
   uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
   在UE中，TexCoord已经是[0,1]范围，需要：
   UV = UV * 2.0 - 1.0;

Q: 性能太差怎么办？
A:
   1. 减少光线步进次数
   2. 使用更简单的SDF函数
   3. 添加提前退出条件
   4. 考虑使用预烘焙的纹理

Q: 如何添加更多物体？
A: 在FSceneMap::Map()函数中使用min()组合更多SDF：
   d = min(d, SDSphere(p - float3(x, y, z), radius));
   d = min(d, SDBox(p - float3(x, y, z), size));
   等等

Q: 如何添加动画？
A: 将Time参数传递给SDF函数：
   float spherePos = 1.0 + sin(Time * 2.0) * 0.3;
   float d = SDSphere(p - float3(0.0, spherePos, 0.0), 1.0);
*/
*/
