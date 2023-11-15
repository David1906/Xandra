#!/bin/bash     
. ../commonlib

while getopts s: OPT; do
    case "${OPT}" in
        "s")
            SN=${OPTARG}
            ;;
        *)
            echo "Wrong Parameter..."
            echo "Usage: $(basename $0) -s SN"
            exit 1
            ;;
    esac
done
check_sn

. ./get_bmcip.sh -s ${SN} > /dev/null
. ./load_ip.sh -s ${SN} -k k2v4 > /dev/null

. ${CONFIGPATH}/SKU/${SNPIN}_sku_config
base=$(basename $0)
testitem=${base%.*}
filename="${testitem}.log"
check_log $filename
LOGFILE=${LOGPATH}/${SN}/${filename}
COAPLOG=${LOGPATH}/${SN}/coap_log.json
LAST_SENSOR=${LOGPATH}/${SN}/last_sensor.txt
LAST_SEL=${LOGPATH}/${SN}/last_sel.txt
LAST_K2_LOG=${LOGPATH}/${SN}/last_k2_logs.txt
check_log last_k2_logs.txt
K2_LOG_BDF=${LOGPATH}/${SN}/bdf_list.txt
check_log bdf_list.txt
PCIE_LINK_ERROR=${LOGPATH}/${SN}/pcie_link_error.txt
check_log pcie_link_error.txt
K2_LOG_ERROR=${LOGPATH}/${SN}/k2_log_error.txt
check_log k2_log_error.txt
LAST_LSPCI=${LOGPATH}/${SN}/last_lspci.txt
check_log last_lspci.txt

open_ssh2v4(){
    cd ${NDKPATH}
    tempfile=${LOGPATH}/${SN}/ndk_temp.txt
    ./run_push_keg.sh ${ip_array[4]} ${NDK_KEG} CarbonNDK | tee ${tempfile}
    if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
        echo "Success to open SSH to K2"
    else
        lock=$(cat ${tempfile} | grep -c "locked")
        retry=0
        while ((1))
        do
            ## Found locked
            if [[ ${lock} -ne 0 ]]; then
                echo "sleep 60 and retry"
                sleep 60
                ./run_push_keg.sh ${ip_array[4]} ${NDK_KEG} CarbonNDK | tee ${tempfile}
                if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
                    echo "Success to open SSH to K2"
                    result="PASS"
                    break
                fi
                lock=$(cat ${tempfile} | grep -c "locked")
                retry+=1
            else
                echo "Fail to open SSH to K2 and also no locked found"
                result="FAIL"
                break
            fi

            if [[ ${retry} -gt 5 ]]; then
                echo "Retry over 5 times, k2 card still locked"
                result="FAIL"
                break
            fi
        done
        rm -f ${tempfile}
        if [[ ${result} == "PASS" ]]; then
            echo "Success to open SSH to K2 after retry"
        else
            echo "Failed to open SSH to K2"
            echo "Please check K2 card status"
            errorcode="OPEN_SSH_TO_K2_FAIL"
            show_fail_msg ${errorcode}
            return 1
        fi
    fi
    cd -
}

list_nitro(){
    cd ${NITROPATH}
    ./nitro-bmc -i ${bmcip} sensors list > ${LAST_SENSOR}
    echo "Only show DTS_TEMP|AMB_TEMP, detail please see log: last_sensor.txt"
    cat ${LAST_SENSOR} | egrep "DTS_TEMP|AMB_TEMP"
    ./nitro-bmc -i ${bmcip} sel list > ${LAST_SEL}
    echo "Only show last 15 sel, detail please see log: last_sel.txt"
    cat ${LAST_SEL} | tail -n 15
    cd - >/dev/null 2>&1
}

list_bonito(){
    IPMITOOL sensor list > ${LAST_SENSOR}
    echo "Only show DTS_TEMP|AMB_TEMP, detail please see log: last_sensor.txt"
    cat ${LAST_SENSOR} | egrep "DTS_TEMP|AMB_TEMP"
    IPMITOOL sel list > ${LAST_SEL}
    echo "Only show last 15 sel, detail please see log: last_sel.txt"
    cat ${LAST_SEL} | tail -n 15
}

