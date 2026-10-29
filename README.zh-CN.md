# 能源资料多智能体审阅项目

项目地址：https://github.com/SSCG3/energy-evidence-review

在一个仓库中提供可运行程序、对照测试、英文技术报告和实际截图。项目由周佺喜组织，代码和文档含AI辅助工作，应结合实际提交记录理解贡献。

## 启动

```sh
python3 server.py
```

在noVNC浏览器打开 http://127.0.0.1:8765 。核心功能无需第三方依赖；PDF文字层导入另安装 `requirements-pdf.txt`。

## 协作流程

规划 → 检索 → 提取 → 冲突/版本仲裁 → 来源核对 → 报告，每一步都有实际JSON交接。离线角色采用确定性规则。可选模型流程为DeepSeek分析、GLM复核、DeepSeek报告，只允许国产DeepSeek/GLM模型；密钥在服务器环境中设置，示例见英文README。

## 资料与测试

- 合成储能站、光储园区资料，用于检验冲突、单位、权限及版本关系。
- 美国EIA真实公开数据：2024年加州、纽约州、德州，保留原始JSON、CSV、来源、下载时间和SHA256。
- 40道合成开发题：首条检索28/40、全量检索36/40、协作核对40/40。
- 12项公开数据一致性检查：三种方式均12/12，不夸大改进。
- 模型真实调用状态及用量见 `results/model-validation.json`，单元测试中的模型替身不算真实模型结果。

```sh
python3 -m unittest discover -s tests -v
python3 evaluation/run_comparison.py
python3 evaluation/run_public_data.py
```

参考标签只用于评分，不输入被测程序。当前样例是开发者选取的小规模开发测试，不是独立隐藏测试，更不代表真实能源生产性能。

## 文件

英文10页报告：`docs/technical-report.pdf`；书稿对应及金石元素：`docs/book-method-mapping.md`；截图：`docs/screenshots/`；外部复现方法：`CONTRIBUTING.md`。

可上传PDF/TXT/MD或替换JSON，查看原文、冲突、摘要和过程导出。当前只支持文档中明确列出的字段表达，不是通用事实验证；本地角色切换是演示，不是实际登录权限。没有复制金石源码、内部资料或书稿PDF，没有声称取得外部采用或雇主授权。
