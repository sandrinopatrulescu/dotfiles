


is_internet_working() { # Function to check if internet is working
    # https://www.google.com/search?q=ping+google.com+hangs -> https://superuser.com/questions/675744/why-does-ping-to-google-com-or-8-8-8-8-fails
    nc -w 3 -z google.com 80 >/dev/null 2>&1
}


repeat() { # repeat something N times: re <NR> <COMMAND...>
#    for ((i = 1; i <= $1; i++)); do "${@:2}"; done
     for _ in $(seq 1 "$1"); do "${@:2}"; done
}