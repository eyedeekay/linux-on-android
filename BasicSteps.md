# Introduction #

We need 3 things:
  1. Linux kernel
  1. Linux distribution
  1. X system

## Linux kernel ##
First proposal is to start with the kernel which comes with the phone. We need also the sources. In my case, Samsung Galaxy i7500, I need `GT-I7500_OpenSource_Update4.zip` from http://opensource.samsungmobile.com/. Mirror [here](http://androidforums.com/samsung-i7500/62252-1-6-open-source.html#post602687). Although I actually took Galaxo, the version modified by drakaz http://github.com/drakaz/GalaxoKernel. I think they are not so much different.

Install Android SDK from Google, add it to PATH, download the source, and build it with (instructions from [here](http://www.receptorblog.com/wordpress/howto-compile-a-linux-kernel-for-samsung-galaxy/))
```
alias armmake='make ARCH=arm CROSS_COMPILE=arm-eabi-'
armmake capela_defconfig
armmake
```

Build modules with
```
armmake modules
mkdir modules-out
armmake INSTALL_MOD_PATH=modules-out modules_install
```

A note: the latest kernel from Update4 is 2.6.29. I had some bugs with wifi and decided to try 2.6.27 from Update3. There was some problem because Samsung files are in dos encoding. I had to fix them with `find . -type f -exec fromdos {} \;`

## Linux distribution ##
It is not clear which distribution to choose. The most universal is Debian, so we try it with Debian. These [instructions](http://www.saurik.com/id/10) helped me to get the idea. It was more convenient however to prepare the distribution first in the emulator and then copy to the real phone.

These commands give user 'user' permissions to use network. We add 'root' just in case.
```
groupadd -g 3003 inet
usermod -a -G inet root
usermod -a -G inet user
```

## X system ##
The X-server with xserver-xorg-video-fbdev and xserver-xorg-input-tslib almost works. In fact it is the screen which needs some fix. [This page](http://www.htc-linux.org/wiki/index.php?title=Dream) describes some hacks that work for HTC Dream. There are two points:

  1. Make double buffer into single buffer.
  1. Update the screen every xx milliseconds.

These are done by patching the kernel. Here is a patch for Galaxy. Apply with "patch -p 1"
```
diff --git a/drivers/video/msm/msm_fb.c b/drivers/video/msm/msm_fb.c
index 7a823f3..b2a94ae 100644
--- a/drivers/video/msm/msm_fb.c
+++ b/drivers/video/msm/msm_fb.c
@@ -204,6 +204,27 @@ int msm_fb_detect_client(const char *name)
 	return ret;
 }
 
+static int msmfb_refresh_thread(void *v)
+{
+       struct fb_info *info;
+       struct msm_fb_data_type * mfd;
+       
+       
+       daemonize("msmfb_refreshd");
+       allow_signal(SIGKILL);
+       
+       while (1) {
+               msleep(100);
+               
+               if (num_registered_fb > 0) {
+                       info = registered_fb[0];
+                       msm_fb_pan_display(&info->var, info);
+               }
+       }
+       
+       return 0;
+}
+
 static int msm_fb_probe(struct platform_device *pdev)
 {
 	struct msm_fb_data_type *mfd;
@@ -249,6 +270,7 @@ static int msm_fb_probe(struct platform_device *pdev)
 	if (rc)
 		return rc;
 
+    kernel_thread(msmfb_refresh_thread, NULL, CLONE_KERNEL);
 #ifdef CONFIG_FB_BACKLIGHT
 	msm_fb_config_backlight(mfd);
 #else
diff --git a/drivers/video/msm/panel/mddi/mddi_toshiba_smd.c b/drivers/video/msm/panel/mddi/mddi_toshiba_smd.c
index 7ff1c26..a00e68d 100644
--- a/drivers/video/msm/panel/mddi/mddi_toshiba_smd.c
+++ b/drivers/video/msm/panel/mddi/mddi_toshiba_smd.c
@@ -1711,7 +1711,8 @@ static int __init mddi_toshiba_lcd_smd_init(void)
     pinfo->clk_min =  120000000;
     pinfo->clk_max =  200000000;
 
-	pinfo->fb_num = 2;
+	//pinfo->fb_num = 2;
+	pinfo->fb_num = 1;
 	
 	ret = platform_device_register(&this_device);
 	if (ret)

```

/etc/X11/xorg.conf should look like this:
```
Section "InputDevice"
	Identifier	"Touchscreen"
	Driver		"tslib"
	Option		"Device"	"/dev/input/event2"
EndSection

Section "Device"
	Identifier	"Configured Video Device"
	Driver "fbdev"
	Option		"fbdev"		"/dev/graphics/fb0"
EndSection

Section "Monitor"
	Identifier	"Configured Monitor"
	Option		"DPMS"	"false"
EndSection

Section "Screen"
	Identifier	"Default Screen"
	Monitor		"Configured Monitor"
	Device          "Configured Video Device"
EndSection

Section "ServerLayout"
	Identifier	"Default"
	Screen		"Default Screen"
	InputDevice	"Touchscreen" "CorePointer"
EndSection

Section "ServerFlags"
	Option		"DefaultServerLayout"	"Default"
EndSection
```