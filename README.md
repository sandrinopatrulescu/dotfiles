# dotfiles

# TO DO

## Fix assumings:
1. env TRASH in functions tot()

Written @ 2022-01-10 22:23

## Fix Dependencies between env, functions and alias 

Choose a new order or stick with this one : alias <- functions <- env ( <- means left depends on right)

functions depend on the following aliases:
fdate
grep
java
src
trash

how to fix function dependency on java:
create env var JAVA_HOME="... jdk-17.01"
and
replace in functions java and javac with $JAVA_HOME/java...

Fix assumings 

Written @ 2022-01-10 22:05


