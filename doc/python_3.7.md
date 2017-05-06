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

You will need to install the zlib1g library as well or the Python self-tests will fail:
```
sudo apt-get install zlib1g
```

Next you will need to set the configuration options.  We do not want to replace the existing system installed version of
Python 3, so we will specify an alternative installation directory; you may need to modify this directory for your
system.

```
./configure --enable-optimizations --prefix=/usr/local/python_latest --program-suffix=-3.7.0a
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
x@lunar:~$ /usr/local/python_latest/bin/python3.7 --version
Python 3.7.0a0

```


## (Optional) Adding to .bashrc
We will want to provide an alias so we can use the new interpreter without specifying the entire path every time.  To do
this, we add an entry to our `.bashrc`:
```
alias p37="/usr/local/python_latest/bin/python3.7"
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

