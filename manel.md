## Manel

<pre>
[ 前端 Vue3 ]        
    ↓       
[ Django API 层 (REST API) ]                
        ↓           
[ Platform Logic / Service 层 (业务逻辑) ]                      
            ↓           
[ CloudDriver 抽象层 (这里才决定你用 K8s、OpenStack 还是模拟) ]         
                    ↓           
[ 真实云平台 (Kubernetes / OpenStack / Mock / Docker / 其他) ]
</pre>
