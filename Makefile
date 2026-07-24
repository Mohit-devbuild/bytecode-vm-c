CC = gcc

CFLAGS = -Wall -Wextra -std=c99 -g

SRC = $(wildcard *.c)

TARGET = build/clox.exe

all:
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)