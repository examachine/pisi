
find pisi -iname '*.py' | grep -v pisi/cli/commands.py >exclude
python tools/pygettext.py -D -X exclude -o po/pisi.pot pisi pisi-cli scripts
msgmerge -U po/tr.po po/pisi.pot
rm exclude
