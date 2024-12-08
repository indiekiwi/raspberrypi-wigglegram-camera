#!/bin/bash

check_service_status() {
    local service=$1
    local status=$(systemctl is-active "$service")
    return $( [ "$status" == "active" ] && echo 0 || echo 1 )
}
check_service_status "webserver.service"
WEB_STATUS=$?

check_service_status "hardwareserver.service"
HW_STATUS=$?

if [ $WEB_STATUS -eq 0 ]; then
    echo -e "    \e[32mWeb Server (running)\e[0m"
    echo "        1. Reload"
    echo "        2. Stop"
else
    echo -e "    \e[31mWeb Server (not running)\e[0m"
    echo "        3. Start"
fi
echo ""
if [ $HW_STATUS -eq 0 ]; then
check_service_status "hardwareserver.service"
    echo -e "    \e[32mHardware Server (running)\e[0m"
    echo "    Hardware Server:"
    echo "        4. Reload"
    echo "        5. Stop"
else
    echo -e "    \e[31mHardware Server (not running)\e[0m"
    echo "        6. Start"
fi
echo ""
echo "    7. Exit"
echo ""
read -p "Input: " choice

case $choice in
    1)
        if [ $WEB_STATUS -eq 0 ]; then
            echo "Restarting webserver.service..."
            sudo systemctl restart webserver.service
        fi
        ;;
    2)
        if [ $WEB_STATUS -eq 0 ]; then
            echo "Stopping webserver.service..."
            sudo systemctl stop webserver.service
        fi
        ;;
    3)
        if [ $WEB_STATUS -eq 1 ]; then
            echo "Starting webserver.service..."
            sudo systemctl start webserver.service
        fi
        ;;
    4)
        if [ $HW_STATUS -eq 0 ]; then
            echo "Restarting hardwareserver.service..."
            sudo systemctl restart hardwareserver.service
        fi
        ;;
    5)
        if [ $HW_STATUS -eq 0 ]; then
            echo "Stopping hardwareserver.service..."
            sudo systemctl stop hardwareserver.service
        fi
        ;;
    6)
        if [ $HW_STATUS -eq 1 ]; then
            echo "Starting hardwareserver.service..."
            sudo systemctl start hardwareserver.service
        fi
        ;;
    7)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac
