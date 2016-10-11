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
VGGNoDilationDef = [
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
        [2, 2, 1, 1, 'pool5'],
        [3, 1, 3, 3, 'fc6'],
        [1, 1, 0, 1, 'fc7'],
        [1, 1, 0, 1, 'conv6_1'],
        [3, 2, 1, 1, 'conv6_2'],
        [1, 1, 0, 1, 'conv7_1'],
        [3, 2, 1, 1, 'conv7_2'],
        [1, 1, 0, 1, 'conv8_1'],
        [3, 2, 1, 1, 'conv8_2'],
        [2, 1, 0, 1, 'pool6'],
        ]

'''
calculate the receptivefield size, absolute stride size, blob size
'''
def calcRF(netDef=VGGDef, inputSize=300):
    r = 1 #receptive field
    s = 1 #absolute stride
    output = [[r,s,inputSize,'data']]
    for layer in netDef:
        k, rs, p, d, name = layer #kernel size and relative stride
        r = r + d * (k - 1) * s # r_i = r_i-1 + (k_i - 1) * s_i-1
        s = s * rs # s_i = s_i-1 * rs_i
        inputSize = (inputSize - (d * (k - 1) + 1) + 2*p)/rs + 1
        output.append([r, s, inputSize, name])
    return output

'''
project the receptive field of the given pixel (layer, x, y) down to input space

layerNo is in the scale of number of feature maps, which is 1 larger than number
of kernels.
'''
def projectRF(layerNo=0, x=0, y=0, netDef=VGGDef, inputSize=300, layers=None):
    '''first calculate the layer info. The only thing needed is blob size'''
    if not layers:
        layers = calcRF(netDef, inputSize)
    boxes = []
    '''
    1. find the four corner pixel on the previous layer
    2. for each corner pixel, only find the one pixel on the same direction
    there after
    '''
    while layerNo < 0:
        layerNo += len(layers)
    #current layer
    corners = [(x,y)]*4 #the four corner points are the same point as (x,y)
    boxes.append({
        'name': layers[layerNo][-1],
        'receptiveField': layers[layerNo][0],
        'absoluteStride': layers[layerNo][1],
        'blobSize': layers[layerNo][2],
        'corners': corners
        })

    '''project the first layer, generate the first four corner points'''
    kernelSize, relativeStride, padding, dilation, name = netDef[layerNo-1] #This layer's kernel size info
    kernelSize = (kernelSize - 1) * dilation + 1
    prevBlobSize = layers[layerNo-1][2] #previous layer's blobSize, used to constrain coordinates
    if x < 0 or x >= prevBlobSize or y < 0 or y >= prevBlobSize:
        raise Exception('x,y range illegal: {}'.format((x,y)))
    corners = rectify([
        (0-padding+x*relativeStride, 0-padding+y*relativeStride), #left top corner
        (0-padding+kernelSize-1+x*relativeStride, 0-padding+y*relativeStride), #right top corner
        (0-padding+kernelSize-1+x*relativeStride, 0-padding+kernelSize-1+y*relativeStride), #right bottom corner
        (0-padding+x*relativeStride, 0-padding+kernelSize-1+y*relativeStride), #left bottom corner
        ], prevBlobSize)
    boxes.append({
        'name': layers[layerNo-1][-1], #name of feature map, as marked by outputing kernel name
        'receptiveField': layers[layerNo-1][0], #receptive field size of feature map
        'absoluteStride': layers[layerNo-1][1], #absolute stride size of feature map
        'blobSize': layers[layerNo-1][2], #blobSize of THIS feature map
        'corners': corners
        })
    layerNo -= 1

    '''now propagate the corners down to the input layer'''
    while layerNo > 0:
        kernelSize, relativeStride, padding, dilation, name = netDef[layerNo-1]
        kernelSize = (kernelSize - 1) * dilation + 1
        prevBlobSize = layers[layerNo-1][2]
        corners = rectify([
            (0-padding+corners[0][0]*relativeStride, 0-padding+corners[0][1]*relativeStride), #left top corner
            (0-padding+kernelSize-1+corners[1][0]*relativeStride, 0-padding+corners[1][1]*relativeStride), #right top corner
            (0-padding+kernelSize-1+corners[2][0]*relativeStride, 0-padding+kernelSize-1+corners[2][1]*relativeStride), #right bottom corner
            (0-padding+corners[3][0]*relativeStride, 0-padding+kernelSize-1+corners[3][1]*relativeStride), #left bottom corner
            ], prevBlobSize)
        boxes.append({
            'name': layers[layerNo-1][-1],
            'receptiveField': layers[layerNo-1][0],
            'absoluteStride': layers[layerNo-1][1],
            'blobSize': layers[layerNo-1][2],
            'corners': corners
            })
        layerNo -= 1

    boxes.reverse() #reverse the order so that the data layer is at the smallest index
    return boxes, layers

def projectLayers(layersToProject=['conv4_3', 'pool6'], netDef=VGGDef, inputSize=300):
    '''first calculate the layer info. The only thing needed is blob size'''
    layers = calcRF(netDef, inputSize)
    '''put the layer informatin into a dictionary'''
    layerDict = {}
    for idx, layer in enumerate(layers):
        layerDict[layer[-1]] = layer+[idx]

    boxesByLayers = {}
    for l in layersToProject:
        receptiveField, absoluteStride, blobSize, name, idx = layerDict[l]
        boxes = []
        '''row-major order'''
        for y in xrange(blobSize):
            for x in xrange(blobSize):
                ret, _ = projectRF(idx, x, y, netDef=VGGDef,
                        inputSize=inputSize, layers=layers)
                corners = ret[0]['corners']
                xmin = corners[0][0]
                ymin = corners[0][1]
                xmax = corners[2][0]
                ymax = corners[2][1]
                boxes.append({'xmin':xmin, 'ymin':ymin, 'xmax':xmax, 'ymax':ymax})
        boxesByLayers[l] = boxes

    return boxesByLayers


def rectify(box, blobSize):
    return [tuple(min(blobSize-1, max(val, 0)) for val in point) for point in box]

if __name__ == '__main__':
    #for row in calcRF():
    #    print("layer {}, receptive field {}, absolute stride {}, output blob width {}".format(row[-1],row[0],row[1],row[2]))

    layerNo = -1
    x = 0
    y = 0
    boxes, layers = projectRF(layerNo, x, y, netDef=VGGDef)
    for idx, box in enumerate(boxes):
        print 'layer={} receptiveField={} absoluteStride={} blob={} corners={}'.format(box['name'], box['receptiveField'], box['absoluteStride'], box['blobSize'], box['corners'])
