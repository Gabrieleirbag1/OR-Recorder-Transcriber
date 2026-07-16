#!bin/bash

##############################################################################################################################################################
# This script has to be run in the root directory of the project.
# This script sets up the Sphinx documentation for a Python project.
# It creates a docs directory, sets up the Sphinx configuration, and generates the documentation.
# The script assumes that the project directory contains Python files that need to be documented.
# The script uses the sphinx-quickstart command to set up the Sphinx configuration.
# The script uses the sphinx.ext.autodoc, sphinx.ext.napoleon, and sphinx.ext.viewcode extensions.
# The script uses the sphinx_rtd_theme for the HTML theme.
# The script generates the documentation in HTML format.
# The script adds a modules.rst file to the docs directory that includes the documentation for all Python modules in the project.
# The script updates index.rst file to the docs directory that includes links to the modules.rst file and the genindex, modindex, and search indices.
# The script assumes that the project directory is a Python package and that the Python files in the project directory are modules that need to be documented.

# This is an example of the directory structure of the project:
# .
# ├── docs/
# ├── src/
# │   ├── main.py
# │   ├── utils.py
# │   └── ...
# └── sphinx_doc_setup.sh
##############################################################################################################################################################

function sphinx_make () {
    cd docs
    make html
}

function sphinx_index () {
    index_file="$PWD/docs/index.rst"
    echo "" >> "$index_file"
    echo "   modules" >> "$index_file"
    echo "" >> "$index_file"
    echo "Indices and tables" >> "$index_file"
    echo "==================" >> "$index_file"
    echo "" >> "$index_file"
    echo "* :ref:\`genindex\`" >> "$index_file"
    echo "* :ref:\`modindex\`" >> "$index_file"
    echo "* :ref:\`search\`" >> "$index_file"
}

function sphinx_modules (){
    modules_file="$PWD/docs/modules.rst"
    touch "$modules_file"

    echo "Modules" > "$modules_file"
    echo "=========" >> "$modules_file"
    echo "" >> "$modules_file"
    echo ".. toctree::" >> "$modules_file"
    echo "   :maxdepth: 2" >> "$modules_file"
    echo "   :caption: Contents:" >> "$modules_file"
    echo "" >> "$modules_file"

    for file in "$project_path"/*.py; do
        module_name=$(basename "$file" .py)
        echo ".. automodule:: $module_name" >> "$modules_file"
        echo "   :members:" >> "$modules_file"
        echo "   :undoc-members:" >> "$modules_file"
        echo "   :show-inheritance:" >> "$modules_file"
        echo "" >> "$modules_file"
    done
}

function sphinx_config () {
    conf_file="$PWD/docs/conf.py"

    insert_line="sys.path.insert(0, os.path.abspath('$relative_path'))"
    if ! grep -qxF "$insert_line" "$conf_file"; then
        sed -i "1 i $insert_line" "$conf_file"
    fi

    if ! grep -qxF 'import sys' "$conf_file"; then
        sed -i "1 i import sys" "$conf_file"
    fi

    if ! grep -qxF 'import os' "$conf_file"; then
        sed -i "1 i import os" "$conf_file"
    fi

    if grep -q '^extensions' "$conf_file"; then
        sed -i "s|^extensions.*|extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx.ext.viewcode']|" "$conf_file"
    else
        echo "extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx.ext.viewcode']" >> "$conf_file"
    fi

    if grep -q '^html_theme' "$conf_file"; then
        sed -i "s|^html_theme.*|html_theme = 'sphinx_rtd_theme'|" "$conf_file"
    else
        echo "html_theme = 'sphinx_rtd_theme'" >> "$conf_file"
    fi
}

function sphinx_setup () {
    pip install sphinx sphinx-rtd-theme
    if [ -d docs ]; then
        read -p $'\e[1;31mDo you want to overwrite the existing docs directory? [y/n]: \e[0m' overwrite
        if [ "$overwrite" == "y" ]; then
            rm -rf docs
        else 
            echo -e "\e[1;31mKeeping the existing docs directory. Exiting...\e[0m"
            exit 1
        fi
    fi
    mkdir docs
    sphinx-quickstart docs
}
    
function set_project_relative_path() {
    if [[ "$project_path" != /* ]]; then
            project_path="$(realpath "$PWD/$project_path")"
        else
            project_path="$(realpath "$project_path")"
        fi

        if [ ! -d "$project_path" ]; then
            echo -e "\e[1;31mThe specified project directory does not exist. Exiting...\e[0m"
            exit 1
        fi

        abs_docs_path="$PWD/docs"

        relative_path="$(realpath --relative-to="$abs_docs_path" "$project_path")"
}

function sphinx_main() {
    read -p $'\e[1;36mEnter the path of the project directory: \e[0m' project_path
    set_project_relative_path
    sphinx_setup
    sphinx_config
    sphinx_modules
    sphinx_index
    sphinx_make
}

sphinx_main