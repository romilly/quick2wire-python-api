def revision():
    try:
        with open('/proc/cpuinfo','r') as f:
            for line in f:
                if line.startswith('Revision'):
                    code = line.rstrip()[-4:]
                    if code in ['0002', '0003']:
                        return 1
                    elif code in ['0010', '0012']:
                        # Attempting to catch the A+/B+. Technically wrong number,
                        # but I don't know what to put considering they are rev 1
                        # with conflicts with the 1st rev B's...
                        return 3
                    else:
                        return 2
            else:
                return 0
    except:
        return 0
