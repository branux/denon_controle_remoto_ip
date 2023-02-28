REMOTO_PY = remoto.py
REMOTO = remoto

INSTALL = install
PREFIX = /usr/local/bin

.NOTPARALLEL:

.PHONY: all
all:

.PHONY: install
install:
	$(INSTALL) -Dm 0755 $(REMOTO_PY) $(DESTDIR)$(PREFIX)/$(REMOTO)

.PHONY: uninstall
uninstall:
	$(RM) $(DESTDIR)$(PREFIX)/$(REMOTO)

.PHONY: clean
clean:

