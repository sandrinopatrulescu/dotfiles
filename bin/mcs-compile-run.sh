#!/bin/bash

# compile and run a Windows Forms (.NET Framework) Program


references_dir="/mnt/e/Scratch/csharp/mono-manual-install-01/mono-6.12.0.122/external/binary-reference-assemblies/v4.8/"
bin_dir="/mnt/e/Scratch/csharp/mono-manual-install-01/mono-6.12.0.122/runtime/_tmpinst/bin/"
compiler="${bin_dir}/mcs"
run="${bin_dir}/mono"

if [ $# -lt 1 ]; then
    echo "You must enter the project directory"; exit 1
fi

project_dir="$1"
project_name="$(basename "$project_dir")"

source_files_dir="${project_dir}" # or "${project_dir}/src"
out_dir="${project_dir}/bin/Debug/"
out_file="${out_dir}/${project_name}.exe"

source_files="$(find "$source_files_dir" -iname "*.cs")"

# exit

reference_options=""
for lib in System.Data System.Windows.Forms System.Drawing; do
    reference_option="-r:${references_dir}/{$lib}"
    
    if [ "$reference_options" == "" ]; then
        reference_options="$reference_option"
    else
        reference_options="$reference_options $reference_option"
    fi
done


$compiler -out:"$out_file" $reference_options "$source_files" &&\ 
    (cd "$out_dir" && $run "$out_file")


