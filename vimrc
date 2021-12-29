"### Part 1: keybinds and others

nnoremap confe :e $MYVIMRC<CR> " Edit vimr configuration file [1]
nnoremap confr :source $MYVIMRC<CR> " Reload vims configuration file [1]
nnoremap <F2> :noh<CR> 
noremap <F3> :so $MYVIMRC<CR>
noremap <F4> :set number!<Bar>set number?<CR> "<-[7]   :set number!<CR>
noremap <F5> :set cursorline!<CR>
nnoremap <F6> :set invpaste paste?<CR> " [6]
set pastetoggle=<F6> " [6]

nnoremap ; :

noremap <Leader>x :w<CR>
nnoremap <Leader>t :sh<CR> " open shell, exit with Ctrl+D

noremap <Up> gk
noremap <Down> gj

"set compatible " enable option [2]
"set compatible! " append ! to toggle the option [2]
"set compatible? " find out whether is enabled [2]
"set compatible& " reset to default vim option [2]
set nocompatible " prepend 'no' to disable the option [2]


"### Part 2: options

" Colors
syntax enable " enable syntax processing [5]
colo default " line 
colo delek " line 

" Space & Tabs
set tabstop=4 " number of visual spaces per TAB [5]
set softtabstop=4 " number of spaces in tab when editing [5]
set expandtab " replace tab with spaces [5]
set tabstop=4 " regarding tab size [4]
set shiftwidth=4 " regarding tab size [4]
set smarttab " when deleting beginning whitespaces, delete 1 tab worth of spaces [4]

" UI Config
set ruler " display cursor's position [3]
"set cursorline " highlight current line [5]
filetype plugin indent on  " enable filetype plugins and indent (it uses 2 tabs) [2]
set wildmenu " visual autocomplete for command menu [5]
set lazyredraw " redraw only when we need to. [5]
set showmatch " show matching brackets [5]
"set titlestring=%t " set window tile to filename [3]
set showcmd " display the letters typed
let g:is_bash = 1 " :help ft-sh-syntax 

" Searching
set hlsearch " highlight all search mathes; disable with :noh [3]
noh " remove the hightlighting that appears after sourcing the config file while in vim
set incsearch " see the search result as you type [3]
set ignorecase " case-insensitive search [3]
set smartcase " lower -> insensitive; 1 upper -> sensitive [3]

" Folding
set autoindent " Enter => same indentation on the next line [3]

" Movement
nnoremap j gj " move vertically by visual line [5]
nnoremap k gk " move vertically by visual line [5]



"### Part 3: Sources List

"[1] https://www.cyberciti.biz/faq/how-to-reload-vimrc-file-without-restarting-vim-on-linux-unix/
"[2] https://www.barbarianmeetscoding.com/blog/exploring-vim-setting-up-your-vim-to-be-more-awesome-at-vim
"[3] https://linuxhint.com/important_vim_settings/
"[4] https://medium.com/swlh/setting-up-vim-940eaf179fc8
"[5] !!! https://dougblack.io/words/a-good-vimrc.html (see especially gundo, SilverSearcher and CtrlP)
"[6] https://vim.fandom.com/wiki/Toggle_auto-indenting_for_code_paste#Paste_toggle
"[7] https://vim.fandom.com/wiki/Best_Vim_Tips#More.2C_unformatted_tips

"### Part 4: Color List

"blue
"darkblue 2
"default 2
"delek 1
"desert 1
"elflord
"evening
"industry
"koehler
"morning
"murphy
"pablo
"peachpuff 2
"ron
"shine
"slate 3
"torte
"zellner


"### Part 5: To test

"set sm " show matching () or {}
"set ai " auto identention during text entry
"let java_highlight_all=1 " idk
"let java_highlight_functions="style" " vimdoc syntax: following java guidelines about class and function names
"let java_allow_cpp_keywords=1 "don't mark errors for porting with C++
"let java_highlight_java_lang_ids=1 " highlight java.lang.* identifiers
"set foldlevel=1 " lines indented a single tie should be shown
"set wm=10 " set wrap margin 10 spaces from right edge of the screen

