
def getsize(ballance_ratio):
    if ballance_ratio > 18:
        multiply_size = 1.5
    elif ballance_ratio > 15 and ballance_ratio <= 18:
        multiply_size = 1.4
    elif ballance_ratio > 12 and ballance_ratio <= 15:
        multiply_size = 1.3
    else:
        multiply_size = 1.2
    return multiply_size

getsize(19)