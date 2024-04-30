import matplotlib.pyplot as plt
import numpy as np
import skimage.io as skio
import scipy
import rle
import zlib
from skimage.util import view_as_blocks
from skimage.color import rgb2ycbcr, ycbcr2rgb

def poop():
    return 0


# given an image, return image in YCbCr color space
# instead of red, green, blue channels, one brightness channel and two channels indicating deviation in blue and red respectively
# conversion taken from [wikipedia](https://en.wikipedia.org/wiki/YCbCr)
# according to ITU-R BT.709 convension
def rgb_to_YCbCr(img_array): 
    #test
    img = img_array / 255 # convert to floating_point
    
    # same matrix scipy usses for this
    conv_matrix = np.matrix(
    [[65.481, 128.553, 24.966], 
     [-37.797, -74.203, 112.0], 
     [112.0, -93.786, -18.214]])
    
    # reshape to do matrix multiplication across color channels easier
    img_reshape = np.reshape(img, (img.shape[0] * img.shape[1], img.shape[2]))

    # do matrix multiplication to switch color spaces
    converted_reshaped = img_reshape * np.transpose(conv_matrix)

    # go back to original shape
    converted = np.reshape(np.asarray(converted_reshaped), img.shape)

    Y = converted[..., 0] + 16
    Cb = converted[..., 1] + 128
    Cr = converted[..., 2] + 128

    
    return (Y, Cb, Cr)


def YCbCr_to_rgb(channel_array):

    inv_matrix = np.matrix(
    [[65.481, 128.553, 24.966], 
     [-37.797, -74.203, 112.0], 
     [112.0, -93.786, -18.214]])
    
    conv_matrix = np.linalg.inv(inv_matrix)

    img = np.transpose(np.asarray(channel_array), (1, 2, 0))
    
    img[..., 0] -= 16
    img[..., 1] -= 128
    img[..., 2] -= 128
    
    # reshape to do matrix multiplication across color channels easier
    img_reshape = np.reshape(img, (img.shape[0] * img.shape[1], img.shape[2]))

    # do matrix multiplication to switch color spaces
    before_rounding = img_reshape * np.transpose(conv_matrix)

    range = before_rounding.max() - before_rounding.min()
    before_rounding -= before_rounding.min()
    before_rounding /= range
    
    # go back to original shape
    converted = np.reshape(np.asarray(before_rounding), img.shape)

    img_array = (converted * 255).astype(np.uint8)

    return img_array

def calculate_downsampling_ratios(ratio):
    if ratio == "4:2:0":
        return [(1,1), (2,2), (2,2)]
    elif ratio == "4:2:2":
        return [(1,1), (2,1), (2,1)] # obviously change if i want new ratios
    else:
        return [(1,1), (8,8), (8,8)]

def downscale_colors(channel, **kwargs):
    i = kwargs["index"]
    ratio = kwargs["downsample_ratio"]
    factors = calculate_downsampling_ratios(ratio)[i]
    return channel[::factors[1], ::factors[0]]

def rescale_colors(channel, **kwargs):
    # fill out 2x2 squares with downsampled value
    i = kwargs["index"]
    ratio = kwargs["downsample_ratio"]
    factors = calculate_downsampling_ratios(ratio)[i]
    return np.repeat(np.repeat(channel, factors[0], axis=1), factors[1], axis=0)


def form_blocks(channel, **kwargs):
    block_size = kwargs['block_size']

    return view_as_blocks(channel, (block_size, block_size))

def reconstruct_blocks(channel, **kwargs):
    block_size = kwargs['block_size']

    shape = (channel.shape[0] * block_size, channel.shape[1] * block_size)
    wrong_order = np.transpose(channel,axes=(0,2,1,3)) # i have no clue why this works but my intuition told me to do it
    new_channel = wrong_order.reshape(shape)

    return new_channel

def calculate_blocked_dct(channel, **kwargs):
    channel -= 128 # want the whole thing centered at 0
    dct = scipy.fftpack.dctn(channel, axes=(-2,-1))
    return dct

def inverse_block_dct(channel, **kwargs):
    idct = scipy.fftpack.idctn(channel, axes=(-2,-1))
    idct += 128 # recenter to fit range
    return idct

