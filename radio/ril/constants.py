import os.path


def get_header_path(name):
    modpath = os.path.dirname(__file__)
    return os.path.join(modpath, 'headers', name)


STRIP_CHARS = ' ,\n\t\r'

class RequestType:
    def __init__(self, id, name, input, output):
        self.id = id
        self.name = name
        self.input = input
        self.output = output
        
    def __repr__(self):
        return 'Request %d: %s(%s) : %s' % (self.id, self.name, self.input, \
            self.output)
        
class EventType:
    def __init__(self, id, name, output):
        self.id = id
        self.name = name
        self.output = output
        
    def __repr__(self):
        return 'Event %d: %s : %s' % (self.id, self.name, self.output)
        

requests = []
events = []

class MalformedHeaderException(Exception):
    pass
    

def remove_prefix(str, prefix):
    if not str.startswith(prefix):
        print str, prefix
        raise MalformedHeaderException()
    return str[len(prefix):]


def load_constants(prefix):
    f = open(get_header_path('ril.h'), 'rt')
    
    constants = {}

    for line in f:
        line = line.strip(STRIP_CHARS)
        if line.startswith('#define'):
            spl = line.split()
            name = spl[1]
            if name.startswith(prefix):
                value = int(spl[2])
                constants[name] = value
    f.close()
    return constants


def load_requests():
    prefix = 'RIL_REQUEST_'
    constants = load_constants(prefix)

    f = open(get_header_path('ril_commands.h'), 'rt')
    
    for line in f:
        line = line.strip(STRIP_CHARS)
        if line.startswith('{') and line.endswith('}'):
            line = line[1:-1]
            spl = line.split(',')
            name = spl[0].strip(STRIP_CHARS)
            input = spl[1].strip(STRIP_CHARS)
            output = spl[2].strip(STRIP_CHARS)
            if name != '0':
                id = constants[name]
                name = name[len(prefix):].lower()
                input = remove_prefix(input, 'dispatch')
                output = remove_prefix(output, 'response')
                requests.append(RequestType(id, name, input, output))


def load_events():
    prefix = 'RIL_UNSOL_'
    constants = load_constants(prefix)
    
    f = open(get_header_path('ril_unsol_commands.h'), 'rt')
    
    for line in f:
        line = line.strip(STRIP_CHARS)
        if line.startswith('{') and line.endswith('}'):
            line = line[1:-1]
            spl = line.split(',')
            name = spl[0].strip(STRIP_CHARS)
            output = spl[1].strip(STRIP_CHARS)
            if name != '0':
                id = constants[name]
                name = name[len(prefix):].lower()
                output = remove_prefix(output, 'response')
                events.append(EventType(id, name, output))


load_requests()
load_events()


def example():
    for req in requests:
        print req
    for ev in events:
        print ev

if __name__=='__main__':
    example()

