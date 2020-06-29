#!/bin/bash
cd $(dirname $0)
cd local_tool
if [ -f local_tool.py ]; then
python local_tool.py
fi
