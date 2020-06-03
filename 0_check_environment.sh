#!/bin/bash

CURRENT_DIR=$(dirname $0)

PYTHON_MAJOR_VERSION=3
PYTHON_MINOR_VERSION=6

TRUE=1
FALSE=0

VENV_PATH=$CURRENT_DIR/venv

VENV_PACKAGES=(
    BeautifulSoup4
    pdfminer
    numpy
    pandas
    matplotlib
    scikit-learn
    Pillow
)

RECORD_FILE_IF_CHECK_OK=$CURRENT_DIR/check_environment_ok.tmp

BACKGROUND_WHITE='\e[0;30;47m'
BACKGROUND_RESET='\e[0m'

get_python_version(){
    local python_version=$(python3 -V | awk '{print $2}')
    echo $python_version
}

get_python_main_version(){
    local python_version=$1   
    echo ${python_version%.*}
}

get_python_venv_package_name(){
    local python_main_version=$1
    echo "python"$python_main_version"-venv"
}

check_python_version(){
    local python_version=$1
    local major_version=$(echo $python_version | cut -d "." -f 1)
    local miner_version=$(echo $python_version | cut -d "." -f 2)
    
    if [ $major_version -lt $PYTHON_MAJOR_VERSION ]; then
        return $FALSE
    fi
    
    if [ $miner_version -lt $PYTHON_MINOR_VERSION ]; then
        return $FALSE
    fi

    return $TRUE
}

check_python_venv(){
    local python_venv_package=$1
    local check_venv_install=$(dpkg -l | grep $python_venv_package)

    if [ -z "$check_venv_install" ]; then
        return $FALSE
    else
        return $TRUE
    fi
}

check_python_venv_packages(){
    local ret=$TRUE
    for package in "${VENV_PACKAGES[@]}"; do
        check_package=$(pip list | grep -i $package)

        if [ -z "$check_package" ]; then
            echo "need to install package '$package' in venv"
            while true; do
                echo -ne "Do you want to install ${BACKGROUND_WHITE}$package${BACKGROUND_RESET} by pip automatically?"
                read -p " [Y/N] " reply
                
                case $reply in
                    [Yy]* )
                        echo_highlight "pip install $package";
                        pip install $package;
                        exit_stat=$?
                        if [ $exit_stat -ne 0 ]; then
                            echo_highlight "ERROR: pip install $package failed, please fix it"
                            ret=$FALSE
                        fi
                        break;;
                    [Nn]* )
                        ret=$FALSE;
                        break;;
                    * ) echo "Please answer yes or no.";;
                esac
            done
        fi
    done
    return $ret
}

echo_highlight(){
    local str=$1
    echo -e "${BACKGROUND_WHITE}$1${BACKGROUND_RESET}";
}

python_version=$(get_python_version)
python_main_version=$(get_python_main_version $python_version)
python_venv_package=$(get_python_venv_package_name $python_main_version)
echo "python version is $python_version"
echo "python main version is $python_main_version"
echo "expected python venv package is $python_venv_package"


check_python_version $python_version
check_version=$?
if [ $check_version -eq $FALSE ]; then
    echo_highlight "ERROR: need to install python version greater than $PYTHON_MAJOR_VERSION.$PYTHON_MINOR_VERSION, exiting..."
    exit 1
fi

check_python_venv $python_venv_package
check_venv=$?
if [ $check_venv -eq $FALSE ]; then
    echo_highlight "ERROR: need to install $python_venv_package, exiting..."
    exit 1
fi

if [ ! -d "$VENV_PATH" ]; then
    echo_highlight "ERROR: there is no $python_venv_package folder($VENV_PATH) for this app"
    echo_highlight "please generate venv like: $ python3 -m venv venv"
    echo "exiting..."
    exit 1    
fi

source $VENV_PATH/bin/activate
ret=$?

if [ $ret -ne 0 ]; then
    echo_highlight "ERROR: activate venv failed, please check venv environment, exiting..."
    exit 1
fi

check_python_venv_packages
check_venv_package=$?
if [ $check_venv_package -eq $FALSE ]; then
    echo_highlight "ERROR: need to install lacked package, exiting..."
    exit 1
fi

echo "simple environment checks OK"
touch $RECORD_FILE_IF_CHECK_OK