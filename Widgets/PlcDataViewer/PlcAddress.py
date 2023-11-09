class PlcAdress:
    ADDR_MAC = 80  # D80-D91 MAC address
    MAC_LEN = 11

    ADDR_SN = 100  # D100—D116 Serial number
    SN_LEN = 16

    ADDR_DEVICE_NO = 300  # D300 Test fixture number
    ADDR_MODE = 301  # D301 Test fixture automatic/manual mode 0 manual 1 automatic
    ADDR_HEARTBEAT = 302  # D302 The default is 1, we have to write 0 every 10 seconds
    ADDR_TEST_NO = 303  # D303 Test number
    ADDR_TEST_RESULT = 305  # D305 1:Pass 2:Fail 3:stop
    ADDR_REQUEST_MODE = 306  # D306 request mode Request to switch to manual mode 0: No action 1: Make a request
    ADDR_RETURN_MODE = 307  # D307 return mode  Manual mode confirmation 0: No action 1: OK, switchable 2: NG, not switchable
    ADDR_SEND_IN_OUT_ENABLE = (
        308  # D308 0: The elevator does not operate 1: The elevator operates
    )
    ADDR_FIXTURE_STATUS = 309  # D309 1: Request to place the board 2. Testing 3. Test finished 4. Request to take the board
    ADDR_LIFTER = 310  # D310 0: The lift is not in the safe position 1: The lift is in the safe position
    ADDR_SCAN = 311  # D311 1：Scan code NG
    ADDR_FIXTURE_ERROR = 312  # D312 The fixture reports an error

    ADDR_TCCS_TASK_NO = 320  # D320-D335 TCCS task number
    TCCS_TASK_NO_LEN = 15

    ADDR_MODEL_ID = 340  # D340-D355 Model number
    MODEL_ID_LEN = 15

    ADDR_FIXTURE_ID = 360  # D360-D375 Fixture ID
    FIXTURE_ID_LEN = 15

    STARTADDR = ADDR_MAC
    ENDADDR = ADDR_FIXTURE_ID + FIXTURE_ID_LEN

    START_CHUNK1 = STARTADDR
    CHUNK1_LEN = 124
    START_CHUNK2 = STARTADDR + CHUNK1_LEN
    CHUNK2_LEN = 116
    START_CHUNK3 = STARTADDR + CHUNK1_LEN + CHUNK2_LEN
    CHUNK3_LEN = 125
