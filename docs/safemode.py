"""Persist CircuitPython's safe-mode reason before normal code can run again."""
try:
    import supervisor
    reason = supervisor.runtime.safe_mode_reason
    # CircuitPython itself skips this file for user-requested safe mode.
    if reason != supervisor.SafeModeReason.USER:
        import time
        import microcontroller
        from diagnostic_log import IncidentLog

        epoch_offset = 946684800 - int(time.mktime((2000, 1, 1, 0, 0, 0, 5, 1, -1)))
        incidents = IncidentLog(microcontroller.nvm, epoch_offset, watchdog=microcontroller.watchdog)
        incidents.record('SAFE_MODE', str(reason))
except Exception as error:
    # USB may not be ready here; this message is only a best-effort fallback.
    print('Safe-mode logging unavailable:', type(error).__name__)
