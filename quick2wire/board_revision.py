"""
This function returns 2 for the 40 pin pin-out and 1 for 26 pin. Otherwise it returns 0
"""
def revision():
    pinout1 = ['0002','0003','0004','0005','0006','0007','0008','0009','000d','000e','000f','0011','0014']
    pinout2 = ['0012','0015','a01041','a21041','a22042','900092','900093','9000C1','a02082','a22082','a020d3']
    
    try:
        with open('/proc/cpuinfo','r') as f:
            for line in f:
                if line.startswith('Revision'):
                    if line.rstrip()[-4:] in pinout1:
                        return 1
                    elif line.rstrip()[-4:] in pinout2:
                        return 2
                    elif line.rstrip()[-6:] in pinout2:
                        return 2
                    else:
                        return 0
            else:
                return 0
    except:
        return 0

"""
These have i2c-0 as default
Pi 1 Model B Rev 1                0002
Pi 1 Model B Rev 1 ECN0001        0003
Pi 1 Model B Rev 2                0004, 0005, 0006
Pi 1 Model A                      0007, 0008, 0009
Pi 1 Model B Rev 2                000d, 000e, 000f
Pi 1 Compute Module               0011, 0014

These have i2c-1 as default
Pi 1 Model A+                     0012, 0015
Pi 2 Model B V1.1                 a01041, a21041
Pi 2 Model B V1.2                 a22042
Pi Zero V1.2                      900092
Pi Zero V1.3                      900093
Pi Zero W                         9000C1
Pi 3 Model B                      a02082, a22082
Pi 3 Model B+                     a020d3
"""
