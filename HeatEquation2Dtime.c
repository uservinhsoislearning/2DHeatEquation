#include <stdio.h>
#include <malloc.h>
#include <time.h>
#define Ntime 50 
#define M 64
#define N 64
#define dx 0.1
#define dy 0.1
#define dt 0.1
#define D 0.01

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

void derivative(float *T, float *dT) //co dinh gia tri bien == 25.0
{
    float c,left,right,up,down;
    int i,j;
    for (i=1;i<M-1;i++)
    {
        for (j=1;j<N-1;j++)
        {
            up = *(T+(i-1)*N+j);
            down = *(T+(i+1)*N+j);
            left = *(T+i*N+j-1);
            right = *(T+i*N+j+1);
            c = *(T+i*N+j);
            *(dT+i*N+j) = D*(((up-2*c+down)/(dx*dx))+((left-2*c+right)/(dy*dy)));
        }
    }
}

void solvingODE(float *T, float *dT)
{
    int i,j;
    for (i=0;i<M;i++)
    {
        for (j=0;j<N;j++)
        {
            *(T+i*N+j) = *(T+i*N+j) + dt*(*(dT+i*N+j));
        }
    }
}

int main()
{
    float *Tcpu,*dTcpu;
    Tcpu  = (float *) malloc ((M*N)*sizeof(float));
    dTcpu = (float *) malloc ((M*N)*sizeof(float));
    initialize(Tcpu);
    clock_t start = clock();
    for (int t=0;t<Ntime;t++)
    {
        derivative(Tcpu,dTcpu);
        solvingODE(Tcpu,dTcpu);
    }
    clock_t end = clock();
    double cpu_time = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("CPU Time: %f seconds\n", cpu_time);
    free(Tcpu);
    free(dTcpu);
    return 0;
}
