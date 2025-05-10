#!/bin/bash

# 获取脚本所在目录作为项目根目录
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 添加项目根目录到PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT

# 执行调度器脚本
python $PROJECT_ROOT/scheduler/scheduler.py