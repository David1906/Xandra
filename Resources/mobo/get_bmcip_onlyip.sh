#!/bin/bash     
##**********************************************************************************
## Project      : AWS   
## Filename     : get_bmcip.sh
## Description  : Get BMC IP
## Usage        : ./get_bmcip.sh -s $SN
##
## Copyright (c) Since 2019 Foxconn IND., Group. All Rights Reserved
##
## Version History
## -------------------------------
## Version      : 1.0.1
## Release date : 20231102
## Revised by   : Omar Ascencio
## Changelog    : Read only bmc ip
#**********************************************************************************
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

. ${CONFIGPATH}/SKU/${SNPIN}_sku_config

base=$(basename $0)
testitem=${base%.*}
filename="${testitem}.log"
#check_log ${filename}
LOGFILE=${LOGPATH}/${SN}/${filename}
LOGFILETXT=${LOGPATH}/${SN}/bmcip.txt

HEX_MAC(){
    DATA=$1
    D1=`echo -e "$DATA" | awk '{print substr($1,1,2)}'`
    D2=`echo -e "$DATA" | awk '{print substr($1,3,2)}'`
    D3=`echo -e "$DATA" | awk '{print substr($1,5,2)}'`
    D4=`echo -e "$DATA" | awk '{print substr($1,7,2)}'`
    D5=`echo -e "$DATA" | awk '{print substr($1,9,2)}'`
    D6=`echo -e "$DATA" | awk '{print substr($1,11,2)}'`
    MAC="$D1:$D2:$D3:$D4:$D5:$D6"
}

get_bmc_mac(){
    if [[ -f "${LOGPATH}/${SN}/bmcmac.txt" ]];then
        bmcmac=`cat ${LOGPATH}/${SN}/bmcmac.txt`
        
    #else 
    #    echo "No BMC MAC FILE" | tee ${LOGFILE}
    fi 
	

    #while ((1))
    #do 
    #if [[ "$bmcmac" == "00:11:22:33:44:55" ]] || [[ "$bmcmac" == "" ]]; then
    #    read -p "Please enter BMC MAC: " bmcmac
    #    export bmcmac
    #    echo $bmcmac > ${LOGPATH}/${SN}/bmcmac.txt
    #fi

    mac_len=`echo -e "$bmcmac" | awk '{print length($0)}'`
    if [[ "$mac_len" == 12 ]] || [[ "$mac_len" == 17 ]]; then 
        if [[ "$mac_len" == 12 ]];then 
            HEX_MAC $bmcmac
            bmcmac=$MAC
            #echo "BMC MAC is: ${bmcmac}"	
            export bmcmac				
        fi 
	#break
    else 
	#echo -e "The Mac Address length is $mac_len"
    fi
    #done
}

get_ip_from_dhcp(){	
    #echo ${bmcmac,,}  ## change to lowercase
#    arp -n | grep -i ${bmcmac,,} 
    bmcip=`arp -n | grep -i ${bmcmac,,} | awk '{print $1}'`
    if [[ ${#bmcip} -eq 0 ]];then
        dhcpd_leases_file="/var/lib/dhcpd/dhcpd.leases"
        bmcip=`cat ${dhcpd_leases_file} | grep -i "${bmcmac}" -B 8 | awk '/lease / {print $2}'| tail -n1`
    elif [ ${#bmcip} -gt 15 ];then
        ip1=`echo ${bmcip} | awk -F " " '{print $1}'`
        echo ${ip1}
        ping -c 5 ${ip1} 
        ip2=`echo ${bmcip} | awk -F " " '{print $2}'`
        echo ${ip2}
        ping -c 5 ${ip2}
        bmcip=`arp -n | grep -i ${bmcmac,,} | awk '{print $1}'`
    fi

    #echo ${bmcip}
    export bmcip
    echo ${bmcip} > ${LOGFILETXT}
    echo ${bmcip} > ${LOGFILE}
}

get_bmcip(){
    #ping_retry=0
    #while ((1))
    #do 
    #if [[ "$bmcip" == "0.0.0.0" ]] || [[ "$bmcip" == "" ]];then
    #    echo "Please connect the bmc cable to PXE"
    #    read -p "Please enter BMC IP: " bmcip
        export bmcip
        echo $bmcip >  ${LOGPATH}/${SN}/bmcip.txt
        echo $bmcip >> ${LOGFILE}
    #fi

    #    break
   # (( ping_retry++ ))
#    r=$(IPMITOOL raw 6 1)
#    res2=$?
#    echo $r 
#    if [ ${res2} -ne 0 ];then
#        show_fail_msg "IPMITOOL command"
#    fi

#    if [ ${res} -ne 0 ] || [ ${res2} -ne 0 ];then
#        show_fail_msg "BMC FUNCTION"
#        exit 1
#    else
#        echo "BMC IP is working ...."
#        break
#    fi
    #done 
}

get_bmc_mac
get_ip_from_dhcp
get_bmcip

##########################################SHOULD BE MOVE NEXT TIME##################################################
#echo "[ISSUE for Gv2 EVT 20200506 SHORT-SOLUTION] FST is not ready, cause 100% fan overflow" | tee -a ${LOGFILE}
#bmcip_f=$(cat ${LOGPATH}/${SN}/bmcip.txt)
#check_fan=$(ipmitool -I lanplus -H ${bmcip_f} -U admin -P admin raw 0x34 0x68 0x03 | awk '{print $NF}')

### L6
#if [[ ${check_fan} != "3c" ]] && [[ ${stid} == "L6" ]];then
#    echo "Due to noise concern, MFG requests to reduce fan to manual 60%" | tee -a ${LOGFILE}
#    ipmitool -I lanplus -H ${bmcip_f} -U admin -P admin raw 0x34 0x68 0x01 0xff 0x3c
#fi

## RD_HPL (Move to start_test.sh)
#if [[ ${check_fan} != "64" ]] && [[ ${stid} == "RD_HPL" ]];then
#    echo "Due to AWS HPL request, set the fan to manual 100%"
#    ipmitool -I lanplus -H ${bmcip_f} -U admin -P admin raw 0x34 0x68 0x01 0xff 0x64
#fi
###################################################################################################################

