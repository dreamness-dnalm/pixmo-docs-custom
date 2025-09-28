# PIXMO-DOCS  
FORKED FROM (allenai/pixmo-docs)[https://github.com/allenai/pixmo-docs]  

## 变更  
* 移除模型判断功能, 所有模型均使用openai api  
* 输出数据集时, 默认同时输出jsonl和png. 添加--no-export禁用  
* 移除上传huggingface功能
* 移除对persona强制禁止中文的限制
* 添加--language参数, 可指定生成的语言, 默认英文


## 参数
* -p PIPELINE, --pipeline PIPELINE  
    指定使用的pipeline, 可选值有:  
    "PlotlyChartPipeline" (默认)
* -t TYPE, --type TYPE  
    指定生成的数据类型, 默认值: "bar chart"
* -n NUM_SAMPLES, --num_samples NUM_SAMPLES  
    指定生成的数据样本数, 默认值: 1
* --language LANGUAGE  
    指定生成的语言, 默认 值: "English"