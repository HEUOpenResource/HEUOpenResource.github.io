# 贡献指南

## 概览


- 资源列表下载页 位于 `docs/resource` 目录中进行开发维护,完整内容由项目根目录的三个py脚本生成。
- 功能页面/博客  (~~暂时~~)位于 `docs/blog` 目录中进行开发维护,可以引入自定义组件，参考下面。


## 开发配置

开发要求（仅供参考）：

[![Node.js](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/HEUOpenResource/HEUOpenResource.github.io/main/package.json&query=$.engines.node&label=Node.js&color=339933&logo=node.js)](https://nodejs.org/)
[![npm](https://img.shields.io/badge/npm%20%3E%3D%2011.7.0-CB3837?logo=npm)](https://www.npmjs.com/)

>nodejs的安装教程自行搜索

克隆代码仓库

```sh
git clone https://github.com/HEUOpenResource/HEUOpenResource.github.io.git
```

安装依赖：

```sh
npm i
```

由于前端课程资料页的科目导航列是调用Github API读取[资源仓库](https://github.com/HEUOpenResource/heu-icicles)来获取的，所以无论是在本地调试还是构建的时候都会调用这个 Github的API，为了避免速率限制，建议先去[申请](https://github.com/settings/tokens)一个Github的Token，并且在项目根目录新建一个`.env`文件,你可以这样：

```sh
cp  .env.example .env
```
然后把你的token填进去，最后得到的`.env`文件长这样式儿：

```sh
GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```


### 本地调试

可以直接执行

```sh
npm run docs:dev
```
### 生成网页

构建源代码需要执行：

```sh
npm run docs:build
```

### 【本地】完整预览或构建网页

> 首先得安装python，最新的版本应该就行（仓库自动化构建时使用的3.13版本），详细安装教程自行搜索

此时需要拉取完整的资源仓库文件列表、贡献者，然后生成对应的markdown到对应的文件夹中，此时我们就需要像本仓库的workflow文件那样运行python脚本了：

```yml
      # 如果 update.py 依赖第三方库，取消注释此步
      - name: 📦 安装 Python 依赖
        run: pip install -r requirements.txt

      # 执行项目根目录的 update.py
      - name: 🛠️ 更新资料表以及正常贡献者
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python update.py

      # 执行项目根目录的 addContributors.py（细分到每一个科目） 、allContributors.py（“介绍”页面中显示）
      - name: 👥 添加非Github贡献者
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python addContributors.py
          python allContributors.py
```

可以看到，当执行python脚本的时候也需要环境变量中含有GITHUB_TOKEN，为了方便开发调试，我们引入了python包：`python-dotenv`,在执行py脚本的时候也会自动读取项目根目录的.env文件中的环境变量，这和上面配置的.env是一样的，只需要配置一次即可。

所以在执行py脚本之前不要忘了安装这个包，只需要执行：

```sh
pip install -r requirements.txt
```

然后执行脚本：

```sh
python update.py
python addContributors.py
python allContributors.py
```

执行完这些python脚本之后，再次本地调试或者预览即可。

### 【在线】调试

这个在线环境免登录即可查看
[https://stackblitz.com/github/HEUOpenResource/HEUOpenResource.github.io](https://stackblitz.com/github/HEUOpenResource/HEUOpenResource.github.io)
但是有时候不太方便，建议还是将代码拉取到本地进行调试


