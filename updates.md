Notes:
-leave 3 lines between dates


### 2022-02-02

### 15:44
#### alias
* add `restart1`


### 21:16
#### functions
* add `beep()`

### 2022-01-13

### 12:25
#### functions
* modify `tot()` to display full path in `0.info`


### 16:59
#### functions
* add `sp2()` because arguments with spaces would not work using sp()


### 20:56
#### functions
* add `tt() [<nr of lines>]` to show trash log's tail



### 2022-01-11

### 00:01
#### alias
* add `functionsa` to sort alphabetically

### 00:03
#### functions
* rename `get()` to `getvar()`

### 13:34
#### functions
* rename `check_errors` to `err`
* `err()`: redirect message to STDOUT

### 13:58
#### functions
* `tot()` made variables local

### 15:49
#### functions
* add `how()`

### 17:50
#### env
* add `JAVAFX_ARGS` to compile JavaFX applications


### 18:34
#### functions
* add `jfxr()` to rcompile and run JavaFX applications



### 00:05
#### functions
* add Notes

### 01:20
#### functions
* add skeletion for `jfxr` to compile & run JavaFX programs in 1 command



### 2022-01-10

### 02:28
#### alias
* add `gs` and `gl` for `git status` and `git log`


### 20:18
#### functions
* chose a way to have them categorized: `### category name ###`

### 20:22
#### alias
* add `fcats` to show function categories

### 20:24
#### alias
* add line numbers for `fcats`

### 20:44
#### alias
* add `lrt` and `lrth`
* very small organization

### 20:56
#### alias
* add `-T` option to grep for `fcats`
* add `acats` for listing categories in the `alias` file

### 21:41
#### env
* add `TRASH=/mnt/e/trash`

### 23:10
#### functions
* add `tot` aka totrash, used for moving files to trash
* make use of `check_errors`


### 23:43
#### alias
* modify `functions` to show line numbers with alignment 


### 23:55
#### functions & bin/ccc
* copied function `ccc()` to `bin/ccc` and commented it out



### 2022-01-09

### 00:31
#### functions
* add cd functions that wraps the builtin cd and changes xfce tab title

### 03:41
#### alias
* add `untar` to extract .tar.gz files

###  17:23
#### env
* add `shopt -s glostar` to find files and dirs recursively using ls ./\*\*/
\*.ext



### 2022-01-08

### 22:26
#### alias
* add javafxc and javafx



### 2022-01-05

### 21:57
#### functions
* fix `append-path` interpreting argument literally because of double quotes


#### 21:28
#### functions 
* modify `apppend-path` to test if directory exists and use it in `env`



#### 21:05
#### env
* add lvim to `PATH`



#### 20:44
#### install.conf.yaml
* remove the comment for commit message related to adding the bin folder





#### 20:26
#### general
* add `updates.md`

#### bashrc
* add comment for the `nvm` stuff

#### env
* fix `~/dotfiles/bin` being added multiple times to `PATH`
* add `nvm`'s stuff which was initially added to `bashrc` to a new category called `Software Related`

#### functions  
* fix `append-path()`not using `export PATH`
