# !/bin/bash
 #杀死相应的进程

kill_process(){
	PROCESS=`ps -ef|grep 'python app.py'|grep -v grep|grep -v PPID|awk '{ print $2}'`
	for i in "$PROCESS"
	do
	  echo "Kill the $1 process [ $i ]"
	  kill -9 $i
	done
}

start_process(){
	cd '/data/app/finance'
	python app.py &
}

# 开启程序
if [[ 'start' == $1 ]]
then
	echo "finance starting..."
	
	kill_process
	start_process
fi

# 关闭程序
if [[ 'stop' == $1 ]]
then
	echo "finance stop..."
	kill_process
fi




