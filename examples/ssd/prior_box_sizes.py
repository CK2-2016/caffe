# network definitions, in [kernelsize, relative stride, padding, dilation]
VGGDef = [
        [3, 1, 1, 1, 'conv1_1'],
        [3, 1, 1, 1, 'conv1_2'],
        [2, 2, 0, 1, 'pool1'],
        [3, 1, 1, 1, 'conv2_1'],
        [3, 1, 1, 1, 'conv2_2'],
        [2, 2, 0, 1, 'pool2'],
        [3, 1, 1, 1, 'conv3_1'],
        [3, 1, 1, 1, 'conv3_2'],
        [3, 1, 1, 1, 'conv3_3'],
        [2, 2, 1, 1, 'pool3'],
        [3, 1, 1, 1, 'conv4_1'],
        [3, 1, 1, 1, 'conv4_2'],
        [3, 1, 1, 1, 'conv4_3'],
        [2, 2, 0, 1, 'pool4'],
        [3, 1, 1, 1, 'conv5_1'],
        [3, 1, 1, 1, 'conv5_2'],
        [3, 1, 1, 1, 'conv5_3'],
        [3, 1, 1, 1, 'pool5'],
        [3, 1, 6, 6, 'fc6'],
        [1, 1, 0, 1, 'fc7'],
        [1, 1, 0, 1, 'conv6_1'],
        [3, 2, 1, 1, 'conv6_2'],
        [1, 1, 0, 1, 'conv7_1'],
        [3, 2, 1, 1, 'conv7_2'],
        [1, 1, 0, 1, 'conv8_1'],
        [3, 2, 1, 1, 'conv8_2'],
        [3, 1, 0, 1, 'pool6'],
        ]

def calcRF(netDef=VGGDef, inputSize=300):
    r = 1
    s = 1
    output = []
    for layer in netDef:
        k, rs, p, d, name = layer #kernel size and relative stride
        r = r + (k - 1) * s # r_i = r_i-1 + (k_i - 1) * s_i-1
        s = s * rs # s_i = s_i-1 * rs_i
        inputSize = (inputSize - d * (k - rs) + 2*p)/rs
        output.append([r, s, inputSize, name])
    return output

if __name__ == '__main__':
    for row in calcRF():
        print("layer {}, receptive field {}, absolute stride {}, blob width {}".format(row[-1],row[0],row[1],row[2]))
