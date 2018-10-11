IDIR = lmic
TDIR = ttn
ODIR = obj
CC = g++
CFLAGS = -I$(IDIR)
LDFLAGS = -lwiringPi

_DEPS = config.h hal.h lmic.h local_hal.hal lorabase.h oslmic.h
DEPs = $(patsubst %, $(IDIR)/%, $(_DEPS))

_OBJ = aes.o hal.o lmic.o oslmic.o radio.o
OBJ = $(patsubst %, $(ODIR)/%, $(_OBJ))

$(ODIR)/%.o: $(IDIR)/%.c $(DEPS) | $(ODIR)
	$(CC) -c -o $@ $< $(CFLAGS)

$(TDIR)/thethingsnetwork-send-v1: $(TDIR)/thethingsnetwork-send-v1.cpp $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LDFLAGS)

$(ODIR):
	mkdir -p $@

.PHONY: all clean

all: $(TDIR)/thethingsnetwork-send-v1

clean:
	rm -f $(ODIR)/*.o $(TDIR)/thethingsnetwork-send-v1