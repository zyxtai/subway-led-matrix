"""Board entry point: record startup before importing the display application."""
import time
import microcontroller
import diagnostic_log

try:
    epoch_offset = 946684800 - int(time.mktime((2000, 1, 1, 0, 0, 0, 5, 1, -1)))
    incidents = diagnostic_log.IncidentLog(microcontroller.nvm, epoch_offset)
except Exception as error:
    incidents = None
    print("Persistent logging unavailable:", type(error).__name__)

diagnostic_log.startup = diagnostic_log.StartupDiagnostics(incidents)
diagnostic_log.startup.first('BOOT', str(microcontroller.cpu.reset_reason))
try:
    import sign_app
except Exception as error:
    diagnostic_log.startup.failure(error)
    raise
