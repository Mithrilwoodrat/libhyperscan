cat hs.h|grep '#define HS*' > defines
cat defines |awk -F' ' '{print $2 "=" $3}'
cat defines |awk '{printf("%d:\"%s\",\n", $3 ,$2)}'
