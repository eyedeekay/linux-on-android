## Main Debian repository ##
We use testing/squeeze. Before I tried lenny, but touchscreen driver didn't work.

## Touchscreen driver for Xorg ##
xserver-xorg-input-tslib 0.0.6-4 (from squeeze). The driver from lenny had some positioning problems.

## Matchbox WM ##
I compiled matchbox-window-manager-2-simple from the matchbox repository. This [patch here](http://www.mail-archive.com/debian-bugs-closed@lists.debian.org/msg236404.html) helped to build libmatchbox

## lxpanel ##
lxpanel 0.5.5-2 (from sid). The version from squeeze did not always load the menu giving error "unable to connect to menu-cached" in .xsession-errors. They use different versions of libmenu-cache: libmenu-cache0 and libmenu-cache1