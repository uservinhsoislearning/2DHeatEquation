#include <stdio.h>
#include <malloc.h>
#include <cuda.h>
#define Ntime 50 
#define M 64
#define N 64
#define dx 0.1
#define dy 0.1
#define dt 0.1
#define D 0.01
#define BlockSizeX 16 
#define BlockSizeY 16 
#define GridSizeX 4 // 64:16 = 128
#define GridSizeY 4 // 64:16 = 128

void printGrid(float *T)
{
    int i,j;
    for (i=0;i<M;i++)
    {
        for (j=0;j<N;j++)
        {
            printf("%.2f ", *(T+i*N+j));
        }
        printf("\n");
    }
}

void initialize(float *T)
{
    int i,j;
    for (i=0;i<M;i++)
    {
        for (j=0;j<N;j++)
        {
            if ((i>=(M/2-4*(M/64)))&&(i<(M/2+4*(M/64)))&&(j>=(N/2-4*(N/64)))&&(j<(N/2+4*(N/64))))
                *(T+i*N+j) = 100.0;
            else
                *(T+i*N+j) = 25.0;
        }
    }
}

//Biến đổi phương trình đạo hàm riêng thành phương trình vi phân toàn phần (ODE) 

__global__ void Derivative(float *T, float *dT)
{
    float c,left,right,up,down;
    int i = blockIdx.y * blockDim.y + threadIdx.y;
    int j = blockIdx.x * blockDim.x + threadIdx.x;

    if (i >= 1 && i < M - 1 && j >= 1 && j < N - 1) {
        up = *(T+(i-1)*N+j);
        down = *(T+(i+1)*N+j);
        left = *(T+i*N+j-1);
        right = *(T+i*N+j+1);
        c = *(T+i*N+j);
        *(dT+i*N+j) = D*(((up-2*c+down)/(dx*dx))+((left-2*c+right)/(dy*dy)));
    }
}
 
//Giải phương trình đã biến đổi (bằng euler thuận)

__global__ void SolvingODE(float *T, float *dT)
{
    int i = blockIdx.y * blockDim.y + threadIdx.y;
    int j = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < M && j < N) {
            *(T+i*N+j) = *(T+i*N+j) + dt*(*(dT+i*N+j));
    }
}

int main() 
{
    float *Tcpu;
    Tcpu = (float*)malloc((M*N)*sizeof(float));
    initialize(Tcpu);
    // CUDA code
    // 1.Declare, allocate mem
    float *Tgpu, *dTgpu; 
    cudaMalloc((void**)&Tgpu, (M*N)*sizeof(float));
    cudaMalloc((void**)&dTgpu, (M*N)*sizeof(float));
    // 2.Copy input from CPU to GPU
    cudaMemcpy(Tgpu, Tcpu, (M*N)*sizeof(float), cudaMemcpyHostToDevice);
    // 3.Define Block and Threads Structures 
    dim3 dimGrid(GridSizeX, GridSizeY);
    dim3 dimBlock(BlockSizeX, BlockSizeY);
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    cudaEventRecord(start);
    
    for (int t=0; t<Ntime; t++) {
        Derivative<<<dimGrid,dimBlock>>>(Tgpu,dTgpu);
        SolvingODE<<<dimGrid,dimBlock>>>(Tgpu,dTgpu);
    }
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    float milliseconds = 0;
    cudaEventElapsedTime(&milliseconds, start, stop);
    printf("GPU Time: %f ms\n", milliseconds);
    cudaMemcpy(Tcpu, Tgpu, M*N * sizeof(float), cudaMemcpyDeviceToHost);
    // Giải phóng bộ nhớ
    free(Tcpu);
    cudaFree(Tgpu);
    cudaFree(dTgpu);
    return 0;
}
