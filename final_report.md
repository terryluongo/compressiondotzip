# Exploring JPEG Compression: Dynamic Quantization

## A CSCI 0452 Project by Terry Luongo and Jiffy Lesica

### **Introduction**:

Over the course of this semester, we have grounded our study of image processing in understanding images to be digitally stored as a multi-dimensional array of data: pixel/channel values, to be a bit more specific. While an image itself is defined from a two-dimensional function (Gonzalez, Digital Image Processing), the data structures and values within each dimension can be manipulated so as to manipulate a local region of an image, or apply some universal transformation across the entire image. In sum, a digital image is comprised of dimensionally organized data which can be operated on so as to extract or change information within an image.

It is from this abstracted understanding that an array (no pun intended) of questions arises on digital images. Our project focuses on two in particular:

1. What can we learn about information extracted from a digital image and

2. How can we use the information we extract from an image to ___ apply some transformation to that same image?

#### Understanding JPEG Through the Lens of Data

Particularly, we applied these questions to the JPEG compression algorithm. Since 1992, the JPEG Image Compression Method has been one of the most successful and ubiquitous algorithms in the field of image processing. JPEG is a lossy image compression method. As with any compression method, the JPEG algorithm works to reduce the amount of data - the means by which an image is conveyed - required to represent information - i.e. the image itself (Gonzalez 540). The algorith takes in an image and 'identifies' repeated patterns in its data - leveraging the fact that images are stored digitally as organized arrays of data - and replaces them with shorter patterns. This allows for the file to be stored with less data, which facilitates efficient image storage and transmission. However, JPEG is particular in that it is a lossy compression method. This means that in the process of compression, the JPEG algorithm throws away 'non-essential' image data. While this does allow for the image to be stored with less data, it also means that data is lost which cannot be recovered when a JPEG-compressed image is reconstruced. Thus, while the JPEG compression algorithm reduces the size of an image file to be stored, it also reduces the resolution of an image, which can compromise image integrity.

#### How Does JPEG Work?

So, how does the JPEG algorithm itself really work. The algorithm is based on 2 psychovisual principles.

1. Changes in Brightness are More Important than Changes in Color to a Human Observer: While the human eye has 90-120 million brightness-sensitive rods in the retina, it only has about 4.5-6 million color-sensitive cones.

2. Low-frequency Changes in an Image are More Important than High-frequency Changes to a Human Observer: The human eye can distinguish low-frequency light changes like the edges of larger objects better than high frequency light changes like the fine details between blades of grass.

Through a series of transformative steps, the JPEG algorithm identifies data patterns and operates on a given image array based on these assumptions:

1. Color Conversion and Subsampling: The image data divided into 1 luminance (Y) and 2 color (Cb, Cr) channels. The values in the color channels can be optionally subsampled - A.K.A. some 'non-essential' color values are removed from the image representation without significantly affecting the visible image info (rememver psychovisual principle 1!). Imagine an image array with a grid of pixel values, and each pixel value represents some brightness level as well as a certain combination of two colors. What we have basically done is separated each component part of each pixel value into its own data array. Each of the three channels produced by step 1 are thus arrays of the same dimension as the original image. 

2. Block-procession and DCT Transformation: For each of the three arrays we now have, each channel is further subdivided into 8x8 blocks (Ex. a 64x64 pixel image would become an 8x8 array of 8x8 pixel arrays). Each of these blocks is now transformed using the Discrete Cosine Transformation (DCT) from the spatial domain to the frequency domain. This operations gives us access to the frequency domain representation of these blocks. In other words, we can now see how much high-frequency change versus low-frequency change is present across each block of our image (remember psychovisual principle 2!).