def quantize(channel, **kwargs):
    quality = kwargs['q']
    
    # as specified in JPEG standard
    #https://stackoverflow.com/questions/29215879/how-can-i-generalize-the-quantization-matrix-in-jpeg-compression
    default = np.array([
    [6, 4, 4, 6, 10, 16, 20, 24],
    [5, 5, 6, 8, 10, 23, 24, 22],
    [6, 5, 6, 10, 16, 23, 28, 22],
    [6, 7, 9, 12, 20, 35, 32, 25],
    [7, 9, 15, 22, 27, 44, 41, 31],
    [10, 14, 22, 26, 32, 42, 45, 37],
    [20, 26, 31, 35, 41, 48, 48, 40],
    [29, 37, 38, 39, 45, 40, 41, 40]
    ])

    divide = 1 / default # because we are dividing

    result = channel * divide[np.newaxis, np.newaxis, :, :]
    int_result = result.astype(np.int16) 

    return int_result


def dequantize(channel, **kwargs):
    quality = kwargs['q']
    
    default = np.array([
    [6, 4, 4, 6, 10, 16, 20, 24],
    [5, 5, 6, 8, 10, 23, 24, 22],
    [6, 5, 6, 10, 16, 23, 28, 22],
    [6, 7, 9, 12, 20, 35, 32, 25],
    [7, 9, 15, 22, 27, 44, 41, 31],
    [10, 14, 22, 26, 32, 42, 45, 37],
    [20, 26, 31, 35, 41, 48, 48, 40],
    [29, 37, 38, 39, 45, 40, 41, 40]
    ])
    q = default

    result = channel * q[np.newaxis, np.newaxis, :, :]
    
    return result



def zigzag(channel, **kwargs):
    block_size = kwargs['block_size']
    
    #https://stackoverflow.com/questions/39440633/matrix-to-vector-with-python-numpy
    canon_order = np.reshape(np.arange(0, block_size ** 2), (block_size, block_size))
    
    zigzag_order =  np.concatenate([np.diagonal(canon_order[::-1,:], 
                                                k)[::(2*(k % 2)-1)] for k in range(1 - block_size, block_size)])

    zigzagged = np.empty_like(channel)
    zigzagged = np.reshape(zigzagged, newshape = (zigzagged.shape[0], zigzagged.shape[1], zigzagged.shape[-1] * zigzagged.shape[-2]))

    a, b, _, _ = channel.shape
    for i in range(a):
        for j in range(b):
            # ravel and order with fixed ordering every time
            zigzagged[i,j] = np.ravel(channel[i,j])[zigzag_order]

    return zigzagged


def unzigzag(channel, **kwargs):
    block_size = kwargs['block_size']
    
    #https://stackoverflow.com/questions/39440633/matrix-to-vector-with-python-numpy
    canon_order = np.reshape(np.arange(0, block_size ** 2), (block_size, block_size))
    
    zigzag_order =  np.concatenate([np.diagonal(canon_order[::-1,:], 
                                                k)[::(2*(k % 2)-1)] for k in range(1 - block_size, block_size)])

    # get back to canonical basis
    inv_order = np.argsort(zigzag_order)
 
    
    channel_reconstructed = np.zeros((channel.shape[0], channel.shape[1], block_size, block_size), dtype = channel.dtype)
    a, b, c = channel.shape
    for i in range(a):
        for j in range(b):
            raveled_fixed_order = channel[i,j][inv_order]
            channel_reconstructed[i,j] = np.reshape(raveled_fixed_order,(8,8))

    return channel_reconstructed    


def ravel_channels(img_tuple):
    stream = np.asarray([])
    
    for channel in img_tuple:
        stream = np.append(stream, np.ravel(channel))
        
    return stream      


def reshape_channels(stream, shape):
    Y_raveled = stream[0:shape[0] * shape[1]]
    Cb_raveled = stream[shape[0]*shape[1]: shape[0]*shape[1] + ((shape[0]//2) * (shape[1]//2))]
    Cr_raveled = stream[shape[0]*shape[1] + ((shape[0]//2) * (shape[1]//2)): ]
    
    Y = np.reshape(Y_raveled, (shape[0]//8, shape[1]//8, shape[2]))
    Cb = np.reshape(Cb_raveled, (shape[0]//16, shape[1]//16, shape[2]))
    Cr = np.reshape(Cr_raveled, (shape[0]//16, shape[1]//16, shape[2]))

    return [Y, Cb, Cr]
