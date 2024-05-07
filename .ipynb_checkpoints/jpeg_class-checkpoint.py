import matplotlib.pyplot as plt
import numpy as np
import skimage.io as skio
import scipy
import rle
import zstd
import os
import pickle
from skimage.util import view_as_blocks
from skimage.color import rgb2ycbcr, ycbcr2rgb
import saliency
import codec

import importlib
importlib.reload(codec)
importlib.reload(saliency)




class JPEG:
    def __init__(self, img_array, q, block_size = 8, downsample_ratio = "4:2:0", dynamic = False):
        # could have sensitivity to saliency be a parameter
        # could have type of saliency be a parameter
        self.img_array = img_array
        self.block_size = block_size
        self.downsample_ratio = downsample_ratio
        self.dynamic = dynamic


        # how is dynamic quantization going to work?  channel wise or should i do it with a single grayscale array
        # probably that, would save the most space
        # how to deal with downsampling in Cb and Cr channels?
        self.q_array = saliency.std_LoG_view(img_array) if dynamic else None
        self.q = q
        self.Y = None
        self.Cb = None
        self.Cr = None

        
    # makes/displays img array
    def show_image(self):
        plt.imshow(self.img_array)


    
    # saves to binary, compresses
    def save_image(self, filename):
        pickled_data = pickle.dumps(self)
        compressed_data = zstd.compress(pickled_data)
        with open(filename, 'wb') as f:
            f.write(compressed_data)


    
    def load_image(filename):
        with open(filename, 'rb') as f:
            compressed = f.read()
    
        decompressed = zstd.decompress(compressed)
        data = pickle.loads(decompressed)

        return data


    
    def compare_image(self, img):
        fig, axs = plt.subplots(1, 2)
        fig.set_figheight(12)
        fig.set_figwidth(15)
        
        axs[0].imshow(img)
        axs[0].set_title("Original")
        
        axs[1].imshow(self.img_array)
        axs[1].set_title("Reconstruction")


    
    def compare_slice(self, img, start = 50, end = 75):
        fig, axs = plt.subplots(1, 2)
        fig.set_figheight(12)
        fig.set_figwidth(15)
        
        axs[0].imshow(img[start:end, start:end])
        axs[0].set_title("Original")
        
        axs[1].imshow(self.img_array[start:end, start:end])
        axs[1].set_title("Reconstruction")


    
    def print_block(self,block_x = 25, block_y = 25, channel = "Y"):
        print(self.__dict__[channel][block_y, block_x])


    
    # ripped this straight from Claude...
    # we can batch apply our functions now, channel wise (less for loops in function)
    def process_channels(self, function, **kwargs):
        channels = [self.Y, self.Cb, self.Cr]
        processed_channels = []

        for i, channel in enumerate(channels):
            processed_channel = function(channel, **kwargs, index = i) # need to pass through all the stuff we might need
            processed_channels.append(processed_channel)

        self.Y, self.Cb, self.Cr = processed_channels


    
    # 1. rgb_2_ycbcr, 2. downsampling, 3. blocking, 4. DCT, 5. quantizing, 6. zigzagging
    def encode(self, max_step = 6):
        
        self.Y, self.Cb, self.Cr = codec.rgb_to_YCbCr(self.img_array)
        
        functions = [codec.downscale_colors, codec.form_blocks, codec.calculate_blocked_dct, codec.quantize, codec.zigzag]
        kwargs = {"block_size": self.block_size, "q": self.q, "downsample_ratio": self.downsample_ratio, 
                  "dynamic": self.dynamic, "q_array": self.q_array}
        
        for f in functions[: max_step - 1]:
            self.process_channels(f, **kwargs)

    
    
    def decode(self, from_step = 6):

        functions = [codec.rescale_colors, codec.reconstruct_blocks, codec.inverse_block_dct, codec.dequantize, codec.unzigzag]
        kwargs = {"block_size": self.block_size, "q": self.q, "downsample_ratio": self.downsample_ratio, 
                  "dynamic": self.dynamic, "q_array": self.q_array}
        
        while from_step > 1:
            self.process_channels(functions[from_step - 2], **kwargs)
            from_step -= 1

        self.img_array = codec.YCbCr_to_rgb([self.Y, self.Cb, self.Cr])


    
    # use these to I only pickle what is necessary.  otherwise it wouldn't save space at all
    def __getstate__(self):
        # Return a dictionary containing only the attributes you want to pickle
        return {'q': self.q, 'block_size': self.block_size, 
                'downsample_ratio': self.downsample_ratio, 
                'dynamic': self.dynamic, 'q_array': self.q_array,
                'Y': self.Y, 'Cb': self.Cb, 'Cr': self.Cr}


    
    def __setstate__(self, state):
        # Restore the unpickled state
        self.q = state['q']
        self.block_size = state['block_size']
        self.downsample_ratio = state['downsample_ratio']
        self.dynamic = state['dynamic']
        self.q_array = state['q_array']
        self.Y = state['Y']
        self.Cb = state['Cb']
        self.Cr = state['Cr']
        self.img_array = None