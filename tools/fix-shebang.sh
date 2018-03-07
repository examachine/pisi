#!/bin/sh

# try to avoid changing files under .git directories

#grep -rli --exclude '*.git*' '#!/usr/bin/python' .  | \
#xargs -I {} gsed -i '' -e 's/#!\/usr\/bin\/python/#!\/usr\/bin\/env python/' {}

greptile -x .py -l -i -g '#!/usr/bin/env python' -r '#!/usr/bin/python' .

