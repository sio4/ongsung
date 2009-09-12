#
# main makefile for ongsung-tunnel.
#


BINS		= tunneld
LIBRARIES	= libtelnet

CC		= gcc
CFLAGS		= -g -O2 -Wall -Ilibtelnet
LDFLAGS		= -ltelnet -Llibtelnet/.libs



all: $(BINS)


libtelnet/.libs/libtelnet.so: libtelnet/.libs/libtelnet.a

libtelnet/.libs/libtelnet.a:
	cd libtelnet; ./configure --prefix=/opt/ongsung
	make -C libtelnet



.c.o:
	$(CC) -c $(CFLAGS) -o $@ $<



tunneld: tunneld.o libtelnet/.libs/libtelnet.so
	$(CC) $(LDFLAGS) -o $@ $<



clean:
	-make clean -C libtelnet
	-rm -f *.o

distclean:
	-make distclean -C libtelnet
	-rm -f *.o $(BINS)
