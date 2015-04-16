def get_jobname(line):
    if line.find("//") == 0:
        term = line.find(" JOB")
        if term > 2:
            jobname = line[2:term]
            return (True, jobname)
    return (False, None)

def is_distribute(line):
    print "distribute line is ", line
    if line.find("DIST") == 0:
        parts = line.split(" ")
        if parts[1] == "MAIL":
            return (True, 0)
        if parts[1] == "FILE":
            return (True, 1)
        return (False, None)

def is_add(line):
    parts = line.split(" ")
    if line.find("ADD ") == 0 and len(parts) == 5 and parts[2].find("@") > 0:
            return (True, [parts[1], parts[2], parts[3],parts[4].strip()])
    return (False, None)

def is_addr(line):
    if line.find("@") > 0:
        return (True, line.strip())
    return (False, None)

def is_review(line):
    if line.find("REV") > -1:
        return (True, None)
    return (False,None)


