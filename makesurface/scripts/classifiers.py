def jenksMatrices(data, nClasses):
    lowerClassLimits = np.zeros((len(data) + 1, nClasses + 1))
    varianceCombinations = np.zeros((len(data) + 1, nClasses + 1))
    variance = 0
    
    lowerClassLimits[1][1:-1] = 1
    varianceCombinations[2:-1][1:-1] = np.inf
        
    for l in range(2, len(data) + 1):
        tSum = 0
        sumSquares = 0
        w = 0
        i4 = 0
        
        for m in range(1, l + 1):
            lowerClassLimit = l - m + 1
            val = data[lowerClassLimit - 1]
            w += 1
            tSum += 1
            sumSquares += val * val
            variance = sumSquares - (tSum * tSum) / w
            
            i4 = lowerClassLimit - 1
            
            if i4 != 0:
                for j in range(2, nClasses):
                    if varianceCombinations[l][j] >= (variance + varianceCombinations[i4][j - 1]):
                        lowerClassLimits[l][j] = lowerClassLimit
                        varianceCombinations[l][j] = variance + varianceCombinations[i4][j - 1]
        
        lowerClassLimits[l][1] = 1
        varianceCombinations[l][1] = variance
        
    return {
            'lowerClassLimits': lowerClassLimits,
            'varianceCombinations': varianceCombinations
            }
def jenksBreaks(data, lowerClassLimits, nClasses):
    k = len(data) - 1
    kClass = np.zeros(nClasses + 1)
    countNum = nClasses
    kClass[nClasses] = data[-1]
    kClass[0] = data[0]
    
    while countNum > 1:
        kClass[countNum - 1] = data[int(lowerClassLimits[int(k)][countNum] - 2)]
        k = lowerClassLimits[int(k)][countNum] - 1
        countNum -= 1
    
    return kClass

def jenks(data, nClasses):
    if nClasses > len(data):
        return null
    data = np.array(data)
    data.sort()
    
    matrices = jenksMatrices(data, nClasses)
    lowerClassLimits = matrices['lowerClassLimits']

    return jenksBreaks(data, lowerClassLimits, nClasses)