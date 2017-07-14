# pyhyperscan

ctypes 对 hyperscan 的封装，支持最新版的 hyperscan(4.5.x)

## 使用方法

从 https://github.com/01org/hyperscan 获取最新的 hyperscan , 编译并安装

~~~
cd hyperscan
mkdir build
cd build
cmake .. -DBUILD_SHARED_LIBS=1
make install
~~~

使用示例见 `main`
