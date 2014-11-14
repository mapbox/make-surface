import numpy as np

def jenksMatrices(data, nClasses):
    # in the original implementation, these matrices are referred to
    # as `LC` and `OP`
    #
    # * lower_class_limits (LC): optimal lower class limits
    # * variance_combinations (OP): optimal variance combinations for all classes
    lowerClassLimits = np.zeros((len(data) + 1, nClasses + 1))
    varianceCombinations = np.zeros((len(data) + 1, nClasses + 1))

    # the variance, as computed at each step in the calculation
    variance = 0
    lowerClassLimits[1][1:-1] = 1

    # in the original implementation, 9999999 is used but
    # since numpy has np.inf, we use that
    varianceCombinations[2:-1][1:-1] = np.inf

    for l in range(2, len(data) + 1):
        # `SZ` originally. this is the sum of the values seen thus
        # far when calculating variance.
        tSum = 0
        // `ZSQ` originally. the sum of squares of values seen
                // thus far
        sumSquares = 0
        // `WT` originally. This is the number of
        w = 0
        // `IV` originally
        i4 = 0
        
        for m in range(1, l + 1):
            # `III` originally
            lowerClassLimit = l - m + 1
            val = data[lowerClassLimit - 1]

            # here we're estimating variance for each potential classing
            # of the data, for each potential number of classes. `w`
            # is the number of data points considered so far.
            w += 1

            # increase the current sum and sum-of-squares
            tSum += 1
            sumSquares += val ** 2

            # the variance at this point in the sequence is the difference
            # between the sum of squares and the total x 2, over the number
            # of samples.
            variance = sumSquares - (tSum * tSum) / w
            
            i4 = lowerClassLimit - 1
            
            if i4 != 0:
                for j in range(2, nClasses):
                    # if adding this element to an existing class
                    # will increase its variance beyond the limit, break
                    # the class at this point, setting the `lower_class_limit`
                    # at this point.
                    if varianceCombinations[l][j] >= (variance + varianceCombinations[i4][j - 1]):
                        lowerClassLimits[l][j] = lowerClassLimit
                        varianceCombinations[l][j] = variance + varianceCombinations[i4][j - 1]
        
        lowerClassLimits[l][1] = 1
        varianceCombinations[l][1] = variance

    # return the two matrices. for just providing breaks, only
    # `lower_class_limits` is needed, but variances can be useful to
    # evaluate goodness of fit.
    return {
            'lowerClassLimits': lowerClassLimits,
            'varianceCombinations': varianceCombinations
            }

def jenksBreaks(data, lowerClassLimits, nClasses):
    k = len(data) - 1
    kClass = np.zeros(nClasses + 1)
    countNum = nClasses

    # the calculation of classes will never include the upper and
    # lower bounds, so we need to explicitly set them
    kClass[nClasses] = data[-1]
    kClass[0] = data[0]
    
    while countNum > 1:
        kClass[countNum - 1] = data[int(lowerClassLimits[int(k)][countNum] - 2)]
        k = lowerClassLimits[int(k)][countNum] - 1
        countNum -= 1
    
    return kClass

# # [Jenks natural breaks optimization](http:#en.wikipedia.org/wiki/Jenks_natural_breaks_optimization)
#
# Implementations: [1](http:#danieljlewis.org/files/2010/06/Jenks.pdf) (python),
# [2](https:#github.com/vvoovv/djeo-jenks/blob/master/main.js) (buggy),
# [3](https:#github.com/simogeo/geostats/blob/master/lib/geostats.js#L407) (works)
#
# Depends on `jenksBreaks()` and `jenksMatrices()`
#
# Copied and modified from Tom MacWright's JS implementation in Simple Statistics (https://github.com/tmcw/simple-statistics)


def jenks(data, nClasses):
    if nClasses > len(data):
        return null
    data = np.array(data)
    data.sort()
    
    matrices = jenksMatrices(data, nClasses)
    lowerClassLimits = matrices['lowerClassLimits']

    return jenksBreaks(data, lowerClassLimits, nClasses)