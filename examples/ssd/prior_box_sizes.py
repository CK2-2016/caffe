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
        [3, 1, 6, 6, 'fc6'], #TODO: fix the absolute stride calculation to handle dilation
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
    r = 1 #receptive field
    s = 1 #absolute stride
    output = [[r,s,inputSize,'data']]
    for layer in netDef:
        k, rs, p, d, name = layer #kernel size and relative stride
        r = r + (k - 1) * s # r_i = r_i-1 + (k_i - 1) * s_i-1
        s = s * rs # s_i = s_i-1 * rs_i
        inputSize = (inputSize - (d * (k - 1) + 1) + 2*p)/rs + 1
        output.append([r, s, inputSize, name])
    return output

'''
project the receptive field of the given pixel (layer, x, y) down to input space
'''
def projectRF(layerNo=0, x=0, y=0, netDef=VGGDef, inputSize=300):
    '''first calculate the layer info. The only thing needed is blob size'''
    layers = calcRF(netDef, inputSize)
    '''
    1. find the four corner pixel on the previous layer
    2. for each corner pixel, only find the one pixel on the same direction
    there after
    '''
    while layerNo < 0:
        layerNo += len(layers)
    if layerNo == 0: #data layer
        return [(x,y)]*4 #the four corner points are the same point as (x,y)
    print 'layer={} receptiveField={} absoluteStride={} blob={} x={} y={}'.format(layers[layerNo][-1], layers[layerNo][0], layers[layerNo][1],layers[layerNo][2], x, y)

    kernelSize, relativeStride, padding, dilation, name = netDef[layerNo-1] #This layer's kernel size info
    kernelSize = (kernelSize - 1) * dilation + 1
    blobSize = layers[layerNo-1][2] #previous layer's blobSize
    if x < 0 or x >= blobSize or y < 0 or y >= blobSize:
        raise Exception('x,y range illegal: {}'.format((x,y)))
    corners = rectify([
        (0-padding+x*relativeStride, 0-padding+y*relativeStride), #left top corner
        (0-padding+kernelSize-1+x*relativeStride, 0-padding+y*relativeStride), #right top corner
        (0-padding+kernelSize-1+x*relativeStride, 0-padding+kernelSize-1+y*relativeStride), #right bottom corner
        (0-padding+x*relativeStride, 0-padding+kernelSize-1+y*relativeStride), #left bottom corner
        ], blobSize)
    layerNo -= 1
    print 'layer={} receptiveField={} absoluteStride={} blob={} corners={}'.format(layers[layerNo][-1], layers[layerNo][0], layers[layerNo][1],layers[layerNo][2],corners)

    while layerNo > 0:
        '''propagate the corners down until we come to layerNo 0'''
        kernelSize, relativeStride, padding, dilation, name = netDef[layerNo-1]
        kernelSize = (kernelSize - 1) * dilation + 1
        blobSize = layers[layerNo-1][2]
        corners = rectify([
            (0-padding+corners[0][0]*relativeStride, 0-padding+corners[0][1]*relativeStride), #left top corner
            (0-padding+kernelSize-1+corners[1][0]*relativeStride, 0-padding+corners[1][1]*relativeStride), #right top corner
            (0-padding+kernelSize-1+corners[2][0]*relativeStride, 0-padding+kernelSize-1+corners[2][1]*relativeStride), #right bottom corner
            (0-padding+corners[3][0]*relativeStride, 0-padding+kernelSize-1+corners[3][1]*relativeStride), #left bottom corner
            ], blobSize)
        layerNo -= 1
        print 'layer={} receptiveField={} absoluteStride={} blob={} corners={}'.format(layers[layerNo][-1], layers[layerNo][0], layers[layerNo][1],layers[layerNo][2],corners)

    return corners

def rectify(box, blobSize):
    return [tuple(min(blobSize-1, max(val, 0)) for val in point) for point in box]

if __name__ == '__main__':
    #for row in calcRF():
    #    print("layer {}, receptive field {}, absolute stride {}, output blob width {}".format(row[-1],row[0],row[1],row[2]))

    layerNo = -5
    x = 0
    y = 0
    print ("layerNo={} x={} y={} four corners: {}".format(layerNo, x, y, projectRF(layerNo, x, y)))
