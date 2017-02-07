#!/bin/bash

rm -rf minime
mkdir minime
rm -f *.pisi 

pisi build comp/ab/pspec.xml -D./minime
pisi it ab-1.06-1.pisi -D./minime

pisi build comp/bc/pspec.xml -D./minime
pisi it bc-1.06-1.pisi -D./minime

pisi build comp/cd/pspec.xml -D./minime
pisi it cd-1.06-1.pisi -D./minime

for i in `seq 1 10`
do
    pisi it ab-1.06-1.pisi -D./minime --yes-all
done

for i in `seq 1 10`
do
    pisi remove cd -D./minime
    pisi it cd-1.06-1.pisi -D./minime
done

pisi build lang/de/pspec.xml -D./minime
pisi it de-1.06-1.pisi -D./minime

pisi build lang/ef/pspec.xml -D./minime
pisi it ef-1.06-1.pisi -D./minime

pisi rebuild-db -D./minime --yes-all

pisi remove ab -D./minime --yes-all

pisi li -D./minime
