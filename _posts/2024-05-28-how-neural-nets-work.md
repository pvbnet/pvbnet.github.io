---
layout: post
title: "We do know how AI models work"
author: "Peter van Beek"
---

Please stop saying we don't know how artificial neural networks work!

<!--more-->

In news/popular media about generative AI and large language models (LLMs), I often see/hear someone say that "we don't know how these AI models work". Of course, all AI models were built by engineers, and we plainly do know how they work.

So, hoping to take away some of the mystery for a wider audience, and, frankly, just to prove a point, let me describe how artificial neural networks work, in non-engineer terms.

Let's start with an example from computer vision. We might ask an image recognition model to describe the scene in the photo below.

<img src="/assets/posts/2024-05-28-how-neural-nets-work/1TgzV2mo0KVs-wFZTt2k4Rg.jpeg" alt="Example scene for image recognition" style="width: 50%; max-width: 400px;">

Digital images are just a rectangular arrangement of pixels, and each pixel is a triplet of red, green, blue number values. In essence, this image is represented by a bunch of numbers. These numbers representing the image are stored and provided as inputs to the image recognition model in a particular way. However, here I will just refer to the input as a sequence of values _x_₁, _x_₂, …

Other types of data such as digitized speech, audio clips, or text, can all be represented by a sequence of numbers. The particular way that the data is organized into digital numbers is of course important and is different in each case, but we will ignore those aspects here.

Now, what happens when we feed our image data to a neural net? First, some of the input values _x_₁, _x_₂, … are multiplied by weights _w_₁, _w_₂, …, and the resulting products are added together, along with an offset _b_:

<img class="formula" src="/assets/posts/2024-05-28-how-neural-nets-work/107WjJk9KFffP5FWuqyQcZA.png" alt="Weighted sum formula">

Often, the above weighted summation is followed by a simple nonlinear operation:

<img class="formula" src="/assets/posts/2024-05-28-how-neural-nets-work/14J7BUnBbrWU8gsr6LTxMbw.png" alt="ReLU nonlinear operation">

which gives us an intermediate output value _y_. This step simply sets its input to 0 if it's negative, otherwise it's unchanged. It just means that the output is active when the initial weighted sum is large enough, otherwise, it is zero. Sometimes, slightly fancier functions are used, but this simple operation works remarkably well in many models. However simple mathematically, this operation is one of the keys to making artificial neural nets work.

And that's basically all that happens in an artificial neural net!

Well, actually, the above basic step is repeated many, many, **many** times. Let me write down just two weighted sums as an example:

<img class="formula" src="/assets/posts/2024-05-28-how-neural-nets-work/1zsHadffaiUi3aLpJY-fHiA.png" alt="Two weighted sums example">

Here, we used the same set of input values twice, with different sets of weights, to calculate two different outputs. This is typically done tens or hundreds of times. This type of operation might be applied in a similar way many times across an image, across an audio clip, or across a text sample.

Is that it, then? Well actually, we are going to apply operations like the above many, many, **many**, times, in sequential passes. Previous outputs (_y_'s) become inputs (_x_'s) to subsequent passes. Each pass (actually called layer) has its own set of specific weights. Note, the outputs (_y_'s) of the above operation are clearly no longer original input values. At this point, these are referred to as feature values. Each represents some _feature_ of the original network inputs (the samples of text, audio, images, etc.).

Initially, this would be a very simple feature of the input, e.g. the "blue-ness" of a few image pixels, the "brightness difference" between a couple of image pixels, or the rise or drop in the amplitude of audio samples. However, after several passes as described above, these intermediate features become more complex and may become responsive to specific shapes like corners, squares, circles in the input. After more passes, these features can become even more complex and may represent the visual presence of everyday objects in the image!

The specific nature of these features is determined by the _weights_ (_w_'s). In most instances, these model weights are learned during the process of _training_ and then fixed when applied in practice. These infamous weights (along with the specific ways the above-mentioned layers are designed) determine its overall function and capability.

The output of a neural network is again just a bunch or numbers. In some applications, the outputs can be of a similar type to the inputs. For example, when translating text, both input and output represent text. In image recognition applications, the outputs may be numbers that represent things we may see in an image. For example, "sky" might be represented by the number 1, "sea" might be represented by the number 2, "sand" by the number 3, etc. In LLMs, generated text is broken down into fragments of words represented by so-called "tokens", each consisting of multiple numbers.

So, is that all there is to it? Mmmh, OK, I left out the process of training, which is basically a way of tweaking the weights over and over, in such a way that the network behaves more closely to what we want. How do we define what we want? Using lots, and lots, and **lots** of example data. Also, by defining objectives and penalties to nudge this process in the right direction.

Honestly, of course I left out a lot more. I don't mean to diminish the vast amount of amazing research and development work that has been done and continues to be done by many engineers and scientists in the machine learning field. Or the new applications and businesses this development is generating, at lightning speed.

But I just wanted to focus here on the simplicity of the actual operations happening in today's artificial neural networks. Just built from basic multiplications, additions, and comparisons of numbers. There are no magical or unknown steps. No dark matter, quantum entanglement, or panpsychism needed.

What is surprising, however, is that these neural networks work so incredibly well. This approach has been shown to outperform previous techniques in a large and growing set of problems and applications. By scaling up the number of basic operations, scaling up the number of weights, and scaling up the training data sets.

An open question is what this means for us humans. In various domains, these neural nets appear to be capable of performing tasks that only humans could do until now, although still in narrow and shallow ways, for now. Let me know your thoughts in the comments!
