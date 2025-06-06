# visualization.py
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm

def read_tensor_from_csv(filepath):
    """
    Reads a tensor of shape (T, M, N) from a CSV file.
    Assumes the file format includes headers like 'TimeStep t (x.xx seconds)'.
    """
    tensor = []
    with open(filepath, 'r') as f:
        lines = f.readlines()

    current_grid = []
    for line in lines:
        line = line.strip()
        if line.startswith("TimeStep"):
            if current_grid:
                tensor.append(np.array(current_grid, dtype=float))
                current_grid = []
        elif line:
            current_grid.append([float(x) for x in line.split(',')])

    if current_grid:
        tensor.append(np.array(current_grid, dtype=float))  # Append the last grid

    return np.array(tensor)  # Shape: (T, M, N)


# def create_custom_colormap():
#     """Returns a colormap that fades from light gray (cool) → red → white (hot)."""
#     colors = [
#         (0.85, 0.85, 0.85),  # Light gray for 25°C (cool, metal-like)
#         (1.0, 0.0, 0.0),     # Red for mid temps
#         (1.0, 1.0, 1.0)      # White for 100°C (hot)
#     ]
#     cmap_name = 'gray_red_white'
#     return LinearSegmentedColormap.from_list(cmap_name, colors, N=256)
#     return cm.get_cmap('plasma')

def animate_comparison(tensor1, tensor2, label1="CUDA", label2="Non-CUDA", interval=100):
    T = min(tensor1.shape[0], tensor2.shape[0])
    vmin = min(tensor1.min(), tensor2.min())
    vmax = max(tensor1.max(), tensor2.max())

    # cmap = create_custom_colormap()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    img1 = ax1.imshow(tensor1[0], cmap='plasma', interpolation='nearest', vmin=vmin, vmax=vmax)
    img2 = ax2.imshow(tensor2[0], cmap='plasma', interpolation='nearest', vmin=vmin, vmax=vmax)

    ax1.set_xlim(20, 44)
    ax1.set_ylim(44, 20)  # reverse Y to match imshow orientation
    ax2.set_xlim(20, 44)
    ax2.set_ylim(44, 20)

    ax1.set_title(label1)
    ax2.set_title(label2)

    fig.suptitle("Heat Diffusion", fontsize=14)
    fig.tight_layout()
    fig.subplots_adjust(top=0.88)
    fig.colorbar(img1, ax=[ax1, ax2], orientation='vertical', shrink=0.8)

    def update(frame):
        img1.set_data(tensor1[frame])
        img2.set_data(tensor2[frame])
        ax1.set_title(f"{label1}")
        ax2.set_title(f"{label2}")
        return [img1, img2]

    ani = animation.FuncAnimation(fig, update, frames=T, interval=interval, blit=False)
    plt.show()

def visualize_last_frame(tensor, label="Result", xlim=(0, None), ylim=(None, 0)):
    last_frame = tensor[-1]
    M, N = last_frame.shape

    # Defaults if not provided
    x_start, x_end = xlim[0], xlim[1] if xlim[1] is not None else N
    y_end, y_start = ylim[0], ylim[1] if ylim[1] is not None else 0  # reversed Y

    # Proper slicing (Y reversed for imshow)
    x_start = int(x_start)
    x_end = int(x_end)
    y_start = int(y_start)
    y_end = int(y_end)

    # Ensure bounds are valid
    x_start, x_end = max(0, x_start), min(N, x_end)
    y_start, y_end = max(0, y_start), min(M, y_end)

    # Slice the data
    Z = last_frame[y_start:y_end, x_start:x_end]
    Y, X = np.meshgrid(np.arange(y_start, y_end), np.arange(x_start, x_end), indexing='ij')

    fig = plt.figure(figsize=(12, 5))

    # 2D heatmap
    ax1 = fig.add_subplot(1, 2, 1)
    im = ax1.imshow(Z, cmap='plasma', interpolation='bilinear',
                    extent=[x_start, x_end, y_end, y_start])  # flip Y for imshow
    ax1.set_title(f"{label} - 2D Heatmap")
    fig.colorbar(im, ax=ax1, shrink=0.8, label='Temperature')

    # 3D surface plot
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    surf = ax2.plot_surface(X, Y, Z, cmap='plasma', edgecolor='none')
    ax2.set_title(f"{label} - 3D Surface")
    fig.colorbar(surf, ax=ax2, shrink=0.6, aspect=10, label='Temperature')

    plt.tight_layout()
    plt.show()

def main():
    # Files: update these if names change
    cuda_file = "state_data/tensor_output_cuda64x64.csv"
    noncuda_file = "state_data/tensor_output64x64.csv"

    print("Loading CUDA tensor...")
    cuda_tensor = read_tensor_from_csv(cuda_file)

    print("Loading Non-CUDA tensor...")
    noncuda_tensor = read_tensor_from_csv(noncuda_file)

    print("Launching comparison animation...")
    animate_comparison(cuda_tensor, noncuda_tensor, label1="CUDA", label2="Non-CUDA")

    # print("Showing final CUDA frame...")
    # visualize_last_frame(cuda_tensor, label="Last frame", xlim=(20, 44), ylim=(44, 20))

if __name__ == "__main__":
    main()
