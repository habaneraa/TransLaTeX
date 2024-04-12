# 用户指南

## 本工具能做什么，不能做什么

本工具用于：

- 根据你指定的语言，翻译 LaTeX 源码中的文本部分
- 自动处理 LaTeX 项目结构，生成一个新的 LaTeX 项目，保持文本以外的其他部分不变，以便于 LaTeX 编译或迁移到其他文档模版

本工具**并不能**：

- 直接翻译 PDF 文件
- 编译 LaTeX 源码或生成 PDF 文件

## 准备工作

第一，准备 LaTeX 编译环境，用于将翻译后的源码制成 PDF 文档。

- 推荐 [Overleaf](https://cn.overleaf.com/)，无需搭建本地环境
- 本地编译可使用 TeXLive

第二，如果你有特定的排版需求（例如提交外文翻译作业），可以寻求第三方 LaTeX 模版，例如 [BIThesis](https://github.com/BITNP/BIThesis/tree/main/templates/paper-translation)。

第三，准备大模型 API Key。

- 可直接使用 OpenAI 官方 API 调用 GPT 模型系列
- 如果没有条件，可以使用国内的 OpenAI API 代理服务，有时第三方代理的价格甚至更实惠
- 除 OpenAI 外，众多 LLM 服务商也都可使用，因为他们的 API 接口是和 OpenAI 兼容的。（例如 [DeepSeek 开放平台](https://platform.deepseek.com/)）
- 你需要确认以下内容并提供给 TransLaTeX
  - API 服务地址，应该类似于 `https://api.openai.com/v1`
  - 你的 API 密钥
  - 模型的上下文长度 (context length)，为了防止翻译工作超出模型 token 限制，chunk size 不得超过模型限制的一半

## 安装

如果你使用 [pipx](https://pipx.pypa.io/latest/)，只需以下一个命令即可自动安装，安装后可以直接在命令行启动。

```bash
pipx install git+https://github.com/habaneraa/TransLaTeX.git
trans-latex
```

如果不使用 pipx，那么请自行准备 Python 环境，可以采用如下方式：

首先用你喜欢的方式创建一个 Python 3.12 的环境，例如：

```bash
conda create -n translatex python>3.12
```

然后使用 pip 命令即可安装：

```bash
pip install git+https://github.com/habaneraa/TransLaTeX.git
```

## 使用

在环境内使用以下命令即可启动终端 UI

```bash
python -m trans_latex
```

请根据 UI 指引，设置翻译任务。由于大模型生成文本较慢，调用 API 通常会有数十秒等待，所以翻译整个项目可能需要几分钟时间。

翻译可能会产生一些 API 费用，本应用会给出相应估计。一组典型的数据：一篇英文文献包含 5000~10000 词，外加各种 LaTeX 源码，prompt 占用约 20k tokens，假设翻译生成部分也为 20k tokens，那么按照 OpenAI `gpt-3.5-turbo` 的计费方式，产生一篇翻译的 API 价格为 $(0.5+1.5) \times 0.02=0.04$ USD.

## 其他

项目刚刚完成开发，可能有较多 bug，欢迎 issue / pull request。若有疑问，可以在 [GitHub 讨论区](https://github.com/habaneraa/TransLaTeX/discussions) 发帖。如果后续发现讨论需求较多，再考虑建群。
