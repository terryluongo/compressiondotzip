import matplotlib.pyplot as plt
import cv2
import scipy
import ipywidgets as wdg
import skimage.io as skio
import skimage.util as skut
import skimage.color as skolor
import skimage.measure as skm
import skimage.transform as skitran
import skimage.exposure as ske
import skimage.filters as skif
import numpy as np


def create_LoG(img, sigma, rToG = True):
    if rToG:
        img = skolor.rgb2gray(img)
    
    return skif.difference_of_gaussians(img, sigma, channel_axis = -1)



def LoG_view(img, sigma, rToG = True):
    """
    Displays 8x8 block LoG view of an image. If rToG is not False, will assume original image is RGB
    and convert to grayscale.
    """
    if rToG:
        img = skolor.rgb2gray(img)
    
    filtered = skif.difference_of_gaussians(img, sigma, channel_axis = -1)

    plt.figure()
    plt.imshow(filtered, cmap='gray')
    plt.title(f"Edge detected image with sigma {sigma}")

def mean_LoG_view(img, sigma, rToG = True):
    """
    Displays MEAN 8x8 block LoG view of an image. If rToG is not False, will assume original image is RGB
    and convert to grayscale.
    
    """
    LoG = create_LoG(img, sigma, rToG)

    imsize = LoG.shape
    mean_array = np.zeros(imsize)

    for i in range(0, imsize[0], 8):
        for j in range(0, imsize[1], 8):
            mean_array[i:(i+8),j:(j+8)] = np.mean(LoG[i:(i+8), j:(j+8)])

    plt.figure()
    plt.imshow(mean_array, cmap='gray')
    plt.title(f"8x8 mean blocks of image LoG with sigma = {sigma}")

def std_LoG_view(img, sigma = 5, rToG = True):
    """
    Displays STANDARD DEVIATION of 8x8 block LoG view of an image. If rToG is not False, will assume original image is RGB
    and convert to grayscale.
    """
    LoG = create_LoG(img, sigma, rToG)

    imsize = LoG.shape
    std_array = np.zeros(imsize)

    # Do 8x8 DCT on image (in-place)
    for i in range(0, imsize[0], 8):
        for j in range(0, imsize[1], 8):
            std_array[i:(i+8),j:(j+8)] = np.std(LoG[i:(i+8), j:(j+8)])

    sliced = std_array[::8, ::8]

    rang = sliced.max() - sliced.min()
    sliced -= sliced.min()
    sliced /= rang
    sliced *= 255
    return sliced.astype(np.uint8)