list_k2_log(){
    DROPLET=${ip_array[4]}
    K2_LOG_LIST=$(coap -O65001,0 -Y coaps+tcp://${DROPLET}/api-v2/logs | egrep "firmware-2.*json|firmware-uc-2.*json")
    err_p=0
    err_t=0
    echo "Check k2 logs to show PCIe/temp error, and save to last_k2_logs.txt"
    for k2_log in ${K2_LOG_LIST[@]}
    do
        echo "Checking: ${k2_log}"
        ## Fail items - PCIe
        coap -O65001,0 -Y coaps+tcp://${DROPLET}/api-v2/logs/${k2_log} | egrep -v "Got unmapped physical MB" | egrep -i "AER Uncorrected Fatal|PCIe ABORT|PCIe.*failed to link"
        if [[ $? -eq 0 ]];then
            coap -O65001,0 -Y coaps+tcp://${DROPLET}/api-v2/logs/${k2_log} | grep "bdf" >> ${K2_LOG_BDF}
            coap -O65001,0 -Y coaps+tcp://${DROPLET}/api-v2/logs/${k2_log} | grep "PCIe.*failed to link" >> ${PCIE_LINK_ERROR}
            (( err_p++ ))
        fi
        ## Fail items - temp
        coap -O65001,0 -Y coaps+tcp://${DROPLET}/api-v2/logs/${k2_log} | grep -i "SOC temperature is out of threshold range"
        if [[ $? -eq 0 ]];then
            (( err_t++ ))
        fi

        echo "Saving: ${k2_log}"
        echo "${k2_log}" >> ${LAST_K2_LOG}
        coap -O65001,0 -Y coaps+tcp://${DROPLET}/api-v2/logs/${k2_log} >> ${LAST_K2_LOG}
        echo "" >> ${LAST_K2_LOG}
    done

    if [[ ${err_p} -ne 0 ]] || [[ ${err_t} -ne 0 ]];then
        echo -ne "\033[31m"
        echo -e "Found ${err_p} log(s) with PCIe ERROR!"
        if [[ ${err_p} -ne 0 ]];then
            cat ${K2_LOG_BDF}
            cat ${PCIE_LINK_ERROR}
            echo ""
            k2_0_error=$(cat ${K2_LOG_BDF} | grep -c "(1:)0:0.0")
            k2_1_error=$(cat ${K2_LOG_BDF} | grep -c "(0:)0:0.0")
            k2_2_error=$(cat ${K2_LOG_BDF} | grep -c "(0:)0:2.0")
            k2_3_error=$(cat ${K2_LOG_BDF} | grep -c "(3:)0:0.0")
            ssd_error=$(cat ${K2_LOG_BDF} | grep -c "(2:)0:1.0")
            pcie_error=$(cat ${PCIE_LINK_ERROR} | grep -c "PCIe.*failed to link")
            if [[ ${k2_0_error} -ne 0 ]];then
                echo "Please check port3/K2V4#0(MP)" | tee -a  ${K2_LOG_ERROR}
            fi
            if [[ ${k2_1_error} -ne 0 ]];then
                echo "Please check port0/K2V4#1" | tee -a  ${K2_LOG_ERROR}
            fi
            if [[ ${k2_2_error} -ne 0 ]];then
                echo "Please check port2/K2V4#2" | tee -a  ${K2_LOG_ERROR}
            fi
            if [[ ${k2_3_error} -ne 0 ]];then
                echo "Please check port9/K2V4#3" | tee -a  ${K2_LOG_ERROR}
            fi
            if [[ ${ssd_error} -ne 0 ]];then
                echo "Please check port7/SSD" | tee -a  ${K2_LOG_ERROR}
            fi
            if [[ ${pcie_error} -ne 0 ]];then
                cat ${PCIE_LINK_ERROR} | grep "PCIe.*failed to link" | awk -F ',' '{print $4}' | tee -a  ${K2_LOG_ERROR}
            fi
            if [[ ${k2_0_error} -eq 0 ]] && [[ ${k2_1_error} -eq 0 ]] && [[ ${k2_2_error} -eq 0 ]] && [[ ${k2_3_error} -eq 0 ]] && [[ ${ssd_error} -eq 0 ]] && [[  ${pcie_error} -eq 0 ]];then
                echo "Please SOL to MB SoC" | tee -a  ${K2_LOG_ERROR}
                echo "Under the SOL to MB SoC state, run UUT Reset script with -o parameter to DC the system in another terminal and check whick PCIe got ERROR" | tee -a  ${K2_LOG_ERROR}
            fi
        fi
        echo -e "Found ${err_t} log(s) with temp ERROR!"
        echo -ne "\033[0m"
        return 1
    else
        return 0
    fi
}

delete_k2_log(){
    open_ssh2v4
    if [[ $? -ne 0 ]];then
        return 1
    fi

    echo "Delete old k2 logs in /local/logs/archive"
    /usr/bin/expect << K2V4_SSH
    spawn ${SSH[4]}
    set timeout 60
    expect "~ #"
    send "cd /local/logs/archive\r"
    expect "/local/logs/archive #"
    send "rm *\r"
    send "exit\r"
    expect eof
K2V4_SSH

    echo -e "\rDelete old k2 logs in /local/logs-v2"
    /usr/bin/expect << K2V4_SSSSH 
    spawn ${SSH[4]}
    set timeout 60
    expect "~ #"
    send "cd /local/logs-v2\r"
    expect "/local/logs-v2 #"
    send "rm -r *\r"
    send "exit\r"
    expect eof
K2V4_SSSSH

    #DROPLET=${ip_array[4]}
    #K2_LOG_LIST=$(coap -O65001,0 -Y coaps+tcp://${DROPLET}/api-v2/logs | egrep "firmware-2.*json|firmware-uc-2.*json")

    #echo "Delete old k2 logs"
    #for k2_log in ${K2_LOG_LIST[@]}
    #do
    #    echo "Delete: ${k2_log}"
    #    coap -O65001,0 -Y -m PUT coaps+tcp://${DROPLET}/api-v1/debug/utils/delete?file=/local/logs-v2/${k2_log}
    #done
}

save_lspci(){
    echo "Save lspci in log, for detail, please see log: last_lspci.txt"
    echo "LSPCI LIST" > ${LAST_LSPCI}
    echo "" >> ${LAST_LSPCI}
    for h in ${MB_LIST[@]}
    do
        txt=${LOGPATH}/${SN}/mb${h}_ip.txt
        target=$(cat ${txt})
        SSH="sshpass -p 123456 ssh -o StrictHostKeyChecking=no root@${target}"
        echo "MB${h} lspci" >> ${LAST_LSPCI}
        ${SSH} "lspci -vvv" >> ${LAST_LSPCI}
    done
}

run_process(){
    is_nitro=$(run_command -l ${COAPLOG} -r 3 coap -O65001,0 -Y -m GET coaps+tcp://${ip_array[4]}/api-v1/bmc/mc | grep -i "firmware_revision" | grep -c '"9\.*')
    if [[ ${is_nitro} -gt 0 ]]; then
        list_nitro 
    else
        list_bonito
    fi
    list_k2_log
    res=$?
    if [[ "${stid}" == "L6" ]] || [[ "${PROJECT}" == "HANUMAN00MB" ]] || [[ "${PROJECT}" == "HANUMAN00MP" ]] || [[ "${PROJECT}" == "HANUMAN00" ]];then
        l6=1
        delete_k2_log
        if [[ $? -ne 0 ]];then
            show_fail_msg "Failed to open SSH to K2, remove k2 logs fail"
        fi
        save_lspci
    fi

    if [[ ${res} -ne 0 ]]; then
        echo -ne "\033[31m"
        echo ""
        if [[ ${l6} -eq 1 ]];then
            echo "For lspci detail, please see log: last_lspci.txt"
        fi
        echo "Found something wrong in k2 logs, please check the error message above"
        echo "For sensor/sel/k2 log detail, please see log: last_sensor.txt, last_sensor.txt, last_k2_logs.txt"
        echo -ne "\033[0m"
    else
        echo ""
        if [[ ${l6} -eq 1 ]];then
            echo "For lspci detail, please see log: last_lspci.txt"
        fi
        echo "For sensor/sel/k2 log detail, please see log: last_sensor.txt, last_sensor.txt, last_k2_logs.txt"
    fi
}

run_process | tee -a ${LOGFILE}
