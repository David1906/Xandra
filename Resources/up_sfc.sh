#!/bin/bash
. ../commonlib
while getopts s: OPT; do
    case "${OPT}" in
        "s")
            BSN=${OPTARG}
            ;;
        *)
            echo "Wrong Parameter..."
            echo "Usage: $(basename $0) -s BSN -p logpath"
            exit 1
            ;;
    esac
done


SNPIN=${BSN:0:9}
. ${CONFIGPATH}/${SNPIN}/${SNPIN}_sku_config

base=$(basename $0)
testitem=${base%.*}
filename="${testitem}.log"
check_log ${filename}
LOGFILE=${LOGPATH}/${BSN}/$filename
# Disabled for retest . ./get_bmcip.sh -s ${BSN}

StationID=${Station_ID}
FILE=${LOGPATH}/${BSN}/StationID.txt
if [ -e ${FILE} ]; then
    StationID=$(<${LOGPATH}/${BSN}/StationID.txt)
fi

SN_ID="${StationID}${BSN}"
PN_ID="${SNPIN}-600-G"
mac=${MAC}

OP_ID=$(cat ${LOGPATH}/${BSN}/OPID.txt)
if [ -z "$OP_ID" ]; then
    OP_ID="Lunar"
fi

mount_sfc()
{

    sfc_exist=$(mount | grep -cE "Lunar.*./home/Project/Station")
    if [[ ${sfc_exist} -eq 0 ]];then 
    
        mount -v -t cifs -o username=$USERNAME,password=$PASSWORD,sec=ntlm //$SERVERIP/Lunar /home/Project/Station  > /dev/null
        wRet=" $? "
        if [ $wRet = 0 ];then
            show_pass_msg "Mount SFC Station folder"
        else
            show_fail_msg "Mount SFC Station folder"
            exit 1
        fi	

    fi 

}

send_log()
{
     echo -e "${Station_ID}\n${BSN}\n${OP_ID}\nPASS\n0" > ${LOGPATH}/${BSN}/${SN_ID}.LOG
     cd /home/Project/Station
     if [ -f $SN_ID.* ];then
            rm -f $SN_ID.*
     fi
     for (( x=0;x<3;x++ )); do
     cp -rf ${LOGPATH}/${BSN}/${SN_ID}.LOG  .
     sleep 1      
 
     if [ -f ${SN_ID}.EEE ];then
        show_pass_msg "Get ${SN_ID}.EEE"
        cp -rf $SN_ID.EEE ${LOGPATH}/${BSN}
        break
     elif [ -f ${SN_ID}.FFF ];then
        show_fail_msg "Get ${SN_ID}.FFF"
        cat ${SN_ID}.FFF
        exit 1
     elif [ $x -eq 2 ];then
        show_fail_msg "Get ${SN_ID}.EEE"
        exit 1
     fi
   done

}


## MAIN

show_title_msg "${testitem}" | tee -a ${LOGFILE}
START=$(date)


echo "Mount SFC share folders"

mount_sfc | tee -a ${LOGFILE}
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    exit 1
fi

sleep 1

###################################################################################
#send_xxx for test!
###################################################################################
echo "Upload result to sfc"
send_log | tee -a ${LOGFILE}
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    exit 1
fi

cd /home/Project/Station
rm -rf ${SN_ID}.EEE  ${SN_ID}.FFF ${SN_ID}.LOG
rm -rf ${LOGPATH}/${BSN}/${SN_ID}.FFF

show_end_msg | tee -a ${LOGFILE}

