"""Record safe mode and recover unattended operation after a native hard fault."""
RECOVERY_DELAY_SECONDS = 30

try:
    import supervisor
    import time
    import microcontroller

    reason = supervisor.runtime.safe_mode_reason
    # CircuitPython itself skips this file for user-requested safe mode.
    if reason != supervisor.SafeModeReason.USER:
        try:
            from diagnostic_log import IncidentLog

            epoch_offset = 946684800 - int(time.mktime((2000, 1, 1, 0, 0, 0, 5, 1, -1)))
            incidents = IncidentLog(microcontroller.nvm, epoch_offset, watchdog=microcontroller.watchdog)
            incidents.record('SAFE_MODE', str(reason))
            if reason == supervisor.SafeModeReason.HARD_FAULT:
                incidents.record('RECOVERY_REQUEST', str(reason)+' delay=30s')
        except Exception as error:
            print('Safe-mode logging unavailable:', type(error).__name__)
        if reason == supervisor.SafeModeReason.HARD_FAULT:
            # A repeated crash waits on every attempt; other safe modes stay open.
            time.sleep(RECOVERY_DELAY_SECONDS)
            microcontroller.reset()
except Exception as error:
    # USB may not be ready here; this message is only a best-effort fallback.
    print('Safe-mode recovery unavailable:', type(error).__name__)
