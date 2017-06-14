# Building Python 3.7.0a

## About
Tux 2.0 and greater has settled on Python 3.7.0a as the minimum version supported for all aspects of the project.  This
was done for a variety of reasons, but primarily due to outdated versions being distributed with various versions of
Linux.  The Python 3 documentation references at a minimum 3.6.1, and 3.7.0a was the latest version as of writing
(5/5/2017).  Note that this is the minimum version; all work should support 3.7.0a and greater.

All instruction are written for Debian unstable.  You may need to modify some paths to allow the build system to work on
a different distribution.


## Installing and Building
Begin by cloning the Python GitHub repository:
```
git clone https://github.com/python/cpython.git
cd cpython
```

You will need to install a number of dependencies or the build will very, and it is very time consuming:
```
sudo apt-get update
sudo apt-get dist-upgrade
sudo apt-get install zlib1g zlib1g-dev build-essential libncursesw5-dev libgdbm-dev libc6-dev libssl-dev openssl libffi-dev
```

Next you will need to set the configuration options.  We do not want to replace the existing system installed version of
Python 3, so we will specify an alternative installation directory; you may need to modify this directory for your
system.

```
./configure --enable-optimizations --prefix=/usr/local/bin/python_latest --program-suffix=-3.7.0a
```

Now we build the source with the applied configuration.  This will take some time to complete:
```
make -j`nproc`
```

Finally we will install the new packages.  Note this will re-run the tests from above:
```
sudo make altinstall -j`nproc`
```


## Verification
To verify the new interpreter works as expected, run the following command.  You should get output similar to below:
```
x@lunar:~$ /usr/local/bin/python_latest/bin/python3.7 --version
Python 3.7.0a0

```

## Setting up the module path
By default, the new Python version will not be able to see modules and packages from the existing Python 3 installation.
We will add them to the search path.  First, open up the system version of Python 3 and type the following:
```
x@lunar:~/p/tmp$ python3

>>> import sys
>>> print("%s" % sys.path)
['', '/usr/lib/python3.4', '/usr/lib/python3.4/plat-arm-linux-gnueabihf', '/usr/lib/python3.4/lib-dynload', '/usr/local/lib/python3.4/dist-packages', '/usr/lib/python3/dist-packages']
>>> 
```

Here we are interested in the last two paths, but you can add them all if you want.  Exit out of the system version of
Python 3 and add the following to your `.bashrc` file:
```
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.4/dist-packages:/usr/lib/python3/dist-packages
```

Then re-source your `.bashrc` file and check to make sure the paths were added:
```
x@lunar:~/p/tmp$ . ~/.bashrc 
x@lunar:~/p/tmp$ p37
Python 3.7.0a0 (heads/master:23ec4b5, Jun 14 2017, 18:26:33) 
[GCC 4.9.2] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> print("%s" % sys.path)
['', '/home/x/p/tmp', '/usr/local/lib/python3.4/dist-packages', '/usr/lib/python3/dist-packages', '/usr/local/bin/python_latest/lib/python37.zip', '/usr/local/bin/python_latest/lib/python3.7', '/usr/local/bin/python_latest/lib/python3.7/lib-dynload', '/home/x/.local/lib/python3.7/site-packages', '/usr/local/bin/python_latest/lib/python3.7/site-packages']
>>> import gpiozero
>>> 
x@lunar:~/p/tmp$ 
```

## (Optional) Adding to .bashrc
We will want to provide an alias so we can use the new interpreter without specifying the entire path every time.  To do
this, we add an entry to our `.bashrc`:
```
alias p37="/usr/local/bin/python_latest/bin/python3.7"
```

Finally, re-source your `.bashrc` in any open terminal windows, or restart them for it to take effect:
```
. ~/.bashrc
```

You can test with the following command:
```
x@lunar:~$ p37 --version
Python 3.7.0a0
```

