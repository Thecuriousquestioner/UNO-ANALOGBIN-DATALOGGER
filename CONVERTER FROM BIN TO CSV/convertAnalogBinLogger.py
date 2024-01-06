from datetime import datetime
import struct
import sys
import os

if (len(sys.argv) < 2):
  print("Please provide a file to convert: ex. python convert.py inputfilename.bin")
  sys.exit(1)

inputfile = sys.argv[1]

if not inputfile or not os.path.exists(inputfile):
  print("Please provide a file to convert: python convert.py inputfilename.bin")
  sys.exit(1)

if inputfile.endswith(".bin") or inputfile.endswith(".BIN"): 
  outfile = inputfile[:-4] + ".csv"
else:
  outfile = inputfile + ".csv"

print("Writing to ", outfile)

out = open(outfile, 'w') 

metadata_fmt = '=128L'
metadata_len = struct.calcsize(metadata_fmt)
metadata_unpack = struct.Struct(metadata_fmt).unpack_from

block8_fmt = '=2h508c'
block16_fmt = '=256h'

with open(inputfile, "rb") as f:
    #out.write('DateTime,')
    #out.write(f.readline().decode("utf-8"))
    count = 0;


    metadata = metadata_unpack(f.read(metadata_len))

    adcFreq = metadata[0]
    cpuFreq = metadata[1]
    sampleInterval = metadata[2]
    recordEightBits = metadata[3]
    timestamp = metadata[4]

    pinCountIdx = 5; 
    pinCount = metadata[pinCountIdx]

    print('adcFreq:', adcFreq, ' cpuFreq:', cpuFreq, ' sampleInterval:', sampleInterval, ' recordEightBits:', recordEightBits ,' timestamp:', timestamp,' pinCount:', pinCount)

    if recordEightBits == 0:
      numOfBits = 10
    else:
      numOfBits = 8
    out.write("Interval,%0.2fus,RTC,%s,adcFreq,%d,cpuFreq,%d,sampleRate,%d,numOfBits,%d,pinCount,%d\n" % (1000000 * sampleInterval / cpuFreq, datetime.fromtimestamp(timestamp), adcFreq, cpuFreq,cpuFreq / sampleInterval, numOfBits, pinCount))
    for i in range(pinCount):
      if i:
        out.write(",")
      out.write("A%d" % metadata[pinCountIdx + i + 1])
    out.write("\n")
    if recordEightBits:
      print('Recording 8 bits');
      block_fmt = block8_fmt
    else:
      block_fmt = block16_fmt

    block_len = struct.calcsize(block_fmt)
    block_unpack = struct.Struct(block_fmt).unpack_from
    
    while True:
        data = f.read(block_len)
        if not data: break
        s = block_unpack(data)
        #print('Count ', s[0], ',', 'Overrun ',s[1])
        for i in range(int(s[0]/pinCount)): 
          for j in range(pinCount):
            if j:
              out.write(',')
            out.write('%d' % s[2 + (i * pinCount) + j])
          out.write('\n')
        count = count + 1
        #print('.', end='')
        if count % 100 == 0:
          sys.stdout.flush()


print('Enjoy your data!')

out.close() 
  
