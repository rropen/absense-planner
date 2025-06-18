SHELL = /bin/sh

ifeq ($(OS), Windows_NT)
all: windows
else
all: unix
endif

windows:
	.\setup.bat

unix:
	./setup.sh