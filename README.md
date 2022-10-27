# ETL video-encoding

![alt text](arch/arch.jpg)
#### Start
```bash
make start
```

#### Stop
```bash
make stop
```

#### Deploy Flow
Изменить настроки ``flow`` можно тут ```deploy/video_encoding.yaml```
после чего необходимо выполнить команду.
```bash
make apply-deploy
```

#### Worker
```bash
make agent-start
```

#### Other
Другие команды можно посмотреть в Makefile