3. Quantization: In quantization, we map the largest set of frequency values to a smaller set of discrete finite values. Quantization is where we determine the final quality of our image, and how lossy we want out compression. In any user-oriented implementation of JPEG compression, a person will get to choose the quality of the image that is output. This is fundamentally a way to allow the user to choose the degree of quantization their image undergoes. Depending on the quality you degree of quantization you choose, the quality of your compressed image will change. The more heavily the quantization is applied, the more frequency information you will throw away and replace. This means that a greater range of values from your original channel will be mapped to the same smaller set of values to represent your final image.

    Imagine this: You have an image that is represented using 4 shades of blue. The numbers 1.0, 1.1, 1.2, and 1.3 each represent a different shade of blue. If I wanted to compress this image, a more heavily quantized version would say "Hey, 1.0, 1.1, 1.2, and 1.3 all look pretty similar, so in our new image lets just set any pixel that is 1.0, 1.1, 1.2, or 1.3 to 1.0". While you'd only have to use one color value to represent your image (1.0), you will also lose all the detailed nuance of the image you originally had because every pixel is the same color! On the other hand, a lower quantization step would say "Hey, 1.0 and 1.1 look pretty similar to each other, and 1.2 and 1.3 look pretty similar to eachother. In our new image, lets set any pixel that is 1.0 or 1.1 to 1.0, and any pixel that is 1.2 or 1.3 to 1.2". Now, while we still lose some color information in our final image, we will still retain some more detail. However, since we are using 2 colors to represent the image, it will take more unique data to represent the image. Now, imagine extrapolating this basic process to 100s of color and brightness values on very high resolution images; you can drastically impact the quality of your final image by increasing the degree of quantization.

    Programmatically this process works by using quantization tables. A quantization table is an 8x8 table of whole numbers multiplied by a coefficient. In JPEG compression, each 8x8 DCT block of an image is divided by these quantization table and the pixel value resulting from each division is rounded to meet the smaller set of finite values you are mapping to. As you change the degree of quantization, the coefficient of each quantization table changes. The table values have been calculated mathematically to a JPEG standard so that as the degree of quantization increases, the resulting change in the quantization table coefficient will mean more data values from the original image are mapped to the same finite values (in other words, the high quantization results in more image information being lost).

    Depending on the degree of quantization you choose, the quantization table/coefficient will be used for every 8x8 block of your image. Thus, the JPEG quantization is applied universally.

4. Reorder and Variable Length Encoding: In quantization we have technically lost frequency information, but still have the same amount of data (there is still 1 datum for each pixel in our channel). In this final step, we perform lossless data compression. By reducing the variability of pixel values in step 3, we have made our image 'more compressible'. Using a zig-zag pattern, we order our new set of pixel values from lowest frequency to highest frequency, and now have repeated chunks of data next to eachother to compress.

#### The First Question: Make it Dynamic?

As mentioned above, the JPEG algorithm is applied universally, particularly when it comes to quantization. In other words - regardless of the particular frequncies of an 8x8 DCT block - the same quantization table is used on every block: Each block undergoes the same degree of quantization. What this means is that in a high-quantization implementation, blocks with what may be visually important details will get compressed as much as those with non-essential details. And, on the other hand, in low-quantization implementations blocks which represent non-essential details will continue to use more data to represent their information. When we came across this, we began to wonder if the algorithm needed to be this way. We ultimately landed on the question that would drive our entire project: How could we make quantization dynamic - can we extract information about what is 'important' in our 8x8 DCT blocks and use that information to dynamically apply an 'optimal' degree of quantization on each of our DCT blocks? To put it more simply, does quantization have to be universal?

#### Saliency Methods:

From this question, we began to explore the information that can be extracted from our 8x8 image blocks, and really images in general. Was there anything that could actually indicate what was visually 'important' in an image? Thanks to the advice of Professor Vaccari, we eventually came across the concept of saliencyt. In essence, saliency is what "stands out" in a photo or scene. Every day of our lives humans employ the process of saliency detection to automatically locate the 'important' part of an image or scene which they face and focus on it: we automatically try and determine the most important parts of the world we see before us!

In computer vision, a saliency map can be produced from an image to actually highlight the regions on which people's eyes first focus. For example, in the below image comparison you can see how the saliency map on the right-hand side actually brightens some of the regions of the original image on the left-hand side; the castle and the bright patches in the clouds are all highlighted in the map. These are all the parts of the image our eyes immediately lock on to.

This discovery was exactly what we were looking for, and brought us to the second essential question of our project: Knowing what the saliency map represents, could we the information it holds to dynamically and efficiently compress our original image?

#### Expanding and Exploring Saliency

From this point, we made the choose to expand our exploration of saliency of saliency, to other metrics or image transformation which could help us identify what 'stands out' in an image and adjust compression accordingly. We ultimately landed on 3 different expanded saliency methods:

1. Saliency Maps: Transformed images which themselves highlight the salient details in an original image.

2. DCT: An image's DCT represents not just the frequencies which are present in a given image, but more importantly use pixel intensity to represent how often those frequencies are present in an image (the brighter a pixel on a DCT, the more often the frequency associated with that frequency appears in the original image). This was particularly interesting considering the JPEG Algorithm already operates on these blocks.

3. Difference of Gaussian (DoG)/Laplacian of Gaussian (LoG) for Edge Detection: An LoG filter can be applied over an image to highlight edges of certain sizes/widths within an image. LoG can be approximated using an adjusted DoG filter which is computationally more efficient.

### **Methods**:

### Step 1: Implementing Basic JPEG Algorithm

