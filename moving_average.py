#Perform moving average
#Hyomin Kim 7/10/2020
#Source: https://stackoverflow.com/questions/13728392/moving-average-or-running-mean


def moving_average(data, windowsize):

    cumsum, moving_aves = [0], []
    for i, x in enumerate(data, 1):
        cumsum.append(cumsum[i-1] + x)
        if i>=windowsize:
            moving_ave = (cumsum[i] - cumsum[i-windowsize])/windowsize
            moving_aves.append(moving_ave)
    
    return moving_aves
