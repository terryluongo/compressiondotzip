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

def mean_LoG_view(img, sigma = 5, rToG = True):
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

    sliced = mean_array[::8, ::8]

    rang = sliced.max() - sliced.min()
    sliced -= sliced.min()
    sliced /= rang
    sliced *= 255
    return sliced.astype(np.uint8)

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



# Saliency Maps

def create_saliency(img, mode = 'FG'):
    """
    Creates saliency map of image using cv2 Spectral Residual or Fine Grained
    Method (depending on mode parameter). If no mode passed, Fine Grained used.

    returns saliency map
    """
    if mode == 'SR':
        saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
        (success, saliencyMap) = saliency.computeSaliency(img)
        
        return saliencyMap
    elif mode == 'FG':
        saliency = cv2.saliency.StaticSaliencyFineGrained_create()
        (success, saliencyMap) = saliency.computeSaliency(img)
     
        return saliencyMap
    
# Functions to calculate metrics from saliency maps, and hold in 8x8 blocks

def mean_saliency_view(img, mode = 'FG'):
    """
    Calculates mean of saliency map luminance values in 8x8 blocks across image.
    """
    salMap = create_saliency(img, mode)

    imsize = salMap.shape
    mean_array = np.zeros(imsize)

    # Do 8x8 DCT on image (in-place)
    for i in range(0, imsize[0], 8):
        for j in range(0, imsize[1], 8):
            mean_array[i:(i+8),j:(j+8)] = np.mean(salMap[i:(i+8), j:(j+8)])
    
    sliced = mean_array[::8, ::8]

    rang = sliced.max() - sliced.min()
    sliced -= sliced.min()
    sliced /= rang
    sliced *= 255

    return sliced.astype(np.uint8)

def std_saliency_view(img, mode = 'FG'):
    """
    Calculates standard deviation of saliency map luminance values in 8x8 blocks across image.
    """
    salMap = create_saliency(img, mode)

    imsize = salMap.shape
    std_array = np.zeros(imsize)

    # Do 8x8 DCT on image (in-place)
    for i in range(0, imsize[0], 8):
        for j in range(0, imsize[1], 8):
            std_array[i:(i+8),j:(j+8)] = np.std(salMap[i:(i+8), j:(j+8)])
    
    
    sliced = std_array[::8, ::8]

    rang = sliced.max() - sliced.min()
    sliced -= sliced.min()
    sliced /= rang
    sliced *= 255

    return sliced.astype(np.uint8)

# DCT views

def mean_dct_view(img, rToG = True):
    """
    Takes an image as input, converts to grayscale from RGB (unless rToG is False)
    And creates array which holds mean of DCT of image split into 8x8 blocks.
    """
    if rToG:
        img = skolor.rgb2gray(img)

    imsize = img.shape
    mean_array = np.zeros(imsize)

    # Do 8x8 DCT on image (in-place)
    for i in range(0, imsize[0], 8):
        for j in range(0, imsize[1], 8):
            mean_array[i:(i+8),j:(j+8)] = np.mean(scipy.fft.dctn(img[i:(i+8), j:(j+8)]))
    
    sliced = mean_array[::8, ::8]

    rang = sliced.max() - sliced.min()
    sliced -= sliced.min()
    sliced /= rang
    sliced *= 255

    return sliced.astype(np.uint8)


def std_dct_view(img, rToG = True):
    if rToG:
        img = skolor.rgb2gray(img)

    imsize = img.shape
    std_array = np.zeros(imsize)

    # Do 8x8 DCT on image (in-place)
    for i in range(0, imsize[0], 8):
        for j in range(0, imsize[1], 8):
            std_array[i:(i+8),j:(j+8)] = np.std(scipy.fft.dctn(img[i:(i+8), j:(j+8)]))
    
    sliced = std_array[::8, ::8]

    rang = sliced.max() - sliced.min()
    sliced -= sliced.min()
    sliced /= rang
    sliced *= 255

    return sliced.astype(np.uint8)
