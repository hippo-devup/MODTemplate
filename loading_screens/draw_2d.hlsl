Texture1D<float4> IniParams : register(t120);

struct vs2ps 
{
	float4 pos : SV_Position0;
	float2 uv : TEXCOORD1;
};



#ifdef VERTEX_SHADER


void main(out vs2ps output, uint vertex : SV_VertexID)
{
	switch(vertex) 
	{
		case 0:
			output.pos.xy = float2(-1, 1);
			output.uv = float2(0,1);
			break;
		case 1:
			output.pos.xy = float2(-1, -1);
			output.uv = float2(0,0);
			break;
		case 2:
			output.pos.xy = float2(1, 1);
			output.uv = float2(1,1);
			break;
		case 3:
			output.pos.xy = float2(1, -1);
			output.uv = float2(1,0);
			break;
		default:
			output.pos.xy = 0;
			output.uv = float2(0,0);
			break;
	};
	
	output.pos.zw = float2(0, 1);
}


#endif



#ifdef PIXEL_SHADER


SamplerState linearSampler : register(s0);
Texture2DArray<float4> Animation : register(t85);
#define frameIndex IniParams[85].x

void main(vs2ps input, out float4 result : SV_Target0)
{
		result = Animation.SampleLevel(linearSampler, float3(input.uv, frameIndex), 0);
		result.xyz = exp2((log2(result.xyz) * 1.025) * 2.05) / 1.025;
}


#endif