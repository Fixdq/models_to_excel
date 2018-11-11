### 描述：
- 脚本主要用于Django项目，将项目中的models的简要信息统计到Excel中。

###	使用说明：
1. 在项目根目录下运行,Excel文件输出在根目录下
``` bash
python read_django  
```
2. 指定项目的根目录路径，,Excel文件输出在根目录下
``` bash
python read_django  "D:\fixdq\model_read"
```
3. 指定项目的根目录路径，,指定Excel文件输出路径
``` bash
python read_django  "D:\fixdq\model_read" "C:\Users\fegnt\Desktop"
```
### 备注：
- 该脚本用于我自己的项目，如有需求，请根据自己项目的编码风格修改脚本内容。
- 欢迎技术交流