The first step was to implement the basic JPEG algorithm. Terry created a codec file which included a function definition for each method required in both JPEG compression and decompression. By defining our own methods for each step of the process, we had the advantage of both A. getting a detailed understanding of the algorithm before adjusting it and B. being able to make later additions/changes to our algorithm to help us dynamically adjust quantization. Terry then created a JPEG class file which image files could be loaded, and run through the methods defined in the CODEC file.

**FOR TERRY: specifically explain how you chose the quantization table you did and how the coefficient is calculated.

#### Step 2: Transforming By Saliency

Once we had a fundamental grasp on the JPEG algorithm implementation, it came time to work on the saliency methods upon which we would dynamize it. Knowing that quantization was performed on the 8x8 DCT blocks of the original image, we decided to apply each saliency method to each 8x8 block of our image separately so that the information extracted from them - which will be used to dynamically adjust quantization - will be local to the block too. For example, we would not calculate the saliency map of an image all at once, but the saliency map of each 8x8 block in the original image which corresponds to the DCT blocks to be quantized.

1. Saliency Maps: OpenCV implements static saliency - the saliency of a single, still image frame - by two methods. In each method, the resulting pixels of the saliency map have a brightness value which is proportional to the saliency of the corresponding pixel in the original image.

    a. Spectral Residual (SR): Spends less time computing the saliency of each frame, resulting in quicker computation but less detailed saliency map.

    b. Fine Grained (FG): A more detailed approachs that works 'better' when the details of an image are very small. However, it takes longer to operate on an image.

    We preferred to work with the Fine Grained method as - despite the computational slowdown - our aim was to retain details in our image which FG facilitated in more than SR.

2. DCT Blocks: Using the Scipy FFT Package we performed a DCT on each 8x8 block in our original image, giving us the local frequency domain representations of our image blocks.

3. DoG/LoG: Using Skimage's DoG function we approximated an LoG filter for our images. By adjusting the sigma value passed to our filter we can change the size of the Gaussian filter initially passed over our image and isolate edges of specific sizes to be highlighted. To approximate the LoG, pass None to the high_sigma parameter of Skimage's DoG function and the high_sigma will be calculated as 1.6x the low_sigma value passed to the function. This ratio - originally proposed by Marr and Hildreth in 1980 (https://royalsocietypublishing.org/doi/10.1098/rspb.1980.0020).


#### Step 3: Extracting From Saliency

Now having the saliency of our 8x8 blocks established, we needed to choose what information we could extract to adjust our JPEG quantization. We knew that in blocks with more salient information - the more important details in that block - we wanted to quantize those blocks to a lesser degree. We also know that in each of thse saliency blocks, pixel luminance was represented proportionally to the saliency of that pixel in the original. So, we decided two ways we could calulate the saliency across a whole 8x8 block was by taking the mean and/or standard deviation luminance value of that block.

Following step 2 and step 3, for any given image we now had a 2-dimensional saliency block whose values represented the mean saliency or standard deviation of saliency for each corresponding 8x8 block which will be quantized in the JPEG algorithm.

Example. Steps 2 and 3 Illustratred Intuitively:

- Say we start off with a 64x64 pixel image we want to compress using our JPEG algorithm, this means that during the DCT transformation step of the algorithm it will be split up into an 8x8 array of 8x8 pixel DCT blocks. Imagine eact of these DCT blocks as its own whole unit which can be operated on. This would mean there is now an 8x8 array of individual DCT units which are about to be quantized (note: each of these units still holds a 2D set of values, but this visualization aids in the intuitive explanation of our procedure).

- Now, say we want to calculate the saliency maps within the 64x64 pixel image to dynamically adjust quantization on the above mentioned blocks. In the same way we indpendently apply the DCT transformation on each 8x8 block within our image, we will apply our saliency function provided by scipy. We now will have an 8x8 array of 8x8 pixel saliency blocks which highlight the important details within regions of our original image. Imagine again that each of these blocks is an independent unit which can be operated on independently of the others in the array. We thus have an 8x8 array of individual saliency maps.

- Now, say we choose to calculate the mean luminance of the pixels in each of these 8x8 saliency blocks. Once that is complete, we will have an 8x8 saliency array whose values each represent the mean saliency value of a corresponding region in our DCT array which are waiting for quantization. The [0,0] index of the saliency array corresponds to the the [0,0] index of the DCT array which is about to be quantized. The [0,1] index of the saliency array corresponds to the saliency of the [0,1] index of the DCT array which is about to be quantized. Ultimately [0,0]-[7,7] index of the saliency array will always correspond of the [0,0]-[7,7] index of the DCT array which is about to be quantized.

#### Step 4: Dynamically Adjusting Quantization

*FOR JIFFY: once you explain the part about calculating the quantization coefficient I can def explain this so you don't have to worry about it. I'll also include one of those intuitive explanations.






