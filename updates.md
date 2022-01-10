Notes:
-leave 3 lines between dates



### 2022-01-10

### 02:28
#### alias
* add `gs` and `gl` for `git status` and `git log`


### 20:18
#### functions
* chose a way to have them categorized: `### category name ###`

### 20:22
### alias
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
