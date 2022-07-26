NAME MIPmodel
ROWS
 N  COST
 L  LIM1
 G  LIM2
 E  MYEQN
COLUMNS
    XONE  COST       1
    XONE  LIM1       1
    XONE  LIM2       1
    YTWO     COST       4
    YTWO     LIM1       1
    YTWO     MYEQN       -1
    ZTHREE     COST       9
    ZTHREE     LIM2      1
    ZTHREE     MYEQN      1
RHS
    RHS1      LIM1  5
    RHS1      LIM2  10
    RHS1      MYEQN  7
BOUNDS
 UP BND1      XONE  4
 LO BND1      YTWO  -1
 UP BND1      YTWO  1
ENDATA
