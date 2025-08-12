# zeek 二次开发
- zeek 已经做到了无文件控制台输出  

zeek 指令无文件控制台输出运行指令  
`zeek -i enp6s0 -C -B af_packet --pseudo-realtime LogAscii::use_json=T LogAscii::output_to_stdout=T`
- 参数解释
    - `-i <interface>` 指定监听网卡
    - `-C` 不进行校验和验证 (Checksum offload)
    - `-B af_packet` 加载 af_packet 插件，利用 zero-copy 抓包
    - `--pseudo-realtim` 让 zeek 接近实时速度处理离线流量


