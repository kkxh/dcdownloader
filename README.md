# DCDownloader

![python](https://img.shields.io/badge/python-3.11%2B-green.svg)
[![GitHub license](https://img.shields.io/github/license/dev-techmoe/python-dcdownloader.svg)](https://github.com/dev-techmoe/python-dcdownloader/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/dev-techmoe/python-dcdownloader.svg)](https://github.com/dev-techmoe/python-dcdownloader/stargazers)

> 维护状态：这是从 `dev-techmoe/python-dcdownloader` 继续开发的新项目起点。原项目采用 MIT License，并已于 2022-11-09 归档为只读；本仓库保留原始许可与作者署名，在此基础上继续做兼容性修复、依赖升级和 Parser 扩展。

面向指定图片内容站点的可适配爬取框架，用 Parser 快速提取图片并整理成册。

## 新维护计划

当前首要目标不是立刻扩大站点支持，而是先恢复项目的可维护性：

* 保留原有命令行入口 `dcdownloader` 和 Parser 机制，避免破坏已有用户脚本。
* 升级到现代 Python 版本与依赖栈，替换已经过时的 `aiohttp` 调用方式。
* 建立可重复运行的测试与 CI，再逐步打磨 Parser 适配接口。
* 明确爬取边界，优先支持用户指定站点的合规、低压力抓取与成册整理。

详细路线见 [ROADMAP.md](ROADMAP.md)。

## 本地开发

建议使用 Python 3.11 或 3.12 创建虚拟环境：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest
```

当前测试以 `SimpleParser` 和本地 Flask 测试服务器为稳定契约，真实站点 Parser 需要按目标网站单独适配和复核。
Parser 适配流程见 [docs/parser-adapter-guide.md](docs/parser-adapter-guide.md)。

## 说明
DCDownloader 现在的目标是作为一个轻量、异步、可快速适配的图片抓取与成册整理框架。使用者为目标网站编写 Parser，框架负责请求、并发控制、图片下载和目录整理。
目前项目中内置的 Parser 包括：

* SimpleParser  一个Parser的例子，希望自己编写Parser的话可以参考这个的实现，同时也应用于单元测试过程中。
* EhentaiParser  旧有示例 Parser，后续需要按当前站点情况重新复核。

## 安装
### Windows 
[exe可执行文件下载](https://github.com/dev-techmoe/python-dcdownloader/releases)  

### Linux/OSX  
请确认您本机已安装 python 和 pip，建议使用 Python 3.11 或 3.12。
```bash
$ pip3 install https://github.com/dev-techmoe/python-dcdownloader/archive/master.zip
$ dcdownloader -h
```

## 可用命令
```
usage: dcdownloader [-h] [--proxy PROXY] [--no-verify-ssl] [-v] [-V] [--fetch-only]
               URL [OUTPUT_PATH]

positional arguments:
  URL              target URL
  OUTPUT_PATH      output path of downloaded file (default: current directory)

optional arguments:
  -h, --help       show this help message and exit
  --proxy PROXY    HTTP proxy address for connection
  --no-verify-ssl  Disable the SSL certificate verifying when connecting
  -v, --version    show version
  -V, --verbose    show more running detail
  --fetch-only     Ignore all download process (only fetch chapter and image urls)

```

## 免责声明
这个项目更多的其实是作为作者个人的练习项目存在，方便使用只是其二。为了不对目标站造成困扰，默认并发数应保持在温和范围内。由于使用者自身使用所造成的问题作者不付任何责任，同时作者不对任何下载内容承担任何责任。

## 贡献
本项目欢迎提交 PR。你可以帮助改进 Parser 接口、下载调度、成册整理和指定网站适配，但请确保适配行为符合目标网站规则与相关法律要求。

## License
MIT
