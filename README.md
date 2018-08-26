# libhyperscan

Python ctypes 对 hyperscan 的封装，支持最新版的 hyperscan(4.5.x)

Simple Python ctypes warp for the Hyperscan project.

supported hyperscan version : 4.5.x

require: python 2.7 +

## Installation

Please install hyperscan first

Download latest hyperscan from https://github.com/01org/hyperscan and install

~~~
cd hyperscan
mkdir build
cd build
cmake .. -DBUILD_SHARED_LIBS=1
make install
~~~

## Example Usage

```
def test():
    lib = LibHyperScan()
    print lib.version()
    lib.compile('A*')
    lib.compile('BA*')
    lib.scan("BAAA")
    lib.compile("^ER.*")
    lib.scan("BAAA")
    lib.scan("ERROR, FUCK")
    lib.compile_multi(["ABC", "BAAA"], [123,456])
    lib.scan("BAAAAAAA")
```