'''
Example output:

Request 1: get_sim_status(Void) : SimStatus
Request 2: enter_sim_pin(Strings) : Ints
Request 3: enter_sim_puk(Strings) : Ints
Request 4: enter_sim_pin2(Strings) : Ints
Request 5: enter_sim_puk2(Strings) : Ints
Request 6: change_sim_pin(Strings) : Ints
Request 7: change_sim_pin2(Strings) : Ints
Request 8: enter_network_depersonalization(Strings) : Ints
Request 9: get_current_calls(Void) : CallList
Request 10: dial(Dial) : Void
Request 11: get_imsi(Void) : String
Request 12: hangup(Ints) : Void
Request 13: hangup_waiting_or_background(Void) : Void
Request 14: hangup_foreground_resume_background(Void) : Void
Request 15: switch_waiting_or_holding_and_active(Void) : Void
Request 16: conference(Void) : Void
Request 17: udub(Void) : Void
Request 18: last_call_fail_cause(Void) : Ints
Request 19: signal_strength(Void) : RilSignalStrength
Request 20: registration_state(Void) : Strings
Request 21: gprs_registration_state(Void) : Strings
Request 22: operator(Void) : Strings
Request 23: radio_power(Ints) : Void
Request 24: dtmf(String) : Void
Request 25: send_sms(Strings) : SMS
Request 26: send_sms_expect_more(Strings) : SMS
Request 27: setup_data_call(Strings) : Strings
Request 28: sim_io(SIM_IO) : SIM_IO
Request 29: send_ussd(String) : Void
Request 30: cancel_ussd(Void) : Void
Request 31: get_clir(Void) : Ints
Request 32: set_clir(Ints) : Void
Request 33: query_call_forward_status(CallForward) : CallForwards
Request 34: set_call_forward(CallForward) : Void
Request 35: query_call_waiting(Ints) : Ints
Request 36: set_call_waiting(Ints) : Void
Request 37: sms_acknowledge(Ints) : Void
Request 38: get_imei(Void) : String
Request 39: get_imeisv(Void) : String
Request 40: answer(Void) : Void
Request 41: deactivate_data_call(Strings) : Void
Request 42: query_facility_lock(Strings) : Ints
Request 43: set_facility_lock(Strings) : Ints
Request 44: change_barring_password(Strings) : Void
Request 45: query_network_selection_mode(Void) : Ints
Request 46: set_network_selection_automatic(Void) : Void
Request 47: set_network_selection_manual(String) : Void
Request 48: query_available_networks(Void) : Strings
Request 49: dtmf_start(String) : Void
Request 50: dtmf_stop(Void) : Void
Request 51: baseband_version(Void) : String
Request 52: separate_connection(Ints) : Void
Request 53: set_mute(Ints) : Void
Request 54: get_mute(Void) : Ints
Request 55: query_clip(Void) : Ints
Request 56: last_data_call_fail_cause(Void) : Ints
Request 57: data_call_list(Void) : DataCallList
Request 58: reset_radio(Void) : Void
Request 59: oem_hook_raw(Raw) : Raw
Request 60: oem_hook_strings(Strings) : Strings
Request 61: screen_state(Ints) : Void
Request 62: set_supp_svc_notification(Ints) : Void
Request 63: write_sms_to_sim(SmsWrite) : Ints
Request 64: delete_sms_on_sim(Ints) : Void
Request 65: set_band_mode(Ints) : Void
Request 66: query_available_band_mode(Void) : Ints
Request 67: stk_get_profile(Void) : String
Request 68: stk_set_profile(String) : Void
Request 69: stk_send_envelope_command(String) : String
Request 70: stk_send_terminal_response(String) : Void
Request 71: stk_handle_call_setup_requested_from_sim(Ints) : Void
Request 72: explicit_call_transfer(Void) : Void
Request 73: set_preferred_network_type(Ints) : Void
Request 74: get_preferred_network_type(Void) : Ints
Request 75: get_neighboring_cell_ids(Void) : CellList
Request 76: set_location_updates(Ints) : Void
Request 77: cdma_set_subscription(Ints) : Void
Request 78: cdma_set_roaming_preference(Ints) : Void
Request 79: cdma_query_roaming_preference(Void) : Ints
Request 80: set_tty_mode(Ints) : Void
Request 81: query_tty_mode(Void) : Ints
Request 82: cdma_set_preferred_voice_privacy_mode(Ints) : Void
Request 83: cdma_query_preferred_voice_privacy_mode(Void) : Ints
Request 84: cdma_flash(String) : Void
Request 85: cdma_burst_dtmf(Strings) : Void
Request 86: cdma_validate_akey(String) : Void
Request 87: cdma_send_sms(CdmaSms) : SMS
Request 88: cdma_sms_acknowledge(CdmaSmsAck) : Void
Request 89: gsm_get_broadcast_sms_config(Void) : GsmBrSmsCnf
Request 90: gsm_set_broadcast_sms_config(GsmBrSmsCnf) : Void
Request 91: gsm_sms_broadcast_activation(Ints) : Void
Request 92: cdma_get_broadcast_sms_config(Void) : CdmaBrSmsCnf
Request 93: cdma_set_broadcast_sms_config(CdmaBrSmsCnf) : Void
Request 94: cdma_sms_broadcast_activation(Ints) : Void
Request 95: cdma_subscription(Void) : Strings
Request 96: cdma_write_sms_to_ruim(RilCdmaSmsWriteArgs) : Ints
Request 97: cdma_delete_sms_on_ruim(Ints) : Void
Request 98: device_identity(Void) : Strings
Request 99: exit_emergency_callback_mode(Void) : Void
Request 100: get_smsc_address(Void) : String
Request 101: set_smsc_address(String) : Void
Request 102: report_sms_memory_status(Ints) : Void
Request 103: report_stk_service_is_running(Void) : Void
Event 1000: response_radio_state_changed : Void
Event 1001: response_call_state_changed : Void
Event 1002: response_network_state_changed : Void
Event 1003: response_new_sms : String
Event 1004: response_new_sms_status_report : String
Event 1005: response_new_sms_on_sim : Ints
Event 1006: on_ussd : Strings
Event 1007: on_ussd_request : Void
Event 1008: nitz_time_received : String
Event 1009: signal_strength : RilSignalStrength
Event 1010: data_call_list_changed : DataCallList
Event 1011: supp_svc_notification : Ssn
Event 1012: stk_session_end : Void
Event 1013: stk_proactive_command : String
Event 1014: stk_event_notify : String
Event 1015: stk_call_setup : Ints
Event 1016: sim_sms_storage_full : Void
Event 1017: sim_refresh : Ints
Event 1018: call_ring : CallRing
Event 1019: response_sim_status_changed : Void
Event 1020: response_cdma_new_sms : CdmaSms
Event 1021: response_new_broadcast_sms : String
Event 1022: cdma_ruim_sms_storage_full : Void
Event 1023: restricted_state_changed : Ints
Event 1024: enter_emergency_callback_mode : Void
Event 1025: cdma_call_waiting : CdmaCallWaiting
Event 1026: cdma_ota_provision_status : Ints
Event 1027: cdma_info_rec : CdmaInformationRecords
Event 1028: oem_hook_raw : Raw
'''
