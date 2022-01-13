# dotfiles

# TO DO
**Other To DOs @** ```Evernote/Tree/Useful```


Written @ 2022-01-13 21:13
## Add folding in all the files https://www.freecodecamp.org/news/vimrc-configuration-guide-customize-your-vim-editor/



## `templ` script to generate a runnable example in various programming languages
Written @ 2022-01-11 16:46


## function err() https://google.github.io/styleguide/shellguide.html#s3.1-stdout-vs-stderr
- learn about bash redirection
- learn about the difference between $@ and $\*

Written @ 2022-01-11 13:31




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


