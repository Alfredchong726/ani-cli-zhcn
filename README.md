# ani-cli-zhcn

这个repo是基于[ani-cli](https://github.com/pystardust/ani-cli)的，但是这个repo所找到的动漫是中文字幕的。

所有动漫来源都源自 https://www.agedm.org/

- [ani-cli-zhcn](#ani-cli-zhcn)
    - [下载](#下载)
    - [使用](#使用)
    - [打包](#打包)


### 下载
目前的下载方法只支持安装源代码
```bash
git clone git@github.com:Alfredchong726/ani-cli-zhcn.git
cd ani-cli-zhcn
source venv/bin/activate
pip install requirements.txt
```

### 使用
```bash
./ani-cli-zhcn 番名
```

### 打包
如果你下载了源代码并且修改了源代码，那么可以重新将源代码打包成程序，打包程序之前要确定已经下载了pyinstaller,当然，你也可以使用cx_freeze
```bash
pip install pyinstaller
pyinstaller --onefile ani-cli-zhcn.py
sudo mv dist/ani-cli-zhcn /usr/bin/
```
