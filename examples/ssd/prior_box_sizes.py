# network definitions, in [kernelsize, relative stride]
VGGDef = [
        [3, 1, 'conv1_1'],
        [3, 1, 'conv1_2'],
        [2, 2, 'pool1'],
        [3, 1, 'conv2_1'],
        [3, 1, 'conv2_2'],
        [2, 2, 'pool2'],
        [3, 1, 'conv3_1'],
        [3, 1, 'conv3_2'],
        [3, 1, 'conv3_3'],
        [2, 2, 'pool3'],
        [3, 1, 'conv4_1'],
        [3, 1, 'conv4_2'],
        [3, 1, 'conv4_3'],
        [2, 2, 'pool4'],
        [3, 1, 'conv5_1'],
        [3, 1, 'conv5_2'],
        [3, 1, 'conv5_3'],
        [2, 2, 'pool5'],
        [3, 1, 'fc6'],
        [1, 1, 'fc7'],
        [1, 1, 'conv6_1'],
        [3, 2, 'conv6_2'],
        [1, 1, 'conv7_1'],
        [3, 2, 'conv7_2'],
        [1, 1, 'conv8_1'],
        [3, 2, 'conv8_2'],
        ]

def calcRF(netDef=VGGDef):
    r = 1
    s = 1
    output = []
    for layer in netDef:
        k, rs, name = layer #kernel size and relative stride
        r = r + (k - 1) * s # r_i = r_i-1 + (k_i - 1) * s_i-1
        s = s * rs # s_i = s_i-1 * rs_i
        output.append([r, s, name])
    return output

if __name__ == '__main__':
    for row in calcRF():
        print("layer {}, receptive field {}, absolute stride {}".format(row[2],row[0],row[1]))
