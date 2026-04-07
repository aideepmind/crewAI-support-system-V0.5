## 注意事项
yaml文件的格式

## 要使用python -m 执行，
否则有可能使用的是conda的python 环境，没有使用 .venv中定义的环境
后者 conda deactivate 关闭conda环境




source .venv/bin/activate
 which python
 pip list | grep fastapi
 echo $PYTHONPATH
 export PYTHONPATH="${PYTHONPATH}:$(pwd)/tests"
 python -c "from tests.chatservice import app; print('导入成功!')"
 ##uvicorn tests.chatservice:app --host 0.0.0.0 --port 8001 --reload

 ##启动环境
 . ./.env. 配置环境变量
python -m uvicorn src.support.service.chatservice:app --host 0.0.0.0 --port 8001 --reload


 生成class文档
 pdoc ./app/models/mylib.py -o docs/