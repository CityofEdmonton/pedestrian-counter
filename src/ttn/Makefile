CFLAGS=-g -I../../lmic
LDFLAGS=-lwiringPi

thethingsnetwork-send-v1: thethingsnetwork-send-v1.cpp
	cd ../../lmic && $(MAKE)
#	$(CC) $(CFLAGS) -fPIC -c thethingsnetwork-send-v1.cpp
#	$(CC) -shared -Wl,-soname,lora-ttn.so -o lora-ttn.so thethingsnetwork-send-v1.o ../../lmic/*.o $(LDFLAGS)
	$(CC) $(CFLAGS) -o thethingsnetwork-send-v1 thethingsnetwork-send-v1.cpp ../../lmic/*.o $(LDFLAGS)



all: thethingsnetwork-send-v1

.PHONY: clean

clean:
#	rm -f *.o thethingsnetwork-send-v1.o
	rm -f *.o thethingsnetwork-send-v1
